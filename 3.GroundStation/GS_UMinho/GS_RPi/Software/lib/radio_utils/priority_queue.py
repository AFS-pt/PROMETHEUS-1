# Based on CPython's heapq
# Converted to a max heap, and greatly simplified
# https://github.com/python/cpython/blob/3.10/Lib/heapq.py
""" Priority Queue Algorithm

Usage:

>>> heap = []         # creates an empty heap
>>> push(heap, item)  # pushes a new item on the heap
>>> item = pop(heap)  # pops the largest item from the heap
>>> item = heap[0]    # largest item on the heap without popping it
>>> heapify(x)        # transforms list into a heap, in-place, in linear time
"""

__all__ = ['push', 'pop', 'heapify']

def push(heap, item):
    """Push item onto heap, maintaining the heap invariant.

    :param heap: The heap to push the item onto
    :type heap: list
    :param item: Any well ordered item
    """
    heap.append(item)
    _siftdown_max(heap, 0, len(heap) - 1)

def pop(heap):
    """Pop the largest item off the heap, maintaining the heap invariant.

    :param heap: The heap to pop the item from
    :type heap: list
    """
    lastelt = heap.pop()    # raises appropriate IndexError if heap is empty
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup_max(heap, 0)
        return returnitem
    return lastelt

def heapify(heap):
    """Transform list into a maxheap, in-place, in O(len(x)) time.

    :param heap: The list to heapify
    :type heap: list
    """
    n = len(heap)
    for i in reversed(range(n // 2)):
        _siftup_max(heap, i)
    return heap

def _siftdown_max(heap, startpos, pos):
    'Maxheap variant of _siftdown'
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    while pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        if parent < newitem:
            heap[pos] = parent
            pos = parentpos
            continue
        break
    heap[pos] = newitem

def _siftup_max(heap, pos):
    'Maxheap variant of _siftup'
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the larger child until hitting a leaf.
    childpos = 2 * pos + 1    # leftmost child position
    while childpos < endpos:
        # Set childpos to index of larger child.
        rightpos = childpos + 1
        if rightpos < endpos and not heap[rightpos] < heap[childpos]:
            childpos = rightpos
        # Move the larger child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2 * pos + 1
    # The leaf at pos is empty now.  Put newitem there, and bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown_max(heap, startpos, pos)
