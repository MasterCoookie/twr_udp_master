import sys

from queuer import Queuer
from udp_socket import UDPSocket

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot

class Worker(QObject):
    pass

class MainWindow(QMainWindow):
    pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())