### dltpy - library and utilities for DLT logging

#### Installing
##### Requirements (not handled by pip/setuptools)
 - native build environment: `python3-dev`, `cmake` and a [decent c++ compiler supporting c++17](https://en.cppreference.com/w/cpp/compiler_support#cpp17).
 - [`fmtlib`](https://github.com/fmtlib/fmt) for native logging and formatting exceptions

##### Installation
Once the requirements mentioned above are ready, you can install dltpy with pip just as any other python package:

 - current master from git:
```
pip install --user git+https://github.com/Equidamoid/dltpy.git
```
 - last version from pypi:
```
pip install --user dltpy
```
 - an editable "developer" mode:
```$xslt
git clone https://github.com/Equidamoid/dltpy.git
pip install --user -e dltpy
```


#### Using

There are 3 commandline utilities that demonstrate usage of the library:
 - `dltpy-print` prints specified .dlt file as plain text. "text-like" payloads are decoded and printed as text, others are `repr()`ed
 - `dltpy-filter` filters out unneeded boring messages. Run it with `-f IDS:OF YOUR:APPS` and enjoy tiny logs that take seconds to load.
 - `dltpy-receive` demonstrates integration with asyncio and direct use of the native module, like `dlt-receive`. The main difference is that it gracefully reconnects if, for example, your device reboots.

Please note that non-`verbose` messages are skipped by `DltFile` since it has no way of decoding the payload.
