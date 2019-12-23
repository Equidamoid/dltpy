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

template<int N>
struct SubByteValue{
    int value;
//    template<typename std::enable_if<N == 1>::type* = 0>
    operator bool() const{
        static_assert(N == 1, "Can't cast to boolean, N != 1");
        return value;
    }
    operator int() const{
        return value;
    }
};

using BooleanFlag = SubByteValue<1>;


template<class Char, int... Lengths>
Char* read_bitmask(Char* begin, int offset, SubByteValue<Lengths>&... values);

template<class Char>
Char* read_bitmask(Char* begin, int offset){
    if (offset % 8){
        throw std::runtime_error("Bitmask must take complete bytes");
    }
//    static_assert((offset % 8) == 0, "Bitmask must take complete bytes");
    return begin + (offset / 8);
}

template<class Char, int Len, int... Lengths>
Char* read_bitmask(Char* begin, int offset, SubByteValue<Len>& val, SubByteValue<Lengths>&... values){
    val.value = 0;
    for(int i = offset; i < offset + Len; i++){
        uint8_t bit = ((begin[i / 8] << (i % 8)) & 128) >> 7 ;
        //uint8_t bit = ((begin[i / 8] >> (i % 8)) & 1)  ;
        val.value <<= 1;
        val.value += bit;
    }
    if (val.value >= (1<<Len)){
        abort();
    }
    return read_bitmask(begin, offset + Len, values...);
}
