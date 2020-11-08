import math

from rpi_ws281x import PixelStrip, Color
import sys
import time
from config import *

LED_COUNT = get_led_count()
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()


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
        theaterChase(p, Color(127, 0, 0))
    elif x == 'chaseBlue':
        theaterChase(p, Color(0, 0, 127))
    elif x == 'christmas1':
        theaterChaseMultiColor(p, Color(235, 64, 52), Color(0, 222, 33))
    elif x == 'twilight':
        twilight_cycle(p)
    elif x == 'rainbow':
        rainbow(p)
    elif x == 'rainbowCycle':
        rainbowCycle(p)
    elif x == 'wipe':
        colorWipe(p, Color(0, 0, 0), 10)
    elif x == 'clear':
        colorInstant(p, Color(0, 0, 0))
    else:
        print("No option selected...")


def colorInstant(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=100):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def theaterChaseMultiColor(strip, color1, color2, wait_ms=50, iterations=100):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color1)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color2)


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


def twilight_wheel(pos):
    """
    pink = R:255 G:0 B:255
    cyan = R:0 G:255 B:255

    0 -> 300

    at 0 red should be 255 and green 0
    at 150 red should be 0 and green 0
    at 300 red should be 0 and green 255


    f(x) = x/255
    f(

    """
    temp = 1.0 / 48.0
    add_val = 150
    if pos > 149:
        add_val = 0
    sin_pos = math.sin(temp * (pos + add_val))
    cos_pos = math.sin(2 * temp * (pos + add_val))

    r = int(sin_pos * 255)
    if r < 0:
        r = 0
    g = int(cos_pos * 255)
    if g < 0:
        g = 0
    b = 255

    color = Color(r, g, b)
    return color


def twilight_wheel2(pos):
    if pos <= 85:
        return Color(pos , 255 - pos * 3, 255)
    elif pos <= 170:
        pos -= 85
        return Color(255 - pos * 3, 0, 255)
    else:
        pos -= 170
        return Color(0, pos * 3, 255)


def rainbow(strip, wait_ms=20, iterations=10000):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def twilight(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, twilight_wheel(i))
    strip.show()


def twilight_cycle(strip, wait_ms=20, iterations=10000):
    """Shades of blue through violet blended together in a continuous wave"""
    pixel_colors_by_position = []
    position_math = []

    print("front-load position calculations")
    for i in range(strip.numPixels()):
        position_math.append(int(i * 256 / strip.numPixels()))

    print("front-load color calculations")
    for j in range(256):
        temp_array = []
        for i in range(strip.numPixels()):
            temp_array.append(twilight_wheel2((position_math[i] + j) & 255))
        pixel_colors_by_position.append(temp_array)

    print("beginning color execution")
    for j in range(256 * iterations):
        j_pos = int(j % 256)
        for i in range(strip.numPixels()):
            # Gain significant computational efficiency by front-loading calculations
            strip.setPixelColor(i, pixel_colors_by_position[j_pos][i])
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=10000):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    pixel_colors_by_position = []
    position_math = []

    print("front-load position calculations")
    for i in range(strip.numPixels()):
        position_math.append(int(i * 256 / strip.numPixels()))

    print("front-load color calculations")
    for j in range(256):
        temp_array = []
        for i in range(strip.numPixels()):
            temp_array.append(wheel((position_math[i] + j) & 255))
        pixel_colors_by_position.append(temp_array)

    print("beginning color execution")
    for j in range(256 * iterations):
        j_pos = int(j % 256)
        for i in range(strip.numPixels()):
            # Gain significant computational efficiency by front-loading calculations
            strip.setPixelColor(i, pixel_colors_by_position[j_pos][i])
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


if __name__ == '__main__':
    print(sys.argv)
    if sys.argv[1] == "custom":
        colorInstant(strip, Color(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
    else:
        arrangement(strip, sys.argv[1])
