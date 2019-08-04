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

#include "dltreader.h"
#include <boost/python.hpp>
#include "log.h"
#include <bytesobject.h>
using namespace boost::python;

template<size_t N>
auto pyArrayStringToBytes(const std::array<char, N>& arr){
    off_t len = std::find(arr.begin(), arr.end(), '\0') - arr.begin();
    return boost::python::handle<>(PyBytes_FromStringAndSize(arr.begin(), len));
}

object pyGetStorageHeader(const FilteredDltReader& rdr){
    if (rdr.rawStream()){
        return object();
    }
    auto& hdr = rdr.getStorage();
    dict ret;
    ret["ecu"] = pyArrayStringToBytes(hdr.ecu_id);
    ret["ts_sec"] = hdr.ts_sec;
    ret["ts_msec"] = hdr.ts_msec;
    return ret;
}
object pyGetBasicHeader(const FilteredDltReader& rdr){
    auto& hdr = rdr.getBasic();
    dict ret;
    if (hdr.has_tmsp.value){
        ret["tmsp"] = hdr.tmsp;
    }
    return ret;
}

object pyGetExtHeader(const FilteredDltReader& rdr)
{
    const auto& ext = rdr.getExtended();
    dict ret;
    ret["app"] = pyArrayStringToBytes(ext.app);
    ret["ctx"] = pyArrayStringToBytes(ext.ctx);
    ret["arg_count"] = ext.arg_count;
    ret["verbose"] = static_cast<bool>(ext.verbose);
    return ret;
}

auto pyGetPayload(const FilteredDltReader& rdr){
    auto [begin, len] = rdr.getPayload();
    return boost::python::handle<>(PyMemoryView_FromMemory(begin, len, PyBUF_READ));
}
auto pyGetMessage(const FilteredDltReader& rdr){
    auto [begin, len] = rdr.getMessage();
    return boost::python::handle<>(PyMemoryView_FromMemory(begin, len, PyBUF_READ));
}


void translate_eof(dlt_eof const &e)
{
    PyErr_SetString(PyExc_EOFError, e.what());
}

void translate_io(dlt_io_error const &e)
{
    PyErr_SetString(PyExc_IOError, e.what());
}

object pyGetBuffer(FilteredDltReader& rdr){
    auto buf = (rdr).getBuffer();
    boost::python::object memview(
        boost::python::handle<>(PyMemoryView_FromMemory(std::get<0>(buf), std::get<1>(buf), PyBUF_WRITE)));
    return memview;

}

template<size_t N>
std::array<char, N> to_array(const std::string& str){
    std::array<char, N> ret{0};
    auto l = std::min(str.size(), N);
    std::copy(str.begin(), str.begin() + l, ret.begin());
    return ret;
}

template<size_t N>
std::optional<std::array<char, N>> to_optional_array(object obj){
    if (obj.is_none()){
        return std::nullopt;
    }
    std::string str = extract<std::string>(obj);
    return to_array<N>(str);
}

auto pyMakeReader(bool storage, list flt){
    int fltLen = len(flt);
    std::vector<MsgFilter> filters;
    LOG("makeReader(storage={})", storage);
    for (int i = 0; i < fltLen; i++){
        object f = flt[i];
        filters.push_back({
                to_optional_array<4>(f[0]),
                to_optional_array<4>(f[1])});
    }
    return boost::shared_ptr<FilteredDltReader>(new FilteredDltReader(storage, filters));
}

void pySetLogger(object logger){
    log_printer = [logger](const std::string& line){
                      logger.attr("warning")(line);
                  };
}

void translate_corrupted(dlt_corrupted const &e)
{
    PyErr_SetString(PyExc_ValueError, e.what());
}

BOOST_PYTHON_MODULE(native_dltreader)
{
    class_<MsgFilter>("MsgFilter");
    
    class_<FilteredDltReader, boost::noncopyable>("DltReader", no_init)
        .def("__init__", make_constructor(&pyMakeReader))
        .def("read", &FilteredDltReader::readFiltered)
        .def("get_buffer", &pyGetBuffer)
        .def("get_payload", &pyGetPayload)
        .def("get_message", &pyGetMessage)
        .def("get_basic", &pyGetBasicHeader)
        .def("get_extended", &pyGetExtHeader)
        .def("get_storage", &pyGetStorageHeader)
        .def("consume_message", &DltReader::consumeMessage)
        .def("update_buffer", &DltReader::updateBuffer)
        .def("find_magic", &DltReader::findMagic)
        ;

    def("get_buffer", &pyGetBuffer);
    def("set_logger", &pySetLogger);
    class_<dlt_eof>("DltEof");

    register_exception_translator<dlt_eof>(&translate_eof);
    register_exception_translator<dlt_io_error>(&translate_io);
    register_exception_translator<dlt_corrupted>(&translate_corrupted);
}

