"""The Transmission Queue is a max heap of messages to be transmitted.

Messages must support the `__lt__`, `__le__`, `__eq__`, `__ge__`, and `__gt__` operators.
This enables to the max heap to compare messages based on their priority.
"""
from .queue import Queue

limit = 100
image_queue = Queue(limit)


def enq(msg):
    """Push a filepath on the image queue

    :param msg: The message to push
    :type msg: string
    """
    image_queue.enq(msg)


def peek():
    """Returns the next filepath to an image to be transmitted

    :return: The next filepath to be transmitted
    :rtype: string
    """
    return image_queue.peek()


def pop():
    """Returns the next filepath to be transmitted and removes it from the transmission queue

    :return: The next fielpath to be transmitted
    :rtype: string
    """
    return image_queue.deq()


def empty():
    """Returns if the transmission queue is empty"""
    return image_queue.empty()


def clear():
    """Clears the transmission queue"""
    global image_queue
    image_queue = Queue(limit)


def size():
    """Returns the number of messages in the transmission queue"""
    return image_queue.length