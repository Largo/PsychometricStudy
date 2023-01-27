import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFontDatabase, QFont
import vlc
from vlc import EventType
import time
from time import gmtime, strftime

import qtawesome as qta #https://matiascodesal.com/blog/spice-your-qt-python-font-awesome-icons/

import xlsxwriter

import datetime

app_name = "Psychometric Study"

class Window (QtWidgets.QMainWindow):
	points = 0
	x_axis = []
	y_axis = []
	points_list = []
	locked = False
	playedTimes = 0
	
	MINUTE = 0
	SECOND = 1
	MS	   = 2
	UNIT = 2
	
	record_zeros = False
	eta = 0 ## elapsed time for counter 

	def __init__(self):
		super(Window, self).__init__()
		self.setWindowIcon (QtGui.QIcon('icon.png'))
		self.setWindowTitle(app_name)
		self.setMinimumSize(750, 600)
		self.resize(1200, 1000)
		self.instance = vlc.Instance()
		self.mediaplayer = self.instance.media_player_new()
		
		self.widget = QtWidgets.QWidget(self)
		self.setCentralWidget (self.widget)
		
		self.splashScreen = QtWidgets.QFrame()
		self.splashScreen.setStyleSheet ("QFrame{background: black url(splash.png);background-repeat: no-repeat;background-position: center;}")
		#self.palette = self.splashScreen.palette()
		#self.palette.setColor (QtGui.QPalette.Window,QtGui.QColor(0,0,0))
		#self.palette.setBrush (QtGui.QPalette.Background,QtGui.QBrush(QtGui.QPixmap("splash.png")))
		#self.splashScreen.setPalette(self.palette)
		self.splashScreen.setAutoFillBackground(True)
		self.splashScreen.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.splashScreen.setSizePolicy(self.splashScreen.sizePolicy)
		
		self.videoframe = QtWidgets.QFrame()
		self.palette = self.videoframe.palette()
		self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
		self.videoframe.setPalette(self.palette)
		self.videoframe.setAutoFillBackground(True)
		self.videoframe.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.videoframe.setSizePolicy(self.videoframe.sizePolicy)
		self.videoframe.hide()
		
		self.hboxlayout = QtWidgets.QHBoxLayout()
	
		buttons = [
			{"name": "playButton", "icon": "fa5s.play", "enabled": False, "clicked": self.playClicked},
			{"name": "pauseButton", "icon": "fa5s.pause", "hide": True, "clicked": self.pauseButtonClicked},
			{"name": "backButton", "icon": "fa5s.backward", "enabled": False, "clicked": self.backButtonClicked},
			{"name": "stopButton", "icon": "fa5s.stop", "enabled": False, "clicked": self.stopClicked},
			{"name": "nextButton", "icon": "fa5s.forward", "enabled": False, "clicked": self.nextButtonClicked},
			{"name": "stretch", "type": "stretch", "factor": 1},
			{"name": "incButton", "icon": "fa5s.arrow-circle-up", "enabled": False, "pressed": self.increase, "released": self.releaseButton},
			{"name": "counterLabel", "text": "0"},
			{"name": "decButton", "icon": "fa5s.arrow-circle-down", "enabled": False, "pressed": self.decrease, "released": self.releaseButton},
			{"name": "flipButton", "icon": "fa5s.sync", "enabled": False, "clicked": self.flip},
			{"name": "saveButton", "icon": "fa5s.save", "enabled": False, "clicked": self.save},
		]

		for button in buttons:
			
			if "type" not in button or button["type"] == "button":
				btn = QtWidgets.QPushButton('')
				setattr(self, button["name"], btn)
				btn.setIconSize(QtCore.QSize(50, 50))
			
			if "icon" in button:
				btn.setIcon(qta.icon(button["icon"], color="#3e3e3e"))
			if "text" in button:
				btn.setText(button["text"])
			if "enabled" in button:
				btn.setEnabled(button["enabled"])
			if "hide" in button:
				btn.hide()
			if "clicked" in button:
				btn.clicked.connect(button["clicked"])
			if "pressed" in button:
				btn.pressed.connect(button["pressed"])
			if "released" in button:
				btn.released.connect(button["released"])
			if "type" in button and button["type"] == "stretch":
				self.hboxlayout.addStretch(button["factor"])
			else:
				self.hboxlayout.addWidget(btn)

		self.vboxlayout = QtWidgets.QVBoxLayout()
		self.vboxlayout.setContentsMargins (0, 0, 0, 0)
		self.vboxlayout.addWidget(self.splashScreen)
		self.vboxlayout.addWidget(self.videoframe)
		
		#qslider here
		hbox = QtWidgets.QHBoxLayout()
		hbox.setContentsMargins (10, 0, 10, 0)
		self.timeElapsed = QtWidgets.QLabel("0")

		self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		self.slider.setEnabled (False)
		self.slider.valueChanged.connect(self.sliderChanged)
		self.totalTime = QtWidgets.QLabel("0")
		
		hbox.addWidget (self.timeElapsed)
		hbox.addWidget (self.slider)
		hbox.addWidget (self.totalTime)
		
		#self.vboxlayout.addWidget (self.slider)
		self.vboxlayout.addLayout (hbox)
		
		self.vboxlayout.addLayout (self.hboxlayout)
		self.widget.setLayout(self.vboxlayout)
		
		self.createMenu()

		self.prevSecond =0
		self.prevMin	=0
		
	def updateCounter (self):
		self.counterLabel.setText(str(self.points))
			
	def sliderChanged (self, val):
		cur = self.mediaplayer.get_time()
		self.sliderSilentValue (val)
		self.mediaplayer.set_time (val)
		
	def sliderSilentValue (self, val):
		self.slider.blockSignals (True)
		self.slider.setValue (val)
		self.slider.blockSignals (False)
		
	def pauseButtonClicked (self, event):
		if self.mediaplayer != None:
			self.mediaplayer.pause()
		
	def backButtonClicked (self, event):
		if self.mediaplayer != None:
			self.mediaplayer.set_time(self.mediaplayer.get_time() - 1000)
	
	def nextButtonClicked (self, event):
		if self.mediaplayer != None:
			self.mediaplayer.set_time(self.mediaplayer.get_time() + 1000)
	
	def releaseButton (self):
		self.locked = False
		
	def flip (self):
		tf = self.timeFactor()
		if self.points<10:
			self.points = self.points*(-1)
			self.points_list.append([int(self.mediaplayer.get_time()/tf), self.points])

	def increase (self):
		self.record_zeros = True
		tf = self.timeFactor()
		if self.points<10:
			self.points += 1
			self.points_list.append([int(self.mediaplayer.get_time()/tf), self.points])
			self.locked = True
			self.eta = time.time()
	
	def decrease (self):
		self.record_zeros = True
		tf = self.timeFactor()
		if self.points>(-10):
			self.points -= 1
			self.points_list.append([int(self.mediaplayer.get_time()/tf), self.points])
			self.locked = True
			self.eta = time.time()
			
	def stopPlayer(self):
		self.stopClicked(None)
	
	def end_callback (self, event):	
		self.pauseButton.hide()
		self.playButton.show()

		self.saveButton.setEnabled (True)
		self.incButton.setEnabled (False)
		self.decButton.setEnabled (False)
		self.flipButton.setEnabled (False)
		
		self.showSplash()
		
	def pos_callback (self, event, player): 
		self.updateCounter()
		playerTime = player.get_time() 
		sec = int(playerTime)/1000
		min = int(playerTime)/(60*1000)
		self.timeElapsed.setText(str(datetime.timedelta(seconds=sec)))
		
		if (min != self.prevMin if self.UNIT == self.MINUTE else sec != self.prevSecond) and len(self.points_list)>0:
			tf = self.timeFactor()
			self.points_list.append([int(playerTime/tf), self.points])
				
		if (min != self.prevMin if self.UNIT == self.MINUTE else sec != self.prevSecond) and self.locked == True:
			tf = self.timeFactor()
			self.points_list.append([int(playerTime/tf), self.points])
		
		if (min != self.prevMin if self.UNIT == self.MINUTE else sec != self.prevSecond) and self.locked == False:
			tf = self.timeFactor()
			if (time.time()-self.eta)>=2:
				if self.points>0:
					self.points -= 1
					
				if self.points<0:
					self.points += 1
				
		if self.slider!=None:
			self.sliderSilentValue (int(playerTime))
			
		self.prevSecond = int(playerTime)/1000
		self.prevMin = int(playerTime)/(60*1000)
		
	def setListeners (self):
		
		if self.mediaplayer != None:
			event_manager = self.mediaplayer.event_manager()
			event_manager.event_attach (EventType.MediaPlayerEndReached, self.end_callback)
			event_manager.event_attach(EventType.MediaPlayerPositionChanged, self.pos_callback, self.mediaplayer)
	
	def setTheFilename (self) :
		#QtWidgets.QFileDialog.getOpenFileName(self, "Load Video File", '', "video files (*.*)")
		#self.excelFilename, _ = str(QtWidgets.QFileDialog.getSaveFileName(self, "Save Excel File", '', "video files (*.*)")[0])
		self.excelFilename = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '', 'Excel Files (*.xlsx);;All Files (*)')[0]
		#self.excelFilename = os.path.basename(self.filename)+" ("+str(self.playedTimes)+") "+strftime("%Y-%m-%d %H-%M-%S", gmtime())

	def saveAs (self, event) :
		self.excelFilename = None
		if self.excelFilename is None:
			self.setTheFilename()
		self.save


	def save (self, event):
		self.x_axis = {}
		self.y_axis = {}

		if self.excelFilename is None:
			self.setTheFilename()
		
		if len(self.points_list)>0:
			for i in range(0, len(self.points_list)):
				[y, value] = self.points_list[i]
				self.x_axis.append (y)
				self.y_axis.append (value)
			
			workbook = xlsxwriter.Workbook(self.excelFilename) #'.xlsx'
			worksheet = workbook.add_worksheet()
			
			## chart
			chart = workbook.add_chart({'type':'line'})
			
			data = [self.x_axis, self.y_axis]
			for i in range (0, len(data[0])):
				data[0][i] = str(datetime.timedelta(seconds=int(data[0][i])))
			worksheet.write_column('A1', data[0])
			worksheet.write_column('B1', data[1])
			
			# Configure the charts. In simplest case we just add some data series.
			chart.add_series({
				'categories': '=Sheet1!$A$1:$A$'+str(len(self.x_axis)-1),
				'values': '=Sheet1!$B$1:$B$'+str(len(self.y_axis)-1),
				'name': 'Psychometric Study'
			})
			
			chart.set_y_axis({'name': 'response','name_font': {'size': 14, 'bold': True},'num_font':  {'italic': True }})
			time = "sec"
			if self.UNIT == self.MINUTE:
				time = "min"
			if self.UNIT == self.MS:
				time = "ms"
				
			chart.set_x_axis({'name': 'time ('+str(time)+')','name_font': {'size': 14, 'bold': True},'num_font':  {'italic': True }})
			
			worksheet.insert_chart('C1', chart)
			workbook.close()
			
			QtWidgets.QMessageBox.information(self, "File Saved","File saved at "+os.getcwd()+"\\"+str(self.excelFilename)+".xlsx", QtWidgets.QMessageBox.Yes)
			self.playedTimes += 1
		else:
			QtWidgets.QMessageBox.critical(self, "Error","You need to provide your response to video", QtWidgets.QMessageBox.Yes)

	def timeFactor (self):
		timex =1
		if self.UNIT == self.MINUTE:
			timex = 60*1000
		if self.UNIT == self.SECOND:
			timex = 1000
		if self.UNIT == self.MS:
			timex = 1
		return timex
	
	def resetMetrics(self):
		if self.media != None:
			tf = self.timeFactor()
			duration = int(self.media.get_duration() / tf) # TODO: make sure this is correct
			self.x_axis = [x for x in range (0, duration+1) ]
			self.y_axis = [0 for x in range (0, duration+1) ]
			
			self.points = 0
			self.points_list = []
			
			## initialise seconds elapsed
			self.prevSecond =0
			self.prevMin	=0
			
			## init slider
			self.slider.setRange (0, self.media.get_duration())
			self.slider.setValue (0)
			#self.totalTime.setText(str(self.media.get_duration()/1000))
			self.totalTime.setText(str(datetime.timedelta(seconds=self.media.get_duration()/1000)))
			self.record_zeros = False

	def playClicked (self, event):
		if self.mediaplayer != None:
			self.resetMetrics()
			self.showSplash(False)
			self.mediaplayer.play()
			
			self.playButton.hide()
			self.pauseButton.show()
			
			self.backButton.setEnabled (True)
			self.nextButton.setEnabled (True)
			self.stopButton.setEnabled (True)
			self.saveButton.setEnabled (True)
			self.incButton.setEnabled (True)
			self.decButton.setEnabled (True)
			self.flipButton.setEnabled (True)
			self.slider.setEnabled (True)
			
	def showSplash (self, show=True):
		if show==True:
			self.videoframe.hide()
			self.splashScreen.show()
		else:
			self.videoframe.show()
			self.splashScreen.hide()
			
	def stopClicked (self, event):
		if self.mediaplayer != None:
			print("We have mediaplayer")
			self.mediaplayer.stop()
			self.pauseButton.hide()
			self.playButton.show()
			self.showSplash ()
			
	def loadVideo (self):
		self.stopClicked(None)
		path = str(QtWidgets.QFileDialog.getOpenFileName(self, "Load Video File", '', "video files (*.*)")[0])
		print(path)
		self.filename = path
		self.playedTimes = 0
		if len(path)>0:
			self.UNIT = self.SECOND
		
			self.media = self.instance.media_new(str(path))
			self.mediaplayer.set_media(self.media)
			self.media.parse()
			if sys.platform.startswith('linux'): # for Linux using the X Server
				self.mediaplayer.set_xwindow(self.videoframe.winId())
			elif sys.platform == "win32": # for Windows
				self.mediaplayer.set_hwnd(self.videoframe.winId())
			elif sys.platform == "darwin": # for MacOS
				self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
			
			self.setListeners()
			self.playButton.setEnabled (True)
		
	def createMenu (self):
		self.openAction = QtWidgets.QAction ("Load video file", self, triggered=self.loadVideo)
		self.openAction.setShortcut('Ctrl+O')

		self.saveAction = QtWidgets.QAction ("Save", self, triggered=self.save)
		self.saveAction.setShortcut('Ctrl+S')

		self.saveAsAction = QtWidgets.QAction ("Save as", self, triggered=self.saveAs)

		self.exitAction = QtWidgets.QAction ("Exit", self, triggered=QtCore.QCoreApplication.instance().quit)
		self.exitAction.setShortcut('Ctrl+Q')

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&Session')
		fileMenu.addAction(self.openAction)
		fileMenu.addAction(self.saveAction)
		fileMenu.addAction(self.saveAsAction)
		fileMenu.addAction(self.exitAction)


def crash_handler(exctype, value, traceback):
    # Handle the exception
    print("An error occurred:", value)

if __name__=='__main__':
	sys.excepthook = crash_handler
	app = QtWidgets.QApplication (sys.argv)
	app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
	window = Window()
	window.show()

	sys.exit (app.exec_())