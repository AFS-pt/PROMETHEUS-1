import unittest
import sys

sys.path.insert(0, './state_machine/frame')

from lib.state_machine_utils import validate_config

basicTM = {
    't1': True,
    't2': True,
    't3': True,
}

basicTFM = {
    'tf1': True,
    'tf2': True,
}


tests = [
    {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'Normal': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't2': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't3': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['LowPower', 'DeTumble'],
                'EnterFunctions': ['tf1'],
                'ExitFunctions': ['tf2'],
            },
            'LowPower': {
                'Tasks': {
                    't3': {
                        'Interval': 15.0,
                        'Priority': 1,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal'],
            },
            'DeTumble': {
                'Tasks': {
                    't2': {
                        'Interval': 15.0,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal'],
            }
        },
        'Valid': True,
        'Title': 'Large Correct Config',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'Normal': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't2': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't3': {
                        'Interval': 10,
                        'Priorty': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['LowPower', 'DeTumble'],
                'EnterFunctions': ['tf1'],
                'ExitFunctions': ['tf2'],
            },
            'LowPower': {
                'Tasks': {
                    't3': {
                        'Interval': 15.0,
                        'Priority': 1,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal']
            },
            'DeTumble': {
                'Tasks': {
                    't2': {
                        'Interval': 15.0,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal'],
            }
        },
        'Valid': False,
        'Title': 'Large Incorrect Config (Normal->t3 Priority mispelled)',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': True,
        'Title': 'Small Correct Config',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't5': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'Wrong task name (t5 instead of t1/t2/t3)',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Task': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'Task instead of Tasks',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepTo': [],
            },
        },
        'Valid': False,
        'Title': 'StepTo instead of StepsTo',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
                'ExitFunction': [],
            },
        },
        'Valid': False,
        'Title': 'N->ExitFunction instead of N->ExitFunctions',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
                'EnterFunction': [],
            },
        },
        'Valid': False,
        'Title': 'N->EnterFunction instead of N->EnterFunctions',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {},
                'StepsTo': [],
                'EnterFunctions': [],
                'ExitFunctions': [],
            },
        },
        'Valid': True,
        'Title': 'Valid Taskless Config',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interva': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'N->Tasks->t1->Interva instead of N->Tasks->t1->Interval',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priorit': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'N->Tasks->t1->Priorit instead of N->Tasks->t1->Priority',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['ThisStateDoesNotExist'],
            },
        },
        'Valid': False,
        'Title': 'Invalid Transition Defined',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': "N",
            },
        },
        'Valid': False,
        'Title': 'Wrong type for N->StepsTo',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': "10",
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'Wrong Type For N->Tasks->t1->Interval',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': "3",
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'Wrong Type For N->Tasks->t1->Priority',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': "Yes"
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'Wrong Type For N->Tasks->t1->ScheduleLater',
    },
]


class TestValidateConfig(unittest.TestCase):

    def test(self):
        for v in tests:
            try:
                validate_config(v['config'], v['TaskMap'], v['TransitionFunctionMap'])
            except ValueError as err:
                self.assertTrue(not v['Valid'], msg=f'{v["Title"]} should have no error, but it raised error: {err}')
                continue
            self.assertTrue(v['Valid'], msg=f'{v["Title"]} should have raised an error')
