import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel
import vlc
from vlc import EventType
import time
from time import gmtime, strftime
import winsound

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
		#self.setWindowFlags(QtCore.Qt.WindowTitleHint)
		self.setWindowIcon (QtGui.QIcon('icon.png'))
		self.setWindowTitle(app_name)
		self.setMinimumSize(750, 600)
		#self.setFixedSize(750, 600)
			
		self.instance = vlc.Instance()
		self.mediaplayer = self.instance.media_player_new()
		
		self.widget = QtWidgets.QWidget(self)
		self.setCentralWidget (self.widget)
		
		self.splashScreen = QtWidgets.QFrame()
		self.splashScreen.setStyleSheet ("QFrame{background: black url(splash.png);background-repeat: no-repeat;background-position: center;}")
		#self.palette = self.splashScreen.palette()
		#self.palette.setColor (QtGui.QPalette.Window,QtGui.QColor(0,0,0))
		#self.palette.setBrush (QtGui.QPalette.Background,QtGui.QBrush(QtGui.QPixmap("splash.png"))) # Haha, aren't I so funny??
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
		self.playButton = QtWidgets.QPushButton('')
		self.playButton.setIcon(self.playButton.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
		self.playButton.setEnabled(False)
		self.playButton.clicked.connect(self.playClicked)
		self.hboxlayout.addWidget (self.playButton)

		self.pauseButton = QtWidgets.QPushButton('')
		self.pauseButton.hide()
		self.pauseButton.setIcon(self.pauseButton.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
		self.pauseButton.clicked.connect(self.pauseButtonClicked)
		self.hboxlayout.addWidget (self.pauseButton)

		self.backButton = QtWidgets.QPushButton('')
		self.backButton.setIcon(self.backButton.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
		self.backButton.setEnabled (False)
		self.backButton.clicked.connect(self.backButtonClicked)
		self.hboxlayout.addWidget (self.backButton)

		self.stopButton = QtWidgets.QPushButton('')
		self.stopButton.setIcon(self.stopButton.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
		self.stopButton.setEnabled (False)
		self.stopButton.clicked.connect(self.stopClicked)
		self.hboxlayout.addWidget (self.stopButton)

		self.nextButton = QtWidgets.QPushButton ('')
		self.nextButton.setIcon(self.nextButton.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
		self.nextButton.setEnabled (False)
		self.nextButton.clicked.connect (self.nextButtonClicked)
		self.hboxlayout.addWidget (self.nextButton)

		self.hboxlayout.addStretch (1)
		self.incButton = QtWidgets.QPushButton('')
		self.incButton.setMinimumWidth(100)
		self.incButton.setIcon(self.incButton.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp))
		self.incButton.setEnabled (False)
		#self.incButton.clicked.connect(self.increase)
		self.incButton.pressed.connect(self.increase)
		self.incButton.released.connect(self.releaseButton)
		self.hboxlayout.addWidget (self.incButton)

		self.counterLabel = QtWidgets.QLabel("0")
		#self.counterLabel.hide()
		self.hboxlayout.addWidget (self.counterLabel)

		self.decButton = QtWidgets.QPushButton('')
		self.decButton.setMinimumWidth(100)
		self.decButton.setIcon(self.decButton.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown))
		self.decButton.pressed.connect(self.decrease)
		self.decButton.released.connect(self.releaseButton)
		self.decButton.setEnabled (False)
		self.hboxlayout.addWidget (self.decButton)

		self.hboxlayout.addStretch(1)

		self.flipButton = QtWidgets.QPushButton('')
		self.flipButton.setMinimumWidth(100)
		self.flipButton.setIcon(self.flipButton.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
		self.flipButton.clicked.connect(self.flip)
		#self.flipButton.released.connect(self.releaseButton)
		self.flipButton.setEnabled (False)
		self.hboxlayout.addWidget (self.flipButton)
		
		self.saveButton = QtWidgets.QPushButton('')
		self.saveButton.setMinimumWidth(100)
		self.saveButton.setIcon(self.saveButton.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
		self.saveButton.clicked.connect(self.save)
		self.saveButton.setEnabled (False)
		self.hboxlayout.addWidget (self.saveButton)
		
		self.vboxlayout = QtWidgets.QVBoxLayout()
		self.vboxlayout.setContentsMargins (0, 0, 0, 0)
		self.vboxlayout.addWidget(self.splashScreen)
		self.vboxlayout.addWidget(self.videoframe)
		
		#qslider here
		hbox = QtWidgets.QHBoxLayout()
		hbox.setContentsMargins (10, 0, 10, 0)
		self.timeElapsed = QtWidgets.QLabel("0")
		
		#self.timeElapsed.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		#self.timeElapsed.setSizePolicy(self.timeElapsed.sizePolicy)


		self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		#self.slider = QtGui.QProgressBar()
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
		
	def updateCounter (self):
		self.counterLabel.setText(str(self.points))
	
	def beep (self):
		#winsound.Beep (1000, 200)
		winsound.Beep (500, 50)
		
	def sliderChanged (self, val):
		print("val changed")
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
			#self.y_axis[int(self.mediaplayer.get_time()/tf)] = self.points
			self.beep()
			#print(self.y_axis)
		
	def increase (self):
		self.record_zeros = True
		tf = self.timeFactor()
		if self.points<10:
			self.points += 1
			self.points_list.append([int(self.mediaplayer.get_time()/tf), self.points])
			#self.y_axis[int(self.mediaplayer.get_time()/tf)] = self.points
			self.beep()
			self.locked = True
			#print(self.y_axis)
			self.eta = time.time()
	
	def decrease (self):
		self.record_zeros = True
		tf = self.timeFactor()
		if self.points>(-10):
			self.points -= 1
			self.points_list.append([int(self.mediaplayer.get_time()/tf), self.points])
			#self.y_axis[int(self.mediaplayer.get_time()/tf)] = self.points
			self.beep()
			self.locked = True
			self.eta = time.time()
			
	def stopPlayer(self):
		print("stop player called")
		self.stopClicked(None)
	
	def end_callback (self, event):
		## TODO
		#self.mediaplayer.set_position(0.0)
		'''time.sleep(1)
		self.stopClicked(None)
		time.sleep(1)'''
		
		self.pauseButton.hide()
		self.playButton.show()

		self.saveButton.setEnabled (True)
		self.incButton.setEnabled (False)
		self.decButton.setEnabled (False)
		self.flipButton.setEnabled (False)
		
		'''if self.mediaplayer != None:
			self.stopButton.hide()
			self.playButton.show()'''
	
		##self.unload(".")
		'''time.sleep(3)
		self.stopClicked(None)'''
		#QtCore.QTimer.singleShot(3000, self.stopPlayer)	
		print("ended")
		self.showSplash()
		
	def pos_callback (self, event, player): 
		self.updateCounter()
		sec = int(player.get_time())/1000
		min = int(player.get_time())/(60*1000)
		#self.timeElapsed.setText(str(sec))
		self.timeElapsed.setText(str(datetime.timedelta(seconds=sec)))
		
		if (min != self.prevMin if self.UNIT == self.MINUTE else sec != self.prevSecond) and len(self.points_list)>0:
			tf = self.timeFactor()
			self.points_list.append([int(player.get_time()/tf), self.points])
				
		if (min != self.prevMin if self.UNIT == self.MINUTE else sec != self.prevSecond) and self.locked == True:
			tf = self.timeFactor()
			self.points_list.append([int(player.get_time()/tf), self.points])
		
		if (min != self.prevMin if self.UNIT == self.MINUTE else sec != self.prevSecond) and self.locked == False:
			tf = self.timeFactor()
			if (time.time()-self.eta)>=2:
				if self.points>0:
					self.points -= 1
					#self.points_list.append([int(player.get_time()/tf), self.points])
					#self.y_axis[int(player.get_time()/tf)] = self.points
					
				if self.points<0:
					self.points += 1
					#self.points_list.append([int(player.get_time()/tf), self.points])
					#self.y_axis[int(player.get_time()/tf)] = self.points
				
		if self.slider!=None:
			self.sliderSilentValue (int(player.get_time()))
			
		self.prevSecond = int(player.get_time())/1000
		self.prevMin = int(player.get_time())/(60*1000)
		
	def setListners (self):
		
		if self.mediaplayer != None:
			event_manager = self.mediaplayer.event_manager()
			event_manager.event_attach (EventType.MediaPlayerEndReached, self.end_callback)
			event_manager.event_attach(EventType.MediaPlayerPositionChanged, self.pos_callback, self.mediaplayer)
	
	def save (self, event):
	
		self.x_axis = []
		self.y_axis = []
		
		if len(self.points_list)>0:

			for i in range(0, len(self.points_list)):
				'''try:
					[p_y, p_v] = self.points_list[i-1]
				except Exception:
					[p_y, p_v] = [0, 0]
					
				[y, value] = self.points_list[i]
				
				for k in range(p_y, y):
					self.y_axis[k] = p_v
					
				print(y, value)
				self.y_axis [y] = value'''
				
				[y, value] = self.points_list[i]
				self.x_axis.append (y)
				self.y_axis.append (value)
			'''[ly,lv] = self.points_list[-1]
			for i in range(ly, len(self.y_axis)):
				self.y_axis[i] = lv'''
			
			filename = os.path.basename(self.filename)+" ("+str(self.playedTimes)+") "+strftime("%Y-%m-%d %H-%M-%S", gmtime())
			workbook = xlsxwriter.Workbook(filename+'.xlsx')
			worksheet = workbook.add_worksheet()
			
			## chart
			chart = workbook.add_chart({'type':'line'})
			
			data = [self.x_axis, self.y_axis]
			#worksheet.write_column('A1', data[0])
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
			
			QtWidgets.QMessageBox.information(self, "File Saved","File saved at "+os.getcwd()+"\\"+str(filename)+".xlsx", QtWidgets.QMessageBox.Yes)
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
			self.showSplash(False)
			self.mediaplayer.play()
			
			self.playButton.hide()
			self.pauseButton.show()
			
			self.resetMetrics()
			
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
		
			msgBox = QtWidgets.QMessageBox()
			msgBox.setText('Select unit for time metrics')
			msgBox.addButton(QtWidgets.QPushButton('Minutes'), QtWidgets.QMessageBox.YesRole)
			msgBox.addButton(QtWidgets.QPushButton('Seconds'), QtWidgets.QMessageBox.NoRole)
			msgBox.addButton(QtWidgets.QPushButton('Milliseconds'), QtWidgets.QMessageBox.RejectRole)
			self.UNIT = msgBox.exec_()
		
			self.media = self.instance.media_new(str(path))
			self.mediaplayer.set_media(self.media)
			self.media.parse()
			self.mediaplayer.set_hwnd(self.videoframe.winId())
			
			self.setListners()
			self.playButton.setEnabled (True)
			#self.backButton.setEnabled (True)
			#self.nextButton.setEnabled (True)
			#self.stopButton.setEnabled (True)
			
			#self.incButton.setEnabled (True)
			#self.decButton.setEnabled (True)
		
	def createMenu (self):
		self.openAction = QtWidgets.QAction ("Load video file", self, triggered=self.loadVideo)
		self.openAction.setShortcut('Ctrl+O')
		
		self.exitAction = QtWidgets.QAction ("Exit", self, triggered=QtCore.QCoreApplication.instance().quit)
		self.exitAction.setShortcut('Ctrl+Q')

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&Session')
		fileMenu.addAction(self.openAction)
		fileMenu.addAction(self.exitAction)
		
if __name__=='__main__':
	app = QtWidgets.QApplication (sys.argv)
	window = Window()
	window.show()
	
	sys.exit (app.exec_())