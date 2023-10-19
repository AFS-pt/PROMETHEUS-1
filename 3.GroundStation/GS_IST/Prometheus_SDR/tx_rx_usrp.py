#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Usrp
# Author: Tapparel Joachim@EPFL,TCL
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import gnuradio.lora_sdr as lora_sdr




class tx_rx_usrp(gr.top_block):

    def __init__(self, plutoIP='ip:192.168.2.1'):
        gr.top_block.__init__(self, "Tx Rx Usrp", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.plutoIP = plutoIP

        ##################################################
        # Variables
        ##################################################
        self.soft_decoding = soft_decoding = True
        self.sf = sf = 10
        self.samp_rate_tx = samp_rate_tx = 250000
        self.samp_rate_rx = samp_rate_rx = 250000
        self.pay_len = pay_len = 255
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 2000
        self.cr = cr = 2
        self.center_freq = center_freq = 868100000
        self.bw = bw = 125000
        self.Att_dB = Att_dB = 0

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False)
        self.lora_sdr_payload_id_inc_0 = lora_sdr.payload_id_inc(':')
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate_tx, bw, [0x12], int(20*2**sf*samp_rate_tx/bw))
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, 2, 125000)
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
        self.iio_pluto_source_0.set_bbdc(False)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32(plutoIP if plutoIP else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(250000)
        self.iio_pluto_sink_0.set_frequency(center_freq)
        self.iio_pluto_sink_0.set_samplerate(samp_rate_tx)
        self.iio_pluto_sink_0.set_attenuation(0, 10.0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**((Att_dB)/20))
        self.blocks_multiply_const_vxx_0.set_min_output_buffer(10000000)
        self.blocks_message_strobe_0_0_0 = blocks.message_strobe(pmt.intern("Hello world: 0"), frame_period)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0_0_0, 'strobe'), (self.lora_sdr_payload_id_inc_0, 'msg_in'))
        self.msg_connect((self.blocks_message_strobe_0_0_0, 'strobe'), (self.lora_sdr_whitening_0, 'msg'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.msg_connect((self.lora_sdr_payload_id_inc_0, 'msg_out'), (self.blocks_message_strobe_0_0_0, 'set_msg'))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.lora_sdr_frame_sync_0, 0))
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


    def get_plutoIP(self):
        return self.plutoIP

    def set_plutoIP(self, plutoIP):
        self.plutoIP = plutoIP

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
        self.blocks_message_strobe_0_0_0.set_period(self.frame_period)

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


def main(top_block_cls=tx_rx_usrp, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(plutoIP=options.plutoIP)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
