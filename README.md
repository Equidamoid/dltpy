### dltpy - library and utilities for DLT logging

#### Installing
##### Requirements
dltpy uses native extension to parse and filter messages. This is done purely for performance reasons.
In my usecases which involve filtering out ~95% of the logs it speeds up the processing ~20 times.
As a funny fact, due to stricter filtering `dltpy-dump` is even faster than `dlt-convert -a` for me.

 - `boost::python`. Sorry for the pain. If it complains about it, make sure that you have the `-dev`
 package installed. Also keep in mind that is has to be built/installed for every minor version of python. So if you
 built python 3.7 for your ubuntu 16.04, `apt-get` won't help you, you have to built boost yourself. Sorry again.

 - `fmtlib` for native logging and formatting exceptions

##### Installation
```
git clone git+https://github.com/Equidamoid/dltpy
(cd dltpy; git checkout native-dltreader)
pip install --user ./dltpy
```
TODO: upload to pypi

#### Using

There are 3 commandline utilities that demonstrate usage of the library:
 - `dltpy-print` prints specified .dlt file as plain text. "text-like" payloads are decoded and printed as text, others are `repr()`ed
 - `dltpy-filter` filters out unneeded boring messages. Run it with `-f IDS:OF YOUR:APPS` and enjoy tiny logs that take seconds to load.
 - `dltpy-receive` demonstrates integration with asyncio and direct use of the native module, like `dlt-receive`. The main difference is that it gracefully reconnects if, for example, your device reboots.

Please note that non-`verbose` messages are skipped by `DltFile` since it has no way of decoding the payload.