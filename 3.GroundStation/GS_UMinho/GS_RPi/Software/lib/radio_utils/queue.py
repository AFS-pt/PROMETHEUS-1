"""
Simple Queue library by Thomas Damiani

Implemented via a linked list
"""

class Node:
    def __init__(self, element) -> None:
        self.data = element
        self.next = None

class Queue:
    """Queue class"""
    def __init__(self, max_length):
        """Create an empty list"""
        self.head = Node(None)
        self.tail = self.head
        self.capacity = max_length
        self.length = 0
    
    def empty(self):
        """Queue is empty when the head and tail point to the same Node"""
        return self.tail is self.head
    
    def enq(self, element):
        """
        Places a new node on the end of the list by making tail.next this new
        node and then making the new node the tail
        """
        if self.length + 1 > self.capacity:
            return
        elem = Node(element)
        if not self.tail:
            self.tail.next = elem
        self.tail = elem
        self.length += 1

    def enq(self):
        """
        If queue is not empty, takes the element at the head and returns it
        while making head.next the new head.
        """
        if self.empty():
            raise Exception("Queue Empty")
        result = self.head.data
        self.head = self.head.next
        return result
    
    def peek(self):
        if self.empty():
            raise Exception("Queue Empty")
        return self.head.data