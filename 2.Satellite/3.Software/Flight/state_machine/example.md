# Example Explanation

Build and Run: `sh build.sh drivers/example applications/example && sh run.sh`

The example "flight" software contains an extremely simple state machine with two states called "Normal" and "Special". Both states have their own tasks that run, with a few tasks shared among the two. 

![State machine diagram going to and from Normal and Special mode](./example.png)

## drivers/example/lib/pycubed.py

Bare bones emulation of a sattelite, so that we can get "voltage" readings.
In a real driver this would be much more complex emulation, or the real pycubed driver.

## applications/example/StateMachineConfig.py

Contains the config which defines the following.
1. Which states exist
2. Which tasks run for each state, along with the following properties
    1. The interval at which they are run
    2. Their priority
    3. If they are to be "ScheduledLater" or run immediately when entering the state. 
3. Which transitions are allowed
4. Which functions are run whenever entering an exiting a state (note that the current state, future state, and cubesat is passed to these functions)
5. The TaskMap which maps task names (strings) to their coresponding objects
6. The TransitionFunctionMap which maps names (strings) to their coresponding functions

## applications/example/TransitionFunctions.py

Contains the transition functions which take the origin, destination and a reference to the cubesat object. In the case of the example, it just anounces the transition.

## applications/example/Tasks/battery_task.py

This reads the "battery_voltage" and prints it to the console.

## applications/example/Tasks/every_5_seconds.py

This task runs every 5 seconds, and prints to the console.

## applications/example/Tasks/time_task.py

This task gets and prints the current uptime

## applications/example/Tasks/transition_task.py

This task switches the state between Normal and Special mode.
In the state machine config, we set it to run later so that it runs in 20 or 15 seconds depending on the state.

