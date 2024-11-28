from .message import Message
import os
from .headers import IMAGE_START, IMAGE_MID, IMAGE_END

class ImageMessage(Message):
    """
    encodes JPEG files into packets that can be transmitted over RF
        - works for baseline DCT

    You can find out if your JPEG image uses baseline DCT by looking at the start of frame
    bytes. If they are FFC0, it is baseline otherwise it will be FFC2
    """

    headers = {
        0xFF, 0xD8, 0xC0, 0xC2, 0xC4, 0xDA, 0xDB, 0xDD, 0xFE, 0xD9
    }

    # SIG = bytearray.fromhex("FF")
    SIG = bytearray(1)
    SIG[0] = 0xFF
    # SOI = bytearray.fromhex("D8")     # Start of image
    # SOFb = bytearray.fromhex("C0")     # Start of frame (baseline DCT)
    # SOFp = bytearray.fromhex("C2")     # start of frame (progressive DCT)
    # DHT = bytearray.fromhex("C4")     # Define Huffman Tables
    # SOS = bytearray.fromhex("FFDA")     # Start of scan
    SOS = bytearray(2)
    SOS[0] = 0xFF
    SOS[1] = 0xDA
    # DQT = bytearray.fromhex("DB")     # Define Quntization table
    # DRI = bytearray.fromhex("DD")     # Define Restart Interval
    # RST = bytearray.fromhex("D")      # Restart
    # FLEX = bytearray.fromhex("E")      # Variable
    # CMT = bytearray.fromhex("FE")     # Comment
    # EOI = bytearray.fromhex("FFD9")     # End of Image
    EOI = bytearray(2)
    EOI[0] = 0xFF
    EOI[1] = 0xD9

    def __init__(self, filepath, packet_size) -> None:
        self.packet_size = packet_size
        self.filepath = filepath
        self.length = os.stat(filepath)[6]
        self.sent_packet_len = 0
        self.cursor = 0
        self.in_scan = False
        self.file_err = False
        self.scan_size = ((self.packet_size - 1) // 64) * 64

    def packet(self):
        """
        Packetizes the image into packets of a specified size limit
        Packet 1
            SOI and JFIF-APP0
        Packet 2 to packet i
            comment
        packet i + 1 to packet j
            frame, Quntization and huffman tables
        packet j + 1 to k
            image scan
        """
        next_packet_found = False
        data_len = 0

        try:
            with open(self.filepath, "rb") as file:
                file.seek(self.cursor)
                data_bytes = file.read(self.packet_size - 1)
        except Exception as e:
            print(f"Error reading from image file: {e}")
            self.file_err = True
        
        if self.in_scan:
            """
            Should use 64 byte increments in the image scan section
            """
            data_len = self.scan_size
            packet = bytearray(self.scan_size + 1)
            packet[1:] = data_bytes[0:data_len]
        else:
            """
            If we are stil in the header bytes
            """
            if self.SOS in data_bytes[:2]:
                """
                If SOS sends just the SOS bytes
                """
                self.in_scan = True
                next_packet_found = True
                data_len = 2
            if self.sent_packet_len != 0:
                next_packet_found = True
                data_len = self.sent_packet_len - 1
            length = len(data_bytes)
            bdr = bytearray(reversed(data_bytes))
            start = 1
            while not next_packet_found:
                signal_index = bdr.find(self.SIG, 1, self.packet_size - 1)
                if signal_index == -1:
                    """section is larger than packet size"""
                    data_len = self.packet_size - 1
                    next_packet_found = True
                if bdr[signal_index - 1] in self.headers:
                    data_len = length - signal_index - 1
                    next_packet_found = True
                else:
                    start += signal_index

        packet = bytearray(data_len + 1)
        packet[1:] = data_bytes[0:data_len]
        if self.cursor == 0:
            """start packet"""
            packet[0] = IMAGE_START
        elif self.EOI in packet:
            """end packet"""
            packet[0] = IMAGE_END
        else:
            """mid packet"""
            packet[0] = IMAGE_MID
        self.sent_packet_len = data_len + 1

        return packet, True
    
    def done(self):
        return (self.length <= self.cursor) or self.file_err
    
    def ack(self):
        """
        confirms that we should move to the next packet of info
        """
        self.cursor += self.sent_packet_len - 1
        self.sent_packet_len = 0