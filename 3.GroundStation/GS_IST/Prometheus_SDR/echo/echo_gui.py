#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Echo Gui
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from gnuradio import zeromq
import echo_gui_epy_block_0 as epy_block_0  # embedded python block
import gnuradio.lora_sdr as lora_sdr
import pmt



from gnuradio import qtgui

class echo_gui(gr.top_block, Qt.QWidget):

    def __init__(self, plutoIP='ip:192.168.2.1'):
        gr.top_block.__init__(self, "Echo Gui", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Echo Gui")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "echo_gui")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Parameters
        ##################################################
        self.plutoIP = plutoIP

        ##################################################
        # Variables
        ##################################################
        self.variable_tag_object_0 = variable_tag_object_0 = gr.tag_utils.python_to_tag((0, pmt.intern("key"), pmt.intern("value"), pmt.intern("src")))
        self.soft_decoding = soft_decoding = True
        self.sf = sf = 9
        self.samp_rate_tx = samp_rate_tx = 250000*4
        self.samp_rate_rx = samp_rate_rx = 250000
        self.pay_len = pay_len = 255
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 2000
        self.cr = cr = 4
        self.center_freq = center_freq = 434000000
        self.carrier_freq = carrier_freq = 436567500
        self.bw = bw = 125000
        self.Att_dB = Att_dB = 0

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_msg_source_0 = zeromq.sub_msg_source('tcp://127.0.0.1:5555', 100, False)
        self.qtgui_sink_x_2 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate_tx*10, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_2.set_update_time(1.0/1000)
        self._qtgui_sink_x_2_win = sip.wrapinstance(self.qtgui_sink_x_2.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_2.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_2_win)
        self.qtgui_edit_box_msg_1 = qtgui.edit_box_msg(qtgui.STRING, '', '', False, True, '', None)
        self._qtgui_edit_box_msg_1_win = sip.wrapinstance(self.qtgui_edit_box_msg_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_edit_box_msg_1_win)
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False)
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate_tx, int(bw/2), [0x12], int(20*2**sf*samp_rate_tx/bw))
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, 2, bw)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, 2, True)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], int(samp_rate_rx/bw))
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, False)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif( True, False)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32(plutoIP if plutoIP else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(center_freq)
        self.iio_pluto_source_0.set_samplerate(samp_rate_rx)
        self.iio_pluto_source_0.set_gain_mode(0, 'slow_attack')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(False)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32(plutoIP if plutoIP else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(250000)
        self.iio_pluto_sink_0.set_frequency(center_freq)
        self.iio_pluto_sink_0.set_samplerate(samp_rate_tx)
        self.iio_pluto_sink_0.set_attenuation(0, 10.0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.epy_block_0 = epy_block_0.my_sync_block()
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,0,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**((Att_dB)/20))
        self.blocks_multiply_const_vxx_0.set_min_output_buffer(10000000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0, 'enable'), (self.blocks_selector_0, 'en'))
        self.msg_connect((self.lora_sdr_crc_verif_0, 'msg'), (self.epy_block_0, 'msg_in'))
        self.msg_connect((self.lora_sdr_crc_verif_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.msg_connect((self.qtgui_edit_box_msg_1, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.lora_sdr_whitening_0, 'msg'))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.qtgui_sink_x_2, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_demap_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_demap_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "echo_gui")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_plutoIP(self):
        return self.plutoIP

    def set_plutoIP(self, plutoIP):
        self.plutoIP = plutoIP

    def get_variable_tag_object_0(self):
        return self.variable_tag_object_0

    def set_variable_tag_object_0(self, variable_tag_object_0):
        self.variable_tag_object_0 = variable_tag_object_0

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_sdr_gray_demap_0.set_sf(self.sf)
        self.lora_sdr_hamming_enc_0.set_sf(self.sf)
        self.lora_sdr_interleaver_0.set_sf(self.sf)
        self.lora_sdr_modulate_0.set_sf(self.sf)

    def get_samp_rate_tx(self):
        return self.samp_rate_tx

    def set_samp_rate_tx(self, samp_rate_tx):
        self.samp_rate_tx = samp_rate_tx
        self.iio_pluto_sink_0.set_samplerate(self.samp_rate_tx)
        self.qtgui_sink_x_2.set_frequency_range(self.center_freq, self.samp_rate_tx*10)

    def get_samp_rate_rx(self):
        return self.samp_rate_rx

    def set_samp_rate_rx(self, samp_rate_rx):
        self.samp_rate_rx = samp_rate_rx
        self.iio_pluto_source_0.set_samplerate(self.samp_rate_rx)

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_frame_period(self):
        return self.frame_period

    def set_frame_period(self, frame_period):
        self.frame_period = frame_period

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr
        self.lora_sdr_hamming_enc_0.set_cr(self.cr)
        self.lora_sdr_header_0.set_cr(self.cr)
        self.lora_sdr_interleaver_0.set_cr(self.cr)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.iio_pluto_sink_0.set_frequency(self.center_freq)
        self.iio_pluto_source_0.set_frequency(self.center_freq)
        self.qtgui_sink_x_2.set_frequency_range(self.center_freq, self.samp_rate_tx*10)

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_Att_dB(self):
        return self.Att_dB

    def set_Att_dB(self, Att_dB):
        self.Att_dB = Att_dB
        self.blocks_multiply_const_vxx_0.set_k(10**((self.Att_dB)/20))



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--plutoIP", dest="plutoIP", type=str, default='ip:192.168.2.1',
        help="Set Pluto IP [default=%(default)r]")
    return parser


def main(top_block_cls=echo_gui, options=None):
    if options is None:
        options = argument_parser().parse_args()

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(plutoIP=options.plutoIP)

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
