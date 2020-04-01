#!/usr/bin/python

from neopixel import *
import flask, threading, time

lock = threading.Lock()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

LED_COUNT      = 300
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def colorInstant(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def arrangement(p, x):
    if x == 'wipeGreen':
        colorWipe(p, Color(255, 0, 0), 10)
    elif x == 'wipeRed':
        colorWipe(p, Color(0, 255, 0), 10)
    elif x == 'wipeBlue':
        colorWipe(p, Color(0, 0, 255), 10)
    elif x == 'wipeWhite':
        colorWipe(p, Color(127, 127, 127), 10)
    elif x == 'white':
        colorInstant(p, Color(127, 127, 127))
    elif x == 'red':
        colorInstant(p, Color(0, 255, 0))
    elif x == 'blue':
        colorInstant(p, Color(0, 0, 255))
    elif x == 'green':
        colorInstant(p, Color(255, 0, 0))
    elif x == 'chaseWhite':
        theaterChase(p, Color(127, 127, 127))
    elif x == 'chaseGreen':
        theaterChase(p, Color(127,   0,   0))
    elif x == 'chaseBlue':
        theaterChase(p, Color(  0,   0, 127))
    elif x == 'rainbow':
        rainbow(p)
    elif x == 'rainbowCycle':
        rainbowCycle(p)
    elif x == 'wipe':
        colorWipe(p, Color(0,0,0), 10)
    elif x == 'clear':
        colorInstant(p, Color(0,0,0))
    else:
        print("")

@app.route('/arrange/<section>', methods=['GET'])
def home(section):
    lock.acquire()
    threading.Thread(target=arrangement(strip,section)).start()
    lock.release()
    return "<h1>Indoor Lights!</h1><p>"+str(section)+"</p>"

@app.route('/static/<string:page_name>/')
def render_static(page_name):
    return flask.render_template('%s.html' % page_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')