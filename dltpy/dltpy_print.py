#! /usr/bin/env python3

# This file is part of pydlt
# Copyright 2019  Vladimir Shapranov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging

from dltpy import dltfile
from dltpy import cli_common
from dltpy.transforms import apply_transforms


def main():
    prs = argparse.ArgumentParser()
    prs.add_argument('-f', '--filter', nargs='*',
                     help="Add a filter in for of 'APP:CTX'")
    prs.add_argument('-t', '--transform', nargs='*',
                     help="Use a transform module")
    prs.add_argument('--raw', action='store_true',
                     help="Don't expect storage headers. "
                          "Useful for things like 'socat tcp:host:port stdout | dltpy-print --raw'")
    prs.add_argument('file', nargs=1)
    cli_common.setup_logs()
    args = prs.parse_args()
    fn = args.file[0]
    filters = cli_common.parse_filters(args.filter)
    transforms = cli_common.load_transforms(args.transform)

    logging.warning("Will print file %s with filters: %s", fn, filters)
    with open(fn, 'rb') as fd:
        dltf = dltfile.DltReader(fd.readinto, filters, expect_storage_header=not args.raw)
        dltf = apply_transforms(dltf, transforms)
        for dm in dltf:
            try:
                print(cli_common.message_str(dm))
            except Exception as ex:
                logging.exception("Failed to parse")
                print("ERROR: %s" % ex)


if __name__ == '__main__':
    main()
