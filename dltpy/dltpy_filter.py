#! /usr/bin/env python3
import argparse
import dltpy.dltfile as df
from dltpy import cli_common
from pathlib import Path
import logging


def main():
    prs = argparse.ArgumentParser()
    prs.add_argument('-f', '--filter', help="Messages to pick, 'APP:CTX'", nargs='*')
    prs.add_argument('-s', '--lifecycle-split', action='store_true')
    prs.add_argument('--lifecycle-threshold', type=float, default=30)
    prs.add_argument('-o', '--output')
    prs.add_argument('files', help='files to process', nargs='*')
    cli_common.setup_logs()
    args = prs.parse_args()
    filters = cli_common.parse_filters(args.filter)

    current_ts = 0
    ts_threshold = args.lifecycle_threshold
    out_fn_counter = 0
    out_fn_base = Path(args.output)
    out_fd = None

    if args.lifecycle_split:
        logging.warning("LC split with threshold %.1f sec", ts_threshold) 

    for fn in args.files:
        logging.info("Processing %s", fn)
        with open(fn, 'rb') as f:
            dlt = df.DltReader(f.readinto, filters)
            for msg in dlt:
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
                out_fd.write(msg._raw_message)

    if out_fd is None:
        logging.warning("No records written!")
    else:
        out_fd.close()


if __name__ == '__main__':
    main()
