struct StorageHeader{
    std::array<char, 4> magic;
    uint32_t ts_sec;
    uint32_t ts_msec;
    std::array<char, 4> ecu_id;
};

struct BasicHeader{
    SubByteValue<3> version;
    BooleanFlag
        has_tmsp,
        has_seid,
        has_ecu_id,
        big_endian,
        use_ext;

    uint8_t mcnt{0};
    uint16_t msg_len{0};
    std::array<char, 4> ecu_id{0,0,0,0};
    uint32_t seid{0};
    uint32_t tmsp{0};
};

struct ExtendedHeader{
    SubByteValue<4> mtin;
    SubByteValue<3> mtsp;
    SubByteValue<1> verbose;

    uint8_t arg_count;
    std::array<char, 4> app;
    std::array<char, 4> ctx;
};