from threading import Thread
from remote.websocket import WebsocketServer
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json


class HttpHandler(BaseHTTPRequestHandler):
    """
    简单Web服务Handler
    """
    def do_GET(self):
        file = open("%s/websocket.html" % os.path.dirname(os.path.realpath(__file__)), "rb")
        html = file.read()
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % "UTF-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


class HttpdThread(Thread):
    """
    Web服务 线程
    object.start() 启动线程
    """
    def __init__(self, host='0.0.0.0', port=80):
        super(__class__, self).__init__()
        self.port = port
        self.httpd = HTTPServer((host, self.port), HttpHandler)
        self.daemon = True

    def run(self):
        self.httpd.serve_forever()


class RemoteControlServer(Thread, WebsocketServer):
    """
    远程控制类，通过WebSocket通信
    """
    def __init__(self, pid_params, host='0.0.0.0', http_port=80, websocket_port=9000):
        WebsocketServer.__init__(self, host=host, port=websocket_port)
        Thread.__init__(self)
        self.httpd = HttpdThread(host=host, port=http_port)
        self.received = {
            'joystick': [0, 0],
            'start': 1,
            'pid': pid_params
        }
        self.daemon = True

    def run(self):
        self.httpd.setDaemon(True)
        self.httpd.start()
        self.run_forever()

    def send_data(self, balance_angle, balance_gyro, turn_gyro, pwm_left, pwm_right):
        """
        发送数据
        :param balance_angle: 平衡倾角
        :param balance_gyro: 平衡角速度
        :param turn_gyro: 转向角速度
        :param pwm_left: 左侧PWM
        :param pwm_right: 右侧PWM
        """
        if len(self.clients):
            data = {
                'sensor': ["%.2f" % balance_angle, "%.2f" % balance_gyro, "%.2f" % turn_gyro],
                'pwm': ["%d" % pwm_left, "%d" % pwm_right]
            }
            self.send_message_to_all(json.dumps(data))

    def send_custom_info(self, info):
        """
        发送自定义文本
        :param info: 要发送的文本
        """
        self.send_message_to_all(json.dumps({
            'info': info
        }))

    def message_received(self, client, server, message):
        """
        接收数据后解码json信息
        :param message: {
                  'joystick': [power, turn],
                  'start': 0|1
                  'pid': ['balance|velocity|turn', 'k|p|i|d', value]
                }
        """
        data = json.loads(message)
        if 'joystick' in data:
            self.received['joystick'][0] = data["joystick"][0]     # power
            self.received['joystick'][1] = data["joystick"][1]     # turn
        if 'start' in data:
            self.received['start'] = data["start"]
        if 'pid' in data:
            self.received['pid'][data["pid"][0]][data["pid"][1]] = data['pid'][2]

    def new_client(self, client, server):
        """
        新客户端回调函数
        :param client:
        :param server:
        :return:
        """
        # 初始化客户端PID参数
        self.send_message(client, json.dumps({
            'pid': self.received['pid']
        }))


if __name__ == '__main__':
    """
    测试远程控制服务，每0.5秒通过WebSocket发送测试数据,接受并打印收到数据
    """
    import time
    import random
    from settings import pid_params
    server = RemoteControlServer(pid_params, host='0.0.0.0', http_port=80, websocket_port=9000)
    server.start()

    while True:
        if len(server.clients):
            server.send_data(random.random(), random.random(), random.random(), random.random(), random.random())
            print(server.received)
        time.sleep(0.5)
