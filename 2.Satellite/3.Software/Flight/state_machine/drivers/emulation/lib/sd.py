import os

class SD:

    def __init__(self):
        try:
            os.mkdir('./sd')
        except Exception:
            pass
