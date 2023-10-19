from Tasks.battery_task import task as battery
from Tasks.time_task import task as time
from Tasks.every_5_seconds import task as every5
from Tasks.transition_task import task as transition

from TransitionFunctions import announcer

from config import config  # noqa: F401

TaskMap = {
    'Battery': battery,
    'Transition': transition,
    'Time': time,
    'Every5Seconds': every5,
}

TransitionFunctionMap = {
    'Announcer': announcer
}
