plugin_codes={}
plugin_codes["base.py"]=r'''from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import subprocess

# 集成Plugin类的对象会被自动识别为插件类
# name是插件名称，enable表示插件是否启用，另外，点击插件时会自动调用run函数，因此，子类应该重写该方法。
class Plugin(object):
    menu="插件"   #放在哪个菜单下面
    name="base"   #插件名称
    enable=True   #插件默认启用，可以配置关闭
    type="text"   #text、laboratory。插件默认为文本处理类型，也可以配置为实验室类型，可以自定义界面
    frame_args={"text_tab_num":10, "cur_tab_id":0, "cur_text":"", "tab_laboratory":""}
    #options=[]    #[{"Name":"URL", "Current Setting":"", "Required":"yes", "Description":"目标URL", "obj":url_label }]，用实例对象而不是类对象，确保每个插件的options独立
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36'}
    def _run(self, args):  #当为text类型的插件时，框架调用此函数
        self.frame_args.update(args)
        return self.run(self.frame_args["cur_text"])
        
    def run(self, text=""):
        return text
        
    def buildWindow(self):  #当为有界面的插件时，框架调用此函数，通过在子类中重写该方法，可以实现插件自定义界面
        return self.buildWindowUrl()
        
    def readFile(self, file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            try:
                with open(file, 'r', encoding='gbk') as f:
                    content = f.read()
                return content
            except Exception as e:
                raise Exception("无法识别的文件编码") from e
                
    def writeFile(self, file, content):
        try:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            try:
                with open(file, 'w', encoding='gbk') as f:
                    f.write(content)
            except Exception as e:
                raise Exception("无法识别的文件编码") from e
                
    def executeCommand(self, command, logfunc=None):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        
        while True:
            data=process.stdout.readline()
            try:
                output = data.decode('utf-8')
            except:
                output = data.decode('gbk')
                
            if output == '' and process.poll() is not None:
                break
            if output and not logfunc:
                print(output, end="")
            elif output and logfunc:
                logfunc(output)
        
        return process.poll()  #返回码
                
    def filedialogAskopenfilename(self, **options):
        return filedialog.askopenfilename(**options)
        
    def messageboxShowinfo(self, title=None, message=None, **options):
        return messagebox.showinfo(title=title, message=message, **options)
    
    def onStart(self, event=None):
        self.output_text.insert(tk.END, "onStart\n")
        
    def onStop(self, event=None):
        self.output_text.insert(tk.END, "onStop\n")
        
    def showHelp(self, event=None):
        self.log("[+] show options\n")
        self.showOptions()
        
    def getOptions(self):
        for dic in self.options:
            if "obj" in dic:
                dic["Current Setting"]=dic["obj"].get()
        return self.options
        
    def log(self, *args):
        msg=" ".join([str(x) for x in args])
        self.output_text.insert(tk.END, msg)
        
    def showOptions(self):
        if not self.options:
            self.log("参数为空")
            return
        self.getOptions()
        
        #计算每个key的显示字符个数
        OPTION_KEYS=["Name", "Current Setting", "Required", "Description"]
        klen={}
        for key in OPTION_KEYS:
            l=len(key)
            for dic in self.options:
                if l<len(dic[key]):
                    l=len(dic[key])  #记录最大值
            klen[key]=l
        
        for key in OPTION_KEYS:
            if key==OPTION_KEYS[-1]:
                msg=key
            else:
                msg=key+" "*(klen[key]+4-len(key))
            self.log(msg)
        self.log("\n")
            
        for dic in self.options:
            for key in OPTION_KEYS:
                if key==OPTION_KEYS[-1]:
                    msg=dic[key]
                else:
                    msg=dic[key]+" "*(klen[key]+4-len(dic[key]))
                self.log(msg)
            self.log("\n")
        self.log("\n")
        
    def buildWindowIpPort(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame_horizontal = tk.Frame(tab_laboratory)
        frame_horizontal.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        host_label = tk.Label(frame_horizontal, text="目标地址:")
        host_label.grid(row=0, column=nexti(i=0))
        host_entry = tk.Entry(frame_horizontal, width=20)
        host_entry.grid(row=0, column=nexti())
        port_label = tk.Label(frame_horizontal, text="端口:")
        port_label.grid(row=0, column=nexti())
        port_entry = tk.Entry(frame_horizontal, width=8)
        port_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_start = tk.Button(frame_horizontal, text="开始", command=self.onStart)
        button_start.grid(row=0, column=nexti(), padx=5)
        button_stop = tk.Button(frame_horizontal, text="停止", command=self.onStop)
        button_stop.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_stop = tk.Button(frame_horizontal, text="查看帮助文档", command=self.showHelp)
        button_stop.grid(row=0, column=nexti(), padx=5)

        frame_vertical = tk.Frame(tab_laboratory)
        frame_vertical.grid(row=1, column=0, pady=10, sticky=tk.NSEW)
        self.output_text = tk.Text(frame_vertical)
        self.output_text.pack(expand=1, fill="both")

        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(1, weight=1)
        
        # 设置options
        self.options=Options()
        dic={"Name":"HOST", "Current Setting":"", "Required":"yes", "Description":"目标主机", "obj":host_entry }
        self.options.append(dic)
        dic={"Name":"PORT", "Current Setting":"", "Required":"yes", "Description":"目标端口", "obj":port_entry }
        self.options.append(dic)
        return self.output_text
        
    def buildWindowUrl(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame_horizontal = tk.Frame(tab_laboratory)
        frame_horizontal.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        url_label = tk.Label(frame_horizontal, text="URL:")
        url_label.grid(row=0, column=nexti(i=0))
        url_entry = tk.Entry(frame_horizontal, width=100)
        url_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_start = tk.Button(frame_horizontal, text="开始", command=self.onStart)
        button_start.grid(row=0, column=nexti(), padx=5)
        button_stop = tk.Button(frame_horizontal, text="停止", command=self.onStop)
        button_stop.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_stop = tk.Button(frame_horizontal, text="查看帮助文档", command=self.showHelp)
        button_stop.grid(row=0, column=nexti(), padx=5)

        frame_vertical = tk.Frame(tab_laboratory)
        frame_vertical.grid(row=1, column=0, pady=10, sticky=tk.NSEW)
        self.output_text = tk.Text(frame_vertical)
        self.output_text.pack(expand=1, fill="both")

        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(1, weight=1)
        
        # 设置options
        self.options=Options()
        dic={"Name":"URL", "Current Setting":"", "Required":"yes", "Description":"目标URL", "obj":url_entry }
        self.options.append(dic)
        return self.output_text
        
class Options(list):
    def __init__(self, *args):
        list.__init__(self, *args)
    
    def __getitem__(self, index):
        if isinstance(index, str):
            for dic in self:
                if dic["Name"]==index:
                    return dic["Current Setting"]
        else:
            return super().__getitem__(index)
            
NEXTI=0
def nexti(i=None):
    global NEXTI
    if i!=None:
        NEXTI=i
    pre=NEXTI
    NEXTI+=1
    return pre
    
PluginGlobalStorage={}

'''

plugin_codes["demo.py"]=r'''import json
import base64
import hashlib
import time
import re
import os

# 界面上的菜单顺序默认按照插件子类的定义顺序排列，优先找base.py文件，然后找其他py文件。
# 文件
class LoadFile(Plugin):
    menu="文件"
    name="加载文件"
    def run(self, text):
        file = self.filedialogAskopenfilename(initialdir=os.getcwd())  #弹出对话框选择文件，在Plugin基类里实现
        return self.readFile(file)
        
class SaveFile(Plugin):
    menu="文件"
    name="保存文件"
    def run(self, text):
        now=int(time.time())
        outfile="out_{now}.txt".format(now=now)
        self.writeFile(outfile, text)
        self.messageboxShowinfo("保存成功", "成功保存到"+outfile)
        return text
        
# 文本处理
class RemoveDuplicates(Plugin):
    menu="文本处理"
    name="字典去重"
    def run(self, text):
        if not text:
            return ""
        words = text.strip().replace("\r\n", "\n").split("\n")
        return "\n".join(list(dict.fromkeys(words)))

class SortLines(Plugin):
    menu="文本处理"
    name="字典排序"
    orders={}
    def run(self, text):
        if not text:
            return ""
        
        #默认升序排序，再点一下则降序排序，每个文本窗口都是独立的
        id=self.frame_args["cur_tab_id"]
        if id not in self.orders:
            self.orders[id]=False  #reverse  False 升序；True 降序
        else:
            self.orders[id]=not self.orders[id]
            
        words = text.strip().replace("\r\n", "\n").split("\n")
        words.sort(reverse=self.orders[id])
        return "\n".join(words)
        
class JsonView(Plugin):
    menu="文本处理"
    name="json格式化"
    def run(self, text):
        if not text:
            return ""
        j=json.loads(text)
        #formatted_json = json.dumps(j, indent=4)
        formatted_json = json.dumps(j, indent=4, ensure_ascii=False)
        return formatted_json
        
class ToLower(Plugin):
    menu="文本处理"
    name="转小写"
    def run(self, text):
        if not text:
            return ""
        return text.lower()
        
class ToUpper(Plugin):
    menu="文本处理"
    name="转大写"
    def run(self, text):
        if not text:
            return ""
        return text.upper()
        
# 编码解码
class Base64Encode(Plugin):
    menu="编码解码"
    name="base64编码"
    def run(self, text):
        if not text:
            return ""
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

class Base64Decode(Plugin):
    menu="编码解码"
    name="base64解码"
    def run(self, text):
        if not text:
            return ""
        return base64.b64decode(text).decode("utf-8")
        
class HexEncode(Plugin):
    menu="编码解码"
    name="hex编码"
    def run(self, text):
        if not text:
            return ""
        return text.encode("utf-8").hex()
        
class HexDecode(Plugin):
    menu="编码解码"
    name="hex解码"
    def run(self, text):
        if not text:
            return ""
        decoded_bytes = bytes.fromhex(text)
        return decoded_bytes.decode("utf-8")
        
# 加密解密
class Md5(Plugin):
    menu="加密解密"
    name="md5"
    def run(self, text):
        if not text:
            return ""
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode('utf-8'))
        return md5_hash.hexdigest()
        
class Sha1(Plugin):
    menu="加密解密"
    name="sha1"
    def run(self, text):
        if not text:
            return ""
        sha1_hash = hashlib.sha1()
        sha1_hash.update(text.encode('utf-8'))
        return sha1_hash.hexdigest()
        
# 代码执行
class ExecPython(Plugin):
    menu="代码执行"
    name="执行Python代码"
    def run(self, text):
        if not text:
            return ""
        exec(text)
        return text
        
class EvalPython(Plugin):
    menu="代码执行"
    name="数值计算"
    def run(self, text):
        if not text:
            return ""
        answer = eval(text)
        return "{answer}={expression}".format(answer=answer, expression=text)
        
'''

plugin_codes["laboratory.py"]=r'''import http.server
import socketserver
import threading

class CMD(Plugin):
    menu="实验室"
    name="命令行"
    type="laboratory"
    def buildWindow(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame_horizontal = tk.Frame(tab_laboratory)
        frame_horizontal.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        cmd_label = tk.Label(frame_horizontal, text="CMD:")
        cmd_label.grid(row=0, column=nexti(i=0))
        cmd_entry = tk.Entry(frame_horizontal, width=100)
        cmd_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_start = tk.Button(frame_horizontal, text="执行", command=self.onStart)
        button_start.grid(row=0, column=nexti(), padx=5)
        button_stop = tk.Button(frame_horizontal, text="停止", command=self.onStop)
        button_stop.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_stop = tk.Button(frame_horizontal, text="查看帮助文档", command=self.showHelp)
        button_stop.grid(row=0, column=nexti(), padx=5)

        frame_vertical = tk.Frame(tab_laboratory)
        frame_vertical.grid(row=1, column=0, pady=10, sticky=tk.NSEW)
        self.output_text = tk.Text(frame_vertical)
        self.output_text.pack(expand=1, fill="both")
        
        # 绑定回车事件
        cmd_entry.bind('<Return>', self.onStart)

        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(1, weight=1)
        
        # 设置options
        self.options=Options()
        dic={"Name":"CMD", "Current Setting":"", "Required":"yes", "Description":"执行的命令", "obj":cmd_entry }
        self.options.append(dic)
        return self.output_text
        
    def onStart(self, event=None):
        options=self.getOptions()
        cmd=options["CMD"]
        
        self.log(f"[+] {cmd}\n")
        self.executeCommand(cmd, logfunc=self.log)
        # TODO：添加自定义命令，并使自定义命令和系统命令都支持管道

    def onStop(self, event=None):
        self.log("[*] onStop\n")
            
    def showHelp(self, event=None):
        super().showHelp()
        help="功能上相当于system(CMD)\n\n"\
             "Windows下常用命令：\n"\
             "netstat -ano | findstr LISTEN\t\t\t查看监听端口\n"\
             "\n"
        self.log(help)
        
class WorkflowOrchestration(Plugin):
    menu="实验室"
    name="场景编排demo"
    type="text"
    def run(self, text):
        tasks=[]
        tasks+=[RemoveDuplicates]
        tasks+=[ToLower]
        tasks+=[SortLines]
        
        for _ in tasks:
            text=_().run(text)
        
        return text
    
class HttpServer(Plugin):
    menu="实验室"
    name="http.server"
    type="laboratory"
    server=None
    def buildWindow(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame_horizontal = tk.Frame(tab_laboratory)
        frame_horizontal.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        bind_label = tk.Label(frame_horizontal, text="bind:")
        bind_label.grid(row=0, column=nexti(i=0))
        ip_entry = tk.Entry(frame_horizontal, width=16)
        ip_entry.insert(0, "0.0.0.0")
        ip_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=1).grid(row=0, column=nexti(), padx=2)  #占位
        port_entry = tk.Entry(frame_horizontal, width=6)
        port_entry.insert(0, "5000")
        port_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_start = tk.Button(frame_horizontal, text="开始", command=self.onStart)
        button_start.grid(row=0, column=nexti(), padx=5)
        button_stop = tk.Button(frame_horizontal, text="停止", command=self.onStop)
        button_stop.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_stop = tk.Button(frame_horizontal, text="查看帮助文档", command=self.showHelp)
        button_stop.grid(row=0, column=nexti(), padx=5)

        frame_vertical = tk.Frame(tab_laboratory)
        frame_vertical.grid(row=1, column=0, pady=10, sticky=tk.NSEW)
        self.output_text = tk.Text(frame_vertical)
        self.output_text.pack(expand=1, fill="both")

        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(1, weight=1)
        
        # 设置options
        self.options=Options()
        dic={"Name":"IP", "Current Setting":"", "Required":"yes", "Description":"监听网卡的IP", "obj":ip_entry }
        self.options.append(dic)
        dic={"Name":"PORT", "Current Setting":"", "Required":"yes", "Description":"监听端口", "obj":port_entry }
        self.options.append(dic)
        
        #MyHandler里会用
        PluginGlobalStorage[self.__class__.__name__]={"class_obj":self}
        return self.output_text
        
    def onStart(self, event=None):
        options=self.getOptions()
        IP=options["IP"]
        PORT=int(options["PORT"])
        
        class MyHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                msg=format%args
                obj=PluginGlobalStorage["HttpServer"]["class_obj"]
                obj.log(msg+"\n")
                
        def fn():
            with socketserver.TCPServer((IP, PORT), MyHandler) as self.server:
                self.log(f"监听于{IP}:{PORT}\n")
                self.server.serve_forever()
                
        self.log("[+] 启动Server\n")
        thread = threading.Thread(target=fn)
        thread.start()

    def onStop(self, event=None):
        if self.server:
            self.log("[+] 关闭Server\n")
            self.server.shutdown()
            self.server=None
        else:
            self.log("[*] Server未启动\n")
            
    def showHelp(self, event=None):
        super().showHelp()
        self.log("相当于在python3下调用：\n")
        self.log("python -m http.server port\n\n")
        self.log("或者相当于在python2.7下调用：\n")
        self.log("python -m SimpleHTTPServer port\n\n")
        
'''
