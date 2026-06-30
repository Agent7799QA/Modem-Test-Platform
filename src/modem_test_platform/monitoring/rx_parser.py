from parser_base import BaseParsingThread
from typing import Container
from crsf_parser import CRSFParser, PacketValidationStatus
from serial import SerialException


class RxParsingThread(BaseParsingThread):

    def run(self):
        crsf_parser = CRSFParser(self.print_frame)
        while self.running:
            try:
                self.wait_for_port()
                
                if not self.port_set and self.running:
                    continue
                if self.serial_port is None:
                    self.serial_port = self.get_port_read_data(self.port_name)
                
                if self.serial_port is not None:
                    data_bytes = self.serial_port.read(100)
                    input = bytearray()
                    input.extend(data_bytes)
                    try:
                        crsf_parser.parse_stream(input)
                    except KeyError as e:
                        if 'frame_length' in str(e):
                            print(f"Невалидный CRSF пакет: {input}")
                        else:
                            print(f"Ошибка парсинга: {e}")
                    except Exception as e:
                        print(f"Общая ошибка парсинга: {e}")
                    # stats = crsf_parser.get_stats()
                    # print(f"valid_frames: {stats.valid_frames}, invalid_frames: {stats.invalid_frames},\
                    #       crc_errors: {stats.crc_errors}, framing_errors: {stats.framing_errors}  \n")

                    if not self.serial_port.is_open:
                        print("RX port was closed unexpectedly")
                        continue
                    
                else:
                    print("RX port failed to open.")
                    continue
                    
            except SerialException as e:
                            print(f"Serial exception occurred: {e}")
                            self.serial_port = None
                            if self.retries >= self.max_retries:
                                print("Maximum retries reached. Exiting.")
                                break
                            self.retries += 1
            finally:
                    if 'serial_port' in locals():
                        try:
                            self.serial_port.close()
                        except Exception as close_e:
                            print(f"Error closing serial port: {close_e}")
                        
    def print_frame(self, frame: Container, status: PacketValidationStatus) -> None:
        # print(f"""{status}\n{frame}""")
        self.rx_data_parsed.emit(f"{frame}")

