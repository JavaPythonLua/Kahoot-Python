import os
import socket
import sqlite3 as sq
from multiprocessing import Process, Event, Queue
import queue
import select
import threading
import pickle
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QLineEdit, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap, QFontMetrics
from PySide6.QtCore import Qt, Signal
import logging
import sys

#Stores of Data:
#HandleSockets.playersConns:dictionary Stores each client's conn under their client number
#{1:<class "socket.socket">,s:<class "socket.socket">}

#clientData:database A sqlite database, just stored in memory holds the client's Number, Nickname & Addr

#NB createNewPlayer takes a tuple as an argument. The tuple must contain these things, in this order (The Client's Nickname, The Client's Addr, The Client's Conn)
class HandleSockets(socket.socket):
    def __init__(self,type:socket.SocketKind=socket.AF_INET,protocol:socket.AddressFamily=socket.SOCK_STREAM,enc:str="utf-8"):
        super().__init__(type,protocol)
        self.enc = enc
        self.bind((socket.gethostbyname(socket.gethostname()),0))
        self.HOST = self.getsockname()[0]
        self.PORT = self.getsockname()[1]
        self.listen()

    def returnConnectionDetails(self):
        return (self.HOST,self.PORT)


    def handleClientQs(self,conn:socket.socket,que,correctAns):
        conn.send("Q".encode(self.enc))
        clientAns = conn.recv(1024).decode(self.enc)
        que.put((conn,clientAns))
        if clientAns == correctAns:
            conn.send("correct".encode(self.enc))
        else:
            conn.send("incorrect".encode(self.enc))


    def endQuizForClients(self,conn:socket.socket,place:int):
        tup = ("e",place)
        conn.send(pickle.dumps(tup))
        conn.close()

class handleClients():
    def __init__(self,QuesNos:int):
        self.SQLConnection = sq.connect(":memory:")
        self.cur = self.SQLConnection.cursor()
        self.quesNos = QuesNos
        self.playersConns = {}
        self.playersNumbers = {}
        self.cur.execute("CREATE TABLE clientData (ClientNo INTEGER PRIMARY KEY AUTOINCREMENT, ClientName VARCHAR(255) NOT NULL, ClientAddr VARCHAR(255) NOT NULL)")
        for i in range(1,QuesNos+1):
            self.cur.execute(f"ALTER TABLE clientData ADD COLUMN Q{i} INTEGER DEFAULT 0")
        self.cur.execute("ALTER TABLE clientData ADD COLUMN Total INTEGER DEFAULT 0")

    def createNewPlayer(self,playerData:tuple):
        self.cur.execute("INSERT INTO clientData (ClientName, ClientAddr) VALUES (?,?)",(playerData[0],str(playerData[1])))
        self.cur.execute("SELECT ClientNo FROM clientData WHERE ClientName=?",(playerData[0],))
        clientNo = self.cur.fetchone()[0]
        self.playersConns[clientNo] = playerData[2]
        self.playersNumbers[playerData[2]] = clientNo

    def fetchClientByNum(self,num):
        clientName = self.cur.execute("SELECT ClientName FROM clientData WHERE ClientNo=?",(num,))
        return clientName

    def fetchClientByConn(self,conn):
        num = self.playersNumbers[conn]
        clientName = self.cur.execute("SELECT ClientName FROM clientData WHERE ClientNo=?", (num,))
        return clientName

    def updateScoresByNum(self,QNo,num:int):
        self.cur.execute(f"UPDATE clientData SET Q{QNo} = ? WHERE ClientNo = ?",(1,num))

    def updateTotals(self):
        self.cur.execute("SELECT COUNT(*) FROM clientData")
        rows = self.cur.fetchone()[0]
        for i in range(1,rows+1):
            total = 0
            for f in range(1, self.quesNos+1):
                self.cur.execute(f"SELECT Q{f} FROM clientData WHERE ClientNo=?",(i,))
                value = self.cur.fetchone()[0]
                total += value
                self.cur.execute(f"UPDATE clientData SET Total=? WHERE ClientNo=?",(total,i))

    def getHighestTotal(self):
        self.cur.execute("SELECT COUNT(*) FROM clientData")
        rows = self.cur.fetchone()[0]
        highest = 0
        totals = []
        for i in range(1,rows+1):
            self.cur.execute("SELECT total FROM clientData WHERE ClientNo=?",(i,))
            total = self.cur.fetchone()[0]
            totals.append(total)
        for i in totals:
            if i > highest:
                highest = i
        self.cur.execute("SELECT ClientName FROM clientData WHERE total=?",(highest,))
        highestName = self.cur.fetchone()[0]
        return (highestName,highest)

class HandlePackFile():
    def __init__(self,packFile):
        if not os.path.exists(packFile):
            raise FileNotFoundError(f"Packfile '{packFile}' cannot be found in CWD")
        else:
            try:
                self.SQLConnection = sq.connect(packFile)
                self.cur = self.SQLConnection.cursor()
            except sq.Error:
                raise sq.DatabaseError("Not a packfile!")

    def fetchNumQuizzes(self):
        try:
            self.cur.execute("SELECT COUNT(*) FROM packData")
        except sq.Error:
            logging.critical("Cannot count rows in packData")
            sys.exit(1)
        NoQuizzes = self.cur.fetchone()[0]
        return NoQuizzes

    def fetchPackDetails(self,QuizNo):
        self.cur.execute("SELECT QuizName FROM packData WHERE QuizNo=?",(QuizNo,))
        QuizName = self.cur.fetchone()[0]
        self.cur.execute("SELECT NoQs FROM packData WHERE QuizNo=?",(QuizNo,))
        NoQs = self.cur.fetchone()[0]
        return (QuizName,NoQs)

    def fetchQuestion(self,QuizName,QuesNo):
        self.cur.execute(f'SELECT QuesName, Ans1, Ans2, Ans3, CorrectAns FROM "{QuizName}" WHERE QuesNo=?',(QuesNo,))
        row = self.cur.fetchone()
        if row is None:
            raise ValueError(f"No question found in table '{QuizName}' with QuesNo={QuesNo}")
        return row

def stopAcceptingClients(stop_accepting):
    input()
    stop_accepting.set()

class serverDetailsWin(QWidget):
    packfileInputted = Signal(object)
    def __init__(self,detailsWinWidth,detailsWinHeight):
        super().__init__()
        self.packfilePath = None
        self.setWindowTitle("Cahoot!")
        self.resize(detailsWinWidth,detailsWinHeight)
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

    def addPackfileFields(self):
        packfileLabel = QLabel("Packfile:")
        packfileLabel.adjustSize()
        self.layout.addWidget(packfileLabel,alignment=Qt.AlignHCenter)
        self.packfileField = QLineEdit()
        self.packfileField.setFixedSize(300, 30)
        self.layout.addWidget(self.packfileField, alignment=Qt.AlignHCenter)

    def addNextStepBtn(self,que):
        self.nextBtn = QPushButton("Continue")
        self.nextBtn.adjustSize()
        self.nextBtn.clicked.connect(lambda: self.onNextBtnClicked(que))
        self.layout.addWidget(self.nextBtn,alignment=Qt.AlignHCenter)

    def onNextBtnClicked(self,que):
        if not self.packfileField.text() is None:
            packFilePath = self.packfileField.text()
            if packFilePath[-3] == ".":
                packFilePath = packFilePath.strip()[:-3]
            self.packfilePath = packFilePath
            self.packfileInputted.emit(self)







def main():
    stop_accepting = threading.Event()
    clientDataQueue = Queue()
    clientAnswerQueue = queue.Queue()
    hpf = HandlePackFile("testPack.db")
    NoQuizzes = hpf.fetchNumQuizzes()
    QuizNames = []
    for i in range(NoQuizzes):
        QuizNames.append(hpf.fetchPackDetails(i+1)[0])
    print(f"There are {NoQuizzes} quizzes in this pack file:")
    for i in range(len(QuizNames)):
        print(f"{i+1}: {QuizNames[i]}")
    print("Please choose a quiz number:")
    ChosenNo = input()
    quizDetails = hpf.fetchPackDetails(ChosenNo)
    NoQs = quizDetails[1]
    hc = handleClients(NoQs)
    hs = HandleSockets()
    details = hs.returnConnectionDetails()
    HOST = details[0]
    PORT = details[1]
    print(f"The host is {HOST}")
    print(f"The port is {PORT}")
    print("Press enter to stop accepting clients")
    stop_accept_thread = threading.Thread(target=stopAcceptingClients,args=(stop_accepting,))
    stop_accept_thread.start()
    while not stop_accepting.is_set():
        ready, _, _ = select.select([hs], [], [], 1)
        if hs in ready:
            conn, addr = hs.accept()
            nickname = conn.recv(1024).decode(hs.enc)
            print(f"{nickname} joined the game")
            hc.createNewPlayer((nickname, addr, conn))
    stop_accept_thread.join()
    print("Starting Quiz")
    while True:
        try:
            clientData = clientDataQueue.get_nowait()
            hc.createNewPlayer(clientData)
        except queue.Empty:
            break
    for i in range(1, NoQs+1):
        print(QuizNames)
        Ques = hpf.fetchQuestion(QuizNames[int(ChosenNo)-1],i)
        print(Ques[0])
        print(f"A: {Ques[1]}\nB: {Ques[2]}\nC: {Ques[3]}")
        correctAns = Ques[4]
        clientAnswerThreads = []
        clientAnswers = 0
        clients = len(hc.playersNumbers)
        for client in hc.playersNumbers.keys():
            thisThread = threading.Thread(target=hs.handleClientQs,args=(client,clientAnswerQueue,Ques[4]))
            clientAnswerThreads.append(thisThread)
            thisThread.start()
        while True:
            try:
                clientAnswerData = clientAnswerQueue.get()
                clientAnswers += 1
                clientNo = hc.playersNumbers[clientAnswerData[0]]
                clientAns = clientAnswerData[1]
                if clientAns == correctAns:
                    hc.updateScoresByNum(i,int(clientNo))
                if clientAnswers == clients:
                    break
            except queue.Empty:
                continue
        for thread in clientAnswerThreads:
            thread.join()
    hc.updateTotals()
    highest = hc.getHighestTotal()
    print(f"{highest[0]} got the highest score of {highest[1]}")
    for client in hc.playersNumbers.keys():
        hs.endQuizForClients(client,1)

def handlePackFileData():
    hpf.__init__(sdw.packfilePath+".db")


if __name__ == "__main__":
    app = QApplication([])
    packfile_queue = queue.Queue()
    global sdw
    global hpf
    global hc
    global hs
    sdw = serverDetailsWin(700,500)
    hpf = HandlePackFile.__new__(HandlePackFile)
    hc = handleClients.__new__(handleClients)
    hs = HandleSockets.__new__(HandleSockets)
    sdw.addPackfileFields()
    sdw.addNextStepBtn(packfile_queue)
    sdw.packfileInputted.connect(handlePackFileData)
    sdw.layout.addStretch()
    sdw.show()
    app.exec()
#I have to add this