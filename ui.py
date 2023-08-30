from typing import List

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLabel, QComboBox, QLineEdit, QListWidget, QListWidgetItem
from pysjtu.models import SelectionClass


class CourseSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.on_select_course_handler = None
        self.on_remove_course_handler = None

        # 设置窗体标题和初始大小
        self.setWindowTitle('抢课助手')
        self.setFixedHeight(600)
        self.setFixedWidth(800)

        # 添加关键词搜索框
        keyword_label = QLabel('关键词：', self)
        keyword_label.setGeometry(50, 50, 60, 20)
        self.keyword_edit = QLineEdit(self)
        self.keyword_edit.setGeometry(110, 50, 200, 20)

        # 添加课程类型下拉框
        sector_label = QLabel('分区：', self)
        sector_label.setGeometry(400, 50, 80, 20)
        self.sector_combobox = QComboBox(self)
        self.sector_combobox.setGeometry(440, 50, 200, 20)

        # 添加课程搜索结果列表
        result_label = QLabel('搜索结果：', self)
        result_label.setGeometry(50, 100, 80, 20)
        self.result_list = QListWidget(self)
        self.result_list.setGeometry(50, 130, 350, 400)

        # 添加已选课程列表
        selected_label = QLabel('已选课程：', self)
        selected_label.setGeometry(450, 100, 80, 20)
        self.selected_list = QListWidget(self)
        self.selected_list.setGeometry(450, 130, 300, 400)

        # 添加选中框
        self.result_list.itemClicked.connect(self.on_result_item_clicked)
        self.result_list.setSelectionMode(QListWidget.MultiSelection)
        self.result_list.setSelectionBehavior(QListWidget.SelectRows)
        self.result_list.setAlternatingRowColors(True)
        # self.result_list.setStyleSheet("QListWidget::item:selected{background-color: rgb(200, 200, 200);}")

    def clear_selection(self):
        self.selected_list.clear()

    def finish_select(self, course: SelectionClass):
        for i in range(self.selected_list.count()):
            selected_item = self.selected_list.item(i)
            if selected_item.data(Qt.UserRole) == course:
                selected_item.setText(selected_item.text().replace("抢课中...", "已选上"))

    def set_on_select_course_handler(self, handler):
        self.on_select_course_handler = handler

    def set_on_remove_course_handler(self, handler):
        self.on_remove_course_handler = handler

    def add_sector_selection_handler(self, handler):
        self.sector_combobox.currentIndexChanged.connect(lambda: handler(self.sector_combobox.currentText()))

    def add_search_handler(self, handler):
        self.keyword_edit.returnPressed.connect(lambda: handler(self.keyword_edit.text()))

    def add_sectors(self, sectors: List[str]):
        self.sector_combobox.addItems(sectors)

    def set_search_results(self, results: List[SelectionClass]):
        print(results)
        self.result_list.clear()
        for result in results:
            self.add_search_result(result)

    def add_search_result(self, result: SelectionClass):
        text = f"{result.name} 已选人数：{result.students_registered} 学分：{result.credit} {result.class_name}"
        item = QListWidgetItem(text, self.result_list)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, result)

    def on_result_item_clicked(self, item):
        # 处理选中结果
        if item.checkState() == Qt.Checked:
            self.add_selected_item(item)
        else:
            self.remove_selected_item(item)

    def add_selected_item(self, item):
        # 添加选中的课程到已选列表中
        course: SelectionClass = item.data(Qt.UserRole)
        selected_text = f"{course.name} 状态：抢课中..."
        selected_item = QListWidgetItem(selected_text, self.selected_list)
        selected_item.setData(Qt.UserRole, item.data(Qt.UserRole))

        if self.on_select_course_handler is not None:
            self.on_select_course_handler(course)

    def remove_selected_item(self, item):
        # 从已选列表中移除选中的课程
        for i in range(self.selected_list.count()):
            selected_item = self.selected_list.item(i)
            if selected_item.data(Qt.UserRole) == item.data(Qt.UserRole):
                self.selected_list.takeItem(i)
                course: SelectionClass = item.data(Qt.UserRole)
                if self.on_remove_course_handler is not None:
                    self.on_remove_course_handler(course)
                break


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)

        self.setWindowTitle('使用 Jaccount 登录')
        self.setFixedWidth(300)

        # 创建用户名和密码输入框
        self.username_input = QtWidgets.QLineEdit(self)
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # 创建登录和取消按钮
        self.login_button = QtWidgets.QPushButton('登录', self)
        self.cancel_button = QtWidgets.QPushButton('取消', self)

        # 将用户名、密码输入框和按钮放入表单布局中
        form_layout = QtWidgets.QFormLayout(self)
        form_layout.addRow('用户名:', self.username_input)
        form_layout.addRow('密码:', self.password_input)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        form_layout.addRow(button_layout)

        # 为登录按钮和取消按钮连接相应的槽函数
        self.login_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_username_password(self):
        # 获取用户名和密码
        return self.username_input.text(), self.password_input.text()
