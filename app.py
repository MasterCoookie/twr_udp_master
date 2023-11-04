import sys
import time

from queuer import Queuer
from udp_socket import UDPSocket
from random_startegy import RandomStrategy

from multiprocessing import Queue, Process, Event

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QListWidget
from PyQt6.QtCore import QThread, QObject, QSize, pyqtSignal as Signal, pyqtSlot as Slot

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

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.setWindowTitle("JK - Queuer")

        self.setGeometry(100, 100, 300, 100)
        
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.list_widget = QListWidget(self)
        self.list_widget.addItem("Device")
        layout.addWidget(self.list_widget, 0, 0, 3, 1)

        add_device_button = QPushButton("Add device", self)
        add_device_button.clicked.connect(self.add_device)

        remove_device_button = QPushButton("Remove device", self)
        remove_device_button.clicked.connect(self.remove_device)

        clear_devices_button = QPushButton("Clear devices", self)
        clear_devices_button.clicked.connect(self.clear_devices)

        start_button = QPushButton("Start", self)
        #TODO - connect

        layout.addWidget(add_device_button, 0, 1)
        layout.addWidget(remove_device_button, 1, 1)
        layout.addWidget(clear_devices_button, 2, 1)
        layout.addWidget(start_button, 3, 0, 3, 1)

    def add_device(self):
        self.list_widget.addItem("Device")

    def remove_device(self):
        self.list_widget.takeItem(self.list_widget.currentRow())

    def clear_devices(self):
        self.list_widget.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
