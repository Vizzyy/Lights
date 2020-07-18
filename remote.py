import threading
import board
import neopixel
import time
from config import *
import rpyc


class PixelStrip(rpyc.Service):
    LED_COUNT = get_led_count()
    pixel_pin = board.D18
    ORDER = neopixel.GRB
    exposed_strip = neopixel.NeoPixel(
        pixel_pin, LED_COUNT, brightness=1, auto_write=False, pixel_order=ORDER
    )

    def exposed_arrangement(self, x):
        if x == 'wipeGreen':
            self.color_wipe((255, 0, 0), 10)
        # elif x == 'wipeRed':
        #     self.color_wipe(Color(0, 255, 0), 10)
        # elif x == 'wipeBlue':
        #     self.color_wipe(Color(0, 0, 255), 10)
        # elif x == 'wipeWhite':
        #     self.color_wipe(Color(127, 127, 127), 10)
        elif x == 'white':
            self.exposed_strip.fill((127, 127, 127))
        elif x == 'red':
            self.exposed_strip.fill((0, 255, 0))
        elif x == 'blue':
            self.exposed_strip.fill((0, 0, 255))
        elif x == 'green':
            self.exposed_strip.fill((255, 0, 0))
        # elif x == 'chaseWhite':
        #     self.theater_chase(Color(127, 127, 127))
        # elif x == 'chaseGreen':
        #     self.theater_chase(Color(127, 0, 0))
        # elif x == 'chaseBlue':
        #     self.theater_chase(Color(0, 0, 127))
        # elif x == 'rainbow':
        #     self.rainbow()
        elif x == 'rainbowCycle':
            self.rainbow_cycle(0.001)
        # elif x == 'wipe':
        #     self.color_wipe(Color(0, 0, 0), 10)
        elif x == 'clear':
            self.exposed_strip.fill((0, 0, 0))
        else:
            print("No option selected...")

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

    def wheel(self, pos):
        if pos < 85:
            return pos * 3, 255 - pos * 3, 0
        elif pos < 170:
            pos -= 85
            return 255 - pos * 3, 0, pos * 3
        else:
            pos -= 170
            return 0, pos * 3, 255 - pos * 3

    def rainbow(self, wait_ms=20, iterations=1000):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.exposed_strip.numPixels()):
                self.exposed_strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.exposed_strip.show()
            time.sleep(wait_ms / 1000.0)

    def sleep_function(self, duration):
        time.sleep(duration)

    def rainbow_cycle(self, wait):
        for j in range(255 * 1000):
            for i in range(self.LED_COUNT):
                pixel_index = (i * 256 // self.LED_COUNT) + j
                self.exposed_strip[i] = self.wheel(pixel_index & 255)
            self.exposed_strip.show()
            thread = threading.Thread(target=self.sleep_function(wait))
            thread.start()
            thread.join()

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


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(PixelStrip(), port=REMOTE_PORT, protocol_config={
        'allow_public_attrs': True,
    })
    print("Opened socket on port: "+str(REMOTE_PORT))
    t.start()
