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


meta:
  id: stored_message
  endian: be
seq:
  - id: storage_hdr
    type: storage_header
  - id: msg
    type: message

types:
  storage_header:
    seq:
      - id: magic
        contents: [DLT, 1]
      - id: ts_sec
        type: u4le
      - id: ts_msec
        type: s4le
      - id: ecu_id
        size: 4
        type: str
        encoding: ascii
  message:
    seq:
      - id: hdr
        type: basic_header
      - id: ext_hdr
        type: extended_header
        if: hdr.use_ext
      - id: payload
        size: hdr.msg_len - 4 - (hdr.has_ecu_id?4:0) - (hdr.has_seid?4:0) - (hdr.has_tmsp?4:0) - (hdr.use_ext?10:0)

  basic_header:
    seq:
      - id: version
        type: b3
      - id: has_tmsp
        type: b1
      - id: has_seid
        type: b1
      - id: has_ecu_id
        type: b1
      - id: big_endian
        type: b1
      - id: use_ext
        type: b1

      - id: mcnt
        type: u1
      - id: msg_len
        type: u2
      - id: ecu_id
        type: str
        encoding: ascii
        size: 4
        if: has_ecu_id
      - id: seid
        type: u4
        if: has_seid
      - id: tmsp
        type: u4
        if: has_tmsp

  extended_header:
    seq:
      - id: mtin
        type: b4
      - id: mstp
        type: b3
      - id: verbose
        type: b1
      - id: arg_count
        type: u1
      - id: app
        type: str
        encoding: ascii
        size: 4
      - id: ctx
        type: str
        encoding: ascii
        size: 4
