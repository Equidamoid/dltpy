import typing
import logging
from dltpy.dltfile import DltMessage

logger = logging.getLogger(__name__)

def apply_transforms(
        it: typing.Iterable[DltMessage],
        transforms: typing.List[typing.Callable[[DltMessage], DltMessage]]):
    for msg in it:
        for tr in transforms:
            try:
                msg = tr(msg)
            except:
                logger.error("Filter failed on %s %r", msg, msg.payload)
                raise
            if msg is None:
                break
        if msg is None:
            logger.warning('Message consumed by a transform')
        else:
            yield msg

