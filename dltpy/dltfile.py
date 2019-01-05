from pathlib import Path
from dltpy.gen.stored_message import StoredMessage
from dltpy.gen.payload_item import PayloadItem
from binascii import hexlify
import logging
import io
logger = logging.getLogger(__name__)

def hex(v):
    return hexlify(v).decode()

def get_value(p: PayloadItem):
    for i in 'str', 'uint', 'sint', 'float', 'bool':
        if hasattr(p, i):
            return getattr(p, i)
    return None

def parse_payload(pl: bytes):
    s = io.BytesIO(pl)
    ret = []
    while s.tell() < len(pl):
        start = s.tell()
        item: PayloadItem = PayloadItem.from_io(s)
        value = get_value(item)
        if value is None:
            logger.error("Can't parse payload %s at offset %d", hex(pl), start)
            return None
        if isinstance(value, PayloadItem.SizedString):
            value = value.data
        ret.append(value)
    return ret

class DltMessage:
    def __init__(self, raw: StoredMessage):
        self._raw_msg: StoredMessage = raw
        self.app: str = None
        self.ctx: str = None
        self.ts: float = None
        self.date: float = None
        self.verbose: bool = None
        self.raw_payload: bytes = None
        self._raw_ext: StoredMessage.ExtendedHeader = None
        self._payload_cache = None
        self.load(raw)

    def load(self, raw: StoredMessage):
        if raw.msg.hdr.use_ext:
            self._raw_ext: StoredMessage.ExtendedHeader = raw.msg.ext_hdr
            self.app = self._raw_ext.app.replace('\0', '')
            self.ctx = self._raw_ext.app.replace('\0', '')
            self.verbose = self._raw_ext.verbose
        if raw.msg.hdr.has_tmsp:
            self.ts = raw.msg.hdr.tmsp * 1e-4

        self.date = raw.storage_hdr.ts_sec + (raw.storage_hdr.ts_msec * 1e-3)
        self.raw_payload = raw.msg.payload

    def __str__(self):
        return 'DltMsg(%s,%s:%s,)' % (self.ts, self.app, self.ctx)

    @property
    def payload(self):
        if self._payload_cache is None:
            self._payload_cache = parse_payload(self.raw_payload)
        return self._payload_cache

class DltFile:
    def __init__(self, fn: Path):
        if not isinstance(fn, Path):
            fn = Path(fn)
        self._fn = fn
        self._f_len = fn.stat().st_size
        self.fd = fn.open('rb')


    def get_next_message(self) -> DltMessage:
        ret = None
        while self.fd.tell() != self._f_len:
            sm = StoredMessage.from_io(self.fd)
            msg = DltMessage(sm)
            if msg.verbose:
                ret = msg
                break

        return ret

    def __iter__(self) -> DltMessage:
        while True:
            ret = self.get_next_message()
            if ret is None:
                return
            yield ret