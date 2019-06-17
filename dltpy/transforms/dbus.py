from debus.marshalling import read_message
from debus.message import Message, MessageType
from dltpy.dltfile import DltMessage
import typing
import logging

logger = logging.getLogger(__name__)

tmpl_ids = ''
tmpl_call = '{msg.sender} -> {msg.destination} {msg.path} {msg.interface}.{msg.member} {msg.payload}'
tmpl_response = '{msg.sender} -> {msg.destination} {msg.payload} to {responseto}'
tmpl_responseto = '[0x{call.serial:04x}] {call.interface}.{call.member} @{call_ts:.4f}'

msg_type_letters = {
}

fmts = {
    MessageType.METHOD_CALL: 'M: ' + tmpl_call,
    MessageType.SIGNAL: 'S: ' + tmpl_call,
    MessageType.ERROR: 'E: ' + tmpl_response,
    MessageType.METHOD_RETURN: 'R: ' + tmpl_response,
}

class DBusDecodeTransform:
    def __init__(self):
        self._pending_calls: typing.Dict[int, (float, Message)] = {}

    def __call__(self, dm: DltMessage):
        if not dm.app in ('DBSE', 'DBSY'):
            return dm
        if not dm.ctx in ('DIN', 'DOUT'):
            return dm
        try:
            dbus_pl = dm.payload[1]
        except IndexError:
            logger.warning("Can't handle payload %r", dm.payload)
            return dm
        msgs: typing.List[Message] = read_message(dbus_pl)
        msgs_txt = []
        for msg in msgs:
            if msg.message_type == MessageType.METHOD_CALL:
                self._pending_calls[msg.serial] = dm.ts, msg

            responseto = None
            if msg.message_type in (MessageType.METHOD_RETURN, MessageType.ERROR):
                call_ts, method_call = self._pending_calls.pop(msg.reply_serial, (None, None))
                responseto = tmpl_responseto.format(call=method_call, call_ts=call_ts) if method_call else '[UNKNOWN]'
            msgs_txt.append(fmts[msg.message_type].format(msg=msg, responseto=responseto))

        dm.human_friendly_override = '\n'.join(msgs_txt)
        return dm

def transform():
    return DBusDecodeTransform()
