#include <pybind11/pybind11.h>
#include "dltreader.h"
#include <algorithm>
#include <fmt/format.h>

namespace py=pybind11;

template<size_t N>
auto pyArrayStringToBytes(const std::array<char, N>& arr){
    off_t len = std::find(arr.begin(), arr.end(), '\0') - arr.begin();
    return py::bytes(arr.begin(), len);
}

template<size_t N>
std::array<char, N> to_array(const std::string& str){
    std::array<char, N> ret{0};
    auto l = std::min(str.size(), N);
    std::copy(str.begin(), str.begin() + l, ret.begin());
    return ret;
}

template<size_t N>
std::optional<std::array<char, N>> to_optional_array(py::object obj){
    if (obj.is_none()){
        return std::nullopt;
    }

    return to_array<N>(obj.cast<std::string>());
}

PYBIND11_MODULE(dltreader_native, m){

    py::class_<MsgFilter>(m, "MsgFilter");

    py::class_<FilteredDltReader>(m, "DltReader")
            .def(py::init([](bool expect_storage, py::list flt){
                int fltLen = py::len(flt);
                std::vector<MsgFilter> filters;
                fmt::print(stderr, "filter len: {}\n", fltLen);
                for (int i = 0; i < fltLen; i++){
                    py::list f = flt[i];
                    filters.push_back({
                                              to_optional_array<4>(f[0]),
                                              to_optional_array<4>(f[1])});
                }
                fmt::print(stderr, "fwd filter len: {}\n", filters.size());
                return new FilteredDltReader(expect_storage, filters);
            }))
            .def("read", &FilteredDltReader::readFiltered)
            .def("get_buffer", [](FilteredDltReader& rdr){
                auto [buf, size] = rdr.getBuffer();
                return py::memoryview(py::buffer_info(buf, size, false));
            })
            .def("get_payload", [](FilteredDltReader& rdr){
                auto [buf, size] = rdr.getPayload();
                return py::memoryview(py::buffer_info(buf, size, true));
            })
            .def("get_message", [](FilteredDltReader& rdr){
                auto [buf, size] = rdr.getMessage();
                return py::memoryview(py::buffer_info(buf, size, true));
            })
            .def("get_basic", [](const FilteredDltReader& rdr){
                auto& hdr = rdr.getBasic();
                py::dict ret;
                if (hdr.has_tmsp.value){
                    ret["tmsp"] = hdr.tmsp;
                }
                return ret;
            })
            .def("get_extended", [](const FilteredDltReader& rdr){
                auto& ext = rdr.getExtended();
                py::dict ret;
                ret["app"] = pyArrayStringToBytes(ext.app);
                ret["ctx"] = pyArrayStringToBytes(ext.ctx);
                ret["arg_count"] = ext.arg_count;
                ret["verbose"] = static_cast<bool>(ext.verbose);
                return ret;
            })
            .def("get_storage", [](const FilteredDltReader& rdr) -> py::object{
                if (rdr.rawStream()){
                    return py::none();
                }
                auto& hdr = rdr.getStorage();
                py::dict ret;
                ret["ecu"] = pyArrayStringToBytes(hdr.ecu_id);
                ret["ts_sec"] = hdr.ts_sec;
                ret["ts_msec"] = hdr.ts_msec;
                return std::move(ret);
            })
            .def("consume_message", &FilteredDltReader::consumeMessage)
            .def("update_buffer", &FilteredDltReader::updateBuffer)
            .def("find_magic", &FilteredDltReader::findMagic)
            ;

    py::class_<dlt_eof>(m, "DltEof");

//    py::register_exception<dlt_eof>(m, "DltEof")
//
//    register_exception_translator<dlt_io_error>(&translate_io);
//    register_exception_translator<dlt_corrupted>(&translate_corrupted);

}