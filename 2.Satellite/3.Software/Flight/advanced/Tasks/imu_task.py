# Task to obtain IMU sensor readings

from Tasks.template_task import Task
import msgpack
import os
from os import stat

SEND_DATA = False # make sure you have an antenna attached!

class task(Task):
    priority = 5
    frequency = 1/10 # once every 10s
    name='imu'
    color = 'green'
    data_file = None

    # we want to initialize the data file only once upon boot
    # so perform our task init and use that as a chance to init the data files
    def __init__(self,satellite):
        super().__init__(satellite)
        self.data_file=self.cubesat.new_file('/data/imu',binary=True)

    async def main_task(self):
        # take IMU readings
        readings = {
            'accel':self.cubesat.acceleration,
            'mag':  self.cubesat.magnetic,
            'gyro': self.cubesat.gyro,
        }

        # store them in our cubesat data_cache object
        self.cubesat.data_cache.update({'imu':readings})

        # print the readings with some fancy formatting
        self.debug('IMU readings (x,y,z)')
        for imu_type in self.cubesat.data_cache['imu']:
            self.debug('{:>5} {}'.format(imu_type,self.cubesat.data_cache['imu'][imu_type]),2)

        # save data to the sd card, but only if we have a proper data file
        if self.data_file is not None:
            # save our readings using msgpack
            with open(self.data_file,'ab') as f:
                msgpack.pack(readings,f)
            # check if the file is getting bigger than we'd like
            if stat(self.data_file)[6] >= 256: # bytes
                if SEND_DATA:
                    print('\nSend IMU data file: {}'.format(self.data_file))
                    with open(self.data_file,'rb') as f:
                        chunk = f.read(64) # each IMU readings is 64 bytes when encoded
                        while chunk:
                            # we could send bigger chunks, radio packet can take 252 bytes
                            self.cubesat.radio1.send(chunk)
                            print(chunk)
                            chunk = f.read(64)
                    print('finished\n')
                else:
                    # print the unpacked data from the file
                    print('\nPrinting IMU data file: {}'.format(self.data_file))
                    with open(self.data_file,'rb') as f:
                        while True:
                            try: print('\t',msgpack.unpack(f))
                            except: break
                    print('finished\n')
                # increment our data file number
                self.data_file=self.cubesat.new_file('/data/imu')


