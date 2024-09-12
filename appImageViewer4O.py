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

import sys
import os.path
#from math import hypot, pi, atan2, cos, sin    # sqrt, cos, sin, tan, log, ceil, floor 
import numpy as np
import cv2
import matplotlib.pyplot as plt

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
		self.setMenuItems4()
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
		#
		# -- your code may be written in between the comment lines below --
		# Check color for pixels in a given distance from center [0.75, 0.95]*radius and for all angles [0,1,2, 359]
		# and give 'score' based on how red the pixel is, red > threshold and red > blue and red > green ??
		# (score may be adjusted by position, based on illumination of disk)
		# Find the weighted (based on score) mean position (x,y) for all checked pixels
		# Find, and print perhaps also show on image, the angle of this mean

		image = self.npImage
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		lower_red1 = np.array([0, 50, 50])
		upper_red1 = np.array([10, 255, 255])
		lower_red2 = np.array([170, 50, 50])
		upper_red2 = np.array([180, 255, 255])

		mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
		mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
		mask_red = mask1 + mask2
		contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		if contours:
			largest_contour = max(contours, key=cv2.contourArea)

			#Find center
			M = cv2.moments(largest_contour)
			if M["m00"] != 0:
				cx = int(M["m10"] / M["m00"])
				cy = int(M["m01"] / M["m00"])
				center = (cx, cy)
				print(f"Coordinate of the red sector center: {center}")
			else:
				print("I can not find a center")
		return center
		
	def findSpeed(self):
		x,y,r,lowpointy = self.findDisk()
		center = self.findRedSector()
		return
		
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
	