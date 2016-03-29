LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s(%(module)s): %(message)s'
        },
    },

    'handlers': {
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'filename': '/var/logs/replaycam.log',
        #     'formatter': 'verbose',
        # },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'ext://sys.stderr'
        },
    },

    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    }
}

VIDEO_DIRECTORY = "/var/www/replaycam/videos/"

# See https://picamera.readthedocs.org/en/release-1.10/fov.html for possible Raspberry Pi Camera settings
RECORDER_CONFIG = {
    "framerate": 42,
    "resolution": (1296, 972),
    "display_framerate": 21,
    "directory": VIDEO_DIRECTORY,
    "bitrate": int(9e6),
    "seconds": 5,
}

INTERFACE = "0.0.0.0"
PORT = 80
