#!/usr/bin/python3
import atexit
import config
import logging.config
from flask import Flask, send_from_directory, Response
from replay_recorder import ReplayRecorder


logging.config.dictConfig(config.LOGGING)
logger = logging.getLogger('__name__')

app = Flask(__name__)

recorder = ReplayRecorder(**config.RECORDER_CONFIG)
recorder.start_recording()
atexit.register(recorder.close)


@app.route('/videos/<path:path>')
def videos(path):
    return send_from_directory(config.VIDEO_DIRECTORY, path)


@app.route('/save')
def save():
    filename = recorder.save()
    path = "/videos/" + filename
    return Response(path, mimetype='text/plain')


if __name__ == "__main__":
    app.run(host=config.INTERFACE, port=config.PORT)
