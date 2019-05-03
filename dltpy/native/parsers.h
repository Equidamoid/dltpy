template<class T>
size_t fill_one(const char* , T&);

template<class T, class Enable=void>
struct filler;

template<int N>
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

template<class T, typename std::enable_if<std::is_integral<T>::value>::type = 0>
size_t fill_one(const char* begin, bool bigend, T& dest){
    char* dest_ptr = reinterpret_cast<char*>(&dest);
    std::copy(begin, begin + sizeof(T), dest_ptr);
    return sizeof(T);
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