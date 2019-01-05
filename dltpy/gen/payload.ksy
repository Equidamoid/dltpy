meta:
  id: payload_item
  endian: be
seq:
  - id: plt
    type: payload_type
  - id: str
    type: sized_string
    if: plt.strg or plt.rawd

  - id: uint
    if: plt.uint
    type:
      switch-on: plt.len
      cases:
        1: u1
        2: u2
        3: u4
        4: u8
        5: b16
#        5: u16
  - id: sint
    if: plt.sint
    type:
      switch-on: plt.len
      cases:
        1: s1
        2: s2
        3: s4
        4: s8
        5: b16
#        5: u16

  - id: bool
    if: plt.bool
    type: s1


types:
  payload_type:
    seq:
      - id: floa
        type: b1
      - id: uint
        type: b1
      - id: sint
        type: b1
      - id: bool
        type: b1
      - id: len
        type: b4

      - id: scod2
        type: b1
      - id: stru
        type: b1
      - id: trai
        type: b1
      - id: fixp
        type: b1
      - id: vari
        type: b1
      - id: rawd
        type: b1
      - id: strg
        type: b1
      - id: aray
        type: b1

      - id: whatever
        type: u2

  sized_string:
    seq:
      - id: len
        type: u2le
      - id: data
#        type: str
#        encoding: utf8
        size: len

