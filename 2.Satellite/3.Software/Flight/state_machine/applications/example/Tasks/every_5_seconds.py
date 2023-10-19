from lib.template_task import Task


class task(Task):
    name = 'every5'
    color = 'pink'

    async def main_task(self):
        self.debug('This task runs every 5 seconds')
