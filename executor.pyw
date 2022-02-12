# -*- coding: UTF-8-*-
# author:　cheneyjin@outlook.com
# update 20220212
import traceback
import _thread
import json
import logging
import os
import re
import sys
import uuid
import time
from subprocess import Popen, PIPE

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QApplication
import cgitb
from cm import UiMainWindow

# import qdarkstyle

cgitb.enable(format='text')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='log.md'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        ui = UiMainWindow(logger)
        ui.setup_ui(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(traceback.format_exc())
