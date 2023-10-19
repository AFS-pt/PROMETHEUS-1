# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Prometheus(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Prometheus.Header(self._io, self, self._root)
        self.packet_id = self._io.read_u1()
        _on = self.packet_id
        if _on == 0:
            self.payload = Prometheus.Telemetry(self._io, self, self._root)
        else:
            self.payload = Prometheus.Image(self._io, self, self._root)

    class SunSensorType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sun_xn = self._io.read_u2le()
            self.sun_yn = self._io.read_u2le()
            self.sun_zn = self._io.read_u2le()
            self.sun_xp = self._io.read_u2le()
            self.sun_yp = self._io.read_u2le()
            self.sun_zp = self._io.read_u2le()


    class Image(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.segment = self._io.read_bytes(251)


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.destination = self._io.read_bytes(1)
            self.node = self._io.read_bytes(1)
            self.identifier = self._io.read_bytes(1)
            self.flags = self._io.read_bytes(1)


    class ImuType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.accel_x = self._io.read_f4le()
            self.accel_y = self._io.read_f4le()
            self.accel_z = self._io.read_f4le()
            self.gyro_x = self._io.read_f4le()
            self.gyro_y = self._io.read_f4le()
            self.gyro_z = self._io.read_f4le()
            self.mag_x = self._io.read_f4le()
            self.mag_y = self._io.read_f4le()
            self.mag_z = self._io.read_f4le()
            self.temp = self._io.read_f4le()


    class Telemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imu = Prometheus.ImuType(self._io, self, self._root)
            self.sun_sensor = Prometheus.SunSensorType(self._io, self, self._root)
            self.vbatt = self._io.read_f4le()
            self.cpu_temp = self._io.read_f4le()



