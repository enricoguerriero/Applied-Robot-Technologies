#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/appAnalogClock.pyw	
# from https://doc.qt.io/qt-5.10/qtwidgets-widgets-analogclock-example.html 
# Karl Skretting, UiS, March 2018	(added seconds too)

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> pythonw appAnalogClock.pyw 

import sys 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QColor, QPainter, QPolygon
from PyQt5.QtCore import QPoint, QTimer, QTime, Qt
 
class AnalogClock(QWidget):
 
	def __init__(self, parent = None):
		super().__init__(parent)  # or
		# super(AnalogClock, self).__init__(parent)   # what is the difference, if any?
		# see: https://python-course.eu/python3_inheritance.php
		self.setWindowTitle('Analog Clock')
		self.setGeometry(500, 100, 400, 400)
		timer = QTimer(parent = self)
		timer.timeout.connect(self.update)
		timer.start(1000)  # [ms]
		return
 
	def paintEvent(self, qpe):
		# implement the QWidget protected function, done when repaint() or update() is invoked
		# or whenever needed. Here timer invoke update() every 1000 ms.
		# the QPaintEvent qpe argument is ignored here
		hourHand = QPolygon( [QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)] )
		minuteHand = QPolygon( [ QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70) ] )
		secondHand = QPolygon( [ QPoint(5, 6), QPoint(-5, 6), QPoint(0, -80) ] )
		hourColor = QColor(127, 0, 127)
		minuteColor = QColor(0, 127, 127, 191)   #  75% opaque
		secondColor = QColor(180, 180, 0, 132)   #  50% opaque
		side = min(self.width(), self.height())
		time = QTime.currentTime()
		
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.translate(self.width()/2, self.height()/2)
		painter.scale(side/200.0, side/200.0)
		#
		painter.setPen(Qt.NoPen)
		painter.setBrush(hourColor)
		painter.save()
		painter.rotate(30.0*((time.hour()+time.minute()/60.0)))
		painter.drawConvexPolygon(hourHand)
		painter.restore()
		#
		painter.setPen(hourColor)
		for i in range(12):
			painter.drawLine(88, 0, 96, 0)
			painter.rotate(30.0)
		#
		painter.setPen(Qt.NoPen)
		painter.setBrush(minuteColor)
		painter.save()
		painter.rotate(6.0*(time.minute() + time.second()/60.0))
		painter.drawConvexPolygon(minuteHand)
		painter.restore()
		#
		painter.setPen(minuteColor)
		for j in range(60):
			if ((j % 5) != 0):
				painter.drawLine(92, 0, 96, 0)
			painter.rotate(6.0)
		#
		painter.setPen(Qt.NoPen)
		painter.setBrush(secondColor)
		painter.save()
		painter.rotate(6.0*time.second())
		painter.drawConvexPolygon(secondHand)
		painter.restore()
		#
		return
 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	clock = AnalogClock()
	clock.show()
	sys.exit(app.exec())