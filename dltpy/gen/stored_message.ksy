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
        type: u4
      - id: ts_msec
        type: u4
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
