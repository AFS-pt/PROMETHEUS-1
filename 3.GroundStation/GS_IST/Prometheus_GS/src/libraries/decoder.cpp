// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

#include "decoder.h"

prometheus_t::prometheus_t(kaitai::kstream* p__io, kaitai::kstruct* p__parent, prometheus_t* p__root) : kaitai::kstruct(p__io) {
    m__parent = p__parent;
    m__root = this;
    m_header = 0;

    try {
        _read();
    } catch(...) {
        _clean_up();
        throw;
    }
}

void prometheus_t::_read() {
    m_header = new header_t(m__io, this, m__root);
    m_packet_id = m__io->read_u1();
    switch (packet_id()) {
    case 0: {
        m_payload = new telemetry_t(m__io, this, m__root);
        break;
    }
    default: {
        m_payload = new image_t(m__io, this, m__root);
        break;
    }
    }
}

prometheus_t::~prometheus_t() {
    _clean_up();
}

void prometheus_t::_clean_up() {
    if (m_header) {
        delete m_header; m_header = 0;
    }
    if (m_payload) {
        delete m_payload; m_payload = 0;
    }
}

prometheus_t::sun_sensor_type_t::sun_sensor_type_t(kaitai::kstream* p__io, prometheus_t::telemetry_t* p__parent, prometheus_t* p__root) : kaitai::kstruct(p__io) {
    m__parent = p__parent;
    m__root = p__root;

    try {
        _read();
    } catch(...) {
        _clean_up();
        throw;
    }
}

void prometheus_t::sun_sensor_type_t::_read() {
    m_sun_xn = m__io->read_u2le();
    m_sun_yn = m__io->read_u2le();
    m_sun_zn = m__io->read_u2le();
    m_sun_xp = m__io->read_u2le();
    m_sun_yp = m__io->read_u2le();
    m_sun_zp = m__io->read_u2le();
}

prometheus_t::sun_sensor_type_t::~sun_sensor_type_t() {
    _clean_up();
}

void prometheus_t::sun_sensor_type_t::_clean_up() {
}

prometheus_t::image_t::image_t(kaitai::kstream* p__io, prometheus_t* p__parent, prometheus_t* p__root) : kaitai::kstruct(p__io) {
    m__parent = p__parent;
    m__root = p__root;

    try {
        _read();
    } catch(...) {
        _clean_up();
        throw;
    }
}

void prometheus_t::image_t::_read() {
    m_total = m__io->read_u1();
    m_segment = m__io->read_bytes(249);
}

prometheus_t::image_t::~image_t() {
    _clean_up();
}

void prometheus_t::image_t::_clean_up() {
}

prometheus_t::header_t::header_t(kaitai::kstream* p__io, prometheus_t* p__parent, prometheus_t* p__root) : kaitai::kstruct(p__io) {
    m__parent = p__parent;
    m__root = p__root;

    try {
        _read();
    } catch(...) {
        _clean_up();
        throw;
    }
}

void prometheus_t::header_t::_read() {
    m_destination = m__io->read_u1();
    m_node = m__io->read_u1();
    m_identifier = m__io->read_u1();
    m_flags = m__io->read_u1();
}

prometheus_t::header_t::~header_t() {
    _clean_up();
}

void prometheus_t::header_t::_clean_up() {
}

prometheus_t::imu_type_t::imu_type_t(kaitai::kstream* p__io, prometheus_t::telemetry_t* p__parent, prometheus_t* p__root) : kaitai::kstruct(p__io) {
    m__parent = p__parent;
    m__root = p__root;

    try {
        _read();
    } catch(...) {
        _clean_up();
        throw;
    }
}

void prometheus_t::imu_type_t::_read() {
    m_accel_x = m__io->read_f4le();
    m_accel_y = m__io->read_f4le();
    m_accel_z = m__io->read_f4le();
    m_gyro_x = m__io->read_f4le();
    m_gyro_y = m__io->read_f4le();
    m_gyro_z = m__io->read_f4le();
    m_mag_x = m__io->read_f4le();
    m_mag_y = m__io->read_f4le();
    m_mag_z = m__io->read_f4le();
    m_temp = m__io->read_f4le();
}

prometheus_t::imu_type_t::~imu_type_t() {
    _clean_up();
}

void prometheus_t::imu_type_t::_clean_up() {
}

prometheus_t::telemetry_t::telemetry_t(kaitai::kstream* p__io, prometheus_t* p__parent, prometheus_t* p__root) : kaitai::kstruct(p__io) {
    m__parent = p__parent;
    m__root = p__root;
    m_imu = 0;
    m_sun_sensor = 0;

    try {
        _read();
    } catch(...) {
        _clean_up();
        throw;
    }
}

void prometheus_t::telemetry_t::_read() {
    m_imu = new imu_type_t(m__io, this, m__root);
    m_sun_sensor = new sun_sensor_type_t(m__io, this, m__root);
    m_vbatt = m__io->read_f4le();
    m_cpu_temp = m__io->read_f4le();
}

prometheus_t::telemetry_t::~telemetry_t() {
    _clean_up();
}

void prometheus_t::telemetry_t::_clean_up() {
    if (m_imu) {
        delete m_imu; m_imu = 0;
    }
    if (m_sun_sensor) {
        delete m_sun_sensor; m_sun_sensor = 0;
    }
}
