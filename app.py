import sys
import time
import logging

from queuer import Queuer
from udp_socket import UDPSocket
from random_startegy import RandomStrategy
from closest_strategy import ClosestStrategy

from multiprocessing import Queue, Process, Event

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QListWidget, QDialog, QLineEdit, QInputDialog, QDialogButtonBox, QFormLayout, QLabel, QStyle, QPlainTextEdit, QFileDialog, QCheckBox
from PyQt6.QtCore import QThread, QObject, QSize, pyqtSignal as Signal, pyqtSlot as Slot, Qt, QSettings

ended = Event()
ended.clear()

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super(QPlainTextEditLogger, self).__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
    
    def write(self, m):
        pass


class Worker(QObject):
    def __init__(self, tags_dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags_dict = tags_dict


    msg_q = Queue()
    result_q = Queue()
    decoded_q = Queue()

    finished = Signal()
    result = Signal(str)

    success_signal = Signal()
    timeout_signal = Signal()
    error_signal = Signal()
    total_signal = Signal()

    def do_work(self):
        # tags_list = {'AA': ('127.0.0.1', 5001, ['BB'])}
        settings = QSettings("JK", "Queuer")
        # self.queuer = Queuer(self.tags_dict, RandomStrategy())
        self.queuer = Queuer(self.tags_dict, ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)
        self.udp_socket = UDPSocket(int(settings.value("out_port", "5000")), len(self.tags_dict), post_send_delay=int(settings.value("delay", "100"))/1000)

        self.queuer.tags_dict = self.queuer.generate_dict(self.tags_dict)

        file_handler = logging.FileHandler(f'{settings.value("log_dir", "./")}/results.log')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)


        p1 = Process(target=self.queuer.queing_process, args=(ended, self.msg_q))
        p2 = Process(target=self.udp_socket.sending_process, args=(ended, self.msg_q, self.result_q))

        p1.start()
        # time to prepare first queue
        time.sleep(.1)
        p2.start()

        while not ended.is_set():
            # logging.warning('DUPA')
            time.sleep(.01)
            self.queuer.results_decode(self.result_q, self.decoded_q)
            while not self.decoded_q.empty():
                result = self.decoded_q.get()
                self.total_signal.emit()
                if result[1] is None:
                    self.result.emit(f"Timeout: {result[0]}")
                    self.timeout_signal.emit()
                elif result[1].startswith("ERR"):
                    self.result.emit(f"Error - {result[0]}: {result[1].strip()}")
                    self.error_signal.emit()
                else:
                    self.result.emit(f"Success - {result[0]}: {result[1].strip()}")
                    self.success_signal.emit()

        p1.join()
        p2.join()

        self.udp_socket.bound_socket.close()
        self.finished.emit()

class SettingsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Settings")

        layout = QFormLayout(self)

        self.settings = QSettings("JK", "Queuer")

        self.out_port_input = QLineEdit(self)
        self.out_port_input.setText(self.settings.value("out_port", "5000"))

        self.delay_input = QLineEdit(self)
        self.delay_input.setText(self.settings.value("delay", "100"))

        self.enable_log_save_label = QLabel("Log directory", self)

        self.log_save_dir_input = QLineEdit(self)
        self.log_save_dir_input.setText(self.settings.value("log_dir", "./"))

        self.log_dir_button = QPushButton("Choose directory", self)
        self.log_dir_button.clicked.connect(self.choose_log_dir)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)

        layout.addRow("Out Port:", self.out_port_input)
        layout.addRow("Delay (ms):", self.delay_input)
        layout.addRow(self.enable_log_save_label)
        layout.addRow(self.log_save_dir_input, self.log_dir_button)
        layout.addWidget(button_box)


        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def accept(self):
        self.settings.setValue("out_port", self.out_port_input.text())
        self.settings.setValue("delay", self.delay_input.text())
        self.settings.setValue("log_dir", self.log_save_dir_input.text())
        super().accept()

    def choose_log_dir(self):
        self.log_dir_input = QFileDialog.getExistingDirectory(self, "Choose directory", self.settings.value("log_dir", ""))
        self.settings.setValue("log_dir", self.log_dir_input)
        self.log_save_dir_input.setText(self.log_dir_input)

    def reject(self):
        super().reject()




class SetupWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tags_dict = {}
        
        self.anchors_list = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.list_widget = QListWidget(self)

        add_tag_button = QPushButton("Add Tag", self)
        add_tag_button.clicked.connect(self.add_tag)

        add_anchor_button = QPushButton("Add Anchor", self)
        add_anchor_button.clicked.connect(self.add_anchor)

        remove_device_button = QPushButton("Remove device", self)
        remove_device_button.clicked.connect(self.remove_device)

        clear_devices_button = QPushButton("Clear devices", self)
        clear_devices_button.clicked.connect(self.clear_devices)

        settings_button = QPushButton("Settings", self)
        settings_button.clicked.connect(self.settings)

        start_button = QPushButton("Start", self)
        start_button.clicked.connect(self.parent().start)

        self.test_button = QPushButton("Test Tag", self)
        self.test_button.clicked.connect(self.test_tag)

        width = 4
        layout.addWidget(self.list_widget, 0, 0, 4, width)
        layout.addWidget(add_tag_button, 0, width)
        layout.addWidget(add_anchor_button, 1, width)
        layout.addWidget(remove_device_button, 2, width)
        layout.addWidget(clear_devices_button, 3, width)
        layout.addWidget(settings_button, 4, 0, 1, 2)
        layout.addWidget(start_button, 4, 2, 1, 2)
        layout.addWidget(self.test_button, 4, width)

    def settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec():
            pass

    def add_tag(self):
        tag_input_dialog = TagInputDialog([anchor[0] for anchor in self.anchors_list], self)
        if tag_input_dialog.exec():
            uwb_address, ip, port, anchors = tag_input_dialog.get_inputs()
            self.list_widget.addItem(uwb_address)
            anchors = [anchor for anchor in self.anchors_list if anchor[0] in anchors]
            print(anchors)
            self.tags_dict[uwb_address] = (ip, port, anchors)

    def add_anchor(self):
        anchor_input_dialog = AnchorInputDialog(self)
        if anchor_input_dialog.exec():
            result= anchor_input_dialog.get_inputs()
            self.list_widget.addItem(result[0])
            self.anchors_list.append(result)

    def remove_device(self):
        if(self.list_widget.currentItem()):
            self.anchors_list.remove(self.list_widget.currentItem().text())
            self.list_widget.takeItem(self.list_widget.currentRow())

    def clear_devices(self):
        self.list_widget.clear()
        self.anchors_list.clear()

    def test_tag(self):
        test_socket = UDPSocket(5000, 1)
        tag_uwb_address = self.list_widget.currentItem().text()
        tag = self.tags_dict[tag_uwb_address]
        test_socket.send(b"TEST", tag[0], int(tag[1]))
        result = test_socket.receive(verbose=True)
        if result[0] is None:
            pixmapi = getattr(QStyle.StandardPixmap, "SP_DialogCancelButton")
            icon = self.style().standardIcon(pixmapi)
            self.test_button.setIcon(icon)
        else:
            pixmapi = getattr(QStyle.StandardPixmap, "SP_DialogApplyButton")
            icon = self.style().standardIcon(pixmapi)
            self.test_button.setIcon(icon)
        test_socket.bound_socket.close()


class CounterLabel(QLabel):
    def __init__(self, label_text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.counter = 0
        self.label_text = label_text
        self.setText(f"{self.label_text} {self.counter}")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def increment(self):
        self.counter += 1
        self.setText(f"{self.label_text} {self.counter}")

class EndWidget(QWidget):
    def __init__(self, success_counter, timeout_counter, error_counter, total_counter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent().setFixedSize(290, 350)
        self.parent().setWindowTitle("JK Queuer - Summary")

        self.success_counter = success_counter
        self.timeout_counter = timeout_counter
        self.error_counter = error_counter
        self.total_counter = total_counter

        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        self.setLayout(layout)

        self.label = QLabel("Monitoring Finished", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.success_counter_label = QLabel(f"Successes: {self.success_counter}", self)
        self.success_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timeout_counter_label = QLabel(f"Timeouts: {self.timeout_counter}", self)
        self.timeout_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_counter_label = QLabel(f"Errors: {self.error_counter}", self)
        self.error_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.total_counter_label = QLabel(f"Total: {self.total_counter}", self)
        self.total_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        layout.addWidget(self.success_counter_label)
        layout.addWidget(self.timeout_counter_label)
        layout.addWidget(self.error_counter_label)
        layout.addWidget(self.total_counter_label)

class WorkingWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.label = QLabel("Working", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logger = QPlainTextEditLogger(self)
        self.logger.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(self.logger)
        logging.getLogger().setLevel(logging.DEBUG)

        

        self.total_counter = CounterLabel("Total", self)
        self.success_counter = CounterLabel("Successes:", self)
        self.timeout_counter = CounterLabel("Timeouts:", self)
        self.error_counter = CounterLabel("Errors:", self)
    
        end_button = QPushButton("End", self)
        end_button.clicked.connect(self.end)


        layout.addWidget(self.label, 0, 3)
        layout.addWidget(self.total_counter, 1, 0)
        layout.addWidget(self.success_counter, 1, 2)
        layout.addWidget(self.timeout_counter, 1, 4)
        layout.addWidget(self.error_counter, 1, 6)
        layout.addWidget(self.logger.widget, 2, 0, 1, 7)
        layout.addWidget(end_button, 3, 2, 1, 3)
    
    def end(self):
        ended.set()

    # To remember the lvls
    # def test(self):
    #     logging.debug('damn, a bug')
    #     logging.info('something to remember')
    #     logging.warning('that\'s not right')
    #     logging.error('foobar')


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())
        
        self.setWindowIcon(QtGui.QIcon('logo.png'))


        self.setup_ui()
        
        self.show()
        

    def setup_ui(self):
        self.setWindowTitle("JK Queuer - Setup")
        self.setFixedSize(500, 175)
        self.setup_widget = SetupWidget(self)
        
        self.setCentralWidget(self.setup_widget)
        
    
    def start(self):
        self.working_widget = WorkingWidget(self)
        self.setCentralWidget(self.working_widget)
        self.setWindowTitle("JK Queuer - Working")
        self.setFixedSize(16777215,16777215)
        self.setBaseSize(500, 300)


        print(self.setup_widget.tags_dict)

        self.worker = Worker(self.setup_widget.tags_dict)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.do_work)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker.result.connect(self.update_result)

        self.worker.success_signal.connect(self.working_widget.success_counter.increment)
        self.worker.timeout_signal.connect(self.working_widget.timeout_counter.increment)
        self.worker.error_signal.connect(self.working_widget.error_counter.increment)
        self.worker.total_signal.connect(self.working_widget.total_counter.increment)

        self.worker.finished.connect(self.switch_to_end)

        self.worker_thread.start()


    def update_result(self, result):
        logging.warning(result)

    def switch_to_end(self):
        self.end_widget = EndWidget(self.working_widget.success_counter.counter,
                                    self.working_widget.timeout_counter.counter,
                                    self.working_widget.error_counter.counter,
                                    self.working_widget.total_counter.counter,
                                    self
                                )
        self.setCentralWidget(self.end_widget)

class TagInputDialog(QDialog):
    def __init__(self, anchors_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Input Tag")

        self.uwb_address_input = QLineEdit(self)
        self.ip_input = QLineEdit(self)
        self.port_input = QLineEdit(self)

        #set default value for inputs
        self.uwb_address_input.setText("AA")
        self.ip_input.setText("127.0.0.1")
        self.port_input.setText("5001")

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
        return (self.uwb_address_input.text(), self.ip_input.text(), int(self.port_input.text()), [item.text() for item in self.list_widget.selectedItems()])

class AnchorInputDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Input Anchor")

        self.uwb_address_input = QLineEdit(self)
        self.x_input = QLineEdit(self)
        self.y_input = QLineEdit(self)
        self.z_input = QLineEdit(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("UWB Address:", self.uwb_address_input)
        layout.addRow("X:", self.x_input)
        layout.addRow("Y:", self.y_input)
        layout.addRow("Z:", self.z_input)

        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()

    def get_inputs(self):
        return (self.uwb_address_input.text(),
                float(self.x_input.text() if self.x_input.text() != '' else 0),
                float(self.y_input.text() if self.y_input.text() != '' else 0),
                float(self.z_input.text() if self.z_input.text() != '' else 0)
        )


if __name__ == "__main__":
    sys.argv += ['-platform', 'windows:darkmode=2']
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    sys.exit(app.exec())
