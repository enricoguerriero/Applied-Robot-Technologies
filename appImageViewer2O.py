#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/appImageViewer2.py
#
#  Extends appImageViewer1 by adding some more functionality using heritage.
#  Now program can capture an image from an IDS camera attached to the USB 
#  gate of the computer. This program also requires IDS pyueye package,
#  https://pypi.org/project/pyueye/ 
#  This program adds only some few methods to appImageViewer1,
#  methods that should make it possible to capture a single image. The new 
#     camera menu has actions for: Camera On, Get One Image, and Camera Off
#  Program tested using IDS XS camera (the small one at UiS, the larger one is CP)
#
#  appImageViewer1.py is basically developed by copying the file appImageViewer.py
#  and then make the wanted changes and additions. This may be a good way to 
#  make a new program, but it also has some disadvantages; if you want to keep and
#  improve the original program, the new improvements should probably also be
#  done in the copied file (appImageViewer1.py) and you thus have to maintain the
#  common code in two files. 
#  
#  A better way to copy functionality is to use heritage. This is the approach done here,
#  the main window in this file is imported from appImageViewer1.py, and then new
#  functionality is added, or existing functionality may be updated. 
#
#  The user manual for IDS camera uEye software development kit (SDK) is helpful
#  for finding and using the IDS interface functions, it used to be available on
#  https://en.ids-imaging.com/manuals/uEye_SDK/EN/uEye_Manual_4.91/index.html
#  but the requested page cannot be found any more (is it somewhere else, like:
#  https://en.ids-imaging.com/files/downloads/ids-software-suite/interfaces/release-notes/python-release-notes_EN.html 
#  https://en.ids-imaging.com/release-note/release-notes-ids-software-suite-4-90.html 
#  http://en.ids-imaging.com/ueye-interface-python.html  (??)
#  ** now it is installed when IDS SW is installed, on my (KS) laptop it is located:
# file:///C:/Program%20Files/IDS/uEye/Help/uEye_Manual/index.html#is_exposuresetexposure.html
#  Also, I have a copy of the SDK user manual September 2008 version on:
#  ...\Dropbox\ELE610\IDS camera\IDS_uEye_SDK_manual_enu*.pdf
#
# Karl Skretting, UiS, November 2018, February 2019, November 2020, June 2022

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> python appImageViewer2.py
# (py38) C:\..\py3> python appImageViewer2.py rutergray.png

_appFileName = "appImageViewer2"
_author = "Karl Skretting, UiS" 
_version = "2022.06.27"

import keyword
import sys
import os.path
from time import sleep
import cv2
import time

import numpy as np

try:
	from clsThresholdDialog import ThresholdDialog
	from PyQt5.QtCore import Qt, QPoint, QRectF, QT_VERSION_STR
	from PyQt5.QtGui import QImage, QPixmap, QTransform
	from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, 
			QGraphicsScene, QGraphicsPixmapItem)
except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes

try:
	from pyueye import ueye
	from pyueye_example_camera import Camera
	from pyueye_example_utils import ImageData, ImageBuffer  # FrameThread, 
	ueyeOK = True
except ImportError:
	ueye_error = f"{_appFileName}: Requires IDS pyueye example files (and IDS camera)." 
	# raise ImportError(ueye_error)
	ueyeOK = False   # --> may run program even without pyueye
#end try, import pyueye

from appImageViewer1O import myPath, MainWindow as inheritedMainWindow 
from myImageTools import np2qimage

class MainWindow(inheritedMainWindow):  
	"""MainWindow class for this image viewer is inherited from another image viewer."""
	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		# print( f"File {_appFileName}: (debug) first line in MainWindow.__init__()" )
		super().__init__(fName, parent)  # use inherited __init__ with extension as follows
		# 
		# set appFileName as it should be, it is set wrong in super()...
		self.appFileName = _appFileName 
		if self.pixmap.isNull(): 
			self.setWindowTitle(self.appFileName)
			self.npImage = np.array([])  # size == 0  
		else:
			self.setWindowTitle( f"{self.appFileName} : {fName}" ) 
			self.pixmap2image2np()   # function defined in appImageViewer1.py
		# 
		self.cam = None
		self.camOn = False
		#
		# I had some trouble finding a good way to inherit (and add modifications to) 
		# functions 'initMenu' and 'setMenuItems' from appImageViewer1
		# To avoid any complications the corresponding functions are given new names here,
		# thus risking that the inherited (or the new ones) are not executed whenever they should be.
		self.initMenu2()
		self.setMenuItems2()
		# print(f"File {_appFileName}: (debug) last line in MainWindow.__init__()")
		return
	
	def initMenu2(self):
		"""Initialize Camera menu."""
		# print( f"File {_appFileName}: (debug) first line in initMenu2()" ) 
		a = self.qaCameraOn = QAction('Camera on', self)
		a.triggered.connect(self.cameraOn)
		#
		a = self.qaCameraInfo = QAction('Print camera info', self)
		a.triggered.connect(self.printCameraInfo)
		#
		a = self.qaGetOneImage = QAction('Get one image', self)
		a.setShortcut('Ctrl+N')
		a.triggered.connect(self.getOneImage)
		#
		a = self.qaGetOneImageV2 = QAction('Get one image (ver.2 2022)', self)
		a.triggered.connect(self.getOneImageV2)
		#
		a = self.qaCameraOff = QAction('Camera off', self)
		a.triggered.connect(self.cameraOff)
		#
		a = self.qanewcamerafunction = QAction('New camera function', self)
		a.triggered.connect(self.newCameraFunction)
		#
		a = self.qaBlackDots = QAction('Add black dots', self)
		a.triggered.connect(self.blackDots)
		#
		a = self.qaFindCircles = QAction('Find circles', self)
		a.triggered.connect(self.findCircles)
		#
		a = self.qaCountEyes = QAction('Count eyes', self)
		a.triggered.connect(self.countEyes)			
		#
		a = self.qaVideoOn = QAction('Count eyes in video', self)
		a.triggered.connect(self.videoOn)	
		#
		camMenu = self.mainMenu.addMenu('&Camera')
		camMenu.addAction(self.qaCameraOn)
		camMenu.addAction(self.qaCameraInfo)
		camMenu.addAction(self.qaGetOneImage)
		camMenu.addAction(self.qaGetOneImageV2)
		camMenu.addAction(self.qaCameraOff)
		camMenu.addAction(self.qanewcamerafunction)
		# print( "File {_appFileName}: (debug) last line in initMenu2()" ) 
		diceMenu = self.mainMenu.addMenu('&Dice')
		diceMenu.addAction(self.qaBlackDots)
		diceMenu.addAction(self.qaFindCircles)
		diceMenu.addAction(self.qaCountEyes)
		diceMenu.addAction(self.qaVideoOn)
		return
	
# Some methods that may be used by several of the menu actions
	def setMenuItems2(self):
		"""Enable/disable menu items as appropriate."""
		# should the 'inherited' function be used, first check if it exists 
		setM = getattr(super(), "setMenuItems", None)  # both 'self' and 'super()' seems to work as intended here
		if callable(setM):
			# print("setMenuItems2(): The 'setMenuItems' function is inherited.")
			setM()  # and run it
		# self.setMenuItems() 
		self.qaCameraOn.setEnabled(ueyeOK and (not self.camOn))
		self.qaCameraInfo.setEnabled(ueyeOK and self.camOn)
		self.qaGetOneImage.setEnabled(ueyeOK and self.camOn)
		self.qaGetOneImageV2.setEnabled(ueyeOK and self.camOn)
		self.qaCameraOff.setEnabled(ueyeOK and self.camOn)
		return
		
	def copy_image(self, image_data):
		"""Copy an image from camera memory to numpy image array 'self.npImage'."""
		tempBilde = image_data.as_1d_image()
		if np.min(tempBilde) != np.max(tempBilde):
			self.npImage = np.copy(tempBilde[:,:,[0,1,2]])  # or [2,1,0] ??  RGB or BGR?
			print( ("copy_image(): 'self.npImage' is an ndarray" + 
					f" of {self.npImage.dtype.name}, shape {str(self.npImage.shape)}.") )
		else: 
			self.npImage = np.array([])  # size == 0
		#end if 
		image_data.unlock()  # important action
		return 
		
# Methods for actions on the Camera-menu
# dette gir ikke samme muligheter som IDS program, autofokus for XS kamera virker ikke her
	def cameraOn(self):
		"""Turn IDS camera on."""
		if ueyeOK and (not self.camOn):
			self.cam = Camera()
			self.cam.init()  # gives error when camera not connected
			self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
			# This function is currently not supported by the camera models USB 3 uEye XC and XS.
			self.cam.set_aoi(0, 0, 720, 1280)  # but this is the size used
			self.cam.alloc(3)  # argument is number of buffers
			self.camOn = True
			self.setMenuItems2()
			print( f"{self.appFileName}: cameraOn() Camera started ok" )
		#
		return
	
	def printCameraInfo(self):
		"""Print some information on camera."""
		if ueyeOK and self.camOn:
			print("printCameraInfo(): print (test) state and settings.")
			# just set a camera option (parameter) even if it is not used here
			d = ueye.double()
			# d1 = ueye.double() 
			# d2 = ueye.double()
			ui1 = ueye.uint()
			retVal = ueye.is_SetFrameRate(self.cam.handle(), 2.0, d)
			if retVal == ueye.IS_SUCCESS:
				print( f"  frame rate set to                      {float(d):8.3f} fps" )
			retVal = ueye.is_Exposure(self.cam.handle(), 
									  ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_DEFAULT, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  default setting for the exposure time  {float(d):8.3f} ms" )
			retVal = ueye.is_Exposure(self.cam.handle(), 
									  ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  minimum exposure time                  {float(d):8.3f} ms" )
			retVal = ueye.is_Exposure(self.cam.handle(), 
									  ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  maximum exposure time                  {float(d):8.3f} ms" )
			# 
			print( f"  sys.getsizeof(d) returns   {sys.getsizeof(d)}  (??)" )
			print( f"  sys.getsizeof(ui1) returns {sys.getsizeof(ui1)}  (??)" )
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FDT_CMD_GET_CAPABILITIES, ui1, 4)
			if ((retVal == ueye.IS_SUCCESS) and (ui1 & ueye.FOC_CAP_AUTOFOCUS_SUPPORTED)):
				print( "  autofocus supported" )
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus() is success          ui1 = {ui1}" )
			else:
				print( f"  is_Focus() is NOT success   retVal = {retVal}" )
			fZR = ueye.IS_RECT()   # may be used to set focus ??
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS, ui1, 0)
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus( ENABLE ) is success      " )
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FOC_CMD_GET_AUTOFOCUS_STATUS, ui1, 4)
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus( STATUS ) is success  ui1 = {ui1}" )
			# her slutter det jeg testet ekstra i 2021
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  currently set exposure time            {float(d):8.3f} ms" )
			d =  ueye.double(5.0)
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  tried to changed exposure time to      {float(d):8.3f} ms" )
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  currently set exposure time            {float(d):8.3f} ms" )
			#
		return
		
	def getOneImageV2(self):
		"""Get one image from IDS camera, version 2, autumn 2022."""
		if not(ueyeOK and self.camOn): 
			# pass  # ignore action
			#else:  
			return
		
		self.view.setMouseTracking(False)
		print( f"{self.appFileName}: getOneImageV2() try to capture one image" )
		imBuf = ImageBuffer()  
		self.cam.freeze_video(True)
		# some sleep does not help
		# sleep(2.5)
		# self.cam.freeze_video(False)
		# sleep(2.5)
		# self.cam.freeze_video(True)
		# function below obsolete in UDS 4.95 -->
		# use is_ImageQueue(), see: https://en.ids-imaging.com/release-note/release-notes-ids-software-suite-4-95.html
		retVal = ueye.is_WaitForNextImage(self.cam.handle(), 1000, imBuf.mem_ptr, imBuf.mem_id)
		if retVal == ueye.IS_SUCCESS:
			print( f"  ueye.IS_SUCCESS: image buffer id = {imBuf.mem_id}" )
			self.copy_image( ImageData(self.cam.handle(), imBuf) )  
			if (self.npImage.size > 0): 
				self.image = np2qimage(self.npImage)
				if (not self.image.isNull()):
					self.pixmap = QPixmap.fromImage(self.image)
					if self.curItem: 
						self.scene.removeItem(self.curItem)
					self.curItem = QGraphicsPixmapItem(self.pixmap)
					self.scene.addItem(self.curItem)
					self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
					self.setWindowTitle( f"{self.appFileName} : Camera image" ) 
					(w,h) = (self.pixmap.width(), self.pixmap.height())
					self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
					self.scaleOne()
					self.view.setMouseTracking(True)
				else:
					self.pixmap = QPixmap()
			else:  
				self.image = QImage()
				self.pixmap = QPixmap()
				print( "  no image in buffer " + str(imBuf) )
		else: 
			self.setWindowTitle( "{self.appFileName}: getOneImage() error retVal = {retVal}" )
		self.setIsAllGray()
		self.setMenuItems2()
		return
	
	def getOneImage(self):
		"""Get one image from IDS camera."""
		if ueyeOK and self.camOn:
			self.view.setMouseTracking(False)
			print( f"{self.appFileName}: getOneImage() try to capture one image" )
			imBuf = ImageBuffer()  
			self.cam.freeze_video(True)
			retVal = ueye.is_WaitForNextImage(self.cam.handle(), 1000, imBuf.mem_ptr, imBuf.mem_id)
			if retVal == ueye.IS_SUCCESS:
				print( f"  ueye.IS_SUCCESS: image buffer id = {imBuf.mem_id}" )
				self.copy_image( ImageData(self.cam.handle(), imBuf) ) 
				if (self.npImage.size > 0):  
					self.image = np2qimage(self.npImage)
					if (not self.image.isNull()):
						self.pixmap = QPixmap.fromImage(self.image)
						if self.curItem: 
							self.scene.removeItem(self.curItem)
						self.curItem = QGraphicsPixmapItem(self.pixmap)
						self.scene.addItem(self.curItem)
						self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
						self.setWindowTitle( f"{self.appFileName} : Camera image" ) 
						(w,h) = (self.pixmap.width(), self.pixmap.height())
						self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
						self.scaleOne()
						self.view.setMouseTracking(True)
					else:
						self.pixmap = QPixmap()
				else:  
					self.image = QImage()
					self.pixmap = QPixmap()
					print( "  no image in buffer " + str(imBuf) )
			else: 
				self.setWindowTitle( "{self.appFileName}: getOneImage() error retVal = {retVal}" )
			self.setIsAllGray()
			self.setMenuItems2()

	def cameraOff(self):
		"""Turn IDS camera off and print some information."""
		if ueyeOK and self.camOn:
			self.cam.exit()
			self.camOn = False
			self.setMenuItems2()
			print( f"{self.appFileName}: cameraOff() Camera stopped ok" )
		return

	def videoOn(self):
		start_time = time.time()
		# Durata del timer in secondi
		timer_duration = 20
		elapsed_time = 0
		print("prova2")
		while elapsed_time <= timer_duration:
			elapsed_time = time.time() - start_time
			self.getOneImageV2()
			print("prova")
			time.sleep(5)
			#self.findCircles()
			#self.countEyes()
   
		print("ciao")
		return

	def newCameraFunction(self):
		"""Get two different images from IDS camera and compute their difference."""
		
		if ueyeOK and self.camOn:

			print(f"{self.appFileName}: newCameraFunction() try to capture the first image")
			self.getOneImage()  
			firstImage = self.npImage 
   
			time.sleep(10)
   
			print(f"{self.appFileName}: newCameraFunction() try to capture the second image")
			self.getOneImage()  
			secondImage = self.npImage  

			if firstImage.shape == secondImage.shape:
				differenceImage = np.abs(firstImage.astype(np.int16) - secondImage.astype(np.int16))
				differenceImage = np.clip(differenceImage, 0, 255).astype(np.uint8)  
				
				differenceQImage = np2qimage(differenceImage)
				
				self.differencePixmap = QPixmap.fromImage(differenceQImage)
				if self.curItem:
					self.scene.removeItem(self.curItem)
				self.curItem = QGraphicsPixmapItem(self.differencePixmap)
				self.scene.addItem(self.curItem)
				self.scene.setSceneRect(0, 0, self.differencePixmap.width(), self.differencePixmap.height())
				self.setWindowTitle(f"{self.appFileName} : Difference Image")
				(w, h) = (self.differencePixmap.width(), self.differencePixmap.height())
				self.status.setText(f"Difference Image: (w,h) = ({w},{h})")
				self.scaleOne()
				self.view.setMouseTracking(True)
			else:
				print("The images have different sizes, cannot compute the difference.")
		else:
			print(f"{self.appFileName}: Camera is not on or ueyeOK is not set.")
		
		return
  
	def blackDots(self):
		grayscale_image = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2GRAY)
		self.prevPixmap = self.pixmap   
		#d = ThresholdDialog(parent=B)   # create object (but does not run it)
		#t = 60  # display dialog and return values
		(used_thr,grayscale_image) = cv2.threshold(grayscale_image, thresh=60, maxval=255, type=cv2.THRESH_BINARY)
  
		# Applica una soglia per ottenere un'immagine binaria
		_, binary_image = cv2.threshold(grayscale_image, thresh=60, maxval=255, type=cv2.THRESH_BINARY_INV)

		# Definisci un kernel (matrice) per le operazioni morfologiche
		kernel = np.ones((3, 3), np.uint8)

		# Applica l'operazione di apertura per rimuovere il rumore (erosione seguita da dilatazione)
		opened_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

		# Trova i contorni nell'immagine binaria
		contours, _ = cv2.findContours(opened_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		# Crea un'immagine vuota per disegnare solo i cerchi trovati
		output_image = np.zeros_like(grayscale_image)

		# Filtro i contorni per mantenere solo i cerchi
		for contour in contours:
			# Calcola l'area del contorno
			area = cv2.contourArea(contour)
			
			# Ignora i contorni troppo piccoli o troppo grandi
			if area < 50 or area > 10000:
				continue
			
			# Approssima il contorno a un cerchio e calcola la rotondità
			perimeter = cv2.arcLength(contour, True)
			circularity = 4 * np.pi * (area / (perimeter ** 2))
			
			# Se la rotondità è prossima a 1, è probabile che sia un cerchio
			if 0.7 < circularity < 1.2:
				cv2.drawContours(output_image, [contour], -1, 255, thickness=cv2.FILLED)
    
		inverted_image = cv2.bitwise_not(output_image)
		self.npImage = inverted_image
  
		print( f"toBinary: The used threshold value is {used_thr}" )
		self.np2image2pixmap(inverted_image, numpyAlso=True)
		self.setWindowTitle( f"{self.appFileName} : binary image with only circle" )
		return

	def prepareHoughCirclesA(self):
		"""Make self.A the gray scale image to detect circles in"""
		if (self.A.size == 0):
			if (len(self.npImage.shape) == 3):
				if (self.npImage.shape[2] == 3):
					self.A = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2GRAY )
					self.B = self.npImage.copy()
				elif (self.npImage.shape[2] == 4):
					self.A = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2GRAY )
					self.B = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2BGR )   
				else:
					print("prepareHoughCircles(): numpy 3D image is not as expected. --> return")
					return
			elif (len(self.npImage.shape) == 2):
				self.A = self.npImage.copy()
				self.B = cv2.cvtColor(self.npImage, cv2.COLOR_GRAY2BGR )   
			else:
				print("prepareHoughCircles(): numpy image is not as expected. --> return")
				return
		return
		
	def prepareHoughCirclesB(self):
		"""Make self.B the BGR image to draw detected circles in"""
		if (len(self.npImage.shape) == 3):
			if (self.npImage.shape[2] == 3):
				self.B = self.npImage.copy()
			elif (self.npImage.shape[2] == 4):
				self.B = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2BGR )   
		elif (len(self.npImage.shape) == 2):
			self.B = cv2.cvtColor(self.npImage, cv2.COLOR_GRAY2BGR )   
		return
		
	def tryHoughCircles(self, t):
		"""Simply display results for the parameters given in tuple 't', without committing."""
		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = t
		print("tryHoughCircles(): now called using:")
		print(f"t = (dp={dp}, minDist={minDist}, param1={param1}, param2={param2}, minRadius={minRadius}, maxRadius={maxRadius})")

		self.prepareHoughCirclesA()  
		C = cv2.HoughCircles(self.A, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
					param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

		self.prepareHoughCirclesB()  
		if C is not None:
			C = np.int16(np.around(C))
			print(f"  'C'  is ndarray of {C.dtype.name}, shape: {str(C.shape)}")
			print(f"  Found {C.shape[1]} circles with radius from {C[0,:,2].min()} to {C[0,:,2].max()}")
			for i in range(min(maxCircles, C.shape[1])):
				(x,y,r) = ( C[0,i,0], C[0,i,1], C[0,i,2] ) 
				cv2.circle(self.B, (x,y), r, (255, 0, 255), 2) 
				print(f"  circle {i} has center in ({x},{y}) and radius {r}")
		self.np2image2pixmap(self.B, numpyAlso=False)   
		return
	
	def findCircles(self):
		"""Find circles in active image using HoughCircles(..)."""
		oldPixmap = self.prevPixmap  
		self.prevPixmap = self.pixmap
		self.A = np.array([])  
		self.prepareHoughCirclesA()  

		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = (2, 40, 100, 60, 20, 60, 20)
		C = cv2.HoughCircles(self.A, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
				param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

		self.prepareHoughCirclesB()  
		if C is not None:
			C = np.int16(np.around(C))
			print(f"  'C'  is ndarray of {C.dtype.name}, shape: {str(C.shape)}")
			self.neyes = C.shape[1]
			for i in range(min(maxCircles, C.shape[1])):
				(x,y,r) = ( C[0,i,0], C[0,i,1], C[0,i,2] )  
				cv2.circle(self.B, (x,y), r, (0, 0, 255), 3) 
		self.A = np.array([])  
		self.np2image2pixmap(self.B, numpyAlso=True)
		self.B = np.array([])  
		self.setWindowTitle(f"{self.appFileName} indicate found circles.")

		return

	def countEyes(self):
		"""A function to count the number of eyes once black dots are added to the image."""
		if self.neyes:
			print(f"Number of eyes: {self.neyes}")
			self.setWindowTitle(f"{self.appFileName}: (Number of eyes: {self.neyes})")
		else:
			print("You have to use FindCircle or BlackDots.")   
 
				  
#end class MainWindow

if __name__ == '__main__':
	print( f"{_appFileName}: (version {_version}), path for images is: {myPath}" )
	print( f"{_appFileName}: Using Qt {QT_VERSION_STR}" )
	mainApp = QApplication(sys.argv)
	if (len(sys.argv) >= 2):
		fn = sys.argv[1]
		if not os.path.isfile(fn):
			fn = myPath + os.path.sep + fn   # alternative location
		mainWin = MainWindow(fName=fn)
	else:
		mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())  # single_trailing_underscore_ is used for avoiding conflict with Python keywords