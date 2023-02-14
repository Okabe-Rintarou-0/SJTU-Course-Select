import sys
import time
from threading import Thread
from typing import Optional, List

import pysjtu
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from pysjtu.exceptions import LoginException, FullCapacityException
from pysjtu.models import SelectionSector, SelectionClass

from ui import LoginDialog, CourseSelectionWindow


class App:
    def __init__(self):
        self.daemon_map: dict = dict()
        self.app = QtWidgets.QApplication(sys.argv)
        self.cli: Optional[pysjtu.Client] = None
        self.selection_window: Optional[CourseSelectionWindow] = None
        self.sector: Optional[SelectionSector] = None
        self.selected_courses: List[SelectionClass] = []
        self.keyword: str = ""

    @staticmethod
    def quit():
        sys.exit(0)

    def handle_login(self):
        login_dialog = LoginDialog()
        while True:
            if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
                username, password = login_dialog.get_username_password()
                print('用户名:', username)
                print('密码:', password)
                try:
                    self.cli = pysjtu.create_client(username=username, password=password)
                    print('登录成功！')
                    return
                except LoginException:
                    print('用户名或密码错误！')
                except Exception as e:
                    print(e)
            else:
                print('登录已取消！')
                self.quit()

    def fetch_sectors(self):
        sectors = [sector.name for sector in self.cli.course_selection_sectors]
        self.selection_window.add_sectors(sectors)
        self.sector = self.cli.course_selection_sectors[0]

    @staticmethod
    def meet_keyword(klass: SelectionClass, keyword: str) -> bool:
        return keyword in klass.name or keyword in klass.class_name

    def fetch_search_results(self):
        if len(self.keyword) == 0:
            results = self.sector.classes
        else:
            results = list(filter(lambda klass: self.meet_keyword(klass, self.keyword), self.sector.classes))
        self.selection_window.set_search_results(results)

    def change_sector(self, sector: str):
        self.sector = next(filter(lambda s: s.name == sector, self.cli.course_selection_sectors))
        print(self.sector)
        self.clear_selection()
        self.fetch_search_results()

    def search(self, keyword: str):
        print(keyword)
        self.keyword = keyword
        self.fetch_search_results()

    class SelectDaemon(QThread):
        signal = pyqtSignal(SelectionClass)

        def __init__(self, course: SelectionClass):
            self.course = course
            super().__init__()

        def run(self) -> None:
            while not self.course.is_registered():
                time.sleep(5)
                try:
                    print(f"Trying to register {self.course.name}...")
                    self.course.register()  # or klass.drop()
                    print("Succeed, quit")
                    break
                except FullCapacityException:
                    print("Failed, retry.")
                    pass  # retry
                except Exception as e:
                    raise e  # or handle other exceptions
            print(f"{self.course.name} 的抢课守护线程退出")
            self.signal.emit(self.course)

    def on_select_course(self, course: SelectionClass):
        daemon = App.SelectDaemon(course)
        daemon.signal.connect(self.selection_window.finish_select)
        self.daemon_map[course.name] = daemon
        daemon.start()

    def clear_selection(self):
        self.selection_window.clear_selection()
        for course in self.daemon_map:
            self.daemon_map[course].quit()

    def on_remove_course(self, course: SelectionClass):
        self.daemon_map[course.name].quit()

    def handle_selection(self):
        self.selection_window = CourseSelectionWindow()
        self.selection_window.add_sector_selection_handler(self.change_sector)
        self.selection_window.add_search_handler(self.search)
        self.selection_window.set_on_select_course_handler(self.on_select_course)
        self.selection_window.set_on_remove_course_handler(self.on_remove_course)
        self.fetch_sectors()
        self.selection_window.show()

    def run(self):
        # self.handle_login()
        self.cli = pysjtu.create_client(username="923048992", password="Linzh8912.")
        self.handle_selection()
        sys.exit(self.app.exec_())
