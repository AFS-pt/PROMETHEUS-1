"""Has a bunch of commands that can be called via radio, with an argument.

Contains a dictionary of commands mapping their 2 byte header to a function.
"""

import time
import os
from lib.pycubed import cubesat
import lib.radio_utils
from lib.radio_utils import transmission_queue as tq
from lib.radio_utils import headers
from lib.radio_utils.disk_buffered_message import DiskBufferedMessage
from lib.radio_utils.memory_buffered_message import MemoryBufferedMessage
from lib.radio_utils.message import Message
import json
import supervisor
from lib.logs import beacon_packet
import msgpack
from io import BytesIO
import struct

NO_OP = b'\x00\x00'
HARD_RESET = b'\x00\x01'
QUERY = b'\x00\x03'
EXEC_PY = b'\x00\x04'
REQUEST_FILE = b'\x00\x05'
LIST_DIR = b'\x00\x06'
TQ_SIZE = b'\x00\x07'
MOVE_FILE = b'\x00\x08'
COPY_FILE = b'\x00\x09'
DELETE_FILE = b'\x00\x10'
RELOAD = b'\x00\x11'
REQUEST_BEACON = b'\x00\x12'
GET_RTC = b'\x00\x13'
SET_RTC_UTIME = b'\x00\x14'
GET_RTC_UTIME = b'\x00\x15'
SET_RTC = b'\x00\x16'
CLEAR_TX_QUEUE = b'\x00\x17'

COMMAND_ERROR_PRIORITY = 9
BEACON_PRIORITY = 10

def noop(self):
    """No operation"""
    self.debug('no-op')

def hreset(self):
    """Hard reset"""
    self.debug('Resetting')
    cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
    cubesat.micro.reset()


def query(task, args):
    """Execute the query as python and return the result"""
    task.debug(f'query: {args}')
    res = str(eval(args))
    _downlink(res)

def exec_py(task, args):
    """Execute the python code, and do not return the result

    :param task: The task that called this function
    :param args: The python code to execute
    :type args: str
    """
    task.debug(f'exec: {args}')
    exec(args)

def request_file(task, file):
    """Request a file to be downlinked

    :param task: The task that called this function
    :param file: The path to the file to downlink
    :type file: str"""
    file = str(file, 'utf-8')
    if file_exists(file):
        tq.push(DiskBufferedMessage(file))
    else:
        task.debug(f'File not found: {file}')
        tq.push(Message(9, b'File not found', with_ack=True))

def list_dir(task, path):
    """List the contents of a directory, and downlink the result

    :param task: The task that called this function
    :param path: The path to the directory to list
    :type path: str
    """
    path = str(path, 'utf-8')
    res = os.listdir(path)
    res = json.dumps(res)
    _downlink(res)

def tq_size(task):
    """Return the length of the transmission queue"""
    len = str(tq.size())
    _downlink(f"{len}")

def move_file(task, args):
    """
    Move a file from source to dest.
    Does not work when moving from sd to flash, should copy files instead.

    :param task: The task that called this function
    :param args: json string [source, dest]
    :type args: str
    """
    try:
        args = json.loads(args)
        os.rename(args[0], args[1])
        task.debug('Sucess moving file')
        tq.push(Message(9, b'Success moving file'))
    except Exception as e:
        task.debug(f'Error moving file: {e}')
        _downlink(f'Error moving file: {e}')

def copy_file(task, args):
    """
    Copy a file from source to dest

    :param task: The task that called this function
    :param args: json string [source, dest]
    :type args: str
    """
    try:
        args = json.loads(args)
        with open(args[0], 'rb') as source, open(args[1], 'wb') as dest:
            _cp(source, dest)
        task.debug('Sucess copying file')
        tq.push(Message(9, b'Success copying file'))
    except Exception as e:
        task.debug(f'Error moving file: {e}')
        _downlink(f'Error moving file: {e}')

def delete_file(task, file):
    """Delete file

    :param task: The task that called this function
    :param file: The path to the file to delete
    :type file: str
    """
    try:
        os.remove(file)
        tq.push(Message(9, b'Success deleting file'))
    except Exception as e:
        task.debug(f'Error deleting file: {e}')
        _downlink(f'Error deleting file: {e}')

async def reload(task):
    """Reloads the flight software

    :param task: The task that called this function
    """
    task.debug('Reloading')
    msg = bytearray([headers.DEFAULT])
    msg.append(b'reset')
    await cubesat.radio.send(data=msg)
    supervisor.reload()

def request_beacon(task):
    """Request a beacon packet

    :param task: The task that called this function
    """
    _downlink_msg(beacon_packet(), header=headers.BEACON, priority=BEACON_PRIORITY, with_ack=False)

def get_rtc(task):
    """Get the RTC time"""
    _downlink_msg(_pack(tuple(cubesat.rtc.datetime)))

def get_rtc_utime(task):
    """Get the RTC time as a unix timestamp"""
    _downlink_msg(struct.pack('i', time.mktime(cubesat.rtc.datetime)))

def set_rtc(task, args):
    """Set the RTC to the passed time"""
    ymdhms = _unpack(args)  # year, month, day, hour, minute, second
    cubesat.rtc.datetime = time.struct_time(ymdhms + [0, -1, -1])
    cubesat.f_datetime_valid = True

def set_rtc_utime(task, args):
    """Set the RTC to the passed time

    :param task: The task that called this function
    :param args: The *unix time* to set the RTC to"""
    utime = struct.unpack(args)
    utime = utime[0]  # unpack returns a "tuple" with one element
    t = time.localtime(utime)
    cubesat.rtc.datetime = t
    cubesat.f_datetime_valid = True

def clear_tx_queue(task):
    """Clear the transmission queue"""
    tq.clear()
    task.debug('Cleared transmission queue')


"""
HELPER FUNCTIONS
"""

def _downlink_msg(data, priority=1, header=0x00, with_ack=True):
    assert (len(data) <= radio_utils.LORA_MAX_PACKET_LEN)
    tq.push(Message(priority, data, header=header, with_ack=with_ack))

def _downlink(data):
    """Write data to a file, and then create a new DiskBufferedMessage to downlink it"""
    if not (cubesat.sdcard and cubesat.vfs):
        if len(data) < 1024:  # 1kb limit for downlink
            tq.push(MemoryBufferedMessage(data))
        else:
            tq.push(Message(COMMAND_ERROR_PRIORITY, b'Downlink too large (sd missing)'))
        return
    fname = f'/sd/downlink/{time.monotonic_ns()}.txt'
    if not file_exists('/sd/downlink'):
        os.mkdir('/sd/downlink')
    f = open(fname, 'w')
    f.write(data)
    f.close()
    tq.push(DiskBufferedMessage(fname))

def _cp(source, dest, buffer_size=1024):
    """
    Copy a file from source to dest. source and dest
    must be file-like objects, i.e. any object with a read or
    write method, like for example StringIO.
    """
    while True:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)

def file_exists(path):
    try:
        os.stat(path)
        return True
    except Exception:
        return False

def _pack(data):
    b = BytesIO()
    msgpack.pack(data, b)
    b.seek(0)
    return b.read()

def _unpack(data):
    b = BytesIO(data)
    return msgpack.unpack(b)


commands = {
    NO_OP: {"function": noop, "name":  "NO_OP", "will_respond": False, "has_args": False},
    HARD_RESET: {"function": hreset, "name": "HARD_RESET", "will_respond": False, "has_args": False},
    QUERY: {"function": query, "name": "QUERY", "will_respond": True, "has_args": True},
    EXEC_PY: {"function": exec_py, "name": "EXEC_PY", "will_respond": False, "has_args": True},
    REQUEST_FILE: {"function": request_file, "name": "REQUEST_FILE", "will_respond": True, "has_args": True},
    LIST_DIR: {"function": list_dir, "name": "LIST_DIR", "will_respond": True, "has_args": True},
    TQ_SIZE: {"function": tq_size, "name": "TQ_SIZE", "will_respond": True, "has_args": False},
    MOVE_FILE: {"function": move_file, "name": "MOVE_FILE", "will_respond": True, "has_args": True},
    COPY_FILE: {"function": copy_file, "name": "COPY_FILE", "will_respond": True, "has_args": True},
    DELETE_FILE: {"function": delete_file, "name": "DELETE_FILE", "will_respond": True, "has_args": True},
    RELOAD: {"function": reload, "name": "RELOAD", "will_respond": True, "has_args": False},
    REQUEST_BEACON: {"function": request_beacon, "name": "REQUEST_BEACON", "will_respond": True, "has_args": False},
    GET_RTC: {"function": get_rtc, "name": "GET_RTC", "will_respond": True, "has_args": False},
    GET_RTC_UTIME: {"function": get_rtc_utime, "name": "GET_RTC_UTIME", "will_respond": True, "has_args": False},
    SET_RTC: {"function": set_rtc, "name": "SET_RTC", "will_respond": False, "has_args": True},
    SET_RTC_UTIME: {"function": set_rtc_utime, "name": "SET_RTC_UTIME", "will_respond": False, "has_args": True},
    CLEAR_TX_QUEUE: {"function": clear_tx_queue, "name": "CLEAR_TX_QUEUE", "will_respond": False, "has_args": False},
}

super_secret_code = b'p\xba\xb8C'
