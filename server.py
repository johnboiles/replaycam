import io
import signal
import recorder
from flask import Flask, request, send_from_directory, Response

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

recorder_handler = recorder.Recorder()
recorder_thread = None
host = "http://10.0.0.58"


@app.route('/videos/<path:path>')
def videos(path):
    return send_from_directory('videos', path)


@app.route('/save')
def save():
    filename = recorder_handler.save()
    path = host + "/videos/" + filename
    return Response(path , mimetype='text/plain')


def cleanup():
    recorder_handler.stop()
    recorder_thread.stop()


if __name__ == "__main__":
    recorder_thread = recorder.StoppableThread(target=recorder_handler.loop)
    recorder_thread.daemon = True
    recorder_thread.start()

    app.run(host='0.0.0.0', port=80)

    cleanup()
