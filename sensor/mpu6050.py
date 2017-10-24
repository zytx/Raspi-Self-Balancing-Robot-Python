import math
from sensor.filter import KalmanFilter
import settings

class MPU6050():

    def __init__(self, pi, address):
        self.pi = pi
        self.fd = pi.i2c_open(1, address, 0)
        pi.i2c_write_byte_data(self.fd, 0x1B, 0x18) # Settinggyro sensitivity to + / - 2000 deg / sec
        pi.i2c_write_byte_data(self.fd, 0x1C, 0x00) # 加速度计 + / -2g

        pi.i2c_write_byte_data(self.fd, 0x19, 0x04) # SMPLRT_DIV 采样率200Hz

        pi.i2c_write_byte_data(self.fd, 0x1A, 0x02) # REGISTER 26 – CONFIGURATION 配置 - DLPF Acc: 94 Hz Gyro: 98 Hz
        # i2cWriteByteData(fd, 0x37, 0x50); # REGISTER 55 - INT  引脚 / 旁路有效
        pi.i2c_write_byte_data(self.fd, 0x38, 0x00) # INTERRUPT ENABLE - 关闭中断

        self.wake()

        self.gyro = {
            'y': 0,
            'z': 0
        }
        self.accel = {
            'x': 0,
            'y': 0,
            'z': 0
        }
        # 平衡倾角
        self.balance_angle = 0
        # 平衡角速度
        self.balance_gyro = 0
        # 转向角速度
        self.turn_gyro = 0

        self.kalman = KalmanFilter()

    def wake(self):
        self.pi.i2c_write_byte_data(self.fd, 0x6B, 0x02) # 关闭休眠 陀螺仪Y轴作为时钟源

    def update(self):
        self.gyro['y'] = (self.pi.i2c_read_byte_data(self.fd, 0x45) << 8) + self.pi.i2c_read_byte_data(self.fd, 0x46)
        self.gyro['z'] = (self.pi.i2c_read_byte_data(self.fd, 0x47) << 8) + self.pi.i2c_read_byte_data(self.fd, 0x48)
        self.accel['x'] = (self.pi.i2c_read_byte_data(self.fd, 0x3B) << 8) + self.pi.i2c_read_byte_data(self.fd, 0x3C)
        self.accel['z'] = (self.pi.i2c_read_byte_data(self.fd, 0x3F) << 8) + self.pi.i2c_read_byte_data(self.fd, 0x40)

        if self.gyro['y'] > 32768: self.gyro['y'] -= 65536;     # 数据类型转换  也可通过short强制类型转换
        if self.gyro['z'] > 32768: self.gyro['z'] -= 65536;
        if self.accel['x'] > 32768: self.accel['x'] -= 65536;
        if self.accel['z'] > 32768: self.accel['z'] -= 65536;

        self.accel['y'] = math.atan2(self.accel['x'], self.accel['z']) * 180 / 3.1415926   # 计算倾角
        self.gyro['y'] /= -16.4    # 陀螺仪量程转换
        self.gyro['z'] /= 16.4

        # 手动修正
        self.gyro['y'] += settings.gyro_offset['y']
        self.gyro['z'] += settings.gyro_offset['z']
        self.accel['x'] += settings.accel_offset['x']
        self.accel['y'] += settings.accel_offset['y']
        self.accel['z'] += settings.accel_offset['z']

        self.balance_angle = self.kalman.filter(self.accel['y'], self.gyro['y'])    # 卡尔曼滤波
        self.balance_gyro = self.gyro['y']
        self.turn_gyro = self.gyro['z']

    def sleep(self):
        self.pi.i2c_write_byte_data(self.fd, 0x6B, 0x42)    # 进入休眠 陀螺仪Y轴作为时钟源

    def close(self):
        self.sleep()
        self.pi.i2c_close(self.fd)