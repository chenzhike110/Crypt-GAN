from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QComboBox, QTextEdit
from Utils import utils
from Caesar import caesar
from Vigenere import vigenere
from Scytale import scytale
import math

class Encoder(QWidget):

    restarted = pyqtSignal(str, str, str)
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
        if self.method.currentIndex() == 0:
            try:
                key = str(int(key))
            except:
                key = '10'
            txt = caesar.caesar(txt, int(key))
        if self.method.currentIndex() == 3:
            txt = vigenere.vigenere(txt, key, False)
        if self.method.currentIndex() == 2:
            try:
                key = str(int(key))
            except:
                key = '10'
            txt = scytale.cipher(txt, int(key), None)
        QMessageBox.information(self, "密文", "{0}".format(txt)) == QMessageBox.Yes
        print("decode!!", key, self.method.currentIndex())
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
        if method == "Caesar":
            key = int(key)
            result = caesar.caesar(txt, 26-key)
        if method == "Vigenere":
            result = vigenere.vigenere(txt, key, True)
        if method == 'Scytale':
            result = scytale.cipher(txt,math.ceil(len(txt)/int(key)),self.resultEdit) 
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
        self.resultEdit.append(' ')
        if method == "Caesar":
            key, result = caesar.crack(txt, self.resultEdit)
            if result == None:
                result = "Failed"
            self.resultEdit.append('Result: '+result)
            self.resultEdit.append(' ')
        if method == "Vigenere":
            result = vigenere.crack(txt, self.resultEdit)
            print(result)
            if result != None:
                self.resultEdit.append('Try key: '+result[0])
                self.resultEdit.append('Get result: '+result[1])
                self.resultEdit.append(' ')
        if method == "Scytale":
            result = scytale.crack(txt, self.resultEdit)
            if result != None:
                self.resultEdit.append('Try key: '+ ''.join([str(i) for i in result[0]]))
                self.resultEdit.append('Get result: '+result[1])
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