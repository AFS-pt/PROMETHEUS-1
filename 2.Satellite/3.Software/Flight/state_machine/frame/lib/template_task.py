from lib.debugcolor import co
from state_machine import state_machine
import traceback


class Task:

    """
    Template task object.
    Stores the task name and color.
    """

    name = 'temp'
    color = 'gray'

    def __init__(self):
        """
        Initialize the Task
        """
        pass

    def debug(self, msg, level=1):
        """
        Print a debug message formatted with the task name and color

        :param msg: Debug message to print
        :type msg: str
        :param level: > 1 will print as a sub-level
        :type level: int
        """
        if level == 1:
            header = f"[{co(msg=self.name,color=self.color)}/{state_machine.state}]"
            msg = f"{header:>35} {msg}"
        else:
            msg = "\t" + f"{'   └── '}{msg}"
        print(msg)
        return msg

    async def main_task(self, *args, **kwargs):
        """
        Contains the code for the user defined task.

        :param `*args`: Variable number of arguments used for task execution.
        :param `**kwargs`: Variable number of keyword arguments used for task execution.
        """
        pass

    async def _run(self):
        """
        Try to run the main task, then call handle_error if an error is raised.
        """
        try:
            await self.main_task()
        except Exception as e:
            await self.handle_error(e)

    async def handle_error(self, error):
        """
        Called when an error is raised in the task.
        """
        formated_exception = traceback.format_exception(error, error, error.__traceback__)
        self.debug(f'[Error] {formated_exception}')
