# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class PayloadItem(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.plt = self._root.PayloadType(self._io, self, self._root)
        if  ((self.plt.strg) or (self.plt.rawd)) :
            self.str = self._root.SizedString(self._io, self, self._root)

        if self.plt.uint:
            _on = self.plt.len
            if _on == 4:
                self.uint = self._io.read_u8le()
            elif _on == 1:
                self.uint = self._io.read_u1()
            elif _on == 3:
                self.uint = self._io.read_u4le()
            elif _on == 5:
                self.uint = self._io.read_bits_int(16)
            elif _on == 2:
                self.uint = self._io.read_u2le()

        if self.plt.sint:
            _on = self.plt.len
            if _on == 4:
                self.sint = self._io.read_s8le()
            elif _on == 1:
                self.sint = self._io.read_s1()
            elif _on == 3:
                self.sint = self._io.read_s4le()
            elif _on == 5:
                self.sint = self._io.read_bits_int(16)
            elif _on == 2:
                self.sint = self._io.read_s2le()

        if self.plt.floa:
            _on = self.plt.len
            if _on == 3:
                self.float = self._io.read_f4le()
            elif _on == 4:
                self.float = self._io.read_f8le()

        if self.plt.bool:
            self.bool = self._io.read_s1()


    class PayloadType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.floa = self._io.read_bits_int(1) != 0
            self.uint = self._io.read_bits_int(1) != 0
            self.sint = self._io.read_bits_int(1) != 0
            self.bool = self._io.read_bits_int(1) != 0
            self.len = self._io.read_bits_int(4)
            self.scod2 = self._io.read_bits_int(1) != 0
            self.stru = self._io.read_bits_int(1) != 0
            self.trai = self._io.read_bits_int(1) != 0
            self.fixp = self._io.read_bits_int(1) != 0
            self.vari = self._io.read_bits_int(1) != 0
            self.rawd = self._io.read_bits_int(1) != 0
            self.strg = self._io.read_bits_int(1) != 0
            self.aray = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.whatever = self._io.read_u2le()


    class SizedString(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len = self._io.read_u2le()
            self.data = self._io.read_bytes(self.len)



