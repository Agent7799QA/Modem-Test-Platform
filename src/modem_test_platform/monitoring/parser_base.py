
import serial.tools.list_ports
import platform


class BaseParsingThread(QThread):
    rx_data_parsed = Signal(str)
    tx_data_parsed = Signal(str)
    serial_status = Signal(str)
    stopped = Signal()

    request_command = Signal(bytes, int)

    def __init__(self):
        super().__init__()
        self.running = True
        self.port_set_condition = QWaitCondition()
        self.port_set_mutex = QMutex()
        self.port_set = False
        self.serial_port = None
        self.port_name = None
        self.request_command.connect(self.start_writing)
        self.max_retries = 500000000
        self.retries = 0
        self.baudrate = 420000
        self.check_os_baudrate()

        self.write_timer = QTimer()
        self.write_timer.timeout.connect(self.write_data)
        self.current_command = None
        self.write_interval = 0
        self.is_writing = False

    def wait_for_port(self) -> None:
        self.port_set_mutex.lock()
        if not self.port_set:
            self.port_set_condition.wait(self.port_set_mutex)
        self.port_set_mutex.unlock()

    def set_port(self, port_name) -> None:
        self.port_set_mutex.lock()
        self.port_name = port_name
        self.port_set = True
        self.port_set_condition.notify_all()
        self.port_set_mutex.unlock()

    def get_port_read_data(self, port_name) -> None:
        try:
            ser = serial.Serial(port=port_name, baudrate=self.baudrate, bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
            all_good = "good"
            self.serial_status.emit(all_good)
            return ser
        except serial.SerialException as e:
            print(f"{e}\n")
            all_bad = "bad"
            self.serial_status.emit(all_bad)
            return None
        
    def start_writing(self, command: bytes, frequency_hz: int = 1):
        """Начинает запись команды с указанной частотой"""

        if frequency_hz <= 0:
            print(f"freq <= 0: {frequency_hz}\n")
            self.stop_writing()
            return
        self.current_command = command
        self.write_interval = int(1000 / frequency_hz)
        self.is_writing = True
        
        if self.write_timer.isActive():
            self.write_timer.stop()
            
        self.write_timer.start(self.write_interval)        
        self.write_data()

    def stop_writing(self):
        """Останавливает запись"""
        self.is_writing = False
        if self.write_timer.isActive():
            self.write_timer.stop()

    def write_data(self):
        """Записывает данные в порт"""
        if not self.is_writing or not self.current_command or not self.serial_port.is_open:
            return
            
        try:
            if self.serial_port.is_open:
                self.serial_port.write(self.current_command)
        except serial.SerialException as e:
            print(f"Write error: {e}")
            self.stop_writing()
            self.serial_status.emit("write_error")

    def check_os_baudrate(self):
        try:            
            if platform.system() == "Windows":
                self.baudrate = 420000
            elif platform.system() == "Darwin":
                self.baudrate = 450000
            else:
                self.baudrate = 420000
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def stop(self) -> None:
        self.running = False
        self.port_set_condition.notify_all() 
        self.stopped.emit()
        if self.serial_port:
            self.serial_port.close()
        self.quit()
        self.wait()

