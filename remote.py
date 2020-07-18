from neopixel import *
import time
from config import *
import rpyc


class PixelStrip(rpyc.Service):
    LED_COUNT = get_led_count()
    LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
    exposed_exit = False
    exposed_strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    exposed_strip.begin()

    def exposed_arrangement(self, x):
        self.exposed_exit = False
        if x == 'wipeGreen':
            self.color_wipe(Color(255, 0, 0), 10)
        elif x == 'wipeRed':
            self.color_wipe(Color(0, 255, 0), 10)
        elif x == 'wipeBlue':
            self.color_wipe(Color(0, 0, 255), 10)
        elif x == 'wipeWhite':
            self.color_wipe(Color(127, 127, 127), 10)
        elif x == 'white':
            self.color_instant(Color(127, 127, 127))
        elif x == 'red':
            self.color_instant(Color(0, 255, 0))
        elif x == 'blue':
            self.color_instant(Color(0, 0, 255))
        elif x == 'green':
            self.color_instant(Color(255, 0, 0))
        elif x == 'chaseWhite':
            self.theater_chase(Color(127, 127, 127))
        elif x == 'chaseGreen':
            self.theater_chase(Color(127, 0, 0))
        elif x == 'chaseBlue':
            self.theater_chase(Color(0, 0, 127))
        elif x == 'rainbow':
            self.rainbow()
        elif x == 'rainbowCycle':
            rpyc.async_(self.rainbow_cycle())
        elif x == 'wipe':
            self.color_wipe(Color(0, 0, 0), 10)
        elif x == 'clear':
            self.color_wipe(Color(0, 0, 0))
        else:
            print("No option selected...")

    def color_instant(self, color):
        for i in range(self.exposed_strip.numPixels()):
            self.exposed_strip.setPixelColor(i, color)
        self.exposed_strip.show()

    def color_wipe(self, color, wait_ms=50):
        for i in range(self.exposed_strip.numPixels()):
            self.exposed_strip.setPixelColor(i, color)
            self.exposed_strip.show()
            time.sleep(wait_ms / 1000.0)

    def theater_chase(self, color, wait_ms=50, iterations=100):
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.exposed_strip.numPixels(), 3):
                    self.exposed_strip.setPixelColor(i + q, color)
                self.exposed_strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.exposed_strip.numPixels(), 3):
                    self.exposed_strip.setPixelColor(i + q, 0)
                if self.exposed_exit:
                    return

    def wheel(self, pos):
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, wait_ms=20, iterations=1000):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.exposed_strip.numPixels()):
                self.exposed_strip.setPixelColor(i, self.wheel((i + j) & 255))
                if self.exposed_exit:
                    return
            self.exposed_strip.show()
            time.sleep(wait_ms / 1000.0)

    def rainbow_cycle(self, wait_ms=20, iterations=1000):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.exposed_strip.numPixels()):
                self.exposed_strip.setPixelColor(i, self.wheel((int(i * 256 / self.exposed_strip.numPixels()) + j) & 255))
                if self.exposed_exit:
                    return
            self.exposed_strip.show()
            print(self.exposed_exit)
            time.sleep(wait_ms / 1000.0)

    def theater_chase_rainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.exposed_strip.numPixels(), 3):
                    self.exposed_strip.setPixelColor(i + q, self.wheel((i + j) % 255))
                self.exposed_strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.exposed_strip.numPixels(), 3):
                    self.exposed_strip.setPixelColor(i + q, 0)
                if self.exposed_exit:
                    return


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(PixelStrip(), port=REMOTE_PORT)
    print("Opened socket on port: "+str(REMOTE_PORT))
    t.start()
