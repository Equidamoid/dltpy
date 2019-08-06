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

#include <algorithm>

template<class T>
struct optional_field{
    bool present;
    T& field;
    optional_field(bool p, T& f): present(p), field(f){}
};

template<class T>
size_t fill_one(const char* , T&);

template<class T, class Enable=void>
struct filler;

template<size_t N>
struct filler<std::array<char, N>>{
    static size_t fill(const char* begin, bool bigend, std::array<char, N>& dest){
        std::copy(begin, begin + N, dest.begin());
        return N;
    }
};

template<class T>
struct filler<T, typename std::enable_if<std::is_integral<T>::value>::type>{
    static size_t fill(const char* begin, bool bigend, T& dest){
        char* dest_ptr = reinterpret_cast<char*>(&dest);
        std::copy(begin, begin + sizeof(T), dest_ptr);
        if (!bigend){
            std::reverse(dest_ptr, dest_ptr + sizeof(T));
        }
        return sizeof(T);
    }
};

template<class T>
struct filler<optional_field<T>>{
    static size_t fill(const char* begin, bool bigend, optional_field<T> dest){
        if (dest.present){
            return filler<T>::fill(begin, bigend, dest.field);
        }
        return 0;
    }
};

//template<class T, typename std::enable_if<std::is_integral<T>::value>::type = 0>
//size_t fill_one(const char* begin, bool bigend, T& dest){
//    char* dest_ptr = reinterpret_cast<char*>(&dest);
//    std::copy(begin, begin + sizeof(T), dest_ptr);
//    return sizeof(T);
//}

template<class T>
struct arg_size{
    static size_t size(const T&){return sizeof(T);}
};

template<class T>
struct arg_size<optional_field<T>>{
    static size_t size(const optional_field<T>& f){return f.present?arg_size<T>::size(f.field):0;}
};

template<class T, size_t N>
struct arg_size<std::array<T, N>>{
    static size_t size(const std::array<T, N>&){return sizeof(T) * N;}
};

//template<class... Args>
//size_t args_size(const Args&...);

template<class Arg>
size_t args_size(const Arg& arg){return arg_size<Arg>::size(arg);}

template<class Arg1, class Arg2, class... Args>
size_t args_size(const Arg1& arg1, const Arg2& arg2, const Args&... args){
    return arg_size<Arg1>::size(arg1) + args_size(arg2, args...);
}


template<class... Args>
const char* fill_struct(const char* begin, const char* end, bool bigend, Args&...);

template<>
const char* fill_struct(const char* begin, const char* end, bool bigend){return begin;}

template<class Arg1, class... Args>
const char* fill_struct(const char* begin, const char* end, bool bigend, Arg1& arg, Args&... args){
    begin += filler<Arg1>::fill(begin, bigend, arg);
    return fill_struct(begin, end, bigend, args...);
}

template<class... Args>
bool fill_struct_if_possible(const char*& begin, const char* end, bool big_end, Args&... args){
    auto size = args_size<Args...>(args...);
    auto expected_end = begin + size;
    if (end < expected_end){
        return false;
    }
    auto ret = fill_struct(begin, end, big_end, args...);
    if (ret != expected_end){
        throw std::runtime_error("Size mismatch, something really bad happened in fill_struct");
    }
    begin = ret;
    return true;
}

// A nasty way to cast char*& to const char*&
template<class... Args>
bool fill_struct_if_possible(char*& begin, char* end, bool big_end, Args&... args){
    const char* _begin = begin;
    bool ret = fill_struct_if_possible(_begin, end, big_end, args...);
    begin = (char*) _begin;
    return ret;
}
