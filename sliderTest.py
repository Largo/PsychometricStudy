from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # create a QAction for "Set Range"
        set_range_action = QAction("Set Range", self)
        set_range_action.triggered.connect(self.showDialog)
        self.menuBar().addAction(set_range_action)
        
    def showDialog(self):
        # create a dialog for defining the range
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Range")
        
        # create a vertical layout for the dialog
        vbox = QVBoxLayout()
        
        # create two sliders for defining the range
        lower_slider = QSlider(Qt.Horizontal)
        lower_slider.setMinimum(-10)
        lower_slider.setMaximum(10)
        lower_slider.setValue(-10)
        
        upper_slider = QSlider(Qt.Horizontal)
        upper_slider.setMinimum(-10)
        upper_slider.setMaximum(10)
        upper_slider.setValue(10)
        
        # create a label to display the range
        label = QLabel("Range: -10 to 10")
        
        # connect the sliders to update the label when the range changes
        lower_slider.valueChanged.connect(lambda value: self.updateRange(value, upper_slider.value(), lower_slider, upper_slider, label))
        upper_slider.valueChanged.connect(lambda value: self.updateRange(lower_slider.value(), value, lower_slider, upper_slider, label))
        
        # create a horizontal layout for the lower slider
        hbox_lower = QHBoxLayout()
        hbox_lower.addWidget(QLabel("Lower Bound"))
        hbox_lower.addWidget(lower_slider)
        
        # create a horizontal layout for the upper slider
        hbox_upper = QHBoxLayout()
        hbox_upper.addWidget(QLabel("Upper Bound"))
        hbox_upper.addWidget(upper_slider)
        
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
        # update the label with the new range values
        label.setText(f"Range: {lower_value} to {upper_value}")

if __name__=='__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
