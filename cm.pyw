# -*- coding: utf-8 -*-
# author:　cheneyjin@outlook.com

import _thread
import json
import logging
import os
import re
import sys
import uuid
from subprocess import Popen, PIPE

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='log.md')
logger = logging.getLogger(__name__)


def validate(file_name_str):
    r_str = r"[\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(r_str, "_", file_name_str)
    return new_title


class Target(object):

    def __init__(self, name, path, root) -> None:
        super().__init__()
        self.name = name
        self.path = path
        self.root = root

    def __str__(self) -> str:
        return "name:{}, path:{}, root:{}".format(self.name, self.path, self.root)


class UiMainWindow(object):

    def __init__(self) -> None:
        super().__init__()
        self.task_id = None
        self.directory = None
        self.target_video_name = "video.m4s"
        self.target_audio_name = "audio.m4s"
        self.target_file_info = "entry.json"

        self.task_list = None
        self.run_path = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
        self.merging = False
        # print(self.run_path)
        self.style = """
                *{
                    font-family: "Microsoft YaHei";
                }
            """

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("bili cache merging tool", "B站缓存合并工具-翻滚吧年糕君"))
        main_window.setFixedSize(main_window.width(), main_window.height())
        main_window.setWindowIcon(QIcon('local/favicon.ico'))
        self.text_view.setText(_translate("copy cache folder from your phone local storage path :\n"
                                          "'/Android/data/tv.danmaku.bili/download' into your pc. \n"
                                          "note: do not change anything in cache folder",
                                          "从手机存储路径：'/Android/data/tv.danmaku.bili/download'\n"
                                          "拷贝缓存<完整文件夹>到电脑中，放于任意目录。"))
        self.text_view.append("\r\n")
        self.text_view.append(_translate("if application gets some exception, "
                                         "please email me at 'cheneyjin@outlook.com' and attach the file named 'log.md'"
                                         "that in application folder."
                                         "email content has picture and text that will be better."
                                         , "如果运行异常，请邮件至'cheneyjin@outlook.com'，"
                                           "邮件中请上传程序目录下的'log.md'文件，"
                                           "内容能图文并茂就更好了~"))
        self.path_select_btn.setText(_translate("select cache path", "选择路径"))
        self.start_btn.setText(_translate("start merge", "开始"))

    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def setup_ui(self, main_window):
        main_window.setObjectName("mainWindow")
        main_window.resize(471, 203)
        main_window.setStyleSheet(self.style)

        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")

        self.vertical_LayoutWidget = QtWidgets.QWidget(self.central_widget)
        self.vertical_LayoutWidget.setGeometry(QtCore.QRect(0, 0, 471, 191))
        self.vertical_LayoutWidget.setObjectName("verticalLayoutWidget")
        self.vertical_LayoutWidget.setContentsMargins(1, 1, 1, 1)
        self.vertical_layout = QtWidgets.QVBoxLayout(self.vertical_LayoutWidget)
        self.vertical_layout.setObjectName("verticalLayout")
        self.path_select_btn = QtWidgets.QPushButton(self.vertical_LayoutWidget)
        self.path_select_btn.setObjectName("path_select_btn")
        self.vertical_layout.addWidget(self.path_select_btn)
        self.text_view = QtWidgets.QTextEdit(self.vertical_LayoutWidget)
        self.text_view.setObjectName("text_view")

        self.vertical_layout.addWidget(self.text_view)
        self.start_btn = QtWidgets.QPushButton(self.vertical_LayoutWidget)
        self.start_btn.setObjectName("start_btn")
        self.start_btn.setContentsMargins(0, 10, 0, 10)
        self.vertical_layout.addWidget(self.start_btn)
        main_window.setCentralWidget(self.central_widget)
        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName("status_bar")
        main_window.setStatusBar(self.status_bar)

        self.path_select_btn.clicked.connect(self.select_path)
        self.start_btn.clicked.connect(self.start_merge)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def start_merge(self):
        if not self.merging:
            self.text_view.setText("开始合并，请等待...")
            self.merging = True
        else:
            self.text_view.append("正在工作，不要重复点击")
            return

        _thread.start_new_thread(self.task, ("Thread-1", 2,))

    def task(self, arg1, arg2):
        try:
            self.task_id = uuid.uuid1()
            logger.info("\nTASK START {}".format(self.task_id))
            for index, f in enumerate(self.task_list):
                cmd = "{}/local/ffmpeg.exe -y -i \"{}/video.m4s\" -i \"{}/audio.m4s\" -c:v copy -c:a aac -strict " \
                      "experimental \"{}/{}.mp4\"".format(self.run_path, f.path, f.path, f.path, validate(f.name))
                logger.info(cmd)
                with Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as p:
                    p.communicate()
                    self.text_view.append("结果: {}, 内容:{}\n进度：{}%".format("已合并", f.name, str(
                        round(((index + 1) / len(self.task_list)) * 100, 2))))
            self.text_view.append("运行结束。 developed by: BILIBILI_ID:1489684 翻滚吧年糕君")
        except Exception as e:
            logger.error(e)
        finally:
            self.merging = False
            logger.info("TASK FINISHED {}".format(self.task_id))

    def select_path(self):
        self.task_list = list()
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "D:/")
        self.text_view.setText("路径: {}".format(self.directory))
        path_str = str(self.directory)
        if "" == path_str:
            self.text_view.append("没选择任何路径。")
        else:
            self.search_path(path_str)
            self.text_view.append("识别到: {}个可合并视频。".format(len(self.task_list)))
        # for f in self.task_list:
        #     print(f)

    def search_path(self, root_path):
        for l in os.listdir(root_path):
            path = os.path.join(root_path, l)
            if os.path.isdir(path):
                self.search_path(path)
            else:
                if path.__contains__(self.target_video_name):
                    self.load_file(path)

    def load_file(self, path):
        parent_path = os.path.abspath(os.path.join(path, ".."))
        file_info_path = "{}/../{}".format(parent_path, self.target_file_info)
        with open(file_info_path, "r", encoding="utf-8") as f:
            file_info = json.load(f)
            t = Target(file_info["page_data"]["download_subtitle"], parent_path, "{}/../".format(parent_path))
            self.task_list.append(t)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
