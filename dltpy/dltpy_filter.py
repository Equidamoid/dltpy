#! /usr/bin/env python3
import argparse
import dltpy.dltfile as df
from pathlib import Path
import logging


def main():
    logging.basicConfig(format='%(asctime)s - %(message)s')
    prs = argparse.ArgumentParser()
    prs.add_argument('-f', '--filter', help="Messages pick, 'APP:CTX'", nargs='*')
    prs.add_argument('-s', '--lifecycle-split', action='store_true')
    prs.add_argument('--lifecycle-threshold', type=float, default=30)
    prs.add_argument('-o', '--output')
    prs.add_argument('files', help='files to process', nargs='*')

    args = prs.parse_args()
    filters = [tuple([i or None for i in flt.split(':')]) for flt in args.filter] if args.filter else None
    logging.warning("Filters: %s", filters)

    current_ts = 0
    ts_threshold = args.lifecycle_threshold
    out_fn_counter = 0
    out_fn_base = Path(args.output)
    out_fd = None

    if args.lifecycle_split:
        logging.warning("LC split with threshold %.1f sec", ts_threshold) 

    for fn in args.files:
        with open(fn, 'rb') as fd:
            dlt = df.DltReader(fd, filters, expect_storage_header=True)
            for msg in dlt:
                # print(msg)
                assert isinstance(msg, df.DltMessage)
                if (msg.ts - current_ts < -ts_threshold and args.lifecycle_split) or out_fd is None:
                    if not out_fd is None:
                        out_fd.close()

                    out_fn = out_fn_base
                    if args.lifecycle_split:
                        out_fn = out_fn_base.parent / ('%s%02d%s' % (out_fn_base.stem, out_fn_counter, out_fn_base.suffix))
                        out_fn_counter += 1

                    out_fd = out_fn.open('wb')
                current_ts = msg.ts
                out_fd.write(msg._raw_data)

    out_fd.close()

if __name__ == '__main__':
    main()
