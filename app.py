import sys
import time

from queuer import Queuer
from udp_socket import UDPSocket
from random_startegy import RandomStrategy

from multiprocessing import Queue, Process, Event

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QListWidget
from PyQt5.QtCore import QThread, QObject, QSize, pyqtSignal as Signal, pyqtSlot as Slot

ended = Event()
ended.clear()

class Worker(QObject):
    msg_q = Queue()
    result_q = Queue()

    def do_work(self, tags_list):
        self.queuer = Queuer(tags_list, RandomStrategy())
        self.udp_socket = UDPSocket(5000, 2)

        p1 = Process(target=self.queuer.queing_process, args=(ended, self.msg_q))
        p2 = Process(target=self.udp_socket.sending_process, args=(ended, self.msg_q, self.result_q))

        p1.start()
        # time to prepare first queue
        time.sleep(.1)
        p2.start()

        p1.join()
        p2.join()

        self.udp_socket.bound_socket.close()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("JK - Queuer")

        self.setMinimumSize(QSize(480, 240))
        
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget, 0, 0, 3, 2)

        self.add_device_button = QPushButton("Add device", self)
        self.add_device_button.clicked.connect(self.add_device)

        self.remove_device_button = QPushButton("Remove device", self)
        self.remove_device_button.clicked.connect(self.remove_device)

        self.clear_devices_button = QPushButton("Clear devices", self)
        self.clear_devices_button.clicked.connect(self.clear_devices)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
