config = {
    "Normal": {
        "Tasks": {
            "Safety": {
                "Interval": 10,
                "Priority": 3,
                "ScheduleLater": False
            },
            "IMU": {
                "Interval": 10,
                "Priority": 5,
                "ScheduleLater": False
            },
            "Telemetry": {
                "Interval": 30,
                "Priority": 1,
                "ScheduleLater": False
            },
            "Blink": {
                "Interval": 0.2,
                "Priority": 255,
                "ScheduleLater": False
            },
            "Time": {
                "Interval": 20,
                "Priority": 4,
                "ScheduleLater": False
            },
            "GNC": {
                "Interval": 0.1,
                "Priority": 3,
                "ScheduleLater": False
            },
            "Radio": {
                "Interval": 0.01,
                "Priority": 0,
                "ScheduleLater": True
            },
        },
        "StepsTo": [
            "Safe",
        ]
    },
    "Safe": {
        "Tasks": {
            "Safety": {
                "Interval": 15.0,
                "Priority": 1,
                "ScheduleLater": False
            },
            "Blink": {
                "Interval": 1,
                "Priority": 255,
                "ScheduleLater": False
            },
        },
        "StepsTo": [
            "Normal",
            "Deployment"
        ],
        "EnterFunctions": [
            "Announcer",
            "LowPowerOn"
        ],
        "ExitFunctions": [
            "Announcer",
            "LowPowerOff"
        ]
    },
    "Deployment": {
        "Tasks": {
            "Radio": {
                "Interval": 30.0,
                "Priority": 3,
                "ScheduleLater": False
            },
            "DeploymentManager": {
                "Interval": 5.0,
                "Priority": 1,
                "ScheduleLater": False
            },
            "Blink": {
                "Interval": 0.2,
                "Priority": 255,
                "ScheduleLater": False
            },
        },
        "StepsTo": [
            "Normal",
            "Safe"
        ]
    }
}

initial = "Deployment"
