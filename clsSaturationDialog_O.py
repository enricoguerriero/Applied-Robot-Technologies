#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsEdgeDialog.py 
#
#  The class EdgeDialog
#
# Karl Skretting, UiS, February 2019, June 2022

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py38
#   (py38) C:\..\py3> python clsEdgeDialog.py
# Example on how to use file in appImageViewer1.py:
#   from clsEdgeDialog import EdgeDialog

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QDialog, QLabel, 
			QRadioButton, QPushButton, QButtonGroup, QFormLayout, QBoxLayout)

class SaturationDialog(QDialog):
	""" A dialog widget for giving parameters to use in a function like
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.title = 'Saturation dialog for changing saturation of the camera'
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 320, 130)
		# contents
		labelK = QLabel('Select k-size to use in Sobel filters.') 
		qrbK1 = QRadioButton('Really low')
		qrbK2 = QRadioButton('Low')
		qrbK3 = QRadioButton('Medium')
		qrbK4 = QRadioButton('High')
		qrbK5 = QRadioButton('Really high')
		qrbK3.setChecked(True)
		self.qbgK = QButtonGroup()
		self.qbgK.addButton(qrbK1, 1)
		self.qbgK.addButton(qrbK2, 2)
		self.qbgK.addButton(qrbK3, 3)
		self.qbgK.addButton(qrbK4, 4)
		self.qbgK.addButton(qrbK5, 5)
		# self.qbgK.buttonClicked.connect(self.tryClicked)
		#
		# tryButton = QPushButton('Try it')
		# tryButton.clicked.connect(self.tryClicked)
		okButton = QPushButton('OK')
		okButton.clicked.connect(self.okClicked)
		cancelButton = QPushButton('Cancel')
		cancelButton.clicked.connect(self.cancelClicked)
		#
		layout = QFormLayout()
		layout.addRow(labelK)
		kLine = QBoxLayout(0)
		kLine.addWidget(qrbK1)
		kLine.addWidget(qrbK2)
		kLine.addWidget(qrbK3)
		kLine.addWidget(qrbK4)
		kLine.addWidget(qrbK5)
		kLine.addStretch()
		layout.addRow(kLine)
		btnLine = QBoxLayout(1)
		btnLine.addWidget(okButton)
		btnLine.addWidget(cancelButton)
		btnLine.addStretch()
		#btnLine.addWidget(tryButton)
		layout.addRow(btnLine)
		self.setLayout(layout)
		return
		
	def getKandS(self):
		valK = self.qbgK.checkedId()
		return (valK)
		
	def okClicked(self):
		self.accept()
		return 
		
	def cancelClicked(self):
		self.reject()
		return 
	
	def tryClicked(self,ignored=None):
		p = self.parent()
		(valK) = self.getKandS()
		p.trySaturation(valK)
		return 
		
	def getValues(self):
		self.exec()
		return self.getKandS()
	#end class EdgeDialog
	
#for testing the dialog
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of EdgeDialog")
		self.setGeometry(150, 50, 800, 600)  # initial window position and size
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the edge dialog')
		qaShowDialog.triggered.connect(self.showDialog)
		#
		qaCloseWin = QAction('closeWin', self)
		qaCloseWin.setShortcut('Ctrl+Q')
		qaCloseWin.setToolTip('Close and quit program')
		qaCloseWin.triggered.connect(self.closeWin)
		#
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(qaShowDialog)
		fileMenu.addAction(qaCloseWin)
		fileMenu.setToolTipsVisible(True)
		#
		return
	#end function __init__
	
	def showDialog(self):   
		d = SaturationDialog(parent=self)   # create object (but does not run it)
		(valK) = d.getValues()   # display dialog and return values
		print( f"SaturationDialog getValues(): valK = {valK}, d.result() is {d.result()}" )
		return
	#end function showDialog
	
	def trySaturation(self, valK):
		print( f"trySaturation(): now called using valK = {valK}")
		return 
	
	def closeWin(self):
		print("Close the main window and quit program.")
		self.close()
		return
		
#end class MainWindow
	
if __name__ == '__main__':
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
	
