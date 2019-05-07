#include <stdio.h>
#include <array>
#include <stdint.h>
#include <type_traits>
#include <string>
#include "bitmasks.h"
#include "parsers.h"
#include "headers.h"
#include <fcntl.h>
#include <unistd.h>
#include <cassert>
#include <vector>

const char* const dlt_magic = "DLT\x01";



class dlt_corrupted: public std::runtime_error{
public:
    using std::runtime_error::runtime_error;
};

class dlt_eof: public std::exception{
};

class DltReader{
    int iFd;
    off_t iInputOffset{0};
    std::array<char, 8196> iBuffer;
    char* iBufferEnd{iBuffer.begin()};
    char* iCursor{iBuffer.begin()};

    std::vector<std::array<std::string, 2>> iFilters;

    StorageHeader iStoragiExtendedHeader;
    BasicHeader iBasicHeader;
    ExtendedHeader iExtendedHeader;

    char* iMessageBegin{nullptr};
    char* iPayloadBegin{nullptr};

    // Same as iCursor?
    char* iPayloadEnd{nullptr};


public:
    DltReader(int fd): iFd{fd} {};
    void setFilters(const std::vector<std::array<std::string, 2>> flt){iFilters = flt;};

    bool checkFilters();

    int ensureBuffer(int len);
    void next();
    void next_safe();

    const StorageHeader& storageHdr() const {return iStoragiExtendedHeader;}
    const BasicHeader& basicHdr() const {return iBasicHeader;}
    const ExtendedHeader* extHdr() const {return iBasicHeader.use_ext.value?&iExtendedHeader:nullptr;}

    const char* messageBegin() const {return iMessageBegin;}
    const char* payloadBegin() const {return iPayloadBegin;}
    const char* payloadEnd() const {return iCursor;}
};

int DltReader::ensureBuffer(int len){
    if (iBufferEnd - iCursor >= len){
        return 0;
    }
    auto offset = iCursor - iBuffer.begin();
    std::copy(iCursor, iBufferEnd, iCursor - offset);
    iCursor -= offset;
    iBufferEnd -= offset;
    iInputOffset += offset;
    if (iBuffer.end() - iBufferEnd <=0 ){
        throw std::runtime_error("Non-positive read() length");
    }
    auto bytes_read = read(iFd, iBufferEnd, iBuffer.end() - iBufferEnd);
    if (!bytes_read){
        fprintf(stderr, "EOF reached\n");
        throw dlt_eof();
    }
    if (bytes_read < 0){
        perror("Can't read");
        throw std::runtime_error("Can't read()");
    }
    iBufferEnd += bytes_read;
    //fprintf(stderr, "Read %ld bytes\n", bytes_read);
    iPayloadBegin = nullptr;
    iPayloadEnd = nullptr;
    return offset;
}

void DltReader::next(){
    ensureBuffer(64);
    const char* d = iCursor;
    d = fill_struct(d, d + 10, false, iStoragiExtendedHeader.magic, iStoragiExtendedHeader.ts_sec, iStoragiExtendedHeader.ts_msec, iStoragiExtendedHeader.ecu_id);
    auto& m = iStoragiExtendedHeader.magic;
    if (!(m[0] == 'D' && m[1] == 'L' && m[2] == 'T')){
        fprintf(stderr, "Magic mismatch!");
        throw dlt_corrupted("Magic mismatch!");
    }
//    assert(m[0] == 'D' && m[1] == 'L' && m[2] == 'T');
    auto msg_begin = d;
    d = read_bitmask(d, 0, iBasicHeader.version,
        iBasicHeader.has_tmsp,
        iBasicHeader.has_seid,
        iBasicHeader.has_ecu_id,
        iBasicHeader.big_endian,
        iBasicHeader.use_ext
    );

    bool bigend = iBasicHeader.big_endian;

    d = fill_struct(d, nullptr, false, iBasicHeader.mcnt, iBasicHeader.msg_len);
    if (iBasicHeader.has_ecu_id) d = fill_struct(d, nullptr, false, iBasicHeader.ecu_id);
    if (iBasicHeader.has_seid) d = fill_struct(d, nullptr, false, iBasicHeader.seid);
    if (iBasicHeader.has_tmsp) d = fill_struct(d, nullptr, false, iBasicHeader.tmsp);
    if (iBasicHeader.msg_len > 4096){
        //abort();
        throw dlt_corrupted("Message is suspiciously long");
    }
    if (iBasicHeader.use_ext){
        d = read_bitmask(
            d, 0,
            iExtendedHeader.mtin,
            iExtendedHeader.mtsp,
            iExtendedHeader.verbose
        );
        d = fill_struct(d, nullptr, false,
            iExtendedHeader.arg_count,
            iExtendedHeader.app,
            iExtendedHeader.ctx
        );

        std::string app(iExtendedHeader.app.begin(), 4);
        std::string ctx(iExtendedHeader.ctx.begin(), 4);
//        printf("v: %d, cnt: %d, %s:%s\n", (int)iExtendedHeader.verbose, (int)iExtendedHeader.arg_count, app.c_str(), ctx.c_str());

    }
    auto msg_end = msg_begin + iBasicHeader.msg_len;

    auto pl_offset = d - iCursor;
    auto pl_end_offset = msg_end - iCursor;

    auto off = ensureBuffer(msg_end - iCursor);

    iMessageBegin = iCursor;
    iPayloadBegin = iCursor + pl_offset;
    iCursor += pl_end_offset;
}

bool DltReader::checkFilters(){
    // No filters -- no filtering
    if (iFilters.empty()){
        return true;
    }
    // No extended header -> no app/ctx -> failed filter
    if (!iBasicHeader.use_ext){
        return false;
    }

    for (const auto& appctx: iFilters){
        if (std::equal(appctx[0].begin(), appctx[0].end(), iExtendedHeader.app.begin())
            && std::equal(appctx[1].begin(), appctx[1].end(), iExtendedHeader.ctx.begin())
        ){
            return true;
        }
    }
    return false;
}

void DltReader::next_safe(){
    while (1){
        try{
            next();
            if (!checkFilters()){
                continue;
            }
            break;
        }
        catch(const dlt_corrupted& ex){
            auto off = iInputOffset + (iCursor - iBuffer.begin());

            fprintf(stderr, "File corrupted (%s) (pos=%d, seq=%d,msglen=%d, end=%d, ver=%d, has_ext=%d), trying to recover...", 
                ex.what(), (int)off, iBasicHeader.mcnt,
                iBasicHeader.msg_len, iBasicHeader.big_endian.value, iBasicHeader.version.value, iBasicHeader.use_ext.value);
            auto cur = iCursor;
            ++iCursor;
            while(1){
                ensureBuffer(4);
                if (std::equal(iCursor, iCursor + 4, dlt_magic)){
                    fprintf(stderr, "Recovered after %d bytes\n", (int)(iCursor - cur));
                    break;
                }
                ++iCursor;
            }
        }
    }
}

#include <boost/python.hpp>

#include <bytesobject.h>
using namespace boost::python;

object pyGetStorageHeader(const DltReader& rdr){
    auto& hdr = rdr.storageHdr();
    dict ret;
    ret["ecu"] = handle<>(PyBytes_FromStringAndSize(hdr.ecu_id.begin(), 4));
    ret["ts_sec"] = hdr.ts_sec;
    ret["ts_msec"] = hdr.ts_msec;
    return ret;
}

object pyGetBasicHeader(const DltReader& rdr){
    auto hdr = rdr.basicHdr();
    dict ret;
    if (hdr.has_tmsp.value){
        ret["tmsp"] = hdr.tmsp;
    }
    return ret;
}

void pySetFilters(DltReader& rdr, object filters){
    std::vector<std::array<std::string, 2>> flt;
    for (int i = 0; i < len(filters); i++){
        flt.push_back({extract<std::string>(filters[i][0]), extract<std::string>(filters[i][1])});
    }
    rdr.setFilters(flt);
}

object pyGetExtHeader(const DltReader& rdr)
{
    auto hdr = rdr.extHdr();
    if (!hdr){
        return object();
    }
    dict ret;
    ret["app"] = boost::python::handle<>(PyBytes_FromStringAndSize(hdr->app.begin(), 4));
    ret["ctx"] = boost::python::handle<>(PyBytes_FromStringAndSize(hdr->ctx.begin(), 4));
    ret["arg_count"] = hdr->arg_count;
    ret["verbose"] = (bool)hdr->verbose.value;
    return ret;
}

object pyGetPayload(const DltReader& rdr){
    auto pbegin = rdr.payloadBegin();
    auto pend = rdr.payloadEnd();
    if (pbegin && pend){
        return object(boost::python::handle<>(PyBytes_FromStringAndSize(pbegin, pend - pbegin)));
    }
    return object();
}

object pyGetRawMessage(const DltReader& rdr){
    auto pbegin = rdr.messageBegin();
    auto pend = rdr.payloadEnd();
    if (pbegin && pend){
        return object(boost::python::handle<>(PyBytes_FromStringAndSize(pbegin, pend - pbegin)));
    }
    return object();
}


void translate(dlt_eof const &e)
{
    PyErr_SetString(PyExc_EOFError, e.what());
}

BOOST_PYTHON_MODULE(native_dltfile)
{
    class_<DltReader>("DltReader", init<int>())
        .def("next_safe", &DltReader::next_safe)
        .def("ext_hdr", &pyGetExtHeader)
        .def("basic_hdr", &pyGetBasicHeader)
        .def("storage_hdr", &pyGetStorageHeader)
        .def("raw_payload", &pyGetPayload)
        .def("raw_message", &pyGetRawMessage)
        .def("set_filters", &pySetFilters)
        ;

    class_<dlt_eof>("DltEof");

    register_exception_translator<dlt_eof>(&translate);
}

int main(){
    int fd = open("/Users/equi/PycharmProjects/dltpy/data/park_crash_1_corrupted.dlt", O_RDONLY);
    assert(fd);
    DltReader r(fd);
    for (int i = 0; i <= 100000; i++)
    {
        r.next_safe();
    }
    return 0;
}

