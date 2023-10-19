meta:
  id: prometheus
  file-extension: prometheus
  endian: le
  
seq:
  - id: header
    type: header
  - id: payload
    type: payload

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
  payload:
    seq:
      - id: imu
        type: imu_type

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

    
