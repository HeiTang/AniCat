# -*- coding: utf-8 -*-

import sys
import os
import time
# import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QListView, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QStringListModel

from Anime1_UI import Ui_MainWindow
import Anime1_Download, Anime1_Search

class Mark(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(Mark, self).__init__(parent)   # 繼承Ui_MainWindow 也就是 mark_tool 內的 class
        self.setupUi(self)   # 建立ui介面
        
        # 這功能主要是點擊了這個按鈕要執行什麼？
        # self.Test_Button 這個 function 在 MarkQtUI.Ui_MainWindow內
        # 因為已經繼承了Ui_MainWindow，因此執行 self.Test_Button
        # 點擊了時候會套用下方的function test_button_clicked，會將值輸出
        # 如果沒有這行，點擊按鈕不會有任何的動作
        self.pushButton_Search.clicked.connect(self.Search_Button_Clicked)
        self.pushButton_Download.clicked.connect(self.Download_Button_Clicked)

    # ====================================================================================================
    
    def logv2(self, title, msg):
        """
        :param title: log 的 開頭
        :param msg: 你想顯示的訊息
        :return: [2020/02/28 14:35:29][test] Hi
        """
        timeStr = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        log_message = '[' + str(timeStr) + '][' + title + '] ' + str(msg)
        # print(log_message)  # 如果你把註解拿掉，你的終端機就會顯示 Log
        return log_message

    


    def Search_Button_Clicked(self):
        self.listWidget.clear()
        Keyword = self.lineEdit_Search.text()
        data = Anime1_Search.Search_Anime1_id(Keyword)
    
        for k , v in data. items ( ) :
            string = str(k) + "：" + str(v)
            self.listWidget.addItem(string)
            self.listWidget.scrollToBottom()
        
    # ====================================================================================================
    
    def Download_Button_Clicked(self):
        id = self.lineEdit_Download.text()
        Anime1_Download.main(id)

if __name__ == "__main__":
    app = QApplication(sys.argv)   # 第一行必備，系統呼叫
    window = Mark()                # 指定 Mark Class 會先執行__init__
    window.show()                  # 將GUI介面顯示出來
    sys.exit(app.exec_())          # 關閉系統