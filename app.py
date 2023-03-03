#! /usr/bin/env python3
import os, sys, ctypes
from pathlib import Path
from os import path

if sys.version_info.major < 3:
    print("This script requires Python 3 or later.")
    sys.exit(1)

# Set paths to the executable file and path to the app.py
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
	bundle_dir = path.abspath(sys._MEIPASS)
	if sys.platform == "darwin":
		executable_dir = path.abspath(Path(sys.executable).parent.parent.parent.parent) # directory where the .app is
	else:
		executable_dir = path.abspath(Path(sys.executable).parent)

else: 
	bundle_dir = path.abspath(Path(__file__).parent)
	executable_dir = bundle_dir

import os, subprocess, json, xlsxwriter, qtawesome, shutil, version
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
try:
	# Load VLC
	if sys.platform == "darwin" or sys.platform == "linux":
		if getattr(sys, 'frozen', False):
			pathToDylib = path.abspath(Path(bundle_dir).parent) + os.sep + 'Resources' + os.sep 
			os.environ.setdefault("LD_LIBRARY_PATH", pathToDylib)
			os.environ.setdefault("VLC_PLUGIN_PATH", pathToDylib + os.sep + 'plugins')
			ctypes.CDLL(pathToDylib +  'libvlccore.dylib')
			ctypes.CDLL(pathToDylib + 'libvlc.dylib')

	import vlc
	from vlc import EventType
except:
	app = QApplication(sys.argv)
	# show error message box if VLC libraries can't be loaded
	msgBox = QMessageBox()
	msgBox.setIcon(QMessageBox.Critical)
	msgBox.setText("Failed to load VLC libraries.")
	msgBox.setWindowTitle("Error")
	sys.exit(msgBox.exec_())
import time, datetime
from time import gmtime, strftime

app_name = "Psychometric Study"

class ClickableSlider(QtWidgets.QSlider):
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Determine the position of the click within the slider
            click_value = self.minimum() + (self.maximum() - self.minimum()) * event.pos().x() / self.width()
            # Set the slider position to the clicked value
            self.setValue(int(click_value))
        super().mousePressEvent(event)

class Window (QtWidgets.QMainWindow):
	points = 0
	x_axis = []
	y_axis = []
	points_list = []
	markers_list = []
	locked = False
	playedTimes = 0

	MINUTE = 0
	SECOND = 1
	MS = 2
	UNIT = 2

	eta = 0  # elapsed time for counter

	def __init__(self):
		super(Window, self).__init__()
		self.setWindowIcon(QtGui.QIcon('icon.png'))
		self.setWindowTitle(app_name)
		self.setMinimumSize(750, 600)
		self.resize(1200, 1000)
		self.vlc_instance = vlc.Instance()
		self.mediaplayer = self.vlc_instance.media_player_new()
		self.media = None

		self.widget = QtWidgets.QWidget(self)
		self.setCentralWidget(self.widget)

		self.defaultConfig = {}
		try:
			# Check if the file exists
			if os.path.isfile("default.json"):
				# Open the file
				with open("default.json", "r") as file:
					# Load the JSON data from the file
					self.defaultConfig = json.load(file)
			else:
				print("The config file does not exist.")

		except Exception as e:
			print(f"An error occurred: {e}")

		self.excelFilename = None
		if "defaultExcelPath" in self.defaultConfig:
			self.excelFilename = self.defaultConfig["defaultExcelPath"]

		self.videoframe = QtWidgets.QFrame()
		self.palette = self.videoframe.palette()
		self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
		self.videoframe.setPalette(self.palette)
		self.videoframe.setAutoFillBackground(True)
		self.videoframe.sizePolicy = QtWidgets.QSizePolicy(
		    QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.videoframe.setSizePolicy(self.videoframe.sizePolicy)

		self.hboxlayout = QtWidgets.QHBoxLayout()
		# add some margins on the left and right
		self.hboxlayout.setContentsMargins(10, 10, 10, 10)

		self.shortcuts = []

		fontColor = "#3e3e3e"

		buttons = [
			{"name": "playButton", "icon": "fa5s.play",
			    "enabled": False, "clicked": self.changePlayButton, "hotkey": ["Space"]},
			{"name": "pauseButton", "icon": "fa5s.pause",
			    "hide": True, "clicked": self.changePlayButton},
			{"name": "backButton", "icon": "fa5s.backward",
			    "enabled": False, "pressed": self.backButtonClicked, "hotkey": ["left"], "setAutoRepeat": True},
			{"name": "stopButton", "icon": "fa5s.stop",
			    "enabled": False, "clicked": self.stopClicked},
			{"name": "nextButton", "icon": "fa5s.forward",
			    "enabled": False, "pressed": self.nextButtonClicked, "hotkey": ["right"], "setAutoRepeat": True},
			{"name": "stretch", "type": "stretch", "factor": 1},
			{"name": "incButton", "icon": "fa5s.arrow-circle-up", "enabled": False,
			    "pressed": self.increase, "released": self.releaseButton, "hotkey": ["Up"], "setAutoRepeat": True, "color": "#76BA1B" }, # green color
			{"name": "counterLabel", "type": "button", "text": "0"},
			{"name": "decButton", "icon": "fa5s.arrow-circle-down", "enabled": False, 
			    "pressed": self.decrease, "released": self.releaseButton, "hotkey": ["Down"], "setAutoRepeat": True, "color": "#FD3F46" }, # red color
			{"name": "stretch", "type": "stretch", "factor": 1},
			{"name": "hiddenButton", "type": "spacer"},
			{"name": "skipButton", "icon": "fa5s.fast-forward",
			    "enabled": False, "pressed": self.skipButtonClicked, "setAutoRepeat": False},
			{"name": "stretch", "type": "stretch", "factor": 1},
			{"name": "markerButton", "icon": "fa5s.surprise",
			    "enabled": False, "clicked": self.addMarker, "hotkey": ["Enter", "Return"], "color": "#F5BD0A"},
			{"name": "saveButton", "icon": "fa5s.save",
			    "enabled": False, "clicked": self.save},
		]

		for button in buttons:
			if "type" not in button or button["type"] == "button":
				btn = QPushButton('')
				setattr(self, button["name"], btn)
				btn.setIconSize(QtCore.QSize(80, 80))
				# set focus policy to no focus
				btn.setFocusPolicy(QtCore.Qt.NoFocus)

			if "type" in button and button["type"] == "spacer":
				btn = QtWidgets.QSpacerItem(90, 90, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
				
			if "icon" in button:
				if "color" in button:
					btn.setIcon(qtawesome.icon(button["icon"], color=button["color"]))
				else:
					btn.setIcon(qtawesome.icon(button["icon"], color=fontColor))
			elif "type" not in button or button["type"] == "button":
				# set width and height to take the same space as the icon plus the padding
				btn.setFixedSize(90, 90)

			if "text" in button:
				btn.setText(button["text"])
				if sys.platform == "darwin":
					btn.setFont(QFont(QFont().defaultFamily(), 67))
				else: 
					btn.setFont(QFont(QFont().defaultFamily(), 21))
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
			if "setAutoRepeat" in button:
				btn.setAutoRepeat(button["setAutoRepeat"])

			if "type" in button and button["type"] == "stretch":
				self.hboxlayout.addStretch(button["factor"])
			elif "type" in button and button["type"] == "spacer":
				self.hboxlayout.addItem(btn)
			else:
				self.hboxlayout.addWidget(btn)

			if "type" not in button or button["type"] == "button":
				if "hotkey" in button:
					# loop over button["hotkey"] and add a shortcut for each one
					for hotkey in button["hotkey"]:
						buttonShortcut = QShortcut(QKeySequence(hotkey), self)
						if "setAutoRepeat" in button:
							buttonShortcut.setAutoRepeat(button["setAutoRepeat"])
						else:
							buttonShortcut.setAutoRepeat(False)
						buttonShortcut.setEnabled(True)
						# add lamda to connect and only run handler if button is enabled and visibily press the button
						buttonShortcut.activated.connect(lambda btn=btn: btn.animateClick(100) if btn.isEnabled() else None)
						# add the shortcut to the list of shortcuts
						self.shortcuts.append(buttonShortcut)
				if "color" in button:
					btn.setStyleSheet("color: " + button["color"])
				else:
					btn.setStyleSheet("color: " + fontColor)

		self.vboxlayout = QtWidgets.QVBoxLayout()
		self.vboxlayout.setContentsMargins(0, 0, 0, 0)
		self.vboxlayout.addWidget(self.videoframe)

		hbox = QtWidgets.QHBoxLayout()
		hbox.setContentsMargins(10, 0, 10, 0)
		self.timeElapsed = QtWidgets.QLabel("0:00:00")

		self.slider = ClickableSlider(QtCore.Qt.Horizontal)
		self.slider.setToolTip("Position")
		self.slider.setMinimum(0)
		self.slider.setMaximum(10000)
		self.slider.setEnabled(False)
		self.slider.valueChanged.connect(self.sliderChanged)

		self.totalTime = QtWidgets.QLabel("0:00:00")
		self.totalTime.setMinimumWidth(105)
		# make sure that time elapsed has a minimum width that is enough to display 0:00:00
		self.timeElapsed.setMinimumWidth(105)	

		hbox.addWidget(self.timeElapsed)
		hbox.addWidget(self.slider)
		hbox.addWidget(self.totalTime)

		self.vboxlayout.addLayout(hbox)
		self.vboxlayout.addLayout(self.hboxlayout)
		self.widget.setLayout(self.vboxlayout)

		# Show the user the hotkeys add after hboxlayout
		self.hotkeyLabel = QtWidgets.QLabel()
		# make the hotkey label wrap
		self.hotkeyLabel.setWordWrap(True)
		# add margin around
		self.hotkeyLabel.setContentsMargins(10, 0, 10, 0)
		self.hotkeyLabel.setText("Hotkeys:&nbsp;<b>Space</b> to play/pause,&nbsp;<b>Enter</b> to add marker,&nbsp;<b>Ctrl+S</b> to save,&nbsp;<b>Up</b>/<b>Down</b> to increase/decrease points")
		
		if sys.platform == "darwin":
			self.hotkeyLabel.setFont(QFont(QFont().defaultFamily(), 25))
		else:
			self.hotkeyLabel.setFont(QFont(QFont().defaultFamily(), 12))
		self.hotkeyLabel.setStyleSheet("color: " + fontColor)
		self.vboxlayout.addWidget(self.hotkeyLabel)

		self.createMenu()

		self.prevSecond = 0
		self.prevMin = 0
		if "defaultVideoPath" in self.defaultConfig:
			self.loadVideoFromPath(self.defaultConfig["defaultVideoPath"])

		self.isPaused = True
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(200)
		self.timer.timeout.connect(self.updateUI)

	def updateCounter(self):
		self.counterLabel.setText(str(self.points))

	def sliderChanged(self, val):
		newPosition = val/10000.0
		if newPosition >= 1.0:
			newPosition = 0.99999
		self.mediaplayer.set_position(newPosition)

	def sliderSilentValue(self, val):
		self.slider.blockSignals(True)
		self.slider.setValue(val)
		self.slider.blockSignals(False)

	def pauseButtonClicked(self, event):
		self.isPaused = True
		if self.mediaplayer != None:
			self.mediaplayer.pause()
			self.pauseButton.hide()
			self.playButton.show()

	def backButtonClicked(self):
		if self.mediaplayer != None:
			self.mediaplayer.set_time(self.mediaplayer.get_time() - 1000)

	def nextButtonClicked(self):
		if self.mediaplayer != None:
			self.mediaplayer.set_time(self.mediaplayer.get_time() + 1000)

	def skipButtonClicked(self):
		if "skipTimeInSec" in self.defaultConfig:
			skipTimeInSec = self.defaultConfig["skipTimeInSec"]
		else:
			skipTimeInSec = 60
		if self.mediaplayer != None:
			if self.mediaplayer.get_time() + (skipTimeInSec * 1000) > self.mediaplayer.get_length():
				self.mediaplayer.set_time(self.mediaplayer.get_length())
			else:
				self.mediaplayer.set_time(self.mediaplayer.get_time() + (skipTimeInSec * 1000))

	def releaseButton(self):
		self.locked = False

	def increase(self):
		tf = self.timeFactor()
		if self.points < self.upper_slider_value:
			self.points += 1
			self.locked = True
			self.eta = time.time()

	def decrease(self):
		tf = self.timeFactor()
		if self.points > (self.lower_slider_value):
			self.points -= 1
			self.locked = True
			self.eta = time.time()

	def stopPlayer(self):
		self.stopClicked(None)

	def end_callback(self, event):
		self.mediaplayer.set_position(0)
		self.sliderSilentValue(0)
		# initialise seconds elapsed
		self.prevSecond = 0
		self.prevMin = 0

	def updateUI(self):
		if not self.isPaused:
			self.playButton.hide()
			self.pauseButton.show()

			self.backButton.setEnabled(True)
			self.nextButton.setEnabled(True)
			self.skipButton.setEnabled(True)
			self.stopButton.setEnabled(True)
			self.saveButton.setEnabled(True)
			self.incButton.setEnabled(True)
			self.decButton.setEnabled(True)
			self.markerButton.setEnabled(True)
			self.slider.setEnabled(True)
		else:
			self.playButton.show()
			self.pauseButton.hide()
			self.backButton.setEnabled(False)
			self.nextButton.setEnabled(False)
			self.skipButton.setEnabled(False)
			self.stopButton.setEnabled(False)
			self.saveButton.setEnabled(False)
			self.incButton.setEnabled(False)
			self.decButton.setEnabled(False)
			self.markerButton.setEnabled(False)
			self.slider.setEnabled(False)

		if self.mediaplayer.is_playing():
			self.updateCounter()
			playerTime = self.mediaplayer.get_time()

			sec = int(playerTime/1000)
			self.timeElapsed.setText(str(datetime.timedelta(seconds=sec)))

			if (sec != self.prevSecond) and len(self.points_list) > 0:
				tf = self.timeFactor()
				self.points_list.append([int(playerTime/tf), self.points])

			if (sec != self.prevSecond):
				tf = self.timeFactor()
				self.points_list.append([int(playerTime/tf), self.points])

			if self.slider != None:
				length = self.mediaplayer.get_length()
				scaled_player_time = int((playerTime / length) * 10000)
				self.sliderSilentValue(scaled_player_time)

			if "autoReturnRatingsToZero" in self.defaultConfig and self.defaultConfig["autoReturnRatingsToZero"] == True:
				if (sec != self.prevSecond) and self.locked == False:
					tf = self.timeFactor()
					if (time.time()-self.eta) >= 2:
						if self.points > 0:
							self.points -= 1

						if self.points < 0:
							self.points += 1

			self.prevSecond = int(playerTime/1000)
			self.prevMin = int(playerTime/(60*1000))
		else:
			self.timer.stop()
			if not self.isPaused:
				self.stopClicked(None)

	def setTheFilename(self):
		self.excelFilename = QtWidgets.QFileDialog.getSaveFileName(
		    None, 'Save File', '', 'Excel Files (*.xlsx);;All Files (*)')[0]

	def saveAs(self, event):
		self.setTheFilename()
		if self.excelFilename is not None:
			self.save(event)

	def save(self, event):
		self.x_axis = []
		self.y_axis = []
		self.markers_axis = []
		temporaryList = {}

		if self.excelFilename is None:
			self.excelFilename = executable_dir + os.sep + os.path.basename(
			    self.filename)+" ("+str(self.playedTimes)+") "+strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".xlsx"

		if len(self.points_list) > 0 or len(self.markers_list) > 0:
			for i in range(0, len(self.points_list)):
				[y, value] = self.points_list[i]
				temporaryList[y] = value
			# Only take the latest value in the list

			# iterate over the hash temporaryList	and get the key and value
			sortedMarkersList = dict(sorted(self.markers_list)).items()
			# turn sortedMarkersList which is an array with [key,value] into a list with key: value
			sortedMarkersList = {k: v for k, v in sortedMarkersList}
			
			for y, value in dict(sorted(temporaryList.items())).items():
				self.x_axis.append(y)
				self.y_axis.append(value)
				if self.lower_slider_value < 0 and self.upper_slider_value > 0:
					markerPosition = 0
				else:
					markerPosition = self.lower_slider_value
				if y in sortedMarkersList:
					currentMarker = markerPosition if sortedMarkersList[y] == 1 else None
				else:
					currentMarker = None
				
				self.markers_axis.append(currentMarker)

			workbook = xlsxwriter.Workbook(self.excelFilename)
			worksheet = workbook.add_worksheet()

			data = [self.x_axis, self.y_axis, self.markers_axis]
			for i in range(0, len(data[0])):
				data[0][i] = str(datetime.timedelta(seconds=int(data[0][i])))
			worksheet.write_column('A1', data[0])
			worksheet.write_column('B1', data[1])
			worksheet.write_column('C1', data[2])

			chart = workbook.add_chart({'type': 'line'})

			chart.add_series({
				'categories': '=Sheet1!$A$1:$A$'+str(len(self.x_axis)),
				'values': '=Sheet1!$B$1:$B$'+str(len(self.y_axis)),
				'name': 'Psychometric Study'
			})

			marker_chart = workbook.add_chart({'type': 'scatter'})
			marker_chart.add_series({
				'categories': '=Sheet1!$A$1:$A$'+str(len(self.x_axis)),
				'values': '=Sheet1!$C$1:$C$'+str(len(self.markers_axis)),
				'name': 'Markers'
			})

			# Combine the charts.
			chart.combine(marker_chart)

			chart.set_y_axis({'name': 'response', 'name_font': {
			                 'size': 14, 'bold': True}, 'num_font':  {'italic': True},
							'min': self.lower_slider_value, 'max': self.upper_slider_value,
							'crossing': self.lower_slider_value
							 })
			time = "sec"

			chart.set_x_axis({'name': 'time ('+str(time)+')',
			                 'name_font': {'size': 14, 'bold': True}, 'num_font':  {'italic': True},
							 
							  'major_gridlines': {
									'visible': True,
									'line': {'width': 1, 'dash_type': 'solid'}
								},
								'position_axis': 'on_tick'
							})

			worksheet.insert_chart('D1', chart)
			try:
				workbook.close()
			except:
				QtWidgets.QMessageBox.critical(self, "File not Saved", "File could not be saved at " + str(self.excelFilename), QtWidgets.QMessageBox.Yes)
			else: 
				QtWidgets.QMessageBox.information(self, "File Saved", "File saved at " + str(self.excelFilename), QtWidgets.QMessageBox.Yes)

			self.playedTimes += 1

			if "openExcelAfterSave" in self.defaultConfig:
				if self.defaultConfig["openExcelAfterSave"] == True:
					# open the excel file right after the save, with support for mac, linux and windows
					if not hasattr(os, 'startfile'):
						os.startfile = lambda f: subprocess.call(["open", f])
						if shutil.which("open") is not None:
							os.startfile = lambda f: subprocess.call(["open", f])
						elif shutil.which("xdg-open") is not None:
							os.startfile = lambda f: subprocess.call(["xdg-open", f])
					os.startfile(self.excelFilename)
		else:
			QtWidgets.QMessageBox.critical(self, "Error","You need to provide your response to video", QtWidgets.QMessageBox.Yes)

	def timeFactor(self):
		timex = 1
		if self.UNIT == self.SECOND:
			timex = 1000
		return timex

	def resetMetrics(self):
		if self.media != None:
			tf = self.timeFactor()
			duration = int(self.media.get_duration() / tf)
			self.x_axis = [x for x in range(0, duration+1)]
			self.y_axis = [0 for x in range(0, duration+1)]

			self.points = 0
			self.points_list = []

			# initialise seconds elapsed
			self.prevSecond = 0
			self.prevMin = 0

			# init slider
			self.slider.setRange(0, 10000)
			self.slider.setValue(0)
			self.totalTime.setText(str(datetime.timedelta(
			    seconds=int(self.media.get_duration()/1000))))
			self.record_zeros = False

	def playClicked(self, event):
		if self.mediaplayer != None:
			self.timer.start()
			self.mediaplayer.play()
			self.isPaused = False

	def changePlayButton(self, event):
		# if the video is playing, change the button to pause
		if self.isPaused == False:
			self.pauseButtonClicked(None)
		else:
			self.playClicked(None)

	def stopClicked(self, event):
		if self.mediaplayer != None:
			self.mediaplayer.stop()
			self.pauseButton.hide()
			self.playButton.show()
			self.resetMetrics()			

	def loadVideo(self):
		self.stopClicked(None)
		path = str(QtWidgets.QFileDialog.getOpenFileName(
		    self, "Load Video File", '', "video files (*.*)")[0])
		self.loadVideoFromPath(path)


	def loadVideoFromPath(self, path):
		print(path)
		self.filename = path
		self.playedTimes = 0
		if len(path) > 0:
			self.UNIT = self.SECOND

			self.media = self.vlc_instance.media_new(str(path))
			self.mediaplayer.set_media(self.media)	
			self.media.parse()

			if sys.platform.startswith('linux'):  # for Linux using the X Server
				self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
			elif sys.platform == "win32":  # for Windows
				self.mediaplayer.set_hwnd(self.videoframe.winId())
			elif sys.platform == "darwin":  # for MacOS
				self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

			self.playButton.setEnabled(True)
			self.resetMetrics()


	def createMenu(self):
		self.openAction = QtWidgets.QAction(
		    "Load video file", self, triggered=self.loadVideo)
		self.openAction.setShortcut('Ctrl+O')

		self.saveAction = QtWidgets.QAction("Save", self, triggered=self.save)
		self.saveAction.setShortcut('Ctrl+S')

		self.saveAsAction = QtWidgets.QAction("Save as", self, triggered=self.saveAs)
		self.saveAsAction.setShortcut('Ctrl+Shift+S')

		self.exitAction = QtWidgets.QAction(
		    "Exit", self, triggered=QtCore.QCoreApplication.instance().quit)
		self.exitAction.setShortcut('Ctrl+Q')

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(self.openAction)
		fileMenu.addAction(self.saveAction)
		fileMenu.addAction(self.saveAsAction)
		fileMenu.addAction(self.exitAction)

		self.initDialog()

		settingsMenu = menubar.addMenu('&Settings')
		set_range_action = QtWidgets.QAction("&Set Range", self)
		set_range_action.triggered.connect(self.showDialog)
		settingsMenu.addAction(set_range_action)

		# Help Menu
		helpMenu = menubar.addMenu('&Help')
		aboutAction = QtWidgets.QAction("&About", self)

		# add a menu item with information about used libraries
		licensesAction = QtWidgets.QAction("&Licenses", self)
		licensesAction.triggered.connect(self.showLicenses)
		helpMenu.addAction(licensesAction)

		aboutAction.triggered.connect(self.showAbout)
		helpMenu.addAction(aboutAction)

	def initDialog(self):
		self.lower_slider_value = -10
		self.upper_slider_value = 10
		if "lowerSliderValue" in self.defaultConfig:
			self.lower_slider_value = self.defaultConfig["lowerSliderValue"]
		if "upperSliderValue" in self.defaultConfig:
			self.upper_slider_value = self.defaultConfig["upperSliderValue"]
	

	def showDialog(self):
        # create a dialog for defining the range
		dialog = QtWidgets.QDialog(self)
		dialog.setWindowTitle("Set Range")

        # create a vertical layout for the dialog
		vbox = QtWidgets.QVBoxLayout()

        # create two sliders for defining the range
		self.lower_slider = QtWidgets.QSlider(Qt.Horizontal)
		self.lower_slider.setMinimum(-10)
		self.lower_slider.setMaximum(10)
		self.lower_slider.setValue(self.lower_slider_value)

		self.upper_slider = QtWidgets.QSlider(Qt.Horizontal)
		self.upper_slider.setMinimum(-10)
		self.upper_slider.setMaximum(10)
		self.upper_slider.setValue(self.upper_slider_value)

        # create a label to display the range
		label = QLabel(f"Range: {self.lower_slider_value} to {self.upper_slider_value}")

        # connect the sliders to update the label when the range changes
		self.lower_slider.valueChanged.connect(lambda value: self.updateRange(
            value, self.upper_slider.value(), self.lower_slider, self.upper_slider, label))
		self.upper_slider.valueChanged.connect(lambda value: self.updateRange(
            self.lower_slider.value(), value, self.lower_slider, self.upper_slider, label))

        # create a horizontal layout for the lower slider
		hbox_lower = QHBoxLayout()
		hbox_lower.addWidget(QLabel("Lower Bound"))
		hbox_lower.addWidget(self.lower_slider)

        # create a horizontal layout for the upper slider
        
		hbox_upper = QHBoxLayout()
		hbox_upper.addWidget(QLabel("Upper Bound"))
		hbox_upper.addWidget(self.upper_slider)

        # add the horizontal layouts and label to the vertical layout
		vbox.addLayout(hbox_lower)
		vbox.addLayout(hbox_upper)
		vbox.addWidget(label)

		# set the vertical layout for the dialog
		dialog.setLayout(vbox)

		# show the dialog
		dialog.exec_()

	def updateRange(self, lower_value, upper_value, lower_slider, upper_slider, label):
		if lower_value > upper_value:
			lower_slider.setValue(upper_value)
			upper_slider.setValue(lower_value)
			self.lower_slider_value = upper_value
			self.upper_slider_value = lower_value
		else:
			self.lower_slider_value = lower_value
			self.upper_slider_value = upper_value

		# update the label with the new range values
		label.setText(f"Range: {lower_value} to {upper_value}")

	def addMarker(self):
		if self.mediaplayer != None:
			tf = self.timeFactor()
			self.markers_list.append([int(self.mediaplayer.get_time()/tf), 1])

	def showAbout(self):
		about_text = "PsychometricStudy Version: " + version.VERSION + "\n\n"
		about_text += """This software was commissioned by Nathan Ducker.
		We kindly request that you cite the applicable paper when using
		this software for your research or publication purposes.

		DUCKER, N.T. (2022), Bridging the Gap Between Willingness to Communicate and Learner Talk. 
		The Modern Language Journal, 106: 216-244. https://doi.org/10.1111/modl.12764
		
		DUCKER, N.T. (2021), Protecting and enhancing willingness to communicate
		with idiodynamic peer-peer strategy sharing.
		System, 103, 102634 https://doi.org/10.1016/j.system.2021.102634

		Ducker, N. (2020). Perceptions of Silence in the Classroom. The TESOL Encyclopedia of English Language Teaching, 
		1–8. doi:https://doi.org/10.1002/9781118784235.eelt0987 

		Nathan Ducker
		Assistant Professor
		Faculty of Humanities
		Miyazaki Municipal University
		Funatsuka 1-1-2
		Miyazaki City
		Miyazaki Prefecture
		880-8520
		Japan
		+ 81-985-20-4817
		
		Nathan Ducker is an Assistant Professor at Miyazaki Municipal University where
		he teaches content classes in intercultural communication and multicultural
		policy. He is a PhD candidate at Aston University, where he studies willingness to
		communicate in the Japanese context. 
		He can be contacted at nathanducker@gmail.com"""

		# Make a window and add the about text
		about_window = QtWidgets.QDialog(self)
		about_window.setWindowTitle("About")
		about_window.setWindowModality(Qt.ApplicationModal)
		about_window.resize(1200, 1100)
		about_texte = QtWidgets.QTextEdit()
		about_texte.setText(about_text)
		about_texte.setReadOnly(True)
		about_texte.setLineWrapColumnOrWidth(600)
		about_texte.setTabStopWidth(2)
		about_texte.setTabChangesFocus(True)
		about_texte.setAcceptRichText(False)

		# add a button to close the window
		about_button = QPushButton("Close", about_window)
		about_button.clicked.connect(about_window.close)
		# add the button to the layout
		about_layout = QtWidgets.QVBoxLayout(about_window)
		about_layout.addWidget(about_texte)
		about_layout.addWidget(about_button)

		# show the window
		about_window.exec_()
		
	def showLicenses(self):
		about_text = "This software is copyrighted by Nathan Ducker. \n"	
		about_text += "This software was created by: \n"
		about_text += "Nathan Ducker, Andi Idogawa \n"
		about_text += "This software uses the following libraries:" + "\n"
		about_text += "Version of the software: " + version.VERSION + "\n"
		about_text += "Python " + sys.version + "\n"
		about_text += "PyQt " + QtCore.PYQT_VERSION_STR + "\n"
		about_text += "XLSXWriter " + xlsxwriter.__version__ + "\n"
		about_text += "The Font Awesome and Elusive Icons fonts are licensed under the SIL Open Font License. \n"
		about_text += "QtAwesome Copyright © 2015-2022 Spyder Project Contributors " + qtawesome.__version__ + "\n"
		about_text += "VLC " + vlc.__version__ + "\n"
		QtWidgets.QMessageBox.about(self, "About", about_text)

def crash_handler(exctype, value, traceback):
    # Handle the exception
	print("An error occurred:", value)

if __name__=='__main__':
	sys.excepthook = crash_handler
	app = QtWidgets.QApplication (sys.argv)
	app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
	window = Window()
	window.show()
	sys.exit(app.exec_())