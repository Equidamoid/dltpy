# This file is part of pydlt
# Copyright 2019  Vladimir Shapranov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from dltpy.gen.payload_item import PayloadItem
from binascii import hexlify
from dltpy.native.dltreader_native import DltReader as DR
import logging
import io
import typing

logger = logging.getLogger(__name__)


def as_hex(v):
    return hexlify(v).decode()


def get_value(p: PayloadItem):
    for i in 'str', 'uint', 'sint', 'float', 'bool':
        if hasattr(p, i):
            return getattr(p, i)
    return None


def decode_payload(pl: bytes):
    s = io.BytesIO(pl)
    ret = []
    while s.tell() < len(pl):
        start = s.tell()
        item: PayloadItem = PayloadItem.from_io(s)
        value = get_value(item)
        if value is None:
            logger.error("Can't parse payload %s at offset %d", as_hex(pl), start)
            return None
        if isinstance(value, PayloadItem.SizedString):
            value = value.data

        # strings are null-terminated in dlt, no need for this null in python
        if item.plt.strg:
            assert value[-1] == 0
            value = value[:-1]
        ret.append(value)
    return ret


class DltMessage:
    def __init__(self, reader: DR):
        self.app: str = None
        self.ctx: str = None
        self.ts: float = None
        self.date: float = None
        self.verbose: bool = None

        self._raw_payload: bytes = None
        self._decoded_payload = None
        self._raw_message = None
        self._load(reader)
        self.human_friendly_override = None

    def _load(self, reader: DR):
        ehdr = reader.get_extended()
        bhdr = reader.get_basic()
        if ehdr:
            self.app = ehdr['app'].replace(b'\0', b'').decode()
            self.ctx = ehdr['ctx'].replace(b'\0', b'').decode()
            self.verbose = ehdr['verbose']

        ts = bhdr.get('tmsp', None)
        if ts:
            self.ts = 1e-4 * ts

        shdr = reader.get_storage()
        if shdr is not None:
            self.date = shdr['ts_sec'] + shdr['ts_msec'] * 1e-6

        # the memory views will be invalidated when the next message is parsed, so need to copy them to a bytes object
        self._raw_payload = bytes(reader.get_payload())
        self._raw_message = bytes(reader.get_message())

    def __str__(self):
        return 'DltMsg(%.4f,%s:%s)' % (self.ts, self.app, self.ctx)

    def match(self, filters: typing.List[typing.Tuple[str, str]]):
        for app, ctx in filters:
            if (app is None or self.app == app) and (ctx is None or self.ctx == ctx):
                return True
        return False

    @property
    def payload(self) -> list:
        """
        Returns parsed message payload
        """
        if self._decoded_payload is None:
            self._decoded_payload = decode_payload(self._raw_payload)
        return self._decoded_payload

    @property
    def human_friendly_payload(self):
        """
        Tries to convert payload to more printable form.
        Can be overridden by `human_friendly_override`
        """
        if self.human_friendly_override is not None:
            return self.human_friendly_override

        pl = self.payload
        if pl and len(pl) == 1 and isinstance(pl[0], bytes):
            pl = pl[0]
            try:
                pl = pl.decode()
                if len(pl) > 1 and pl[-1] == '\0':
                    pl = pl[:-1]
                pl = pl.strip()
            except UnicodeDecodeError:
                pass
        return pl

    @property
    def raw_message(self) -> bytes:
        return self._raw_message


class DltReader:
    def __init__(self,
                 reader: typing.Callable[[memoryview], int],
                 filters: typing.Optional[typing.List[typing.Tuple[str, str]]] = None,
                 capture_raw: bool = False,
                 expect_storage_header: bool = True):
        """

        :param reader: "readinto"-style callback for getting data
        :param filters: list of (app_id, ctx_id) filters
        :param capture_raw:
        :param expect_storage_header: `True` for .dlt files, `False` for "raw" socket streams
        """
        #TODO optional capture_raw
        filters = filters or []
        self.reader = reader
        self.capture_raw = capture_raw
        logger.info("Constructing reader, storage=%s, filters=%r", expect_storage_header, filters)
        self.rdr = DR(expect_storage_header, filters)

    def get_next_message(self) -> typing.Optional[DltMessage]:
        while not self.rdr.read():
            buf = self.rdr.get_buffer()
            l = self.reader(buf)
            logger.debug("Read %d bytes to a buffer of %d", l, len(buf))
            if not l:
                return None
            self.rdr.update_buffer(l)
        m = DltMessage(self.rdr)
        self.rdr.consume_message()
        return m

    def __iter__(self) -> DltMessage:
        while True:
            ret = self.get_next_message()
            if ret is None:
                return
            if not ret.verbose:
                continue
            yield ret
