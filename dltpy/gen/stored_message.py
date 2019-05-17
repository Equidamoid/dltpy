# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class StoredMessage(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.storage_hdr = self._root.StorageHeader(self._io, self, self._root)
        self.msg = self._root.Message(self._io, self, self._root)

    class StorageHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\x44\x4C\x54\x01")
            self.ts_sec = self._io.read_u4le()
            self.ts_msec = self._io.read_s4le()
            self.ecu_id = (self._io.read_bytes(4)).decode(u"ascii")


    class Message(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hdr = self._root.BasicHeader(self._io, self, self._root)
            if self.hdr.use_ext:
                self.ext_hdr = self._root.ExtendedHeader(self._io, self, self._root)

            self.payload = self._io.read_bytes((((((self.hdr.msg_len - 4) - (4 if self.hdr.has_ecu_id else 0)) - (4 if self.hdr.has_seid else 0)) - (4 if self.hdr.has_tmsp else 0)) - (10 if self.hdr.use_ext else 0)))


    class BasicHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_bits_int(3)
            self.has_tmsp = self._io.read_bits_int(1) != 0
            self.has_seid = self._io.read_bits_int(1) != 0
            self.has_ecu_id = self._io.read_bits_int(1) != 0
            self.big_endian = self._io.read_bits_int(1) != 0
            self.use_ext = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.mcnt = self._io.read_u1()
            self.msg_len = self._io.read_u2be()
            if self.has_ecu_id:
                self.ecu_id = (self._io.read_bytes(4)).decode(u"ascii")

            if self.has_seid:
                self.seid = self._io.read_u4be()

            if self.has_tmsp:
                self.tmsp = self._io.read_u4be()



    class ExtendedHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mtin = self._io.read_bits_int(4)
            self.mstp = self._io.read_bits_int(3)
            self.verbose = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.arg_count = self._io.read_u1()
            self.app = (self._io.read_bytes(4)).decode(u"ascii")
            self.ctx = (self._io.read_bytes(4)).decode(u"ascii")



