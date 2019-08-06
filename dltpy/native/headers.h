// This file is part of pydlt
// Copyright 2019  Vladimir Shapranov
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#pragma once

#include <array>
#include <stdint.h>
#include "bitmasks.h"

struct StorageHeader{
    std::array<char, 4> magic;
    uint32_t ts_sec;
    uint32_t ts_msec;
    std::array<char, 4> ecu_id;
};

struct BasicHeader{
    SubByteValue<3> version;
    BooleanFlag
        has_tmsp,
        has_seid,
        has_ecu_id,
        big_endian,
        use_ext;

    uint8_t mcnt{0};
    uint16_t msg_len{0};
    std::array<char, 4> ecu_id{0,0,0,0};
    uint32_t seid{0};
    uint32_t tmsp{0};
};

struct ExtendedHeader{
    SubByteValue<4> mtin;
    SubByteValue<3> mtsp;
    SubByteValue<1> verbose;

    uint8_t arg_count;
    std::array<char, 4> app;
    std::array<char, 4> ctx;
};
