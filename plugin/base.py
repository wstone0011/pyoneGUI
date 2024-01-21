from tkinter import filedialog
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
    plugin_directory=""
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
        
    def executeCommand(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                 preexec_fn=None, close_fds=True,
                 shell=True, cwd=None, env=None, universal_newlines=None,
                 startupinfo=None, creationflags=0,
                 restore_signals=True, start_new_session=False,
                 pass_fds=(), *rest, encoding=None, errors=None, text=None, logfunc=None):
                 
        process = subprocess.Popen(args=args, bufsize=bufsize, executable=executable,
                 stdin=stdin, stdout=stdout, stderr=stderr,
                 preexec_fn=preexec_fn, close_fds=close_fds,
                 shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                 startupinfo=startupinfo, creationflags=creationflags,
                 restore_signals=restore_signals, start_new_session=start_new_session,
                 pass_fds=pass_fds, *rest, encoding=encoding, errors=errors, text=text) # *rest传进来了，但是暂时用不到，可能是为了以后的兼容性
        #process = subprocess.Popen(args, bufsize, executable, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        
        # 实时读取子进程输出
        while True:
            data = process.stdout.readline()
            if data == b'' and process.poll() is not None:
                break
                
            try:
                output = data.decode('utf-8')
            except:
                output = data.decode('gbk')
                
            if output and not logfunc:
                print(output, end="")
            elif output and logfunc:
                logfunc(output)
        # 等待子进程彻底结束
        process.wait()
        
        return process.returncode
                
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

