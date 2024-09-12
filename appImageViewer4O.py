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
import datetime
try:
	from pyueye import ueye
	from clsCamera import Camera
	from pyueye_example_utils import ImageData, ImageBuffer  # FrameThread, 
	ueyeOK = True
except ImportError:
	ueye_error = f"{_appFileName}: Requires IDS pyueye example files (and IDS camera)." 
	# raise ImportError(ueye_error)
	ueyeOK = False   # --> may run program even without pyueye
import matplotlib.pyplot as plt
import math

try:
	from PyQt5.QtCore import Qt, QPoint, QT_VERSION_STR, QTimer 
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
   
		self.capture_running = False
		self.previous_capture_time = None  # Store the timestamp of the previous capture
		self.previous_time_diff = None  # Store the previous time difference
		self.same_time_count = 0  # Counter for how many times the time difference is the same
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.check_for_trigger)

		# 
		# self.view.rubberBandRectGiven.connect(self.methodUsingRubberbandEnd)  
		# # signal is already connected to cropEnd (appImageViewer1), and can be connected to more
		# self.methodUsingRubberbandActive = False    # using this to check if rubber band is to be used here
		#
		self.image_label = QLabel(self)
		self.initMenu4()
		# self.setMenuItems4()
		# print( f"File {_appFileName}: (debug) last line in __init__()" )
		return
	#end function __init__
 
	def cameraOnTrigger(self):
		"""Turn IDS camera on."""
		print( f"{self.appFileName}: cameraOn() called" )
		if ueyeOK and (not self.camOn):
			try:
				print( f"{self.appFileName}: cameraOn() Trying to start camera" )
				self.cam = Camera(0)
				print("Camera object created")
				self.cam.init(trigger = True)  # gives error when camera not connected
				print("Camera initialized")
				# self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
				# print("Color mode set")
				# This function is currently not supported by the camera models USB 3 uEye XC and XS.
				self.cam.set_aoi(0, 0, 720, 1280)  # but this is the size used
				print("AOI set")
				self.cam.alloc(3)  # argument is number of buffers
				print("Buffers allocated")
				self.camOn = True
				self.setMenuItems2()
				print( f"{self.appFileName}: cameraOn() Camera started ok" )

				self.capture_running = True
				self.timer.start(30)  # Poll for trigger every 30ms

			except Exception as e:
				print(f"Error starting camera: {e}")
				self.camOn = False
		return

	def keyPressEvent(self, event):
		"""Handle key presses."""
		if event.key() == Qt.Key_Escape:  # Example: Stop capturing when Esc is pressed
			if self.capture_running:
				self.cameraOff()  # Stop the camera trigger
				self.status.setText("Capture process interrupted by Esc key.")
				print("Process interrupted by Esc key")
	
	def log_trigger_time(trigger_time):
		"""Log the exact time of each trigger to a file."""
		with open('trigger_log.txt', 'a') as log_file:  # 'a' mode appends to the file
			log_file.write(f"Trigger occurred at: {trigger_time.strftime('%Y-%m-%d %H:%M:%S.%f')}\n")
	
	def angularSpeed(self, time_diff):
		"""Calculate the angular speed of the disk."""
		angular_speed = 360 / time_diff
		print(f"\n\nAngular speed: {angular_speed} degrees per second")

	def check_for_trigger(self):
		"""Check if the camera trigger has been activated, and capture the image."""
		if self.camOn:
			frame = self.cam.capture()  # This waits for the trigger to capture an image
			if frame is not None:
				# current capture time
				current_capture_time = datetime.datetime.now()	
	
				# Convert the NumPy array (frame) to QImage
				height, width, channel = frame.shape
				bytes_per_line = 3 * width
				self.image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
				
				# Convert QImage to QPixmap
				self.pixmap = QPixmap.fromImage(self.image)
				
				# Update the QGraphicsScene
				if self.curItem is not None:
					self.scene.removeItem(self.curItem)  # Remove previous pixmap if any
				self.curItem = self.scene.addPixmap(self.pixmap)  # Add the new pixmap to the scene
				
				# Fit the view to the scene
				self.view.fitInView(self.scene.sceneRect(), mode=1)
				self.status.setText("Image captured and displayed.")

				# Optionally save the captured image
				timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
				cv2.imwrite(f'triggered_image_{timestamp}.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
				print(f"Image captured at {timestamp}")
				
				if self.previous_capture_time is not None:
					time_diff = current_capture_time - self.previous_capture_time
					print(f"Time between captures: {time_diff.total_seconds()} seconds")
					time_diff = time_diff.total_seconds()
	 
					if self.previous_time_diff is not None:
						if abs(time_diff - self.previous_time_diff) < 0.00001:  # Check if the time difference is the same
							self.same_time_count += 1
							print(f"Same time difference detected {self.same_time_count} times")
							if self.same_time_count >= 1:  # Stop after detecting same time twice
								self.capture_running = False
								self.cameraOff()   
								self.status.setText("Process stopped due to same time difference.")
								self.angularSpeed(time_diff)
								return
						else:
							self.same_time_count = 0

					self.previous_time_diff = time_diff
				self.previous_capture_time = current_capture_time
	
	
	def cameraOff(self):
		"""Turn IDS camera off and print some information."""
		if ueyeOK and self.camOn:
			self.cam.exit()
			self.camOn = False
			self.timer.stop()  # Stop the timer when stopping the camera
			self.setMenuItems2()
			print( f"{self.appFileName}: cameraOff() Camera stopped ok" )
		return
	
	def initMenu4(self):
		"""Initialize Disk menu."""
		# print( f"File {_appFileName}: (debug) first line in initMenu4()" )
		a = self.qaCameraOnTrigger = QAction('Camera on', self)
		a.triggered.connect(self.cameraOnTrigger)
		a.setToolTip("Turn IDS camera on")
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
		diskMenu.addAction(self.qaCameraOnTrigger)
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
		self.findCircles()
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
		centerCircle = (x,y)
		centerSector1 = (x,lowpointy)
		omega = self.calculate_angular_velocity(centerCircle,centerSector1,center,200000)
		print(omega)
		return

	def calculate_angular_velocity(self, center_circle, center_sector_t1, center_sector_t2, delta_t):
		# Calculate the angle at time t1
		angle_t1 = math.atan2(center_sector_t1[1] - center_circle[1], center_sector_t1[0] - center_circle[0])
		
		# Calculate the angle at time t2
		angle_t2 = math.atan2(center_sector_t2[1] - center_circle[1], center_sector_t2[0] - center_circle[0])
		
		# Angular difference
		delta_theta = angle_t2 - angle_t1
		
		# Ensure the angle is between -pi and pi
		delta_theta = (delta_theta + math.pi) % (2 * math.pi) - math.pi
		
		# Angular velocity
		omega = delta_theta / delta_t
		
		return omega
		
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
	