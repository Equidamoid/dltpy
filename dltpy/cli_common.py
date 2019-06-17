import logging
from dltpy import dltfile
import datetime
import importlib

logger = logging.getLogger(__name__)


def parse_filters(flt_strings):
    return [tuple([i or None for i in flt.split(':')]) for flt in flt_strings] if flt_strings else []


def load_transforms(transform_names):
    def load_one(name: str):
        if not '.' in name:
            name = 'dltpy.transforms.' + name
        logger.info("Loading transform %s", name)
        m = importlib.import_module(name)
        return m.transform()

    return list(map(load_one, transform_names or []))

def setup_logs(debug=False):
    logging.basicConfig(format='[%(asctime)s] - %(message)s', level=logging.DEBUG if debug else logging.WARNING)

def message_str(msg: dltfile.DltMessage):
    txt = '%9.4f\t%-4s:%-4s\t%s' % (msg.ts, msg.app, msg.ctx, msg.human_friendly_payload)
    if msg.date:
        date = datetime.datetime.fromtimestamp(msg.date)
        txt = '%s\t%s' % (date.strftime('%Y-%m-%d %H:%M:%S.%f'), txt)
    return txt

