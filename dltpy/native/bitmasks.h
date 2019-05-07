

template<int N>
struct SubByteValue{
    int value;
//    template<typename std::enable_if<N == 1>::type* = 0>
    operator bool(){
        static_assert(N == 1, "Can't cast to boolean, N != 1");
        return value;
    }
    operator int(){
        return value;
    }
};

using BooleanFlag = SubByteValue<1>;


template<int... Lengths>
const char* read_bitmask(const char* begin, int offset, SubByteValue<Lengths>&... values);

template<>
const char* read_bitmask(const char* begin, int offset){
    if (offset % 8){
        throw std::runtime_error("Bitmask must take complete bytes");
    }
//    static_assert((offset % 8) == 0, "Bitmask must take complete bytes");
    return begin + (offset / 8);
};

template<int Len, int... Lengths>
const char* read_bitmask(const char* begin, int offset, SubByteValue<Len>& val, SubByteValue<Lengths>&... values){
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
