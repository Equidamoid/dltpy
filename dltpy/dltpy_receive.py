import dltpy.dltfile as df
from dltpy import cli_common
import struct
import argparse
import logging
import time
import typing
import socket
import asyncio
import sys
from pathlib import Path
from dltpy.native.dltreader_native import DltReader

logger = logging.getLogger(__name__)


class AsyncReceiver:
    """
    An example of asyncio integration and direct use of the native reader.
    The general flow is as follows:
    reader = DltReader(...)
    while True:
        while reader.read():
            message = Message(reader)
            reader.consume_message() # <- don't forget it!
            do_something(message)
        buffer = reader.get_buffer()
        bytes_read = read_into(buffer)  # try to use something like recv_into() or readinto()
                                        # to avoid unneeded data copying
        reader.update_buffer(bytes_read)

    """
    connect_timeout = 2
    iter_timeout = 2

    def __init__(self,
                 address: typing.Tuple[str, int],
                 out_fn: Path,
                 filters: typing.Optional[typing.List[typing.Tuple[str, str]]] = None):

        self._address = address
        if not isinstance(out_fn, Path):
            out_fn = Path(out_fn)
        self._out_fn = out_fn
        self._filters = filters or []
        self._alive = True
        self._socket: socket.socket = None

    async def run(self):
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        if logger.getEffectiveLevel() < logging.WARNING:
            exc_log = logger.exception
        else:
            exc_log = logger.warning
        with self._out_fn.open('wb') as out:
            while self._alive:
                try:
                    self._socket = socket.socket()
                    self._socket.settimeout(0)
                    self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    if sys.platform.startswith('linux'):
                        # More keepalive config: start after 2 sec, send every 5 sec, fail after 3 missing responses
                        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 2)
                        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)

                    await asyncio.wait_for(loop.sock_connect(self._socket, self._address), self.connect_timeout)
                    logger.info("Connected to %s", self._address)
                    reader = DltReader(False, self._filters)

                    while self._alive:
                        while reader.read():
                            msg = df.DltMessage(reader)
                            reader.consume_message()

                            t = time.time()
                            storage_hdr = b'DLT\x01' + struct.pack('II', int(t), int(1e6 * (t - int(t)))) + b'ECU0'
                            out.write(storage_hdr)
                            out.write(msg.raw_message)

                        buf = reader.get_buffer()

                        try:
                            # in 3.7 we should use sock_recv_into instead
                            data = await asyncio.wait_for(loop.sock_recv(self._socket, len(buf)), self.iter_timeout)
                            if len(data) == 0:
                                logger.warning("Server closed connection")
                                break
                            logger.info("Read %5d/%d bytes", len(data), len(buf))
                            buf[:len(data)] = data
                            reader.update_buffer(len(data))
                        except asyncio.TimeoutError:
                            logger.info("recv() timed out")
                            continue
                except IOError as ex:
                    exc_log("Something went wrong (%s), will try to reconnect.", ex)
                    await asyncio.sleep(self.connect_timeout)
                except ValueError as ex:
                    exc_log("Something went wrong (%s), not an IO problem, reconnecting immediately.", ex)
                finally:
                    if self._socket:
                        self._socket.close()

    def stop(self):
        self._alive = False


def main():
    prs = argparse.ArgumentParser()
    prs.add_argument('--host', default='localhost')
    prs.add_argument('--filter', '-f', help="Filter logs, 'APP:CTX'", nargs='*')
    prs.add_argument('output', help="Save the log to a .dlt file")

    cli_common.setup_logs()

    args = prs.parse_args()

    host = args.host
    port = 3490

    flt = cli_common.parse_filters(args.filter)
    out_fn = args.output
    if ':' in host:
        host, port = host.split(':')
        port = int(port)

    ar = AsyncReceiver((host, port), out_fn, flt)
    asyncio.get_event_loop().run_until_complete(ar.run())


if __name__ == '__main__':
    main()
