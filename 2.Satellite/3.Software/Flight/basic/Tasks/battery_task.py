# check for low battery condition

from Tasks.template_task import Task

class task(Task):
    priority = 3
    frequency = 1/10 # once every 10s
    name='vbatt'
    color = 'orange'

    async def main_task(self):
        vbatt=self.cubesat.battery_voltage
        comp_var = ''

        if vbatt > self.cubesat.vlowbatt:
            comp_var = '>'
        else:
            comp_var = '<'

        self.debug('{:.1f}V {} threshold: {:.1f}V'.format(vbatt,comp_var,self.cubesat.vlowbatt))
