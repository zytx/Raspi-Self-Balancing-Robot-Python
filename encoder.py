import pigpio


class Encoder:

    def __init__(self, pi, pins):
        self.pi = pi
        self.pins = pins

        self.speed = 0
        self.levA = 0
        self.levB = 0

        self.lastGpio = None

        self.cb = []

        for pin in pins:
            self.pi.set_mode(pin, pigpio.INPUT)
            self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
            self.cb.append(self.pi.callback(pin, pigpio.EITHER_EDGE, self._pulse))

    def _pulse(self, gpio, level, tick):

        """
        Decode the rotary encoder pulse.

                     +---------+         +---------+      0
                     |         |         |         |
           A         |         |         |         |
                     |         |         |         |
           +---------+         +---------+         +----- 1

               +---------+         +---------+            0
               |         |         |         |
           B   |         |         |         |
               |         |         |         |
           ----+         +---------+         +---------+  1
        """

        if gpio == self.pins[0]:
            self.levA = level
        else:
            self.levB = level

        if gpio != self.lastGpio:  # debounce
            self.lastGpio = gpio

            if gpio == self.pins[0] and level == 1:
                if self.levB == 1:
                    self.speed += 1
            elif gpio == self.pins[1] and level == 1:
                if self.levA == 1:
                    self.speed -= 1

    def cancel(self):
        """
        Cancel the rotary encoder decoder.
        """
        for cb in self.cb:
            cb.cancel()
        self.speed = 0
        self.levA = 0
        self.levB = 0
        self.lastGpio = None

    def reset(self):
        self.speed = 0
        self.levA = 0
        self.levB = 0
        self.lastGpio = None


if __name__ == '__main__':
    '''
    测试编码器，每0.5秒打印编码器数据
    '''
    import settings
    import time
    pi = pigpio.pi()
    encoder_left = Encoder(pi, settings.PINS['encoder']['left'])
    encoder_right = Encoder(pi, settings.PINS['encoder']['right'])

    while True:
        print("左：", encoder_left.speed, "，右：", encoder_right.speed)
        time.sleep(0.5)
