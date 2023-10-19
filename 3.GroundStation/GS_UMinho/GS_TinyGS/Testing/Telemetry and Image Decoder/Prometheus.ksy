meta:
  id: prometheus
  file-extension: prometheus
  endian: le
  
seq:
  - id: header
    type: header
  - id: packet_id
    type: u1
  - id: payload
    type:
      switch-on: packet_id
      cases:
        0x00: telemetry
        _: image
        
types:
  header:
    seq:
      - id: destination
        size: 1
      - id: node
        size: 1
      - id: identifier
        size: 1
      - id: flags
        size: 1

  telemetry: 
    seq:
      - id: imu
        type: imu_type
      - id: sun_sensor
        type: sun_sensor_type
      - id: vbatt
        type: f4
      - id: cpu_temp
        type: f4

  imu_type:
    seq:
      - id: accel_x
        type: f4
      - id: accel_y
        type: f4
      - id: accel_z
        type: f4
      - id: gyro_x
        type: f4
      - id: gyro_y
        type: f4
      - id: gyro_z
        type: f4
      - id: mag_x
        type: f4
      - id: mag_y
        type: f4
      - id: mag_z
        type: f4
      - id: temp
        type: f4

  sun_sensor_type:
    seq:
      - id: sun_xn
        type: u2
      - id: sun_yn
        type: u2
      - id: sun_zn
        type: u2
      - id: sun_xp
        type: u2
      - id: sun_yp
        type: u2
      - id: sun_zp
        type: u2
  

  image: 
    seq:
      - id: segment
        size: 251
  