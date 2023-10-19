from lib.template_task import Task
from pycubed import cubesat
import logs
import files
import traceback
import time

class LogTask(Task):

    def debug(self, msg, level=1, log=False):
        """
        Print a debug message formatted with the task name and color.
        Also log the message to a log file if log is set to True.

        :param msg: Debug message to print
        :type msg: str
        :param level: > 1 will print as a sub-level
        :type level: int
        :param log: Whether to log the message to a file
        :type log: bool
        """
        msg = super().debug(msg, level)
        if cubesat.sdcard and log:
            try:
                self.log(msg)
            except Exception as e:
                # shouldn't call self.debug to prevent never ending loop
                super().debug(f'Error logging to file: {e}', 1)

    def log(self, msg):
        """
        Log a message to a log file.
        """
        if cubesat.rtc:
            t = cubesat.rtc.datetime
        else:
            t = time.localtime()
        boot_str = f'{cubesat.c_boot:05}'
        hour_stamp = f'{t.tm_year:04}.{t.tm_mon:02}.{t.tm_mday:02}.{t.tm_hour:02}'
        log_fd_path_str = f'/sd/logs/debug/{boot_str}'
        log_fd_str = f'{log_fd_path_str}/{hour_stamp}.txt'
        try:
            log_fd = open(log_fd_str, 'a')
        except Exception:
            files.mkdirp(log_fd_path_str)
            log_fd = open(log_fd_str, 'a')

        log_fd.write(f'[{logs.human_time_stamp(t)}]\n')
        log_fd.write(msg)
        log_fd.write('\n')
        log_fd.close()

    async def handle_error(self, error):
        """
        Called when an error is raised in the task.
        Logs it to the debug logs.
        """
        try:
            formated_exception = traceback.format_exception(error, error, error.__traceback__)
            self.debug(f'[Error] {formated_exception}', log=True)
            cubesat.c_software_error += 1
        except Exception:
            pass
