#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsCamera.py 
#
# Written by Elias Nodland and Vilhem Assersen in UiS Bachelor thesis May 2022
# used in ELE610 by Karl Skretting, froom August 2022

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pyueye import ueye
import datetime
from pyueye_example_utils import (uEyeException, Rect, get_bits_per_pixel,
								  ImageBuffer, check)

class Camera:
    
	def __init__(self, number: int = 0):
		self.pcMem = ueye.c_mem_p()
		self.memId = ueye.int()  
		self.pitch = ueye.int()
		self.img_buffers = []
		self.hCam = ueye.HIDS(number)

	# init starts the camera with given settings
	# x and y are the horisontal and vertical offsets from the top left corner
	# x and width are rounded down to the nearest multiple of 8
	# y and height are rounded down to the nearest multiple of 2
	# exposure is a float number
	# delay is given in microseconds as an int
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

		ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)


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
  
	def __enter__(self):
		self.init()
		return self

	def __exit__(self, _type, value, traceback):
		self.exit()

	def handle(self):
		return self.hCam

	def alloc(self, buffer_count=3):
		rect = self.get_aoi()
		bpp = get_bits_per_pixel(self.get_colormode())

		for buff in self.img_buffers:
			check(ueye.is_FreeImageMem(self.hCam, buff.mem_ptr, buff.mem_id))

		for i in range(buffer_count):
			buff = ImageBuffer()
			ueye.is_AllocImageMem(self.hCam,
								  rect.width, rect.height, bpp,
								  buff.mem_ptr, buff.mem_id)
			
			check(ueye.is_AddToSequence(self.hCam, buff.mem_ptr, buff.mem_id))

			self.img_buffers.append(buff)
		#
		ueye.is_InitImageQueue(self.hCam, 0)
		return

	def exit(self):
		ret = None
		if self.hCam is not None:
			ret = ueye.is_ExitCamera(self.hCam)
		if ret == ueye.IS_SUCCESS:
			self.hCam = None
		return

	def get_aoi(self):
		rect_aoi = ueye.IS_RECT()
		ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

		return Rect(rect_aoi.s32X.value,
					rect_aoi.s32Y.value,
					rect_aoi.s32Width.value,
					rect_aoi.s32Height.value)

	def set_aoi(self, x, y, width, height):
		rect_aoi = ueye.IS_RECT()
		rect_aoi.s32X = ueye.int(x)
		rect_aoi.s32Y = ueye.int(y)
		rect_aoi.s32Width = ueye.int(width)
		rect_aoi.s32Height = ueye.int(height)

		return ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

	def capture_video(self, wait=False):
		wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT  
		# over er pythons variant av ternary operator "?:" i C
		# se Python 3.6 documentation, kap. 6.12. Conditional expressions:
		# https://docs.python.org/3.6/reference/expressions.html#grammar-token-or_test 
		return ueye.is_CaptureVideo(self.hCam, wait_param)

	def stop_video(self):
		return ueye.is_StopLiveVideo(self.hCam, ueye.IS_FORCE_VIDEO_STOP)
	
	def freeze_video(self, wait=False):
		wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
		return ueye.is_FreezeVideo(self.hCam, wait_param)

	def set_colormode(self, colormode):
		check(ueye.is_SetColorMode(self.hCam, colormode))
		
	def get_colormode(self):
		ret = ueye.is_SetColorMode(self.hCam, ueye.IS_GET_COLOR_MODE)
		return ret

	def get_format_list(self):
		count = ueye.UINT()
		check(ueye.is_ImageFormat(self.hCam, ueye.IMGFRMT_CMD_GET_NUM_ENTRIES, count, ueye.sizeof(count)))
		format_list = ueye.IMAGE_FORMAT_LIST(ueye.IMAGE_FORMAT_INFO * count.value)
		format_list.nSizeOfListEntry = ueye.sizeof(ueye.IMAGE_FORMAT_INFO)
		format_list.nNumListElements = count.value
		check(ueye.is_ImageFormat(self.hCam, ueye.IMGFRMT_CMD_GET_LIST,
								  format_list, ueye.sizeof(format_list)))
		return format_list

# end of class Camera:
	
if __name__ == '__main__':
	cam = Camera(0) # create new camera
	# Start camera with certain settings
	cam.init(x = 176, y = 10, width = 928, height = 928,
	         exposure = 2.5, trigger = True, delay = 25000)
	
	while True:
		img = cam.capture()
		img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
		
		# MORE CODE HERE
		
		cv2.imshow("video", img)
		if cv2.waitKey(25) & 0xFF == ord('q'): break
	
	cam.stop()
