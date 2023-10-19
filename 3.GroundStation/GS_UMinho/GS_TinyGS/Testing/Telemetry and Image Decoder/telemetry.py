import struct
import decoder

packetID = 0x00

headerFormat = 'B'*4
imuFormat = 'f'*10
sunFormat = 'H'*6
vbattFormat = 'f'
cputempFormat = 'f'
telemetryFormat = imuFormat + sunFormat + vbattFormat + cputempFormat

# HEADER
destination, node, identifier, flags = 0xab, 0xba, 0x01, 0x00
header = struct.pack(headerFormat, destination, node, identifier, flags)


# IMU
accelX, accelY, accelZ = -0.5435, 1.3647, 9.9240
gyroX, gyroY, gyroZ = -0.1984, 0.5341, -0.0153
magX, magY, magZ = 24.5625, 31.5625, -18.8125
imu_temp = 29.3340
imu = struct.pack(imuFormat, accelX, accelY, accelZ, gyroX, gyroY, gyroZ, magX, magY, magZ, imu_temp)
print('imu: ', imu)

sunXP, sunYP, sunZP = 11, 12, 13
sunXN, sunYN, sunZN = 21, 22, 23
sun_sensors = struct.pack(sunFormat, sunXN, sunYN, sunZN, sunXP, sunYP, sunZP)
print('sun: ', sun_sensors)

vbatt = 4.2

cpu_temp = 30.4

#telemetry = struct.pack('ssff', imu, sun_sensors, vbatt, cpu_temp)

#data = prometheus.Prometheus.Telemetry.from_bytes(telemetry)
imuStruct = struct.Struct(imuFormat)
sunStruct = struct.Struct(sunFormat)
payloadStruct = struct.Struct('{}s'.format(imuStruct.size) + '{}s'.format(sunStruct.size) + 'ff')
payload = payloadStruct.pack(imu, sun_sensors, vbatt, cpu_temp)
headerStruct = struct.Struct(headerFormat)
packetStruct = struct.Struct('{}s'.format(headerStruct.size) + 'B' + '{}s'.format(payloadStruct.size))
packetTX = packetStruct.pack(header, packetID, payload)

print('PACKET: ', packetTX)


##########################################################################################
#                   TRANSMISSION TO GROUNDSTATION ...
##########################################################################################

packetRX = decoder.Prometheus.from_bytes(packetTX)

print(packetRX.payload.imu.temp)
