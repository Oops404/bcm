# -*- coding: utf-8 -*-
# author:　cheneyjin@outlook.com
# update 20210422

import _thread
import json
import logging
import os
import re
import sys
import uuid
from subprocess import Popen, PIPE

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QApplication
import cgitb

style_global = """
        *{
            font-family: "Microsoft YaHei";
        }
    """
cgitb.enable(format='text')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='log.md')

logger = logging.getLogger(__name__)

path_app = os.path.dirname(os.path.abspath(__file__))


def validate(file_name_str):
    r_str = r"[\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(r_str, "_", file_name_str)
    return new_title


class Target(object):

    def __init__(self, name, video_path, audio_path, root) -> None:
        super().__init__()
        self.name = name
        self.video_path = video_path
        self.audio_path = audio_path
        self.root = root

    def __str__(self) -> str:
        return "name:{}, video_path:{}, audio_path:{}, root:{}" \
            .format(self.name, self.video_path, self.audio_path, self.root)


class UiMainWindow(object):

    def __init__(self) -> None:
        super().__init__()
        self.task_id = None
        self.task_list = None
        self.directory = None
        self.target_video_name = "video.m4s"
        self.target_audio_name = "audio.m4s"
        self.target_file_info = "entry.json"

        self.run_path = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
        self.merging = False
        self.searching = False
        self.font = QtGui.QFont()
        self.font.setFamily("Microsoft YaHei Light")
        self.font.setPointSize(10)
        self.translate = QtCore.QCoreApplication.translate

        self.path_output = "{}/{}".format(path_app, self.translate("output", "输出目录"))
        if not os.path.exists(self.path_output):
            os.mkdir(self.path_output)

    def retranslate_ui(self, main_window):
        main_window.setWindowTitle(self.translate("bili cache merging tool", "B站缓存合并工具-翻滚吧年糕君 ID:1489684"))
        main_window.setFixedSize(main_window.width(), main_window.height())
        main_window.setWindowIcon(QIcon('local/favicon.ico'))
        self.text_view.setText(self.translate("copy cache folder from your phone local storage path :\n"
                                              "'/Android/data/tv.danmaku.bili/download' into your pc. \n"
                                              "note: do not change anything in cache folder",
                                              "从手机存储路径：'/Android/data/tv.danmaku.bili/download'"
                                              "拷贝缓存'完整文件夹'到电脑中，放于任意目录。"))
        self.text_view.append("\r")
        self.text_view.append(self.translate("if application gets some exception, "
                                             "please email me at 'cheneyjin@outlook.com' "
                                             "and attach the file named 'log.md'"
                                             "that in application folder.",
                                             "如果运行异常，请邮件至'cheneyjin@outlook.com'， "
                                             "邮件中请上传程序目录下的log.md文件， 内容能图文并茂就更好了~"))
        self.path_select_btn.setText(self.translate("select cache path", "选择路径"))

        self.start_btn.setText(self.translate("start merge", "开始"))

    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def setup_ui(self, main_window):
        main_window.setObjectName("mainWindow")
        main_window.resize(600, 320)
        main_window.setStyleSheet(style_global)

        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")

        self.vertical_LayoutWidget = QtWidgets.QWidget(self.central_widget)
        self.vertical_LayoutWidget.setGeometry(QtCore.QRect(0, 0, 600, 309))
        self.vertical_LayoutWidget.setObjectName("verticalLayoutWidget")
        self.vertical_LayoutWidget.setContentsMargins(1, 1, 1, 1)
        self.vertical_layout = QtWidgets.QVBoxLayout(self.vertical_LayoutWidget)
        self.vertical_layout.setObjectName("verticalLayout")

        self.path_select_btn = QtWidgets.QPushButton(self.vertical_LayoutWidget)
        self.path_select_btn.setObjectName("path_select_btn")
        self.path_select_btn.setFont(self.font)

        self.vertical_layout.addWidget(self.path_select_btn)
        self.text_view = QtWidgets.QTextEdit(self.vertical_LayoutWidget)
        self.text_view.setObjectName("text_view")
        self.text_view.setFont(self.font)

        self.vertical_layout.addWidget(self.text_view)
        self.start_btn = QtWidgets.QPushButton(self.vertical_LayoutWidget)
        self.start_btn.setObjectName("start_btn")
        self.start_btn.setContentsMargins(0, 10, 0, 10)
        self.start_btn.setFont(self.font)

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
        if self.searching:
            self.text_view.append(self.translate("searching cache task is not over, do not click again",
                                                 "检测缓存数量任务还没结束，别点啦！"))
            return
        if not self.merging:
            self.text_view.setText(self.translate("start merging,please wait a minute",
                                                  "开始合并，请等待..."))
            self.merging = True
        else:
            self.text_view.append(self.translate("program is working,do not click again",
                                                 "正在工作，不要重复点击"))
            return

        _thread.start_new_thread(self.task, ("Thread-1", 2,))

    def task(self, arg1, arg2):
        try:
            self.task_id = uuid.uuid1()
            logger.info("\nTASK START {}".format(self.task_id))
            if self.task_list is None or len(self.task_list) < 1:
                self.text_view.append(self.translate("no cache file searched", "别点啦，没检测到文件"))
                return
            for index, f in enumerate(self.task_list):
                cmd = "{}/local/ffmpeg.exe -y -i \"{}\" -i \"{}\" -c:v copy -c:a aac -strict " \
                      "experimental \"{}/{}.mp4\"" \
                    .format(self.run_path, f.video_path, f.audio_path, f.root, f.name)
                logger.info(cmd)
                with Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as p:
                    p.communicate()
                    self.text_view.append("内容:{}，{}\n进度：{}%"
                                          .format(f.name,
                                                  "已合并",
                                                  str(round(((index + 1) / len(self.task_list)) * 100, 2))))
                    self.text_view.moveCursor(QTextCursor.End)
            if os.path.exists(self.path_output):
                self.text_view.append(self.translate("finished. check the output path in app dir.",
                                                     "运行结束，查看应用路径下的输入文件夹吧。"))
            else:
                self.text_view.append(self.translate("output path was not exist, please check result in cache path.",
                                                     "输出文件夹不存在，请在缓存目录下查找合并结果，"
                                                     "或者使用Everything工具搜索缓存路径下MP4后缀的文件。"))
        except Exception as e:
            logger.error(e)
        finally:
            self.merging = False
            logger.info("TASK FINISHED {}".format(self.task_id))

    def select_path(self):
        self.task_list = list()
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(None, self.translate("select cache path", "选取文件夹"),
                                                                    "D:/")
        self.text_view.setText("{}: {}".format(self.translate("path", "路径"), self.directory))
        path_str = str(self.directory)
        if "" == path_str:
            self.text_view.append(self.translate("no path selected", "没选择任何路径。"))
        else:
            self.searching = True
            try:
                self.search_path(path_str)
                self.text_view.append("{}: {}{}".format(self.translate("find", "识别到"),
                                                        len(self.task_list),
                                                        self.translate("cache can merged", "个可合并视频。")))
            finally:
                self.searching = False

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
        name = None
        try:
            with open(file_info_path, "r", encoding="utf-8") as f:
                file_info = json.load(f)
                if "ep" in file_info.keys():
                    name = "({}){}".format(file_info["ep"]["index"], file_info["ep"]["index_title"])
                else:
                    name = file_info["page_data"]["download_subtitle"]
        except Exception as e:
            logger.error(e)
        video_path = "{}/{}".format(parent_path, self.target_video_name)
        audio_path = "{}/{}".format(parent_path, self.target_audio_name)
        video_exist = os.path.exists(video_path)
        audio_exist = os.path.exists(audio_path)
        if video_exist is False or audio_exist is False:
            logger.error("FILE PATH {}:{}".format(video_exist, video_path))
            logger.error("FILE PATH {}:{}".format(audio_exist, audio_path))
            self.text_view.append("{}{}".format(self.translate("missing file detected in cache path: ",
                                                               "检测到缓存存在缺失,路径："), parent_path))
            return
        if os.path.exists(self.path_output):
            parent_path = self.path_output
        t = Target(validate(name) if name is not None else "临时名称{}".format(uuid.uuid1()),
                   video_path, audio_path, parent_path)
        self.task_list.append(t)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
