import serial.tools.list_ports
from PySide6.QtCore import QThread, Signal

class PortMonitorThread(QThread):
    ports_changed = Signal(list)
    stopped = Signal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.last_ports = []

    def run(self):
        while self.running:
            com_ports = [port.device for port in serial.tools.list_ports.comports()
                         if port.description != 'n/a']
            
            self.ports_changed.emit(com_ports)
            self.last_ports = com_ports
            self.msleep(1000)
            if not self.running:
                break

    def stop(self):
        self.running = False
        self.stopped.emit()
