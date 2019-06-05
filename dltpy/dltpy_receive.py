import socket
import dltpy.dltfile as df
import struct
import argparse
import logging
import time

logger = logging.getLogger('__name__')


def main():
    prs = argparse.ArgumentParser()
    prs.add_argument('--host', default='localhost')
    prs.add_argument('--output', '-o')
    logging.basicConfig(format='[%(asctime)s - %(message)s')

    args = prs.parse_args()

    host = args.host
    port = 3490

    out_fn = args.output
    if ':' in host:
        host, port = host.split(':')
        port = int(port)
    logger.warning("Will connect to %s:%d", host, port)
    if out_fn:
        logger.warning("Writing to file %s", out_fn)
        out_fd = open(out_fn, 'wb')
        out_len = 0
        out_cnt = 0

    while True:
        try:
            s = socket.socket()
            s.connect((host, port))
            logger.warning("Connected")
            fd = s.fileno()
            dlt = df.DltFile(fd, expect_storage_header=False)
            for i in dlt:
                assert isinstance(i, df.DltMessage)
                if out_fn:
                    t = time.time()
                    storage_hdr = b'DLT\x01' + struct.pack('II', int(t), int(1e6 * (t - int(t)))) + b'ECUX'
                    out_len += out_fd.write(storage_hdr)
                    out_len += out_fd.write(i._raw_data)
                    out_cnt += 1
                    if not out_cnt % 100:
                        logger.warning("%d bytes written (%d messages)", out_len, out_cnt)
                else:
                    print(i, i.payload)
            logger.warning("EOF")
        except IOError as ex:
            logger.warning("IO error: %s, will retry", ex)
            time.sleep(5)
        except KeyboardInterrupt:
            logger.warning("Interrupted, exiting gracefully")


    pass

if __name__ == '__main__':
    main()
