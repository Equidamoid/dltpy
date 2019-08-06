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

#include "headers.h"
#include <vector>
#include <optional>
#include <tuple>
class dlt_corrupted: public std::runtime_error{
public:
    using std::runtime_error::runtime_error;
};

class dlt_eof: public std::exception{
};

class dlt_io_error: public std::runtime_error{
public:
    using std::runtime_error::runtime_error;
};


  
class DltReader{
    enum class Stage{
        Storage, Basic, Extended, Payload, Done
    };
            
    const Stage iClearStage;
        
    StorageHeader iStorageHeader;
    BasicHeader iBasicHeader;
    ExtendedHeader iExtendedHeader;
        
    Stage iStage{iClearStage};

    std::array<char, 8196> iBuffer;
        
    char* iDataEnd{iBuffer.begin()};
    char* iCursor{iBuffer.begin()};
    char* iMessageBegin{iBuffer.begin()};

    off_t iBasicOffset{0};
    off_t iPayloadOffset{0};
    off_t iPayloadEndOffset{0};
        
    off_t dataLeft();
    void readyOrThrow() const{
        if (iStage != Stage::Done){
            throw std::runtime_error("Not ready yet. Give me more data!");
        }
    }
    void selfcheck();
    std::string str();
public:
    DltReader(bool expectStorage);
    DltReader(const DltReader&) = delete;
        
    bool read();
    bool findMagic();

    void resetMessage();
    void consumeMessage();
    void flush();

    std::tuple<char*, size_t> getBuffer(){flush(); return {iDataEnd, iBuffer.end() - iDataEnd};}
    void updateBuffer(size_t len){iDataEnd += len;}
        
    const StorageHeader& getStorage() const{
        if (iClearStage != Stage::Storage){
            throw std::runtime_error("Storage header won't be read");
        }
        readyOrThrow();
        return iStorageHeader;
    }

    const BasicHeader& getBasic() const{
        readyOrThrow();
        return iBasicHeader;

           
    }

    const ExtendedHeader getExtended() const{
        readyOrThrow();
        if (!iBasicHeader.use_ext){
            throw std::runtime_error("No extended header in current message");
        }
        return iExtendedHeader;
    }

    std::tuple<char*, size_t> getPayload() const{
        readyOrThrow();
        return {iMessageBegin + iPayloadOffset, iPayloadEndOffset - iPayloadOffset};
    }
        
    std::tuple<char*, size_t> getMessage() const{
        readyOrThrow();
        return {iMessageBegin, iPayloadEndOffset};
    }

    bool rawStream() const {
        return iClearStage != Stage::Storage;
    }   
        
};

struct MsgFilter{
    std::optional<std::array<char, 4>> app, ctx;
    bool operator()(const DltReader&) const;
};

class FilteredDltReader: public DltReader{
    std::vector<MsgFilter> iFilters;
    bool iVerboseOnly;
    bool iAutoRecover;
    bool checkFilters();
public:
    FilteredDltReader(bool expectStorage,
                      const std::vector<MsgFilter>& filters,
                      bool verboseOnly = true
        );

    bool readFiltered();
            
};
