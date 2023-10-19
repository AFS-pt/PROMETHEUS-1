"""
PyCubed Beep-Sat Demo (advanced)
    - improved fault handling & tolerance
    - low power mode
    - logging data to sd card
    - over the air commands


M. Holliday
"""

print('\n{lines}\n{:^40}\n{lines}\n'.format('Beep-Sat Demo',lines='-'*40))

print('Initializing PyCubed Hardware...')
import os, tasko, traceback
from pycubed import pocketqube as cubesat

# create asyncio object
cubesat.tasko=tasko
# Dict to store scheduled objects by name
cubesat.scheduled_tasks={}

print('Loading Tasks...',end='')
# schedule all tasks in directory
for file in os.listdir('Tasks'):
    # remove the '.py' from file name
    file=file[:-3]

    # ignore these files
    if file in ("template_task","test_task","listen_task") or file.startswith('._'):
        continue

    # auto-magically import the task file
    exec('import Tasks.{}'.format(file))
    # create a helper object for scheduling the task
    task_obj=eval('Tasks.'+file).task(cubesat)

    # determine if the task wishes to be scheduled later
    if hasattr(task_obj, 'schedule_later') and getattr(task_obj, 'schedule_later'):
        schedule=cubesat.tasko.schedule_later
    else:
        schedule=cubesat.tasko.schedule

    # schedule each task object and add it to our dict
    cubesat.scheduled_tasks[task_obj.name]=schedule(task_obj.frequency,task_obj.main_task,task_obj.priority)
print(len(cubesat.scheduled_tasks),'total')

print('Running...')
try:
    # should run forever
    cubesat.tasko.run()
except Exception as e:
    formated_exception = traceback.format_exception(e, e, e.__traceback__)
    print(formated_exception)
    try:
        # increment our NVM error counter
        cubesat.c_state_err+=1
        # try to log everything
        cubesat.log('{},{},{}'.format(formated_exception,cubesat.c_state_err,cubesat.c_boot))
    except:
        pass

# we shouldn't be here!
print('Engaging fail safe: hard reset')
# from time import sleep
# sleep(10)
# cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
# cubesat.micro.reset()
