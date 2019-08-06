#include <fmt/format.h>
#include <stdio.h>
#include <functional>
#pragma once

using Printer = std::function<void (const std::string&)>;
extern Printer log_printer;

template<class... Arg>
void log(const char* fn, int line, std::string fmt, const Arg&... args){
    auto msg = fmt::format(fmt, args...);
    log_printer(fmt::format("{}:{} - {}", fn, line, msg));
}

#define LOG(FMT, ...) log(__FILE__, __LINE__, FMT, __VA_ARGS__)
