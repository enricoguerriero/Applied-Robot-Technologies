#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/appImageViewer3.py    (dice)
#
#  Extends appImageViewer2 by adding some more functionality using heritage.
#  Some (skeleton) methods for locating dice in image and counting eyes has
#  been implemented here, these can (and should) be further developed.
#  Color menu can have actions for: dice colors, select colors, ...
#  Dice menu can have actions for: locating dices, finding circles, ...
#
# Karl Skretting, UiS, November 2020, June 2022

# Example on how to use file: 
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> python appImageViewer3.py
# (py38) C:\..\py3> python appImageViewer3.py gul4.bmp

_appFileName = "appImageViewer3"
_author = "Karl Skretting, UiS" 
_version = "2022.06.27"

import sys
import os.path
# from turtle import pd
#from math import hypot, pi, atan2, cos, sin    # sqrt, cos, sin, tan, log, ceil, floor 
import numpy as np
import cv2
import pandas as pd
import tkinter as tk

try:
	from PyQt5.QtCore import Qt, QPoint, QT_VERSION_STR  
	from PyQt5.QtGui import QImage, QPixmap, QTransform, QColor
	from PyQt5.QtWidgets import (QApplication, QAction, QFileDialog, QLabel, QGraphicsPixmapItem, QColorDialog, QInputDialog)
except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes

from appImageViewer2O import myPath, MainWindow as inheritedMainWindow 
from clsHoughCirclesDialog import HoughCirclesDialog
from clsSaturationDialog_O import SaturationDialog
from pyueye import ueye
# import tkinter as tk

# define 17 colorNames as in: https://doc.qt.io/qt-5/qcolor.html 
colorNames17 = ['white','black','cyan','darkCyan','red','darkRed','magenta','darkMagenta',
				'green','darkGreen','yellow','darkYellow','blue','darkBlue',
				'gray','darkGray','lightGray']

class MainWindow(inheritedMainWindow):  
	"""MainWindow class for this image viewer is inherited from another image viewer."""
	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		# print( f"File {_appFileName}: (debug) first line in __init__()" )
		super().__init__(fName, parent) # use inherited __init__ with extension as follows
		#
		# set appFileName as it should be, name not inherited from super()...
		self.appFileName = _appFileName 
		if (not self.pixmap.isNull()): 
			self.setWindowTitle( f"{self.appFileName} : {fName}" )
		else:
			self.setWindowTitle(self.appFileName)
		# 
		self.view.rubberBandRectGiven.connect(self.meanColorEnd)  
		# signal is already connected to cropEnd (appImageViewer1), now connected to two slots!
		self.meanColorActive = False  
		#
		self.initMenu3()
		self.setMenuItems3()
		# print( f"File {_appFileName}: (debug) last line in __init__()" )
		return
	#end function __init__
	
	def initMenu3(self):
		"""Initialize Color and Dice menu."""
		# print( f"File {_appFileName}: (debug) first line in initMenu3()" )
		a = self.qaCheck = QAction( "Check color", self) 
		a.triggered.connect(self.checkColor)
		a.setToolTip("Check image and activate menu item accordingly")
		a = self.qaSwapRandB = QAction( "Swap red and blue", self)
		a.triggered.connect(self.swapRandB)
		a.setToolTip("Change from RGB to BGR or opposite")
		a = self.qaEditColors = QAction( "Edit custom colors", self)
		a.triggered.connect(self.editColors)
		a.setToolTip("Edit list of custom colors (in QColorDialog)")
		a = self.qaMeanColor = QAction( "Add mean color", self)
		a.triggered.connect(self.meanColorStart)
		a.setToolTip("Add average color from image rectangle to custom color list")
		a = self.qaClearColors = QAction( "Clear custom colors", self)
		a.triggered.connect(self.clearColors)
		a.setToolTip("Clear custom color list, i.e. set all to 'white'")
		a = self.qaSetColors = QAction( "Set custom colors", self)
		a.triggered.connect(self.setColors)
		a.setToolTip("Set custom color list, i.e. set all to standard colors.")
		#
		a = self.qaDistColorRGB = QAction( "Distance to RGB color", self)
		a.triggered.connect(self.distColorRGB)
		a.setToolTip("Make a gray scale image by distance to a selected RGB color")
		a = self.qaBestDistColorRGB = QAction( "Distance to closest RGB color", self)
		a.triggered.connect(self.bestDistColorRGB)
		a.setToolTip("Make a gray scale image by distance to a closest custom RGB color")
		a = self.qaAttractColorRGB = QAction( "Attract to closest RGB color", self)
		a.triggered.connect(self.attractColorRGB)
		a.setToolTip("Attract image to a custom RGB colors")
  
		a = self.qaFindYellow = QAction( "Find yellow dice", self)
		a.triggered.connect(self.findYellow)
		a.setToolTip("Find yellow dice")
		#
		a = self.qaFindCircles = QAction( "Find circles", self)
		a.triggered.connect(self.findCircles)
		a.setToolTip("Find circles using cv2.HoughCircles(..)")
		#a = self.qaFindDices = QAction( "Find dices", self)
		#a.triggered.connect(self.findDices)
		a.setToolTip("Find dices (TODO)")
		a = self.qaFindEyes = QAction( "Find dice eyes", self)
		a.triggered.connect(self.findEyes)
		a.setToolTip("Find eyes for each dice (TODO)")
		#
		# a = self.qaChangeOption = QAction( "Change camera option", self)
		# a.triggered.connect(self.apply_saturation)
		# a.setToolTip("Change camera option")
		#
		# a = self.qacolorcorrect = QAction( "Color Correction", self)
		# a.triggered.connect(self.apply_color_correction)
		# #
		# a = self.removecolorcorrection = QAction( "Remove Color Correction", self)
		# a.triggered.connect(self.delete_color_correction)
		#
		a = self.qasetsaturation = QAction( "Set Saturation", self)
		a.triggered.connect(self.set_saturation)
		#
		colorMenu = self.mainMenu.addMenu("Color")
		colorMenu.addAction(self.qaCheck)
		colorMenu.addAction(self.qaSwapRandB)
		colorMenu.addAction(self.qaEditColors)
		colorMenu.addAction(self.qaMeanColor)
		colorMenu.addAction(self.qaClearColors)
		colorMenu.addAction(self.qaSetColors)
		colorMenu.addAction(self.qaDistColorRGB)
		colorMenu.addAction(self.qaBestDistColorRGB)
		colorMenu.addAction(self.qaAttractColorRGB)
		colorMenu.addAction(self.qaFindYellow)
		colorMenu.setToolTipsVisible(True)
		# 
		diceMenu = self.mainMenu.addMenu("Dice")
		diceMenu.addAction(self.qaFindCircles)
		#diceMenu.addAction(self.qaFindDices)
		diceMenu.addAction(self.qaFindEyes)
		diceMenu.setToolTipsVisible(True)
		# diceMenu.addAction(self.qacolorcorrect)
		# diceMenu.addAction(self.removecolorcorrection)
		diceMenu.addAction(self.qasetsaturation)
		# diceMenu.addAction(self.qaChangeOption)
		return
	#end function initMenu3
	
# Some methods that may be used by several of the menu actions
	def setMenuItems3(self):
		"""Enable/disable menu items as appropriate."""
		pixmapOK = ((not self.pixmap.isNull()) and isinstance(self.curItem, QGraphicsPixmapItem))
		#
		self.qaCheck.setEnabled(True)   
		self.qaSwapRandB.setEnabled(pixmapOK)   
		self.qaEditColors.setEnabled(True)
		self.qaMeanColor.setEnabled(pixmapOK and (not self.meanColorActive))
		self.qaClearColors.setEnabled(True)
		self.qaSetColors.setEnabled(True)
		self.qaDistColorRGB.setEnabled(pixmapOK)
		self.qaBestDistColorRGB.setEnabled(pixmapOK)
		self.qaAttractColorRGB.setEnabled(pixmapOK)
		self.qaFindCircles.setEnabled(pixmapOK)   # and self.isAllGray ?
		#self.qaFindDices.setEnabled(pixmapOK)   
		self.qaFindEyes.setEnabled(pixmapOK)   
		return
		
# Methods for actions on the Color-menu
	def checkColor(self):
		"""Check colors for image and set menu items according to active image."""
		self.setIsAllGray()   # check color state on self.image (=self.pixmap, and usually also self.npImage)
		self.setMenuItems()
		self.setMenuItems3()
		return 
		
	def swapRandB(self):
		"""Swap red and blue component of RGB or BGR image 
		or swap black and white for gray scale image.
		Have no 'undo' here as doing the operation once more undo these changes, 
		thus 'undo' will undo previous operation as before.
		"""
		# self.prevPixmap = self.pixmap   # to include 'undo', which is not needed here
		if (len(self.npImage.shape) == 3) and (self.npImage.shape[2] >= 3):
			B = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2RGBA)
			self.np2image2pixmap(B, numpyAlso=True)
			self.setWindowTitle( f"{self.appFileName} : image where Red and Blue components are swapped" )
		else:
			print( "swapRandB: npImage is not an RGB/BGR image, swap black and white." )
			B =  255 - self.npImage
			self.np2image2pixmap(B, numpyAlso=True)
			self.setWindowTitle( f"{self.appFileName} : image where black and white are swapped" )
		#
		self.setMenuItems()   # prevPixmap may have changed from None to pixmap
		return
		
	def editColors(self):
		"""Set colors for the custom color list in QColorDialog by simply calling it."""
		newColor = QColorDialog.getColor(title="You may now add or change custom colors.")
		if newColor.isValid():
			print( f"selctColor(): selected color from dialog box is {newColor.name()}." )
			print( f"  There are {QColorDialog.customCount()} colors in the custom color list:" )
			for cNo in range(QColorDialog.customCount()):
				print( f"  {QColorDialog.customColor(cNo).name()}", end="" )
			print(" ")
		else:
			print( "selctColor(): no valid color, [Cancel] button pressed." )
		#
		return
	
	def meanColorStart(self):
		"""Set crop active and turn rubber band on."""
		self.meanColorActive = True
		self.view.rubberBandActive = True
		self.setMenuItems3()  # meanColor should be weak on Color menu
		print( f"{_appFileName}.MainWindow.meanColorStart() started" )
		return
	
	def meanColorEnd(self, rectangle):
		"""Find mean color using the input rectangle (in image pixels) on the current pixmap .
		
		The mean color replaces the first 'white' color in QColorDialog custom color list.
		This function does not change the image.
		"""
		def intRGB(rgb):
			# (r,g,b) = intRGB(rgb)
			r = min(max(0,int(rgb[0]+0.5)),255)
			g = min(max(0,int(rgb[1]+0.5)),255)
			b = min(max(0,int(rgb[2]+0.5)),255)
			return (r,g,b)
		#
		if not self.meanColorActive: 
			return
		#
		self.meanColorActive = False
		verbose = True
		if verbose:
			print( f"{_appFileName}.MainWindow.findColorEnd() started" )
		#
		(x0, y0) = (rectangle.x(), rectangle.y())
		(w, h) = (rectangle.width(), rectangle.height())
		(x1, y1) = (x0+w, y0+h)
		# note shape for self.npImage:              [    y,    x, bgra --> rgb]  # self.npImage.shape[2] == 4
		np_rect = np.float32(np.reshape(self.npImage[y0:y1,x0:x1,[2,1,0]], (w*h, 3)))
		if verbose and isinstance(np_rect, np.ndarray):  # the last test here should always be true
			print( f"  'npImage'  is ndarray of {self.npImage.dtype.name}, shape: {str(self.npImage.shape)}" )
			print( f"  (x0,y0) = ({x0},{y0}),  (x1,y1) = ({x1},{y1}),  (w,h) = ({w},{h})  w*h = {w*h}" )
			print( f"  'np_rect'  is ndarray of {np_rect.dtype.name}, shape: {str(np_rect.shape)}" )
		#
		rgb = np.mean(np_rect, axis=0)  # ndarray
		if verbose:
			print( f"  mean color for rectangle is (rgb) = ({rgb[0]:5.1f}, {rgb[1]:5.1f}, {rgb[2]:5.1f})" )
			(r,g,b) = intRGB(rgb)
			print( f"  mean color for rectangle is (rgb) = ({r:3d},   {g:3d},   {b:3d}  )" )
		#
		for cNo in range(QColorDialog.customCount()):
			if QColorDialog.customColor(cNo) == QColor('white'):
				(r,g,b) = intRGB(rgb)
				QColorDialog.setCustomColor(cNo, QColor(r,g,b))
				break
		#
		self.setMenuItems3()  # meanColor should be turned back on
		#
		return
	
	def clearColors(self):
		"""Clear all custom colors, i.e. set each to 'white'"""
		for cNo in range(QColorDialog.customCount()):
			if not (QColorDialog.customColor(cNo) == QColor('white')):
				QColorDialog.setCustomColor(cNo, QColor('white'))
		return
		
	def setColors(self):
		"""Set all custom colors, i.e. set each to standard color"""
		for cNo in range(min(QColorDialog.customCount(),16)):
			QColorDialog.setCustomColor(cNo, QColor(colorNames17[cNo+1]))
		return
		
	def distColorRGB(self):
		"""Make binary image by testing if pixel color is close to a selected RGB color.
		Distance is measured for each pixel p with color (r,g,b) to selected color (R,G,B) as
		   d = max(abs(r-R), abs(g-G), abs(b-B)), 
		where d is pixel value for resulting gray scale image
		"""
		color = QColorDialog.getColor(title="Select the color to measure distance to.")
		if color.isValid():
			print(f"  selected color is {color.name()}")
			rgb = [color.red(), color.green(), color.blue()]
			A = self.npImage.astype(np.float32)   # active image
			if (len(A.shape) > 2) and (A.shape[2] >= 3): 
				A = A[:,:,[2,1,0]]  # bgr(a) --> rgb
				B = np.ones(shape=A.shape, dtype=np.float32)  # the one color image
				B[:,:,:] = rgb  
				D = np.max(np.abs(A-B),axis=2).astype(np.uint8)  # the distance image
				del B
			else:
				grayLevel = int((color.red() + color.green() + color.blue() + 0.5)/3)
				print(f"Color '{color.name()}' = ({color.red()}, {color.green()}, {color.blue()}) has grayLevel {grayLevel}")
				D = np.abs(A - grayLevel).astype(np.uint8)
				del grayLevel
			#
			print(f"  'A'  is ndarray of {A.dtype.name}, shape: {str(A.shape)}")
			print(f"  'D'  is ndarray of {D.dtype.name}, shape: {str(D.shape)}, max: {D.max()}")
			#
			self.prevPixmap = self.pixmap   
			self.np2image2pixmap(D, numpyAlso=True)
			self.setWindowTitle(f"{self.appFileName} distColorRGB(): distance to color {color.name()}")
			self.checkColor()
			#
		return
			# A possibility could do to threshold the gray scale image here, perhaps as below
			# # could try different values here, like threshold in toBinary()
			# (dist,ok) = QInputDialog.getInt(self,    # parent
					# f"approxColor(): input distance to '{color.name()}'",  # title
					# "Give allowed distance for each color component",      # label
					# value=25, min=0, max=255)
			# print(f"QInputDialog.getInt(..) returned  'dist' = {dist},  'ok' = {ok}")
			# if ok:
				# # oldPixmap = self.prevPixmap
				# self.prevPixmap = self.pixmap   
				# B = 255*(D <= dist).astype(np.uint8)
				# self.np2image2pixmap(B, numpyAlso=True)
				# self.setWindowTitle(f"{self.appFileName} approxColor(): binary image for color {color.name()}")
				# self.setIsAllGray()
			# else:
				# pass  # 
				# # self.pixmap = self.prevPixmap   # restore 
				# # self.pixmap2image2np()
				# # self.prevPixmap = oldPixmap
			#
		
	def bestDistColorRGB(self):
		"""Make binary image by testing if pixel color is close to one of custom RGB color.
		Distance is measured for each pixel p with color (r,g,b) to custom colors (Ri,Gi,Bi) as
		   d = min_i max(abs(r-Ri), abs(g-Gi), abs(b-Bi)),   i in range(nofCustomColors)
		where d is pixel value for resulting gray scale image
		"""
		color = QColorDialog.getColor(title="Check the colors to measure distance to.")
		# but we don't use the returned color, does [Cancel] give not Valid color?
		if color.isValid():  
			# print(f"  selected color is {color.name()}")
			A = self.npImage.astype(np.float32)   # active image
			if (len(A.shape) > 2) and (A.shape[2] >= 3): 
				A = A[:,:,[2,1,0]]  # bgr(a) --> rgb
			D = 255*np.ones((A.shape[0], A.shape[1]), dtype=np.uint8)
			for cNo in range(QColorDialog.customCount()):
				color = QColorDialog.customColor(cNo)
				if not (color == QColor('white')):
					rgb = [color.red(), color.green(), color.blue()]
					grayLevel = int((color.red() + color.green() + color.blue() + 0.5)/3)
					if (len(A.shape) > 2) and (A.shape[2] >= 3): 
						B = np.ones(shape=A.shape, dtype=np.float32)  # the one color image
						B[:,:,:] = rgb  
						Di = np.max(np.abs(A-B),axis=2).astype(np.uint8)  # the distance image
						del B
					else:
						Di = np.abs(A - grayLevel).astype(np.uint8)
					#end if
					D = np.minimum(D,Di)
				#end if
			#end for
			print(f"  'A'  is ndarray of {A.dtype.name}, shape: {str(A.shape)}")
			print(f"  'D'  is ndarray of {D.dtype.name}, shape: {str(D.shape)}, max: {D.max()}")
			#
			self.prevPixmap = self.pixmap   
			self.np2image2pixmap(D, numpyAlso=True)
			self.setWindowTitle(f"{self.appFileName} image after bestDistColorRGB()")
			self.checkColor()
		return

	def identify_color(hsv_color, color_ranges):
		for color_name, (lower, upper) in color_ranges.items():
			if all(lower[i] <= hsv_color[i] <= upper[i] for i in range(3)):
				return color_name
		return 'Unknown'
 
	def get_Color_Name(self,R,G,B, csv):
  
		minimum = 10000
		for i in range(len(csv)):
			d = abs(R- int(csv.loc[i,"R"])) + abs(G-int(csv.loc[i,"G"]))+ abs(B- int(csv.loc[i,"B"]))
			if(d<=minimum):
				minimum = d
				cname = csv.loc[i,"color_name"]
	
		return cname

	def draw_function(self, event, x,y,flags,param):
		if event == cv2.EVENT_LBUTTONDBLCLK:
			global b,g,r,xpos,ypos, clicked
			clicked = True
			xpos = x
			ypos = y
			b,g,r = self.npImage[y,x]
			b = int(b)
			g = int(g)
			r = int(r)
   
	def ColorDetection(self):
	# https://www.kaggle.com/code/mohammedlahsaini/color-detection-using-opencv
	 
		index=["color","color_name","hex","R","G","B"]
		csv = pd.read_csv('../colors.csv', names=index, header=None)
  
		while(1):
	
			cv2.imshow("color detection",self.npImage)
			if (clicked):
				#cv2.rectangle(image, startpoint, endpoint, color, thickness)-1 fills entire rectangle 
				cv2.rectangle(self.npImage,(20,20), (750,60), (b,g,r), -1)
				color_name = self.getColorName(r,g,b, csv) + ' R='+ str(r) +  ' G='+ str(g) +  ' B='+ str(b)
				#cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
				cv2.putText(self.npImage, color_name,(50,50),2,0.8,(255,255,255),2,cv2.LINE_AA)
				#For very light colours we will display text in black colour
				if(r+g+b>=600):
					cv2.putText(self.npImage, color_name,(50,50),2,0.8,(0,0,0),2,cv2.LINE_AA)
					
				clicked=False
			#when user hit esc
			if cv2.waitKey(20) & 0xFF ==27:
				break
			
		cv2.destroyAllWindows()

	def increase_saturation_single_pixel(self, pixel, increment_value):
		# Convert the single RGB pixel to a 1x1x3 image
		pixel_image = np.array([[pixel]], dtype=np.uint8)

		# Convert the pixel from RGB to HLS color space
		hls_pixel = cv2.cvtColor(pixel_image, cv2.COLOR_RGB2HLS)

		# Extract H, L, S values from the HLS representation
		h, l, s = hls_pixel[0, 0]

		# Increase saturation by the increment value, while making sure it stays within [0, 255]
		s = np.clip(s + increment_value, 0, 255)

		# Merge the H, L, S values back
		hls_pixel[0, 0] = [h, l, s]

		# Convert the pixel back to RGB
		rgb_pixel = cv2.cvtColor(hls_pixel, cv2.COLOR_HLS2RGB)

		return rgb_pixel[0, 0]

	def findYellow(self):
		#hsv_image = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2HSV)
		# color_ranges = {
		# 	#'red': ((0, 0, 0), (255, 255, 255), 0),      # Intervallo per il rosso
		# 	'yellow': ((0, 0, 0), (255, 255, 255), 0),  # Intervallo per il giallo
		# 	'pink': ((160, 100, 100), (170, 255, 255), 0),  # Intervallo per il rosa
		# }
		# results = []

		#for color_name, (lower, upper) in color_ranges.items():
			#mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
			#contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   
			# Usa la funzione CountEyes per ottenere il valore del dado
		self.findCircles()
		#eyes_count = self.neyes

		col_dict = {
			"red" : 0,
			"orange" : 0,	
			"yellow" : 0,
			"green" : 0,	
			"blue" : 0,
			"purple" : 0,
			"pink" : 0,
			"gray" : 0
		}
		
		for circle in self.circles:
			valorex = circle[0]
			valorey = circle[1]
			raggio = circle[2]
			#pixeldacampionare1 = (valorex + raggio*1.5, valorey)
			#pixeldacampionare2 = (valorex, valorey + raggio*1.5)
			print(valorex, valorey, raggio)
			print(self.npImage.shape)
			if valorex + round(raggio*1.2) < self.npImage.shape[1]:
				color = self.npImage[valorey, valorex + round(raggio*1.2)]
			elif valorey + round(raggio*1.2) < self.npImage.shape[1]: 
				color = self.npImage[valorey + round(raggio*1.2), valorex ]
			elif valorex - round(raggio*1.2) < self.npImage.shape[1]:
				color = self.npImage[valorey, valorex - round(raggio*1.2)]
			else:
				color = self.npImage[valorey - round(raggio*1.2), valorex]

			#color2 = self.npImage[valorex, valorey+ round(raggio*1.5)]
   
			# Converti il colore da BGR a HSV (se necessario)
			#hsv_color = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]
   
			# for color_name in color_ranges.keys():
			# 	if color_ranges[color_name][0][0] < color[0] and color_ranges[color_name][1][0] > color[0] and color_ranges[color_name][0][1] < color[1] and color_ranges[color_name][1][1] > color[1] and color_ranges[color_name][0][2] < color[2] and color_ranges[color_name][1][2] > color[2]:
			# 		#color_ranges[color_name][2] += 1
			# 		# Estrai il tuple associato al colore 'red'
			# 		current_tuple = color_ranges[color_name]

			# 		# Converti il tuple in una lista per poterlo modificare
			# 		current_list = list(current_tuple)

			# 		# Incrementa il terzo valore (indice 2) di 1
			# 		current_list[2] += 1

			# 		# Riconverti la lista in un tuple e aggiorna il dizionario
			# 		color_ranges[color_name] = tuple(current_list)
			# 		#print("prova")

			R = color[2]
			G = color[1]
			B = color[0]
			print("\nCOLOR : ", R, G, B)
			R, G, B = self.increase_saturation_single_pixel((R, G, B), 50)
			print("\nNEW COLOR : ", R, G, B)

			G = np.int16(G)
			B = np.int16(B)
			R = np.int16(R)


			if R > 50 + G and G > 50 + B:
				c = "orange"
				print("ORANGE DICE")
			elif abs(G - B) < 50 and max(G, B) < 50 + R:
				c = "red"
				print("RED DICE")
			elif abs(R - G) < 50 and min(R, G) > 50 + B:
				c = "yellow"
				print("YELLOW DICE")
			elif G > 50 + max(R, B):
				c = "green"
				print("GREEN DICE")
			elif B > 50 + max(R, G) and abs(R - G) < 50:
				c = "blue"
				print("BLUE DICE")
			elif B > 50 + R and R > 50 + G:
				c = "purple"
				print("PURPLE DICE")
			elif B - R < 50 and B > 50 + G:
				c = "pink"
				print("PINK DICE")
			else:
				c = "gray"
				print("GRAY DICE")
			col_dict[c] += 1
		print(col_dict)
		print("\n REAL OUTPUT : \n")
		for key in col_dict:
			if col_dict[key] > 0:
				print(key, " dice shows ", col_dict[key], " eyes")
		return
		# Converti i risultati in un DataFrame per visualizzarli in tabella
		#results_df = pd.DataFrame(color_ranges.keys(), color_ranges[2])
		# for colorname in color_ranges.keys():
		# 	print(f"{colorname} number of eyes: {color_ranges[colorname][2]}")
		# return
		
	def attractColorRGB(self):
		"""Make image by assigning colors to closest of custom RGB colors."""
		color = QColorDialog.getColor(title="Check the colors to attract image towards.")
		# but we don't use the returned color, does [Cancel] give not Valid color?
		if color.isValid():  
			# print(f"  selected color is {color.name()}")
			A = self.npImage.astype(np.float32)   # active image
			if (len(A.shape) > 2) and (A.shape[2] >= 3): 
				A = A[:,:,[2,1,0]]  # bgr(a) --> rgb
			D = 255*np.ones((A.shape[0], A.shape[1], QColorDialog.customCount()), dtype=np.uint8)   # 3D-array
			for cNo in range(QColorDialog.customCount()):
				color = QColorDialog.customColor(cNo)
				if not (color == QColor('white')):
					rgb = [color.red(), color.green(), color.blue()]
					grayLevel = int((color.red() + color.green() + color.blue() + 0.5)/3)
					if (len(A.shape) > 2) and (A.shape[2] >= 3): 
						B = np.ones(shape=A.shape, dtype=np.float32)  # the one color image
						B[:,:,:] = rgb  
						D[:,:,cNo] = np.max(np.abs(A-B),axis=2).astype(np.uint8)  # the distance images
						del B
					else:
						D[:,:,cNo] = np.abs(A - grayLevel).astype(np.uint8)
					#end if
				#end if
			#end for
			print(f"  'A'  is ndarray of {A.dtype.name}, shape: {str(A.shape)}")
			print(f"  'D'  is ndarray of {D.dtype.name}, shape: {str(D.shape)}, max: {D.max()}")
			(distLimit,ok) = QInputDialog.getInt(self,    # parent
					f"attractColorRGB(): input 'distLimit'",  # title
					"Give limit distance for attracted color (else 'white')",      # label
					value=25, min=0, max=255)
			print(f"QInputDialog.getInt(..) returned  'distLimit' = {distLimit},  'ok' = {ok}")
			if ok:
				B = 255*np.ones((A.shape[0], A.shape[1], 3), dtype=np.uint8)
				minD = D.min(axis=2)  # distance to closest color
				I = D.argmin(axis=2)  # indexes for best color
				for cNo in range(QColorDialog.customCount()):
					color = QColorDialog.customColor(cNo)
					if not (color == QColor('white')):
						idx = np.logical_and(I==cNo, minD<=distLimit)
						print(f"  set {np.count_nonzero(idx)} pixels to color {color.name()}")
						B[idx,0] = color.blue()   # numpy array is BGR!
						B[idx,1] = color.green()
						B[idx,2] = color.red()
					#end if
				#end for
				print(f"  'B'  is ndarray of {B.dtype.name}, shape: {str(B.shape)}")
				#
				self.prevPixmap = self.pixmap   
				self.np2image2pixmap(B, numpyAlso=True)
				self.setWindowTitle(f"{self.appFileName} image after attractColorRGB()")
				self.checkColor()
			#end ok
		return
		
# Methods for actions on the Dice-menu
	def prepareHoughCirclesA(self):
		"""Make self.A the gray scale image to detect circles in"""
		if (self.A.size == 0):
			# make self.A a gray scale image
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
				#end
			elif (len(self.npImage.shape) == 2):
				self.A = self.npImage.copy()
				self.B = cv2.cvtColor(self.npImage, cv2.COLOR_GRAY2BGR )   
			else:
				print("prepareHoughCircles(): numpy image is not as expected. --> return")
				return
			#end
		return
		
	def prepareHoughCirclesB(self):
		"""Make self.B the BGR image to draw detected circles in"""
		if (len(self.npImage.shape) == 3):
			if (self.npImage.shape[2] == 3):
				self.B = self.npImage.copy()
			elif (self.npImage.shape[2] == 4):
				self.B = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2BGR )   
			#end
		elif (len(self.npImage.shape) == 2):
			self.B = cv2.cvtColor(self.npImage, cv2.COLOR_GRAY2BGR )   
		#end
		return
		
	def tryHoughCircles(self, t):
		"""Simply display results for the parameters given in tuple 't', without committing."""
		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = t
		print("tryHoughCircles(): now called using:")
		print(f"t = (dp={dp}, minDist={minDist}, param1={param1}, param2={param2}, minRadius={minRadius}, maxRadius={maxRadius})")
		#
		self.prepareHoughCirclesA()  # check self.A
		C = cv2.HoughCircles(self.A, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
					param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
		#draw circles on B
		self.prepareHoughCirclesB()  # make self.B
		if C is not None:
			C = np.int16(np.around(C))
			print(f"  'C'  is ndarray of {C.dtype.name}, shape: {str(C.shape)}")
			print(f"  Found {C.shape[1]} circles with radius from {C[0,:,2].min()} to {C[0,:,2].max()}")
			for i in range(min(maxCircles, C.shape[1])):
				(x,y,r) = ( C[0,i,0], C[0,i,1], C[0,i,2] )  # center and radius
				cv2.circle(self.B, (x,y), r, (255, 0, 255), 2) # and circle outline 
				print(f"  circle {i} has center in ({x},{y}) and radius {r}")
			#end for
		#end if
		self.np2image2pixmap(self.B, numpyAlso=False)   # note: self.npImage is not updated
		return
	
	def findCircles(self):
		"""Find circles in active image using HoughCircles(..)."""
		oldPixmap = self.prevPixmap  
		self.prevPixmap = self.pixmap
		self.A = np.array([])  
		self.circles = []
		self.prepareHoughCirclesA()  # make self.A
		#find circles, note that HoughCirclesDialog is in another file: clsHoughCirclesDialog.py
		d = HoughCirclesDialog(self, title="Select parameters that locate the dice eyes") 
		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = d.getValues()   # display dialog and return values
		if d.result():
			C = cv2.HoughCircles(self.A, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
					param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
			#draw circles on B
			self.prepareHoughCirclesB()  # make self.B
			if C is not None:
				C = np.int16(np.around(C))
				print(f"  'C'  is ndarray of {C.dtype.name}, shape: {str(C.shape)}")
				self.neyes = C.shape[1]
				for i in range(min(maxCircles, C.shape[1])):
					(x,y,r) = ( C[0,i,0], C[0,i,1], C[0,i,2] )  # center and radius
					self.circles.append((x,y,r))
					# cv2.circle(self.B, (x,y), 1, (0, 100, 100), 3)  # indicate center 
					cv2.circle(self.B, (x,y), r, (255, 0, 255), 3) # and circle outline 
				#end for
			#
			#finish
			self.A = np.array([])  
			self.np2image2pixmap(self.B, numpyAlso=True)
			self.B = np.array([])  
			self.setWindowTitle(f"{self.appFileName} indicate found circles.")
			self.checkColor()
		else:
			self.pixmap = self.prevPixmap   # restore 
			self.pixmap2image2np()
			self.prevPixmap = oldPixmap
		#end if
		return
		
	def findDices(self):
		"""Find dices in active image using ??."""
		print("findDices(..) function is not ready yet.")
		print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		#
		# -- your code may be written in between the comment lines below --
		# find dices by looking for large rectangles (squares) in the image matching each color
		# each color can be a small set of color point that can be loaded into custom color list
		# for each color (point set)
		#	find distance to this color (point set) and threshold
		#	perhaps morphological operations on this binary image, erode and dilate
		#	find large area (and check it is almost square)
		#	(to find eyes too, the number of same size black wholes inside the square could be found)
		#	print results, or indicate it on image
		#
		return
		
	def findEyes(self):
		"""Find how many eyes each dice has using ??."""
		print("findEyes(..) function is not ready yet.")
		print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		#
		# -- your code may be written in between the comment lines below --
		# Make image into a gray scale image, either by straightforward BGR2GRAY or
		#   by distance to all relevant dice colors, (2-4 sample points for each)
		# Threshold this gray scale image by an appropriate value
		# Find many circles (eyes) of appropriate size in this binary image
		# for each circle
		#	find colors for each circle at 0.8*radius and 1.2*radius, ex. 36 points for [0,10,..,350] degrees
		#	check if the circle is an eye of an dice and the color of the dice
		#	print results (and store it)
		# Finally, print or indicate it on image how many eyes there are for each dice
		#
		return

	# def update_saturation(self, value):
	# 	"""This method gets called when the slider value changes"""
	# 	self.saturation_value = value
	# 	print(f"New saturation value: {value}")

	# def apply_color_correction(self):
	# 	"""Apply the saturation value to the camera"""
	# 	SATURATION_FACTOR = 1
	# 	color_correction = ueye.IS_CCOR_ENABLE_NORMAL
	# 	result = ueye.is_SetColorCorrection(self.cam, color_correction, SATURATION_FACTOR)
	# 	if result == ueye.IS_SUCCESS:
	# 		print("Color correction applied")
	# 	else:
	# 		print("Color correction failed")
	
	# def delete_color_correction(self):
	# 	"""Delete the color correction from the camera"""
	# 	color_correction = ueye.IS_CCOR_DISABLE
	# 	result = ueye.is_SetColorCorrection(self.cam, color_correction, 0)
	# 	if result == ueye.IS_SUCCESS:
	# 		print("Color correction deleted")
	# 	else:
	# 		print("Color correction deletion failed")
   
	def change_saturation(self, saturation_factor):
		saturation_factor = ueye.c_int(round(saturation_factor))
		print(saturation_factor)
		result = ueye.is_SetSaturation(ueye.HIDS(0), saturation_factor, saturation_factor)
		if result == ueye.IS_SUCCESS:
			print("Saturation changed")
		else:	
			print("Saturation change failed")
	
	def set_saturation(self):
		d = SaturationDialog(self)
		saturation_index = d.getValues()
		if d.result():
			minim = max(ueye.IS_MIN_SATURATION_U, ueye.IS_MIN_SATURATION_V)
			maxim = min(ueye.IS_MAX_SATURATION_U, ueye.IS_MAX_SATURATION_V)
			print(ueye.IS_MIN_SATURATION_U, ueye.IS_MIN_SATURATION_V)
			print(ueye.IS_MAX_SATURATION_U, ueye.IS_MAX_SATURATION_V)
			print(minim, maxim)
			if saturation_index == 1:
				saturation_factor = minim
			elif saturation_index == 2:
				saturation_factor = (maxim-minim)*1/4 + minim
			elif saturation_index == 3:	
				saturation_factor = (maxim-minim)*2/4 + minim
			elif saturation_index == 4:
				saturation_factor = (maxim-minim)*3/4 + minim
			elif saturation_index == 5:
				saturation_factor = maxim
			self.change_saturation(saturation_factor)
		pass
	
	
	# def changeOption(self):
	# 	# Creiamo una nuova finestra
	# 	settings_window = tk.Toplevel()
	# 	settings_window.title("Camera Settings")
		
	# 	# Aggiungiamo i controlli per le impostazioni della camera
	# 	label = tk.Label(settings_window, text="Imposta esposizione (ms):")
	# 	label.pack(pady=10)
	# 	exposure_entry = tk.Entry(settings_window)
	# 	exposure_entry.pack(pady=10)

	# 	def apply_settings():
	# 		exposure_time = float(exposure_entry.get())
	# 		change_camera_settings(exposure_time)
		
	# 	apply_button = tk.Button(settings_window, text="Applica", command=apply_settings)
	# 	apply_button.pack(pady=20)
		
	# 	# Mostra la finestra
	# 	settings_window.mainloop()

	# 	def change_camera_settings():
	# 		# Inizializza l'handle della camera
	# 		h_cam = ueye.HIDS(0)
	# 		ueye.is_InitCamera(h_cam, None)

	# 		# Configura i parametri della camera
	# 		# Ad esempio, cambiamo l'esposizione
	# 		exposure_time = ueye.DOUBLE(30.0)  # tempo di esposizione in millisecondi
	# 		ueye.is_Exposure(h_cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, exposure_time, ueye.sizeof(exposure_time))

	# 		# Altre configurazioni possono essere aggiunte qui
			
	# 		# Deinizializza la camera quando hai finito
	# 		ueye.is_ExitCamera(h_cam)

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

class NoeGikkFeil(Exception):
	""" Exception used in cam_info() and perhaps other functions (?)
	"""
	def __init__(self, errNo, message):
		self.errNo = errNo
		self.message = message