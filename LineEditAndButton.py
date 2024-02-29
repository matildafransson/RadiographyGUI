
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QSlider, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon


class LineEditAndButton(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self, parent)

        self.selectDirW = QHBoxLayout()
        self.txtZone = QLineEdit()
        self.txtZone.setReadOnly(True)

        self.buttonDir = QPushButton()
        self.buttonDir.setIcon(QIcon('./icon/dirIcon.png'))

        self.selectDirW.addWidget(self.txtZone)
        self.selectDirW.addWidget(self.buttonDir)

        self.setLayout(self.selectDirW)
