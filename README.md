### dltpy - pyre python dlt reader

#### Installing
```
pip install git+https://github.com/Equidamoid/dltpy
```
TODO: upload to pypi

#### Using

See `dltpy_dump.py` as an example. Everything boils down to creating a `DltFile` instance and getting `DltMessage`s out of it.

Please note that non-`verbose` messages are skipped by `DltFile` since it has no way of decoding the payload.

In case you need to access more fields than exposed in `DltMessage` (namely the timestamp, app/context id and the payload), you can read the `_raw_msg` field containing the kataistruct objects.