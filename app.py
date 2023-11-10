import sys
import time

from queuer import Queuer
from udp_socket import UDPSocket
from random_startegy import RandomStrategy

from multiprocessing import Queue, Process, Event

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QListWidget, QDialog, QLineEdit, QInputDialog, QDialogButtonBox, QFormLayout
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

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.anchors_list = []

        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.setWindowTitle("JK - Queuer")

        self.setGeometry(100, 100, 500, 100)

        self.main_container = QWidget(self)
        
        layout = QGridLayout(self.main_container)
        self.main_container.setLayout(layout)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget, 0, 0, 4, 1)

        add_tag_button = QPushButton("Add Tag", self)
        add_tag_button.clicked.connect(self.add_tag)

        add_anchor_button = QPushButton("Add Anchor", self)
        add_anchor_button.clicked.connect(self.add_anchor)

        remove_device_button = QPushButton("Remove device", self)
        remove_device_button.clicked.connect(self.remove_device)

        clear_devices_button = QPushButton("Clear devices", self)
        clear_devices_button.clicked.connect(self.clear_devices)

        start_button = QPushButton("Start", self)
        #TODO - connect

        layout.addWidget(add_tag_button, 0, 1)
        layout.addWidget(add_anchor_button, 1, 1)
        layout.addWidget(remove_device_button, 2, 1)
        layout.addWidget(clear_devices_button, 3, 1)
        layout.addWidget(start_button, 4, 0, 4, 1)

        self.setCentralWidget(self.main_container)

    def add_tag(self):
        tag_input_dialog = TagInputDialog(self.anchors_list, self)
        if tag_input_dialog.exec():
            uwb_address, ip, port, anchors = tag_input_dialog.get_inputs()
            print(anchors)
            self.list_widget.addItem(uwb_address)
            #TODO - add to list

    def add_anchor(self):
        uwb_address, ok = QInputDialog.getText(self, "Add new UWB Anchor", "UWB Address:")
        if ok:
            self.list_widget.addItem(uwb_address)
            self.anchors_list.append(uwb_address)

    def remove_device(self):
        if(self.list_widget.currentItem()):
            self.anchors_list.remove(self.list_widget.currentItem().text())
            self.list_widget.takeItem(self.list_widget.currentRow())

    def clear_devices(self):
        self.list_widget.clear()
        self.anchors_list.clear()

class TagInputDialog(QDialog):
    def __init__(self, anchors_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Input Tag")

        self.uwb_address_input = QLineEdit(self)
        self.ip_input = QLineEdit(self)
        self.port_input = QLineEdit(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)

        self.list_widget = QListWidget(self)
        self.list_widget.addItems(anchors_list)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        layout = QFormLayout(self)
        layout.addRow("UWB Address:", self.uwb_address_input)
        layout.addRow("IP:", self.ip_input)
        layout.addRow("Port:", self.port_input)
        layout.addRow("Anchors:", self.list_widget)

        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()

    def get_inputs(self):
        return (self.uwb_address_input.text(), self.ip_input.text(), self.port_input.text(), [item.text() for item in self.list_widget.selectedItems()])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
