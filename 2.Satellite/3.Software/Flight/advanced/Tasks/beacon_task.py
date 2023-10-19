# Transmit "Hello World" beacon

from Tasks.template_task import Task
import cdh

ANTENNA_ATTACHED = False

class task(Task):
    priority = 1
    frequency = 1/30 # once every 30s
    name='beacon'
    color = 'teal'

    schedule_later = True

    # our 4 byte code to authorize commands
    # pass-code for DEMO PURPOSES ONLY
    super_secret_code = b'p\xba\xb8C'

    cmd_dispatch = {
        'no-op':        cdh.noop,
        'hreset':       cdh.hreset,
        'shutdown':     cdh.shutdown,
        'query':        cdh.query,
        'exec_cmd':     cdh.exec_cmd,
    }

    def __init__(self,satellite):
        super().__init__(satellite)
        # set our radiohead node ID so we can get ACKs
        self.cubesat.radio.node = 0xFA # our ID
        self.cubesat.radio.destination = 0xAB # target's ID

    async def main_task(self):
        """
        If you've attached a 433MHz antenna,
        set the above ANTENNA_ATTACHED variable to True
        to actually send the beacon packet
        """
        if ANTENNA_ATTACHED:
            self.debug("Sending beacon")
            self.cubesat.radio.send("Hello World!",destination=0xFF,keep_listening=True)
        else:
            # Fake beacon since we don't know if an antenna is attached
            print() # blank line
            self.debug("[WARNING]")
            self.debug("NOT sending beacon (unknown antenna state)",2)
            self.debug("If you've attached an antenna, edit '/Tasks/beacon_task.py' to actually beacon", 2)
            print() # blank line
            self.cubesat.radio.listen()

        self.debug("Listening 10s for response (non-blocking)")
        heard_something = await self.cubesat.radio.await_rx(timeout=10)

        if heard_something:
            # retrieve response but don't ACK back unless an antenna is attached
            response = self.cubesat.radio.receive(keep_listening=True,with_ack=ANTENNA_ATTACHED)
            if response is not None:
                self.debug("packet received")
                self.debug('msg: {}, RSSI: {}'.format(response,self.cubesat.radio.last_rssi-137),2)
                self.cubesat.c_gs_resp+=1

                """
                ########### ADVANCED ###########
                Over-the-air commands
                See beep-sat guide for more details
                """
                if len(response) >= 6:
                    if not ANTENNA_ATTACHED:
                        self.debug('Antenna not attached. Skipping over-the-air command handling')
                    else:
                        if response[:4]==self.super_secret_code:
                            cmd=bytes(response[4:6]) # [pass-code(4 bytes)] [cmd 2 bytes] [args]
                            cmd_args=None
                            if len(response) > 6:
                                self.debug('command with args',2)
                                try:
                                    cmd_args=response[6:] # arguments are everything after
                                    self.debug('cmd args: {}'.format(cmd_args),2)
                                except Exception as e:
                                    self.debug('arg decoding error: {}'.format(e),2)
                            if cmd in cdh.commands:
                                try:
                                    if cmd_args is None:
                                        self.debug('running {} (no args)'.format(cdh.commands[cmd]))
                                        self.cmd_dispatch[cdh.commands[cmd]](self)
                                    else:
                                        self.debug('running {} (with args: {})'.format(cdh.commands[cmd],cmd_args))
                                        self.cmd_dispatch[cdh.commands[cmd]](self,cmd_args)
                                except Exception as e:
                                    self.debug('something went wrong: {}'.format(e))
                                    self.cubesat.radio.send(str(e).encode())
                            else:
                                self.debug('invalid command!')
                                self.cubesat.radio.send(b'invalid cmd'+response[4:])
        else:
            self.debug('no messages')
        self.cubesat.radio.sleep()
        self.debug('finished')


