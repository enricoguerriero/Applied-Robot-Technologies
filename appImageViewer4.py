#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/appImageViewer4.py    (disk)
#
#  Extends appImageViewer2 by adding some more functionality using heritage.
#  Some (skeleton) methods for locating disc in image and finding the
#  angle for rotation to estimate disk speed.
#  Disk menu has actions for: locating disc, finding read sector and its angle, ...
#
# Karl Skretting, UiS, November 2020, June 2022

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> python appImageViewer4.py
# (py38) C:\..\py3> python appImageViewer4.py DarkCrop10ms.bmp

_appFileName = "appImageViewer4"
_author = "Karl Skretting, UiS" 
_version = "2022.06.27"

from datetime import datetime
import sys
import os.path
from pyueye import ueye
from clsCamera import Camera
#from math import hypot, pi, atan2, cos, sin    # sqrt, cos, sin, tan, log, ceil, floor 
import numpy as np
import cv2

try:
	from PyQt5.QtCore import Qt, QPoint, QT_VERSION_STR  
	from PyQt5.QtGui import QImage, QPixmap, QTransform, QColor
	from PyQt5.QtWidgets import (QApplication, QAction, QFileDialog, QLabel, 
			QGraphicsPixmapItem, QInputDialog)  # QColorDialog, 
except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes 

from appImageViewer2O import myPath, MainWindow as inheritedMainWindow 

class MainWindow(inheritedMainWindow):  
	"""MainWindow class for this image viewer is inherited from another image viewer."""
	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		# print( f"File {_appFileName}: (debug) first line in __init__()" ) 
		super().__init__(fName, parent)# use inherited __init__ with extension as follows
		#
		# set appFileName as it should be, it is set wrong in super()...
		self.appFileName = _appFileName 
		if (not self.pixmap.isNull()): 
			self.setWindowTitle( f"{self.appFileName} : {fName}" ) 
		else:
			self.setWindowTitle(self.appFileName)
		# 
		# self.view.rubberBandRectGiven.connect(self.methodUsingRubberbandEnd)  
		# # signal is already connected to cropEnd (appImageViewer1), and can be connected to more
		# self.methodUsingRubberbandActive = False    # using this to check if rubber band is to be used here
		#
		self.initMenu4()
		#self.setMenuItems4()
		# print( f"File {_appFileName}: (debug) last line in __init__()" )
		return
	#end function __init__
	
	def initMenu4(self):
		"""Initialize Disk menu."""
		# print( f"File {_appFileName}: (debug) first line in initMenu4()" )
		a = self.qaFindDisk = QAction('Find disk', self)
		a.triggered.connect(self.findDisk)
		a.setToolTip("Find disk using cv2.HoughCircles (TODO)")
		a = self.qaFindRedSector = QAction('Find red sector', self)
		a.triggered.connect(self.findRedSector)
		a.setToolTip("Find angle for red sector center (TODO)")
		a = self.qaFindSpeed = QAction('Find speed', self)
		a.triggered.connect(self.findSpeed)
		a.setToolTip("Find speed for rotating disk (TODO)")
		#
		diskMenu = self.mainMenu.addMenu("Disk")
		diskMenu.addAction(self.qaFindDisk)
		diskMenu.addAction(self.qaFindRedSector)
		diskMenu.addAction(self.qaFindSpeed)
		diskMenu.setToolTipsVisible(True)
		return
	#end function initMenu4
	
# Some methods that may be used by several of the menu actions
	def setMenuItems4(self):
		"""Enable/disable menu items as appropriate."""
		pixmapOK = ((not self.pixmap.isNull()) and isinstance(self.curItem, QGraphicsPixmapItem))
		#
		self.qaFindDisk.setEnabled(pixmapOK)   
		self.qaFindDisk.setEnabled(pixmapOK)   
		self.qaFindDisk.setEnabled(pixmapOK)
		return

	def findCircles(self):
		"""Find circles in active image using HoughCircles(..)."""
		oldPixmap = self.prevPixmap  
		self.prevPixmap = self.pixmap
		self.A = np.array([])  
		self.prepareHoughCirclesA()  

		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = (2, 270, 327, 83, 185, 800, 1)
		C = cv2.HoughCircles(self.A, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
				param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

		self.prepareHoughCirclesB()  
		if C is not None:
			C = np.int16(np.around(C))
			print(f"  'C'  is ndarray of {C.dtype.name}, shape: {str(C.shape)}")
			self.neyes = C.shape[1]
			#for i in range(min(maxCircles, C.shape[1])):
			(x,y,r) = ( C[0,0,0], C[0,0,1], C[0,0,2] )  
			cv2.circle(self.B, (x,y), r, (0, 0, 255), 3) 
		self.A = np.array([])  
		self.np2image2pixmap(self.B, numpyAlso=True)
		self.B = np.array([])  
		self.setWindowTitle(f"{self.appFileName} indicate found circles.")

		x = C[0, 0, 0] #rappresenta la coordinata X del centro del cerchio i
		y = C[0, 0, 1] #rappresenta la coordinata Y del centro del cerchio i
		r = C[0, 0, 2] #rappresenta il raggio del cerchio i
		return x,y,r
		
# Methods for actions on the Disk-menu
	def findDisk(self):
		"""Find the large disk in the center of the image using ??."""
		#print("This function is not ready yet.")
		#print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		#
		# -- your code may be written in between the comment lines below --
		# find a large circle using HoughCircles
		# perhaps locate center better by locating black center more exact
		# print results, or indicate it on image
		#
		x,y,r = self.findCircles()
		lowpointy = y-r
		return x,y,r,lowpointy
		
	def findRedSector(self):
		"""Find red sector for disc in active image using ??."""
		print("This function is not ready yet.")
		print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		#
		# -- your code may be written in between the comment lines below --
		# Check color for pixels in a given distance from center [0.75, 0.95]*radius and for all angles [0,1,2, 359]
		# and give 'score' based on how red the pixel is, red > threshold and red > blue and red > green ??
		# (score may be adjusted by position, based on illumination of disk)
		# Find the weighted (based on score) mean position (x,y) for all checked pixels
		# Find, and print perhaps also show on image, the angle of this mean
		return

	def init(self, x: int = 0, y: int = 0, width: int = 1000,
		     height: int = 1000, exposure: float = 2.0,
		     trigger: bool = False, delay: int = 0):
		ueye.is_InitCamera(self.hCam, None)

		# We do this automatically instead of letting
		# students locate this hard to find bug
		x = x - x%8
		width = width - width%8
		y = y - y%2
		height = height - height%2

		self.width = ueye.int(width)
		self.height = ueye.int(height)
		self.bpp = ueye.int(24)

		rect_aoi = ueye.IS_RECT()
		rect_aoi.s32X = ueye.int(x)
		rect_aoi.s32Y = ueye.int(y)
		rect_aoi.s32Width = ueye.int(width)
		rect_aoi.s32Height = ueye.int(height)
		ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_SET_AOI,
		            rect_aoi, ueye.sizeof(rect_aoi))

		ueye.is_SetColorMode(self.hCam, ueye.IS_CM_RGB8_PACKED)
		ueye.is_AllocImageMem(self.hCam, self.width, self.height,
		                      self.bpp, self.pcMem, self.memId)
		ueye.is_AddToSequence(self.hCam, self.pcMem, self.memId)
		ueye.is_InquireImageMem(self.hCam, self.pcMem, self.memId,
		             self.width, self.height, self.bpp, self.pitch)

		ms = ueye.DOUBLE(exposure)
		ueye.is_Exposure(self.hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, 
		                 ms, ueye.sizeof(ms))

		if trigger:
			ueye.is_SetExternalTrigger(self.hCam, ueye.IS_SET_TRIGGER_LO_HI)
			d = ueye.int(delay)
			ueye.is_SetTriggerDelay(self.hCam, d)

		sucess = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
		return sucess

	# capture captures an image in BGR format
	# if trigger is set, waits for trigger
	# returns the image as a numpy multidimensional array
	def capture(self):
		ueye.is_FreezeVideo(self.hCam, ueye.IS_WAIT)
		img = ueye.get_data(self.pcMem, self.width, self.height,
		                    self.bpp, self.pitch, False)
		img = np.reshape(img, (self.height.value, self.width.value, 3))
		return img


	# stop stops the camera and exits cleanly
	def stop(self):
		ueye.is_StopLiveVideo(self.hCam, ueye.IS_FORCE_VIDEO_STOP)
		ueye.is_FreeImageMem(self.hCam, self.pcMem, self.memId)
		ueye.is_ExitCamera(self.hCam)
		
	def findSpeed(self):
		x,y,r,lowpointy = self.findDisk()
		center = self.findRedSector()
		return

    # Inizializza la telecamera con le impostazioni desiderate
    # Attiviamo il trigger esterno e impostiamo un ritardo di 25ms (25000 microsecondi)
		
#end class MainWindow

if __name__ == '__main__':
	print( f"{_appFileName}: (version {_version}), path for images is: {myPath}" )
	print( f"{_appFileName}: Using Qt {QT_VERSION_STR}" )
	mainApp = QApplication(sys.argv)
	if (len(sys.argv) >= 2):
		fn = sys.argv[1]
		if not os.path.isfile(fn):
			fn = myPath + os.path.sep + fn   # alternative location
		if os.path.isfile(fn):
			mainWin = MainWindow(fName=fn)
		else:
			mainWin = MainWindow()
	else:
		mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
	