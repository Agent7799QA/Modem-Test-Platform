from parser_base import BaseParsingThread

from typing import Container
from crsf_parser import CRSFParser, PacketValidationStatus

from serial import SerialException


class TxParsingThread(BaseParsingThread):
    def run(self):
        while self.running:
            try:
                self.wait_for_port()
                
                if not self.port_set and self.running:
                    continue
                
                self.serial_port = self.get_port_read_data(self.port_name)
                
                if self.serial_port:
                    data_bytes = self.serial_port.read(100)
                    crsf_parser = CRSFParser(self.print_frame)
                    input = bytearray()
                    input.extend(data_bytes)
                    crsf_parser.parse_stream(input)

                    if not self.serial_port.is_open:
                        print("RX port was closed unexpectedly")
                        continue  
                else:
                    print("Tx port failed to open.")
                    continue
             
            except SerialException as e:
                            print(f"Serial exception occurred: {e}")
                            
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
        self.tx_data_parsed.emit(f"{frame}")