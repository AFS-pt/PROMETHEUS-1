#ifndef PROMETHEUS_H_
#define PROMETHEUS_H_

// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

#include "../kaitai/kaitaistruct.h"
#include <stdint.h>

#if KAITAI_STRUCT_VERSION < 9000L
#error "Incompatible Kaitai Struct C++/STL API: version 0.9 or later is required"
#endif

class prometheus_t : public kaitai::kstruct {

public:
    class sun_sensor_type_t;
    class image_t;
    class header_t;
    class imu_type_t;
    class telemetry_t;

    prometheus_t(kaitai::kstream* p__io, kaitai::kstruct* p__parent = 0, prometheus_t* p__root = 0);

private:
    void _read();
    void _clean_up();

public:
    ~prometheus_t();

    class sun_sensor_type_t : public kaitai::kstruct {

    public:

        sun_sensor_type_t(kaitai::kstream* p__io, prometheus_t::telemetry_t* p__parent = 0, prometheus_t* p__root = 0);

    private:
        void _read();
        void _clean_up();

    public:
        ~sun_sensor_type_t();

    private:
        uint16_t m_sun_xn;
        uint16_t m_sun_yn;
        uint16_t m_sun_zn;
        uint16_t m_sun_xp;
        uint16_t m_sun_yp;
        uint16_t m_sun_zp;
        prometheus_t* m__root;
        prometheus_t::telemetry_t* m__parent;

    public:
        uint16_t sun_xn() const { return m_sun_xn; }
        uint16_t sun_yn() const { return m_sun_yn; }
        uint16_t sun_zn() const { return m_sun_zn; }
        uint16_t sun_xp() const { return m_sun_xp; }
        uint16_t sun_yp() const { return m_sun_yp; }
        uint16_t sun_zp() const { return m_sun_zp; }
        prometheus_t* _root() const { return m__root; }
        prometheus_t::telemetry_t* _parent() const { return m__parent; }
    };

    class image_t : public kaitai::kstruct {

    public:

        image_t(kaitai::kstream* p__io, prometheus_t* p__parent = 0, prometheus_t* p__root = 0);

    private:
        void _read();
        void _clean_up();

    public:
        ~image_t();

    private:
        uint8_t m_total;
        std::string m_segment;
        prometheus_t* m__root;
        prometheus_t* m__parent;

    public:
        uint8_t total() const { return m_total; }
        std::string segment() const { return m_segment; }
        prometheus_t* _root() const { return m__root; }
        prometheus_t* _parent() const { return m__parent; }
    };

    class header_t : public kaitai::kstruct {

    public:

        header_t(kaitai::kstream* p__io, prometheus_t* p__parent = 0, prometheus_t* p__root = 0);

    private:
        void _read();
        void _clean_up();

    public:
        ~header_t();

    private:
        uint8_t m_destination;
        uint8_t m_node;
        uint8_t m_identifier;
        uint8_t m_flags;
        prometheus_t* m__root;
        prometheus_t* m__parent;

    public:
        uint8_t destination() const { return m_destination; }
        uint8_t node() const { return m_node; }
        uint8_t identifier() const { return m_identifier; }
        uint8_t flags() const { return m_flags; }
        prometheus_t* _root() const { return m__root; }
        prometheus_t* _parent() const { return m__parent; }
    };

    class imu_type_t : public kaitai::kstruct {

    public:

        imu_type_t(kaitai::kstream* p__io, prometheus_t::telemetry_t* p__parent = 0, prometheus_t* p__root = 0);

    private:
        void _read();
        void _clean_up();

    public:
        ~imu_type_t();

    private:
        float m_accel_x;
        float m_accel_y;
        float m_accel_z;
        float m_gyro_x;
        float m_gyro_y;
        float m_gyro_z;
        float m_mag_x;
        float m_mag_y;
        float m_mag_z;
        float m_temp;
        prometheus_t* m__root;
        prometheus_t::telemetry_t* m__parent;

    public:
        float accel_x() const { return m_accel_x; }
        float accel_y() const { return m_accel_y; }
        float accel_z() const { return m_accel_z; }
        float gyro_x() const { return m_gyro_x; }
        float gyro_y() const { return m_gyro_y; }
        float gyro_z() const { return m_gyro_z; }
        float mag_x() const { return m_mag_x; }
        float mag_y() const { return m_mag_y; }
        float mag_z() const { return m_mag_z; }
        float temp() const { return m_temp; }
        prometheus_t* _root() const { return m__root; }
        prometheus_t::telemetry_t* _parent() const { return m__parent; }
    };

    class telemetry_t : public kaitai::kstruct {

    public:

        telemetry_t(kaitai::kstream* p__io, prometheus_t* p__parent = 0, prometheus_t* p__root = 0);

    private:
        void _read();
        void _clean_up();

    public:
        ~telemetry_t();

    private:
        imu_type_t* m_imu;
        sun_sensor_type_t* m_sun_sensor;
        float m_vbatt;
        float m_cpu_temp;
        prometheus_t* m__root;
        prometheus_t* m__parent;

    public:
        imu_type_t* imu() const { return m_imu; }
        sun_sensor_type_t* sun_sensor() const { return m_sun_sensor; }
        float vbatt() const { return m_vbatt; }
        float cpu_temp() const { return m_cpu_temp; }
        prometheus_t* _root() const { return m__root; }
        prometheus_t* _parent() const { return m__parent; }
    };

private:
    header_t* m_header;
    uint8_t m_packet_id;
    kaitai::kstruct* m_payload;
    prometheus_t* m__root;
    kaitai::kstruct* m__parent;

public:
    header_t* header() const { return m_header; }
    uint8_t packet_id() const { return m_packet_id; }
    kaitai::kstruct* payload() const { return m_payload; }
    prometheus_t* _root() const { return m__root; }
    kaitai::kstruct* _parent() const { return m__parent; }
};

#endif  // PROMETHEUS_H_