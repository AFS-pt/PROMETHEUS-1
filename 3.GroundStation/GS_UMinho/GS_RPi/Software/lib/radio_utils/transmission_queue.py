"""The Transmission Queue is a max heap of messages to be transmitted.

Messages must support the `__lt__`, `__le__`, `__eq__`, `__ge__`, and `__gt__` operators.
This enables to the max heap to compare messages based on their priority.
"""
from . import priority_queue as pq

queue = []
limit = 100

def push(msg):
    """Push a msg into the transmission queue

    :param msg: The message to push
    :type msg: Message | MemoryBufferedMessage | DiskBufferedMessage
    """
    if len(queue) < limit:
        pq.push(queue, msg)
    else:
        raise Exception("Queue is full")

def peek():
    """Returns the next message to be transmitted

    :return: The next message to be transmitted
    :rtype: Message | MemoryBufferedMessage | DiskBufferedMessage
    """
    return queue[0]

def pop():
    """Returns the next message to be transmitted and removes it from the transmission queue

    :return: The next message to be transmitted
    :rtype: Message | MemoryBufferedMessage | DiskBufferedMessage
    """
    return pq.pop(queue)

def empty():
    """Returns if the transmission queue is empty"""
    return len(queue) == 0

def clear():
    """Clears the transmission queue"""
    global queue
    queue = []

def size():
    """Returns the number of messages in the transmission queue"""
    global queue
    return len(queue)
