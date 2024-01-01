import sys
import os
import time
import logging

from queuer import Queuer
from udp_socket import UDPSocket
from random_startegy import RandomStrategy
from closest_strategy import ClosestStrategy
from complete_simultaneus_random_strategy import CompleteSimultaneusRandomStrategy

from multiprocessing import Queue, Process, Event, Manager

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QListWidget, QDialog, QLineEdit, QInputDialog, QDialogButtonBox, QFormLayout, QLabel, QStyle, QPlainTextEdit, QFileDialog, QCheckBox, QFrame, QRadioButton, QSpinBox
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot, Qt, QSettings

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
        settings = QSettings("JK", "Queuer")
        strategy_list = SettingsDialog.get_saved_strategy_list()
        print(strategy_list)
        if strategy_list[0]:
            self.queuer = Queuer(RandomStrategy(), queue_lower_limit=4, queue_upper_limit=4)
        elif strategy_list[1]:
            self.queuer = Queuer(CompleteSimultaneusRandomStrategy(), queue_lower_limit=6, queue_upper_limit=6)
        elif strategy_list[2]:
            self.queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)
        elif strategy_list[3]:
            self.queuer = Queuer(ClosestStrategy(regression_treshold=int(settings.value("regression_treshold", "3"))), queue_lower_limit=4, queue_upper_limit=4)
        # self.queuer = Queuer(RandomStrategy())
        # self.queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)
        # self.queuer = Queuer(CompleteSimultaneusRandomStrategy(), queue_lower_limit=6, queue_upper_limit=6)
        self.udp_socket = UDPSocket(int(settings.value("out_port", "5000")), len(self.tags_dict), post_send_delay=int(settings.value("delay", "100"))/1000)

        generated_dict = self.queuer.generate_dict(self.tags_dict)
        managed_dict = Manager().dict(generated_dict)

        file_handler = logging.FileHandler(f'{settings.value("log_dir", "./")}/results.log')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)


        p1 = Process(target=self.queuer.queing_process, args=(ended, self.msg_q, managed_dict))
        if strategy_list[1]:
            simultaneous_delay = int(settings.value("simultaneus_delay", "1000"))/1000000
            p2 = Process(target=self.udp_socket.sending_simultaneous_process, args=(ended, len(generated_dict), simultaneous_delay, self.msg_q, self.result_q, True))
        else:
            p2 = Process(target=self.udp_socket.sending_process, args=(ended, self.msg_q, self.result_q))

        p1.start()
        # time to prepare first queue
        time.sleep(.1)
        p2.start()

        while not ended.is_set():
            time.sleep(.01)
            self.queuer.results_decode(self.result_q, self.decoded_q, managed_dict)
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

        general_label = QLabel("General", self)
        general_label.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Weight.Bold))

        self.out_port_input = QLineEdit(self)
        self.out_port_input.setText(self.settings.value("out_port", "5000"))

        self.delay_input = QLineEdit(self)
        self.delay_input.setText(self.settings.value("delay", "100"))

        self.enable_log_save_label = QLabel("Log directory", self)

        self.log_save_dir_input = QLineEdit(self)
        self.log_save_dir_input.setText(self.settings.value("log_dir", "./"))

        self.log_dir_button = QPushButton("Choose directory", self)
        self.log_dir_button.clicked.connect(self.choose_log_dir)

        strategy_label = QLabel("Strategy", self)
        strategy_label.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Weight.Bold))

        strategy_list = self.get_saved_strategy_list()

        self.complete_random_radio = QRadioButton("Complete random", self)
        self.complete_random_radio.setChecked(strategy_list[0])
        if self.settings.value("strategy_picked", "0") == "0":
            self.complete_random_radio.setChecked(True)
        
        self.simultaneus_random_radio = QRadioButton("Simultaneus random", self)
        self.simultaneus_random_radio.setChecked(strategy_list[1])
        self.simultaneus_delay_input = QLineEdit(self)
        self.simultaneus_delay_input.setText(self.settings.value("simultaneus_delay", "1000"))

        self.closest_radio = QRadioButton("Closest", self)
        self.closest_radio.setChecked(strategy_list[2])

        self.position_prediction_radio = QRadioButton("Position prediction", self)
        self.position_prediction_radio.setChecked(strategy_list[3])
        self.regression_treshold_input = QLineEdit(self)
        self.regression_treshold_input.setText(self.settings.value("regression_treshold", "3"))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)

        layout.addRow(general_label)
        layout.addRow("Out Port:", self.out_port_input)
        layout.addRow("Delay (ms):", self.delay_input)
        layout.addRow(self.enable_log_save_label)
        layout.addRow(self.log_save_dir_input, self.log_dir_button)
        layout.addRow(strategy_label)
        layout.addRow(self.complete_random_radio)
        layout.addRow(self.simultaneus_random_radio)
        layout.addRow("Delay (µs):", self.simultaneus_delay_input)
        layout.addRow(self.closest_radio)
        layout.addRow(self.position_prediction_radio)
        layout.addRow("Regression treshold:", self.regression_treshold_input)
        layout.addWidget(button_box)


        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    @staticmethod
    def get_saved_strategy_list():
        settings = QSettings("JK", "Queuer")
        strategy_list = [
            settings.value("complete_random", False),
            settings.value("simultaneus_random", False),
            settings.value("closest", False),
            settings.value("position_prediction", False)
        ]

        return [True if item == "true" else False for item in strategy_list]

    def accept(self):
        self.settings.setValue("out_port", self.out_port_input.text())
        self.settings.setValue("delay", self.delay_input.text())
        self.settings.setValue("log_dir", self.log_save_dir_input.text())

        self.settings.setValue("complete_random", self.complete_random_radio.isChecked())
        self.settings.setValue("simultaneus_random", self.simultaneus_random_radio.isChecked())
        self.settings.setValue("closest", self.closest_radio.isChecked())
        self.settings.setValue("position_prediction", self.position_prediction_radio.isChecked())

        self.settings.setValue("strategy_picked", "1")

        self.settings.setValue("simultaneus_delay", self.simultaneus_delay_input.text())
        self.settings.setValue("regression_treshold", self.regression_treshold_input.text())
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
            self.list_widget.addItem(f'TAG: {uwb_address} - IP: {ip}:{port}')
            anchors = [anchor for anchor in self.anchors_list if anchor[0] in anchors]
            print(anchors)
            self.tags_dict[uwb_address] = (ip, port, anchors)

    def add_anchor(self):
        anchor_input_dialog = AnchorInputDialog(self)
        if anchor_input_dialog.exec():
            result= anchor_input_dialog.get_inputs()
            self.list_widget.addItem(f'ANCHOR: {result[0]}')
            self.anchors_list.append(result)

    def remove_device(self):
        if(self.list_widget.currentItem()):
            name = self.list_widget.currentItem().text()
            if name.startswith("TAG"):
                del self.tags_dict[name.split(" ")[1]]
                self.list_widget.takeItem(self.list_widget.currentRow())
            else:
                if self.tags_dict == {}:
                    print(self.tags_dict)
                    self.anchors_list = [anchor for anchor in self.anchors_list if anchor[0] != name.split(" ")[1]]
                    self.list_widget.takeItem(self.list_widget.currentRow())

    def clear_devices(self):
        self.list_widget.clear()
        self.anchors_list.clear()
        self.tags_dict.clear()


    def test_tag(self):
        if self.list_widget.currentItem() is None or not self.list_widget.currentItem().text().startswith("TAG"):
            return
        test_socket = UDPSocket(5000, 1)
        tag_uwb_address = self.list_widget.currentItem().text().split(" ")[1]
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
    def __init__(self, success_counter, timeout_counter, error_counter, total_counter, operation_time, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent().setFixedSize(290, 318)
        self.parent().setWindowTitle("JK Queuer - Summary")

        self.success_counter = success_counter
        self.timeout_counter = timeout_counter
        self.error_counter = error_counter
        self.total_counter = total_counter

        self.operation_time = operation_time

        self.calculate_stats()

        self.setup_ui()

    def calculate_stats(self):
        self.success_rate = (self.success_counter / self.total_counter) * 100 if self.total_counter != 0 else 0
        self.error_rate = (self.error_counter / self.total_counter) * 100 if self.total_counter != 0 else 0
        self.timeout_rate = (self.timeout_counter / self.total_counter) * 100 if self.total_counter != 0 else 0
        self.formatted_time = time.strftime('%H:%M:%S', time.gmtime(self.operation_time))

        settings = QSettings("JK", "Queuer")

        self.log_file_size = os.path.getsize(settings.value("log_dir", "./") + "/results.log") / 1024
        self.log_file_size = round(self.log_file_size, 2)

    def dump_stats(self):
        settings = QSettings("JK", "Queuer")
        with open(settings.value("log_dir", "./") + "stats.txt", "w") as f:
            f.write(f"Successes: {self.success_counter}\n")
            f.write(f"Timeouts: {self.timeout_counter}\n")
            f.write(f"Errors: {self.error_counter}\n")
            f.write(f"Total: {self.total_counter}\n")
            f.write(f"Success rate: {round(self.success_rate, 2)}%\n")
            f.write(f"Error rate: {round(self.error_rate, 2)}%\n")
            f.write(f"Timeout rate: {round(self.timeout_rate, 2)}%\n")
            f.write(f"Log file size: {self.log_file_size}kB\n")
            f.write(f"Operation time: {self.formatted_time}s\n")

        self.dump_stats_button.setText("Stats saved")
        self.dump_stats_button.setEnabled(False)
    
    def setup_ui(self):
        layout = QFormLayout(self)
        self.setLayout(layout)

        self.label = QLabel("Monitoring Finished", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))

        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)

        separator2 = QFrame(self)
        separator2.setFrameShape(QFrame.Shape.HLine)

        self.success_counter_label = QLabel(f"Successes: {self.success_counter}", self)
        self.success_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timeout_counter_label = QLabel(f"Timeouts: {self.timeout_counter}", self)
        self.timeout_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_counter_label = QLabel(f"Errors: {self.error_counter}", self)
        self.error_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.total_counter_label = QLabel(f"Total: {self.total_counter}", self)
        self.total_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.succes_rate_label = QLabel(f"Success rate: {round(self.success_rate, 2)}%", self)
        self.succes_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_rate_label = QLabel(f"Error rate: {round(self.error_rate, 2)}%", self)
        self.error_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timeout_rate_label = QLabel(f"Timeout rate: {round(self.timeout_rate, 2)}%", self)
        self.timeout_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.log_file_size_label = QLabel(f"Log file size: {self.log_file_size}kB", self)
        self.log_file_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.operation_time_label = QLabel(f"Operation time: {self.formatted_time}s", self)
        self.operation_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dump_stats_button = QPushButton("Save stats to file", self)
        self.dump_stats_button.clicked.connect(self.dump_stats)
        self.dump_stats_button.setFixedWidth(170)
        dump_buttonbox = QDialogButtonBox(self)
        dump_buttonbox.addButton(self.dump_stats_button, QDialogButtonBox.ButtonRole.AcceptRole)
        dump_buttonbox.setCenterButtons(True)

        exit_button = QPushButton("Exit", self)
        exit_button.clicked.connect(self.parent().close)

        restart_button = QPushButton("Restart", self)
        restart_button.clicked.connect(self.parent().setup_ui)

        buttonbox = QDialogButtonBox(self)
        buttonbox.addButton(exit_button, QDialogButtonBox.ButtonRole.RejectRole)
        buttonbox.addButton(restart_button, QDialogButtonBox.ButtonRole.AcceptRole)
        buttonbox.setCenterButtons(True)

        layout.addWidget(self.label)
        layout.addWidget(separator)
        layout.addWidget(self.success_counter_label)
        layout.addWidget(self.timeout_counter_label)
        layout.addWidget(self.error_counter_label)
        layout.addWidget(self.total_counter_label)
        layout.addWidget(self.succes_rate_label)
        layout.addWidget(self.error_rate_label)
        layout.addWidget(self.timeout_rate_label)
        layout.addWidget(self.log_file_size_label)
        layout.addWidget(self.operation_time_label)
        layout.addWidget(dump_buttonbox)
        layout.addWidget(separator2)
        layout.addWidget(buttonbox)

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
        self.setFixedSize(400, 175)
        self.setup_widget = SetupWidget(self)
        
        self.setCentralWidget(self.setup_widget)
        
    
    def start(self):
        self.time_started = time.time()
        self.working_widget = WorkingWidget(self)
        self.setCentralWidget(self.working_widget)
        self.setWindowTitle("JK Queuer - Working")
        self.setFixedSize(16777215,16777215)
        self.setBaseSize(500, 300)


        print(self.setup_widget.tags_dict)
        if self.setup_widget.tags_dict == {}:
            # self.setup_widget.tags_dict = {'FF': ('127.0.0.1', 5001, [('AA', 3.0, 4.0, 5.0), ('BB', 2.0, 2.0, 2.0), ('CC', 3.0, 3.0, 3.0), ('DD', 0.0, 0.0, 1.0), ('EE', 0.0, 0.0, 0.5)])}
            self.setup_widget.tags_dict = {'DD': ('192.168.0.112', 7, [('AA', 0.0, 0.0, 0.0), ('BB', 0.0, 0.0, 0.0), ('GG', 0.0, 0.0, 0.0)]), 'EE': ('192.168.0.113', 12, [('AA', 0.0, 0.0, 0.0), ('BB', 0.0, 0.0, 0.0), ('GG', 0.0, 0.0, 0.0)])}

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
                                    time.time() - self.time_started,
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
