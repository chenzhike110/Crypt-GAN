from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QComboBox, QTextEdit
import torch
from Utils import utils
from Caesar import caesar
from Vigenere import vigenere
from Scytale import scytale
from GAN import validate, net
from AES.aes import *
import base64
import math


class Encoder(QWidget):

    restarted = pyqtSignal(str, str, str)
    crake_start = pyqtSignal(str, str)

    netdecrypt = pyqtSignal(torch.Tensor, str, torch.Tensor)
    netcrack = pyqtSignal(torch.Tensor, str)

    def __init__(self, Decoder, Craker, net, *args, **kwargs):
        super(Encoder, self).__init__(*args, **kwargs)
        self.setWindowTitle('Sender')
        self.net = net
        self.decoder = Decoder
        self.craker = Craker
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        txt = QLabel("CryptTools", self)
        txt.setAlignment(Qt.AlignCenter)
        layout.addWidget(txt)
        self.method = QComboBox(self)
        self.method.addItems(["Caesar","AES","Scytale","Vigenere","GAN"])
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
        self.netdecrypt.connect(self.decoder.crack)
        self.netcrack.connect(self.craker.crack)

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
        if self.method.currentIndex() == 1:
            key = key.encode('utf8')
            key = add_to_16(key)
            txt = txt.encode('utf8')
            txt = encrypt(txt, key)
            txt = base64.b64encode(txt)
            txt = txt.decode('utf8')
            key = key.decode('utf8')
        if self.method.currentIndex() == 3:
            txt = vigenere.vigenere(txt, key, False)
        if self.method.currentIndex() == 2:
            try:
                key = str(int(key))
            except:
                key = '10'
            txt = scytale.cipher(txt, int(key), None)
        if self.method.currentIndex() == 4:
            txt, key = validate.random_generate_ptext_and_key(net.PTEXT_SIZE, net.KEY_SIZE)
            ctext = self.net(torch.cat((txt, key), 1).float())
        if self.method.currentIndex() != 4:
            QMessageBox.information(self, "密文", "{0}".format(txt))
            self.restarted.emit(txt, self.method.currentText(), key)
            self.crake_start.emit(txt, self.method.currentText())
        else:
            self.netdecrypt.emit(ctext, self.method.currentText(), key)
            self.netcrack.emit(ctext, self.method.currentText())
            QMessageBox.information(self, "报文信息", "随机生成明文: {0}\n随机生成密钥: {1}\n密文: {2}".format(txt,key,ctext))
        print("decode!!", key, self.method.currentIndex())
        

class Decoder(QWidget):

    def __init__(self, net, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.setWindowTitle('Receiver')
        self.net = net
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
        self.resultEdit.append('Cyphertext: {0}'.format(txt))
        if method == "Caesar":
            key = int(key)
            result = caesar.caesar(txt, 26-key)
        if method == "Vigenere":
            result = vigenere.vigenere(txt, key, True)
        if method == 'Scytale':
            result = scytale.cipher(txt,math.ceil(len(txt)/int(key)),self.resultEdit) 
        if method == "GAN":
            result = self.net(torch.cat((txt, key), 1).float())
        if method == "AES":
            txt = txt.encode('utf8')
            txt = base64.b64decode(txt)
            key = key.encode('utf8')
            result = decrypt(txt, key).decode('utf8')

        self.resultEdit.append('Result: {0}'.format(result))
        self.resultEdit.append(' ')
    
class Listener(QWidget):

    def __init__(self, net, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self.setWindowTitle('Cracker')
        self.resize(600, 300)
        self.net = net
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)
        layout.addWidget(self.resultEdit)
    
    def crack(self, txt, method):
        self.resultEdit.append('start crack ...')
        self.resultEdit.append('Method: '+method)
        self.resultEdit.append('Cyphertext: {0}'.format(txt))
        self.resultEdit.append(' ')
        if method == "Caesar":
            key, result = caesar.crack(txt, self.resultEdit)
            if result == None:
                result = "Failed"
            self.resultEdit.append('Try key: '+key)
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
        if method == "GAN":
            result = self.net(txt)
            if result != None:
                self.resultEdit.append('Get result: {0}'.format(result))
                self.resultEdit.append(' ')
        

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    alice, bob, eve = validate.model_load_checkpoint()

    app = QApplication(sys.argv)

    w2 = Decoder(bob)
    w2.show()

    w3 = Listener(eve)
    w3.show()

    w = Encoder(w2, w3,alice)
    w.show()

    sys.exit(app.exec_())