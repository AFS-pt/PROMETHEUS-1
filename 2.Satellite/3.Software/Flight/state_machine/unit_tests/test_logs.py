import unittest
import sys
from numpy import testing, array
import time

sys.path.insert(0, './state_machine/drivers/emulation')
sys.path.insert(0, './state_machine/drivers/emulation/lib')
sys.path.insert(0, './state_machine/applications/flight')
sys.path.insert(0, './state_machine/frame')

from lib.logs import telemetry_packet, unpack_telemetry
from pycubed import cubesat
from state_machine import state_machine

class TestLogs(unittest.TestCase):

    def test(self):

        mag_in = array([4.0, 3.0, 1.0])
        gyro_in = array([-42.0, 0.1, 7.0])

        cpu_temp_in = 77
        imu_temp_in = 22

        boot_count_in = 453
        f_contact_in = True
        f_burn_in = False
        error_count_in = 13
        vbatt_in = 3.45

        rssi_in = -88.8
        fei_in = -987.0

        state_machine.states = [1, 2, 3, 4]
        state_machine.state = 2
        state_in = state_machine.states.index(state_machine.state)

        lux_xp_in = 12.3
        lux_yp_in = 0.2
        lux_zp_in = 5.0

        lux_xn_in = 6.0
        lux_yn_in = 8.1
        lux_zn_in = 2.0

        time_in = time.localtime()
        tm_min_in = time_in.tm_min
        tm_sec_in = time_in.tm_sec

        cubesat.f_contact = f_contact_in
        cubesat.f_burn = f_burn_in
        cubesat.c_software_error = error_count_in

        cubesat.c_boot = boot_count_in
        cubesat.LOW_VOLTAGE = vbatt_in
        cubesat.randomize_voltage = False

        cubesat._mag = mag_in
        cubesat._gyro = gyro_in
        cubesat._cpu_temp = cpu_temp_in
        cubesat._imu_temperature = imu_temp_in

        cubesat.radio._last_rssi = rssi_in
        cubesat.radio._frequency_error = fei_in

        cubesat._luxp = array([lux_xp_in, lux_yp_in, lux_zp_in])
        cubesat._luxn = array([lux_xn_in, lux_yn_in, lux_zn_in])

        pkt = telemetry_packet(time_in)

        unpacked = unpack_telemetry(pkt)

        """Tests Time Values"""
        self.assertEqual(tm_min_in, unpacked.time.tm_min)
        self.assertEqual(tm_sec_in, unpacked.time.tm_sec)

        """Tests Beacon Values"""
        self.assertEqual(state_in, unpacked.beacon.state_index)
        self.assertEqual(f_contact_in, unpacked.beacon.contact_flag)
        self.assertEqual(f_burn_in, unpacked.beacon.burn_flag)
        self.assertEqual(error_count_in, unpacked.beacon.software_error_count)
        self.assertEqual(boot_count_in, unpacked.beacon.boot_count)
        self.assertAlmostEqual(vbatt_in + 0.01, unpacked.beacon.battery_voltage, places=5)
        self.assertAlmostEqual(cpu_temp_in, unpacked.beacon.cpu_temperature_C, places=5)
        self.assertAlmostEqual(imu_temp_in, unpacked.beacon.imu_temperature_C, places=5)
        self.assertAlmostEqual(rssi_in, unpacked.beacon.RSSI_dB, places=5)
        self.assertAlmostEqual(fei_in, unpacked.beacon.FEI_Hz, places=5)
        testing.assert_array_almost_equal(gyro_in, unpacked.beacon.gyro)
        testing.assert_array_almost_equal(mag_in, unpacked.beacon.mag)

        """Tests System values"""
        self.assertAlmostEqual(lux_xp_in, unpacked.system.lux_xp, places=5)
        self.assertAlmostEqual(lux_yp_in, unpacked.system.lux_yp, places=5)
        self.assertAlmostEqual(lux_zp_in, unpacked.system.lux_zp, places=5)
        self.assertAlmostEqual(lux_xn_in, unpacked.system.lux_xn, places=5)
        self.assertAlmostEqual(lux_yn_in, unpacked.system.lux_yn, places=5)
        self.assertAlmostEqual(lux_zn_in, unpacked.system.lux_zn, places=5)
