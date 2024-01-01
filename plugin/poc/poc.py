import requests
import socket

class PortConnect(Plugin):
    menu="POC脚本"
    name="端口访问"
    type="laboratory"
    def buildWindow(self):  #当为有界面的插件时，框架调用此函数，通过在子类中重写该方法，可以实现插件自定义界面
        return self.buildWindowIpPort()
        
    def onStart(self, event=None):
        options=self.getOptions()
        HOST=options["HOST"]
        PORT=int(options["PORT"])
        if self.isPortOpen(HOST, PORT):
            self.log("{port}/tcp    {status}\n".format(port=PORT, status="open"))
        else:
            self.log("{port}/tcp    {status}\n".format(port=PORT, status="closed"))
            
    def isPortOpen(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 设置超时时间为2秒
            sock.connect((host, port))
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False
        
class HttpGet(Plugin):
    menu="POC脚本"
    name="HTTP访问"
    type="laboratory"
    def onStart(self, event=None):
        options=self.getOptions()
        try:
            res = requests.get(options["URL"], headers=self.headers, timeout=3, verify=False)
            if 200==res.status_code:
                self.log(res.content.decode("utf-8"))
        except Exception as e:
            print(e)
            