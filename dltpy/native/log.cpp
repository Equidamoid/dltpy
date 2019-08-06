#include "log.h"
#include <stdio.h>

auto log_stderr = [](const std::string& line){
		      fprintf(stderr, "%s\n", line.c_str());
		  };
Printer log_printer = log_stderr;
