import picamera
import time
import threading
import subprocess
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AVConvException(Exception):
    pass


class Recorder(object):
    camera = None
    stream = None

    def __init__(self, framerate=90, resolution=(640, 480), display_framerate=30, directory="videos/", bitrate=1700000, seconds=8):
        self.framerate = framerate
        self.display_framerate = display_framerate
        self.resolution = resolution
        self.directory = directory
        self.bitrate = bitrate
        self.seconds = seconds
        self.lock = threading.Lock()

    def start_recording(self):
        self.camera = picamera.PiCamera(resolution=self.resolution, framerate=self.framerate)
        self.stream = picamera.PiCameraCircularIO(self.camera, seconds=self.seconds, bitrate=self.bitrate)
        self._start_recording()

    def _start_recording(self):
        self.camera.start_recording(self.stream, format='h264', bitrate=self.bitrate, quality=0)
        logger.info("Camera started")

    def stop_recording(self):
        self.camera.stop_recording()
        logger.info("Camera stopped")

    def close(self):
        self.stop_recording()
        self.camera.close()
        logger.info("Camera closed")

    def write_video(self, stream, filename="tmp.mp4"):
        # Spawn a transcoding process, mostly to encapsulate the stream
        avconv_cmd = ["avconv", "-r", str(self.framerate), "-i", "-", "-vcodec", "copy", "-threads", "auto", "-r",
                      str(self.display_framerate), filename]
        logger.info("Starting avconv process with command: %s" % ' '.join(avconv_cmd))
        process = subprocess.Popen(avconv_cmd, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)

        # Find the first sps header frame in the video (this is a good place to split h264 streams)
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break

        while True:
            buf = stream.read1()
            if not buf:
                break
            process.stdin.write(buf)

        process.stdin.close()
        process.wait(10)
        if process.returncode is None:
            logger.error("avconv command did not end in time")
            raise AVConvException()
        elif process.returncode != 0:
            logger.error("avconv exited with non-zero return code: %d" % process.returncode)
            raise AVConvException()

    def save(self):
        with self.lock:
            logger.info('Saving replay')
            filename = "%.0f.mp4" % time.time()
            filepath = self.directory + filename
            # Catch 0.5s after the goal
            self.camera.wait_recording(0.5)
            self.stop_recording()
            self.write_video(self.stream, filepath)
            logger.info('Saved replay to %s' % filepath)
            self._start_recording()

        return filename
