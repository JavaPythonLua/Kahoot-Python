#The Client-Side code for Kahoot-Python
#Copyright (C) 2026  Alex Inns

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.


#MUST INSTALL PySide6 & Colorlog beforehand using pip
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QLineEdit, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap, QFontMetrics
from PySide6.QtCore import Qt, Signal
import sys
import logging
import socket
import threading
import colorlog
from time import sleep
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)8s: %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO,stream=sys.stdout)
logging.info("<program>  Copyright (C) <year>  <name of author>")
logging.info("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
logging.info("This is free software, and you are welcome to redistribute it under certain conditions; type `show c' for details.")

class TitleWin(QWidget):
    detailsInputted = Signal(tuple,object)
    def __init__(self,mainWinWidth=400,mainWinHeight=500):
        super().__init__()
        self.setWindowTitle("Cahoot!")
        self.resize(mainWinWidth,mainWinHeight)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def addTitle(self,file):
        label = QLabel()
        pixmap = QPixmap(file)
        if pixmap.isNull():
            logging.warning("Title Image not found")
        label.setPixmap(pixmap)
        label.adjustSize()
        self.layout.addWidget(label, alignment=Qt.AlignTop | Qt.AlignHCenter)

    def addTextFields(self):
        hostLabel = QLabel("Host:")
        hostLabel.adjustSize()
        self.layout.addWidget(hostLabel, alignment=Qt.AlignHCenter)
        self.hostField = QLineEdit()
        self.hostField.setFixedSize(200, 30)
        self.layout.addWidget(self.hostField, alignment=Qt.AlignHCenter)
        portLabel = QLabel("Port:")
        portLabel.adjustSize()
        self.layout.addWidget(portLabel, alignment=Qt.AlignHCenter)
        self.portField = QLineEdit()
        self.portField.setFixedSize(200, 30)
        self.layout.addWidget(self.portField, alignment=Qt.AlignHCenter)
        nicknameLabel = QLabel("Nickname:")
        nicknameLabel.adjustSize()
        self.layout.addWidget(nicknameLabel, alignment=Qt.AlignHCenter)
        self.nicknameField = QLineEdit()
        self.nicknameField.setFixedSize(200,30)
        self.layout.addWidget(self.nicknameField, alignment=Qt.AlignHCenter)

    def addStartButton(self):
        self.connectBtn = QPushButton("Connect!")
        self.connectBtn.adjustSize()
        self.connectBtn.clicked.connect(self.onConnectBtnClicked)
        self.layout.addWidget(self.connectBtn, alignment=Qt.AlignHCenter)

    def onConnectBtnClicked(self):
        host = self.hostField.text().strip()
        port = self.portField.text()
        nickname = self.nicknameField.text()
        self.detailsInputted.emit((host,port,nickname),self)

class QuestionWin(QWidget):
    answerSelected = Signal(str)
    def __init__(self,cahootInstance,args=[],mainWinWidth=700,mainWinHeight=500):
        super().__init__()
        self.setWindowTitle("Cahoot!")
        self.resize(mainWinWidth,mainWinHeight)
        self.layout = QVBoxLayout(self)
        self.socketFramework = cahootInstance

    def addQuestionTitle(self):
        titleLabel = QLabel("Select A, B or C")
        titleLabel.adjustSize()
        self.layout.addWidget(titleLabel,alignment=Qt.AlignHCenter)

    def addQuestionButtons(self):
        self.BtnA = QPushButton("A")
        self.BtnB = QPushButton("B")
        self.BtnC = QPushButton("C")
        self.BtnA.setStyleSheet("""
            QPushButton {
                background-color: #c50101;
                color: white;
                padding: 8px;
                border: 2px solid #ef4d4d;
                border-radius: 8px;
            }
            QPushButton:pressed {
                background-color: #ef4d4d;
                color: black;
                border: 2px solid #c50101;
            }
        """)
        self.BtnB.setStyleSheet("""
                    QPushButton {
                        background-color: #039a09;
                        color: white;
                        padding: 8px;
                        border: 2px solid #60d164;
                        border-radius: 8px;
                    }
                    QPushButton:pressed {
                        background-color: #60d164;
                        color: black;
                        border: 2px solid #039a09;
                    }
                """)
        self.BtnC.setStyleSheet("""
                    QPushButton {
                        background-color: #fada00;
                        color: white;
                        padding: 8px;
                        border: 2px solid #e0d16a;
                        border-radius: 8px;
                    }
                    QPushButton:pressed {
                        background-color: #e0d16a;
                        color: black;
                        border: 2px solid #fada00;
                    }
                """)
        self.BtnA.clicked.connect(lambda: self.answer("a"))
        self.BtnB.clicked.connect(lambda: self.answer("b"))
        self.BtnC.clicked.connect(lambda: self.answer("c"))
        self.answerChosen = None
        self.layout.addWidget(self.BtnA)
        self.layout.addWidget(self.BtnB)
        self.layout.addWidget(self.BtnC)

    def answer(self,option):
        self.answerSelected.emit(option)

class endingWin(QWidget):
    def __init__(self,mainWinWidth=400,mainWinHeight=500):
        super().__init__()
        self.setWindowTitle("Cahoot!")
        self.resize(mainWinWidth,mainWinHeight)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0,0,0,0)
        endQuizLabel = QLabel("That's the end of the quiz!")
        endQuizLabel.adjustSize()
        self.layout.addWidget(endQuizText)

    def addPlaceText(self,place):
        place = int(place)
        if place == 1:
            placeText = "You came in 1st place"
        elif place == 2:
            placeText = "You came in 2nd place"
        elif place == 3:
            placeText = "You came in 3rd place"
        else:
            placeText = "You came in " + str(place) + "th place"
        placeLabel = QLabel(placeText)
        placeLabel.adjustSize()
        self.layout.addWidget(placeLabel)




class clientCahoot:
    def __init__(self,version=socket.AF_INET,protocol=socket.SOCK_STREAM):
        if not type(version) == socket.AddressFamily:
            raise TypeError("Socket version must be <class 'socket.AddressFamily'> not " + str(type(version)))
        if not type(protocol) == socket.SocketKind:
            raise TypeError("Socket protocol must be <class 'socket.SocketKind'> not " + str(type(protocol)))
        self.s = socket.socket(version,protocol)
    def connect(self,HOST,PORT):
        try:
            self.s.connect((HOST,int(PORT)))
            logging.debug("Connecting")
        except ConnectionRefusedError:
            return ("CRE",None)
        except OSError as e:
            return ("OSE",e)
        except TimeoutError:
            return ("TE",None)
        return ("Connected",None)
    def sendNickname(self,nickname="Unnamed Player",encoding='utf-8'):
        self.s.send(nickname.encode(encoding))
    def runQuestions(self,encoding='utf-8'):
        q = self.s.recv(1024).decode(encoding)
        if q == "Q":
            return "question"
        elif q == "e":
            return "end"
        else:
            logging.warning("Did not recieve a question or ending placeholder. Program will skip this question")
            return "skip"
    def sendans(self,ans:str,encoding='utf-8'):
        self.s.send(ans.encode(encoding))
        correct = self.s.recv(1024).decode(encoding)
        if correct == "correct":
            return "correct"
        else:
            return "incorrect"
    def getPlace(self,encoding='utf-8'):
        place = self.s.recv(1024).decode(encoding)
        return place

def answerRecieved(answer):
    pass




def doQuestions():
    global qw
    global cc

def detailsRecieved(details,tw):
    global cc
    global qw
    if not details[1].isdigit():
        logging.info("Port must be a positive integer represented in base 10")
    cc = clientCahoot()
    connected = cc.connect(details[0],int(details[1]))
    if connected[0] == "Connected":
        logging.info("Successfully connected to game")
        cc.sendNickname(details[2])
        tw.close()

    elif connected[0] == "CRE":
        logging.error("Connection was actively refused by the target machine")
    elif connected[0] == "OSE":
        logging.error("An error occurred: " + connected[1])
    elif connected[0] == "TE":
        logging.error("Connection attempt timed out")
    else:
        logging.error("An unknown error occurred")







app = QApplication(sys.argv)
cc = clientCahoot()
tw = TitleWin()
tw.addTitle("Connect-Logo.jpg")
tw.addTextFields()
tw.addStartButton()
tw.detailsInputted.connect(detailsRecieved)
tw.layout.addStretch()
qw = QuestionWin(None)
qw.addQuestionTitle()
qw.addQuestionButtons()
qw.answerSelected.connect(answerRecieved)
qw.layout.addStretch()
tw.show()
app.exec()


