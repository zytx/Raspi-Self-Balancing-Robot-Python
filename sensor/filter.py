import datetime

class KalmanFilter():

    def __init__(self):
        self.Q_angle = 0.001
        self.Q_bias = 0.003
        self.R_measure = 0.03

        self.angle = 0.0
        self.bias = 0.0
        self.P = [
            [0,0],
            [0,0]
        ]

        self.lastTime = datetime.datetime.now()

    def filter(self, newAngle, newRate):
        dt = (datetime.datetime.now() - self.lastTime).total_seconds()
        # print('滤波', dt, end = " ")
        # Discrete Kalman filter time update equations - Time Update ("Predict")
        # Update xhat - Project the state ahead
        # Step 1
        rate = newRate - self.bias
        self.angle += dt * rate

        # Update estimation error covariance - Project the error covariance ahead
        # Step 2
        self.P[0][0] += dt * (dt*self.P[1][1] - self.P[0][1] - self.P[1][0] + self.Q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        # Discrete Kalman filter measurement update equations - Measurement Update ("Correct")
        # Calculate Kalman gain - Compute the Kalman gain
        # Step 4
        S = self.P[0][0] + self.R_measure    # Estimate error
        # Step 5
        K = [           # Kalman gain - This is a 2x1 vector
            self.P[0][0] / S,
            self.P[1][0] / S
        ]

        # Calculate angle and bias - Update estimate with measurement zk (newAngle)
        # Step 3
        y = newAngle - self.angle    # Angle difference
        # Step 6
        self.angle += K[0] * y
        self.bias += K[1] * y

        # Calculate estimation error covariance - Update the error covariance
        # Step 7
        P00_temp = self.P[0][0]
        P01_temp = self.P[0][1]

        self.P[0][0] -= K[0] * P00_temp
        self.P[0][1] -= K[0] * P01_temp
        self.P[1][0] -= K[1] * P00_temp
        self.P[1][1] -= K[1] * P01_temp

        self.lastTime = datetime.datetime.now()
        return self.angle