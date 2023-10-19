# check for low battery condition

from Tasks.template_task import Task
import time

class task(Task):
    priority = 3
    frequency = 1/10 # once every 10s
    name='vbatt'
    color = 'orange'

    timeout=60*60 # 60 min

    async def main_task(self):
        vbatt=self.cubesat.battery_voltage
        comp_var = ''

        if vbatt > self.cubesat.vlowbatt:
            comp_var = '>'
        else:
            comp_var = '<'

        self.debug('{:.1f}V {} threshold: {:.1f}V'.format(vbatt,comp_var,self.cubesat.vlowbatt))

        ########### ADVANCED ###########
        # respond to a low power condition
        if comp_var == '<':
            self.cubesat.f_lowbatt=True
            # if we've timed out, don't do anything
            if self.cubesat.f_lowbtout:
                self.debug('lowbatt timeout flag set! skipping...')
            else:
                _timer=time.monotonic()+self.timeout
                self.debug('low battery detected!',2)
                # stop all tasks
                for t in self.cubesat.scheduled_tasks:
                    self.cubesat.scheduled_tasks[t].stop()

                self.cubesat.powermode('minimum')
                while time.monotonic() < _timer:
                    # sleep for half our remaining time
                    _sleeptime = self.timeout/10
                    self.debug('sleeping for {}s'.format(_sleeptime),2)
                    time.sleep(_sleeptime)
                    self.debug('vbatt: {:.1f}V'.format(self.cubesat.battery_voltage),2)
                    vbatt=self.cubesat.battery_voltage
                    if vbatt > self.cubesat.vlowbatt:
                        self.debug('batteries above threshold',2)
                        self.cubesat.f_lowbatt=False
                        break

                    if time.monotonic() > _timer:
                        self.debug('low batt timeout!',2)
                        # set timeout flag so we know to bypass
                        self.cubesat.f_lowbtout = True
                        # log (if we can)
                        try: self.cubesat.log('low batt timeout',2)
                        except: pass
                        break

                self.debug('waking up')
                # always wake up
                self.cubesat.powermode('normal')
                # give everything a moment to power up
                time.sleep(3)
                # restart all tasks
                for t in self.cubesat.scheduled_tasks:
                    self.cubesat.scheduled_tasks[t].start()

