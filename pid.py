class PID:

    def __init__(self, limit_velocity=10000, limit_turn=150):
        """
        PID 控制类
        :param limit_velocity: number 速度环限幅
        :param limit_turn: number 转向环限幅
        """
        self.velocity = {
            'encoder': 0,
            'encoder_integral': 0
        }
        self.limit_velocity = limit_velocity
        self.limit_turn = limit_turn

    def get_balance_pwm(self, pid_params, angle, gyro):
        return pid_params['k'] * (pid_params['p'] * angle + gyro * pid_params['d'])

    def get_velocity_pwm(self, pid_params, encoder_left, encoder_right, movement):
        encoder_least = encoder_left + encoder_right - 0    # 获取最新速度偏差==测量速度（左右编码器之和）-目标速度（此处为零）
        self.velocity['encoder'] *= 0.7     # 一阶低通滤波器
        self.velocity['encoder'] += encoder_least * 0.3     # 一阶低通滤波器
        self.velocity['encoder_integral'] += self.velocity['encoder']       # 积分出位移积分时间
        self.velocity['encoder_integral'] = self.velocity['encoder_integral'] - movement       # 接收遥控器数据，控制前进后退

        # 没有遥控数据时加速停止过程
        if movement == 0:
            if self.velocity['encoder_integral'] > 1000:
                self.velocity['encoder_integral'] -= 500
            elif self.velocity['encoder_integral'] < -1000:
                self.velocity['encoder_integral'] += 500

        # 限制最大速度
        if self.velocity['encoder_integral'] > self.limit_velocity:
            self.velocity['encoder_integral'] = self.limit_velocity
        elif self.velocity['encoder_integral'] < -self.limit_velocity:
            self.velocity['encoder_integral'] = -self.limit_velocity

        return self.velocity['encoder'] * pid_params['p'] + self.velocity['encoder_integral'] * pid_params['i']

    def get_turn_pwm(self, pid_params, gyro, turn):
        if turn > self.limit_turn:
            turn = self.limit_turn
        elif turn < -self.limit_turn:
            turn = -self.limit_turn
        return turn * pid_params['p'] + gyro * pid_params['d']

    def clean(self):
        self.velocity['encoder'] = 0
        self.velocity['encoder_integral'] = 0   # 电机关闭后需清除积分
