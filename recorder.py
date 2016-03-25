import io
import picamera
import time
import threading
import subprocess


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class Recorder(object):
    save_filename = None
    directory = "videos/"

    def __init__(self, framerate=30, resolution=(1280, 720)):
        self.running = True
        self.framerate = framerate
        self.resolution = resolution

    def stop(self):
        self.running = False

    def write_video(self, stream, filename="tmp"):
        # Write the entire content of the circular buffer to disk. No need to
        # lock the stream here as we're definitely not writing to it
        # simultaneously
        h264_filename = filename + ".h264"
        with io.open(h264_filename, 'wb') as output:
            for frame in stream.frames:
                if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                    stream.seek(frame.position)
                    break
            while True:
                buf = stream.read1()
                if not buf:
                    break
                output.write(buf)

        output.close()
        # avconv -r 30 -i 1458866583.h264 -vcodec copy 1458866583.mp4
        mp4_filename = filename + ".mp4"
        subprocess.call(["avconv", "-r", str(self.framerate), "-i", h264_filename, "-vcodec", "copy", mp4_filename])

        # Wipe the circular stream once we're done
        stream.seek(0)
        stream.truncate()
        return filename

    def save(self):
        filename = "%.0f" % time.time()
        self.save_filename = filename
        return filename + ".mp4"

    def loop(self):
        with picamera.PiCamera() as camera:
            camera.resolution = self.resolution
            camera.framerate = self.framerate
            stream = picamera.PiCameraCircularIO(camera, seconds=1)
            camera.start_recording(stream, format='h264')

            try:
                while self.running:
                    camera.wait_recording(0.1)
                    if self.save_filename is not None:
                        # Write the 10 seconds "before" motion to disk as well
                        self.write_video(stream, self.directory + self.save_filename)
                        print('Saved replay for %s!' % self.save_filename)
                        self.save_filename = None

            finally:
                camera.stop_recording()
