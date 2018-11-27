
from flask import Flask, render_template, Response
from camera import VideoCamera
from openlapr import Alpr
import threading 
output = "Number"
frameG=None
x=0

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


def sample(frame):
    alpr = None
    try:
        alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")

        if not alpr.is_loaded():
            print("Error loading OpenALPR")
        else:
            print("Using OpenALPR " + alpr.get_version())
            alpr.set_top_n(7)
            alpr.set_default_region("wa")
            alpr.set_detect_region(False)
            jpeg_bytes = open(frame, "rb").read()
            results = alpr.recognize_array(jpeg_bytes)
            #print("Image size: %dx%d" %(results['img_width'], results['img_height']))
            #print("Processing Time: %f" % results['processing_time_ms'])
            i = 0
            for plate in results['results']:
                i += 1
                print("Plate #%d" % i)
                print("   %12s %12s" % ("Plate", "Confidence"))
                for candidate in plate['candidates']:
                    prefix = "-"
                    if candidate['matches_template']:
                        prefix = "*"
                    print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))    

thread1 = threading.Thread(target=sample, args=(frameG,))

def gen(camera):
    x=0
    while True:
        frame = camera.get_frame()
        x++;
        if x%5==0:
            frameG=frame
            thread1.start()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        print(output)    

        





@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)