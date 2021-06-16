import PyQt5
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QComboBox, QTextEdit
# from lib.utils import *
from lib import utils
# from lib.validator import *
from tools import caesar

class Encoder(QWidget):

    restarted = pyqtSignal(str, str, int)
    crake_start = pyqtSignal(str, str)

    def __init__(self, Decoder, Craker, *args, **kwargs):
        super(Encoder, self).__init__(*args, **kwargs)
        self.setWindowTitle('Sender')
        self.decoder = Decoder
        self.craker = Craker
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        txt = QLabel("CryptTools", self)
        txt.setAlignment(Qt.AlignCenter)
        layout.addWidget(txt)
        self.method = QComboBox(self)
        self.method.addItems(["Caesar","Aes","Scytale","Vigenere"])
        layout.addWidget(self.method)
        self.keyvalue = QLineEdit(self, placeholderText="使用的Key", returnPressed=self.onChangeDir)
        layout.addWidget(self.keyvalue)
        self.dirEdit = QLineEdit(
            self, placeholderText="请输入要转化的明文", returnPressed=self.onChangeDir)
        layout.addWidget(self.dirEdit)
        layout.addWidget(QPushButton(
            "一键加密", self, clicked=self.onChangeDir))
        self.restarted.connect(self.decoder.crack)
        self.crake_start.connect(self.craker.crack)

    def onChangeDir(self):
        txt = self.dirEdit.text()
        txt = utils.read(txt)
        key = self.keyvalue.text()
        try:
            key = int(key)
        except:
            key = 10
        if self.method.currentIndex() == 0:
            txt = caesar.caesar(txt, key)
        QMessageBox.information(self, "密文", "{0}".format(txt)) == QMessageBox.Yes
        print("decode!!")
        self.restarted.emit(txt, self.method.currentText(), key)
        self.crake_start.emit(txt, self.method.currentText())

class Decoder(QWidget):

    def __init__(self,  *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.setWindowTitle('Receiver')
        self.resize(600, 300)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)
        layout.addWidget(self.resultEdit)
    
    def crack(self, txt, method, key):
        self.resultEdit.append('start decrypt ...')
        self.resultEdit.append('Method: '+method)
        self.resultEdit.append('Key: {0}'.format(key))
        self.resultEdit.append('Cyphertext: '+txt)
        result = caesar.caesar(txt, 26-key)
        self.resultEdit.append('Result: '+result)
        self.resultEdit.append(' ')
    
class Listener(QWidget):

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self.setWindowTitle('Cracker')
        self.resize(600, 300)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)
        layout.addWidget(self.resultEdit)
    
    def crack(self, txt, method):
        self.resultEdit.append('start crack ...')
        self.resultEdit.append('Method: '+method)
        self.resultEdit.append('Cyphertext: '+txt)
        key, result = caesar.crack(txt)
        self.resultEdit.append('Result: '+result)
        self.resultEdit.append(' ')

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    w2 = Decoder()
    w2.show()

    w3 = Listener()
    w3.show()

    w = Encoder(w2, w3)
    w.show()

    sys.exit(app.exec_())