# Raspi-Self-Balancing-Robot-Python
基于Raspberry Pi 2 的二轮自平衡机器人，Python版

## 用法
环境
```
sudo apt-get update
sudo apt-get install python3 pigpio python3-pigpio
```
运行
```
sudo pigpio
python3 robot.py
```
## 远程控制
使用HTML通过WebSocket与后端通信的遥控器
![](docs/img/remote.png)

## MyRaspRobot
![](docs/img/front.png)
![](docs/img/back.png)

## TODO
- 远程调整PID参数