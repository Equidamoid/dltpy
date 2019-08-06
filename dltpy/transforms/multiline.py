from dltpy import DltMessage
from collections import namedtuple
import typing
import logging

logger = logging.getLogger(__name__)

class PendingMessage:
    def __init__(self, start_msg):
        self.start_msg = start_msg
        self.buffer = b''

pl_lengths = {
    b'NWST': 6,
    b'NWCH': 4,
    b'NWEN': 2
}

class MultilineTransform:
    def __init__(self):
        self._pending: typing.Dict[int, PendingMessage] = {}

    def __call__(self, msg: DltMessage):
        try:
            mt = msg.payload[0]
        except (IndexError, TypeError):
            return msg

        if not mt in pl_lengths:
            return msg

        if len(msg.payload) != pl_lengths[mt]:
            logger.warning("Mismatched length of NWxx payload: %r", msg.payload)
            return mt
        logger.info("Multiline message %.4f", msg.ts)
        ml_id = msg.payload[1]
        if mt == b'NWST':
            self._pending[ml_id] = PendingMessage(msg)
            return None
        if mt == b'NWCH':
            self._pending[ml_id].buffer += msg.payload[3]
            return None
        if mt == b'NWEN':
            msg._decoded_payload = b'', self._pending[ml_id].buffer
        return msg

def transform():
    return MultilineTransform()