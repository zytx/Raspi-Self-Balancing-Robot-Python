import pigpio


class Motor:

    def __init__(self, pi, motorpins, pwm_range=255):
        self.pi = pi
        self.pins = motorpins
        self.speed = 0
        self.pwm_range = pwm_range

        for pin in motorpins:
            pi.set_mode(pin, pigpio.OUTPUT)
            pi.set_PWM_range(pin, pwm_range)
            pi.set_PWM_frequency(pin, 50)
            pi.set_PWM_dutycycle(pin, 0)

    def set_pwm(self, pwm):
        """
        设置AB相直流电机PWM值，限幅self.pwm_range决定
        :param pwm: PWM值，正值正转，负值反转
        :return:
        """
        pwm = int(-self.pwm_range if pwm < -self.pwm_range else self.pwm_range if pwm > self.pwm_range else pwm)

        if pwm < 0:
            self.pi.set_PWM_dutycycle(self.pins[0], -pwm)
            self.pi.set_PWM_dutycycle(self.pins[1], 0)
        else:
            self.pi.set_PWM_dutycycle(self.pins[0], 0)
            self.pi.set_PWM_dutycycle(self.pins[1], pwm)

    def stop(self):
        for pin in self.pins:
            self.pi.set_PWM_dutycycle(pin, 0)
