import atexit
import logging.config
from flask import Flask, send_from_directory, Response
from recorder import Recorder


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

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('__name__')

app = Flask(__name__)
app.debug = True

video_directory = "/var/www/replaycam/videos/"
recorder = Recorder(framerate=42, resolution=(1296, 972), display_framerate=21, directory=video_directory)
recorder.start_recording()


def cleanup():
    recorder.close()


@app.route('/videos/<path:path>')
def videos(path):
    return send_from_directory(video_directory, path)


@app.route('/save')
def save():
    filename = recorder.save()
    path = "/videos/" + filename
    return Response(path, mimetype='text/plain')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)


atexit.register(cleanup)
