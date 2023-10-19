import struct, decoder


with open("image.png", "rb") as file:
  image = bytearray(file.read())

print(len(image))

segment_length = 251
total_segments = int(len(image)/segment_length)+1

print(total_segments)

image_segments = []

for i in range(total_segments):
    start = i*segment_length
    end = (i+1)*segment_length
    segment = image[start : end]
    #print('SEGMENT ', i, ': ', segment)
    image_segments.append(segment)


headerFormat = 'B'*4

packets = []
for i in range(total_segments):
    destination, node, identifier, flags = 0xab, 0xba, 0x01, 0x00
    header = struct.pack(headerFormat, destination, node, identifier, flags)
    headerStruct = struct.Struct(headerFormat)
    packetID = i+1
    payloadStruct = struct.Struct('{}s'.format(segment_length))
    payload = payloadStruct.pack(image_segments[i])
    packetStruct = struct.Struct('{}s'.format(headerStruct.size) + 'B' + '{}s'.format(payloadStruct.size))
    packetTx = packetStruct.pack(header, packetID, payload)

    packets.append(packetTx)


##########################################################################################
#                   TRANSMISSION TO GROUNDSTATION ...
##########################################################################################

data = []
for pkt in packets:
    p = decoder.Prometheus.from_bytes(pkt)
    data.append(p.payload.segment)
    print(p.packet_id)

img = b''.join(data)

print(bytearray(img))
print(image)

with open("result.png", "wb") as file:
    file.write(img)
