import tkinter as tk
from tkinter import ttk
from functools import partial
from tkinter import messagebox
import re
import os
import sys
import argparse
#----框架中没有使用但在插件中有使用的库----
from tkinter import filedialog
import builtins
import subprocess
import http.server
import socketserver
import threading
import requests
import socket
import base64
import hashlib
import json
import time
import platform
import uuid
from uncompyle6 import verify
from uncompyle6.main import main, status_msg
from uncompyle6.version import __version__
import uncompyle6.scanners.scanner37
from pwn import *

pyoneGUI_VERSION="pyoneGUI v2.1.0"

class Utils(object):
    @staticmethod
    def readFile(file):
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
            
    @staticmethod
    def writeFile(file, content):
        try:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            try:
                with open(file, 'w', encoding='gbk') as f:
                    f.write(content)
            except Exception as e:
                raise Exception("无法识别的文件编码") from e
    
    @staticmethod
    def traverseDirectory(path="plugin", find=r"^.*\.py$", ignore_dir=set([]), callback=None):
        if not path:
            return
        
        for entry in os.scandir(path):
            if entry.is_file():
                if bool(re.match(f"{find}", entry.name)):
                    if callback:
                        callback(entry)
                    
            elif entry.is_dir():
                if entry.path not in ignore_dir:
                    if entry.name=="__pycache__":  #默认不遍历
                        continue
                    Utils.traverseDirectory(entry.path, find, ignore_dir, callback)

class PluginHub(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.lst_ignore_dirs=[]
        self.lst_py = []
        
    def __getitem__(self, index):
        if isinstance(index, str):
            for dic in self:
                if dic["class"]==index:
                    return dic
        else:
            return super().__getitem__(index)
            
    def loadPlugin(self, plugin_directory="plugin", appended_plugin_directory=""):
        def _getIgnoreDirs(entry):
            lines=Utils.readFile(entry.path).split("\n")
            for ln in lines:
                if ln.startswith("#"):
                    continue
                ln=ln.strip()
                if ln and ln not in self.lst_ignore_dirs:
                    path=os.path.normpath(os.path.dirname(entry.path)+"/"+ln)
                    self.lst_ignore_dirs.append(path)
                    
        base_py=os.path.normpath(plugin_directory+"/base.py")
        def _getLstPy(entry):
            if entry.path==base_py:
                self.lst_py.insert(0, entry.path)
            else:
                self.lst_py.append(entry.path)
                
        dirs_plugin =[plugin_directory]
        dirs_plugin += appended_plugin_directory.split(",")
        for _ in dirs_plugin:
            Utils.traverseDirectory(path=_, find=r"^\.dir_ignore$", ignore_dir=set([""]), callback=_getIgnoreDirs)
            #print(self.lst_ignore_dirs)
            Utils.traverseDirectory(path=_, find=r"^.*\.py$", ignore_dir=set(self.lst_ignore_dirs), callback=_getLstPy)
            #print(self.lst_py)
            
        vlst=[]
        for path in self.lst_py:
            code=Utils.readFile(path)
            exec(code, globals())
            
            #找到Plugin类的子类，并完成实例化。
            for v in globals().values():
                if str(v) not in vlst:  #避免重复实例化
                    vlst.append(str(v)) #用List防重入，效率虽慢，但可以避免{}不可哈希的问题。
                    if Plugin in getattr(v, "__mro__", []):  #形如(<class '__main__.LoadFile'>, <class '__main__.Plugin'>, <class 'object'>)
                        if v.__name__!="Plugin":    #obj.__class__.__name__
                            v.plugin_directory=path.split(os.sep)[0]
                            v.plugin_filepath=path
                            obj=v()
                            self.append({"class":obj.__class__.__name__, "obj":obj})  #不用排序，使用默认顺序挺好，方便控制菜单位置
                    
class Application(tk.Tk):
    def __init__(self, pluginhub=[], first_plugin=None):
        super().__init__()
        self.pluginhub=pluginhub
        self.TextItems={"num":10, "list":[]}  #统一管理tk.Text组件，其中list放{"obj":对象}数组
        self.frame_args={"text_tab_num":self.TextItems["num"], "cur_tab_id":0, "cur_text":"", "tab_laboratory":None, "pluginhub":pluginhub}
        self.last_clicked_plugin=None
        self.help_title="？"
        
        self.title("pyoneGUI")
        self.buildMainWindow()
        
        if first_plugin:
            plugin_dic=self.pluginhub[first_plugin]
            if plugin_dic:
                self.pluginRun(plugin_dic["obj"])

    def buildMainWindow(self):
        # 居中显示窗口
        self.centerWindow()

        # 自定义关闭窗口
        self.protocol("WM_DELETE_WINDOW", self.onClose)

        # 创建菜单栏
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        menu_control={}
        for dic in self.pluginhub:
            obj=dic["obj"]
            if obj.enable:
                if obj.menu not in menu_control:
                    menu_control[obj.menu]=tk.Menu(self.menubar, tearoff=0)
                    self.menubar.add_cascade(label=obj.menu, menu=menu_control[obj.menu])
                cmd = partial(self.pluginRun, obj)  #创建新的函数，固定参数，使有参调用变无参调用。使用functools.partial函数创建了一个新的函数cmd，它会调用self.pluginRun方法并传递参数
                menu_control[obj.menu].add_command(label=obj.name, command=cmd)
                
        self.menubar.add_command(label=self.help_title, command=self.onHelp)
        
        # 创建TAB组件
        self.tab_control = ttk.Notebook(self)
        tabs=[]
        for i in range(0, self.TextItems["num"]):
            tabs.append(ttk.Frame(self.tab_control))
            self.tab_control.add(tabs[i], text=str(i))
        self.tab_control.pack(expand=1, fill="both")

        # 创建文本框
        for i in range(0, self.TextItems["num"]):
            obj=tk.Text(tabs[i])
            #obj.pack(expand=1, fill="both")    # expand=1，组件会随着父容器的扩展而扩展；fill="both" 表示将组件填充满可用空间。两者配合，使得text0可以跟随窗口调整而变化。
            obj.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll_y = ttk.Scrollbar(tabs[i], orient=tk.VERTICAL)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            scroll_y.configure(command=obj.yview)
            obj.configure(yscrollcommand=scroll_y.set)
            self.TextItems["list"].append({"obj":obj})

        # 创建实验室选项卡，并且隐藏
        self.tab_laboratory = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_laboratory, text="实验室")
        self.tab_control.hide(self.tab_laboratory)
        
        # 绑定tab切换事件
        self.tab_control.bind("<<NotebookTabChanged>>", self.tabChanged)
        
        # 插件初始化
        self.frame_args["tab_laboratory"]=self.tab_laboratory
        for dic in self.pluginhub:
            dic["obj"].frame_args.update(self.frame_args)
            
    def centerWindow(self):
        # 获取屏幕宽度和高度
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 计算窗口的宽度和高度
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.65)

        # 计算窗口居中时的坐标
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)

        # 设置窗口在屏幕上的位置
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def onClose(self):
        self.destroy()
        os._exit(0)

    def tabChanged(self, event):
        self.frame_args["cur_tab_id"]=event.widget.index("current")
        
    def pluginRun(self, plugin):
        # 设置帮助菜单
        self.last_clicked_plugin=plugin
        title=f"?{self.last_clicked_plugin.name}"
        self.menubar.entryconfig(self.help_title, label=title)
        self.help_title=title
        
        # 操作输出框内容
        if plugin.type=="text":
            if self.frame_args["cur_tab_id"]>=self.frame_args["text_tab_num"]:
                #messagebox.showinfo(title="提示", message="当前窗口不支持此操作")
                text_obj=self.frame_args["laboratory_output_text_obj"]  #如果当前tab是tab_laboratory，且插件绘制界面的时候返回了输出框对象，则其他插件可操作输出框内容。
                if not text_obj:
                    messagebox.showinfo(title="提示", message="plugin.buildWindow()返回值为空")
                    return
            else:
                text_obj=self.TextItems["list"][self.frame_args["cur_tab_id"]]["obj"]
                
            self.frame_args["cur_text"]=text_obj.get("1.0", tk.END+"-1c")  #end-1c表示位置是在end之前的一个字符，否则会多一个换行符，烦人。
            text=plugin._run(self.frame_args)
            text_obj.delete("1.0", tk.END)
            text_obj.insert(tk.END, text)
        else:
            # 删除所有子组件
            children = self.tab_laboratory.winfo_children()  # 获取子组件列表
            for child in children:
                child.destroy()
                
            # 获取行数和列数
            cols, rows = self.tab_laboratory.grid_size()
            # 重置每一行和每一列的权重
            for col in range(cols):
                self.tab_laboratory.grid_columnconfigure(col, weight=0)
            for row in range(rows):
                self.tab_laboratory.grid_rowconfigure(row, weight=0)
            
            self.frame_args["laboratory_output_text_obj"]=plugin.buildWindow()  #插件通过tab_laboratory操作界面，buildWindow函数会返回一个输出文本的tk.Text对象，方便其他插件更改文本
            self.tab_control.add(self.tab_laboratory, text=plugin.name)  #更改选项卡名称为当前插件的名称
            self.tab_control.select(self.tab_laboratory)    #主动切换到当前插件的选项卡上
            
    def showInfoWindow(self, window, title="关于", content="", btns=[]):
        # 创建弹窗
        window.title(title)
        
        # 获取屏幕宽度和高度
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算窗口的宽度和高度
        window_width = int(screen_width * 0.45)
        window_height = int(screen_height * 0.35)
        
        # 计算窗口居中时的坐标
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)

        # 设置窗口在屏幕上的位置
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        if btns:
            # 添加关闭按钮
            btn_frame = ttk.Frame(window)
            btn_frame.pack(side=tk.BOTTOM, pady=5)
            
            for _ in btns:
                btn = ttk.Button(
                    btn_frame, 
                    text=_["text"],
                    command=_["command"] # 需要自行实现该方法
                )
                btn.pack(side=tk.LEFT, padx=5)
        
        # 最后添加文本控件，窗口缩放的动的就是文本控件，避免了窗口过小看不到底层按钮的情况。
        text_obj = tk.Text(window, wrap="word", padx=5, pady=5)
        text_obj.pack(fill="both", expand=True)
        
        # 填充弹框内容
        text_obj.insert("end", content)
        text_obj.config(state="disabled")  # 禁止编辑
                
    def onHelp(self):
        if self.last_clicked_plugin:
            # 设置帮助菜单
            title=f"?{self.last_clicked_plugin.name}"
            self.menubar.entryconfig(self.help_title, label=title)
            self.help_title=title
            
            window = tk.Toplevel(self)
            content = self.last_clicked_plugin.getDescription()
            btns = [
                {"text":"打开插件目录", "command": lambda:[ subprocess.run(['explorer', '/select,', self.last_clicked_plugin.plugin_filepath], shell=True) if sys.platform == "win32" else os.startfile(os.path.dirname(self.last_clicked_plugin.plugin_filepath)), 
                                                          window.destroy()]},
                {"text":"编辑插件脚本", "command": lambda:[ os.startfile(self.last_clicked_plugin.plugin_filepath),
                                                          window.destroy()]},
                {"text":"关闭", "command": window.destroy}]
            self.showInfoWindow(window, title, content, btns)
        else:
            window = tk.Toplevel(self)
            title=f"关于"
            content = f"""\n{pyoneGUI_VERSION}\n\n绿色灵活，路径无关，插件自由，即改即用，所见即所得。助你轻松记录灵感，沉淀知识，并快速复用。"""
            self.showInfoWindow(window, title, content, [{"text":"关闭", "command":window.destroy}])
            
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", dest="help", action="store_true", help="This help text.")
    parser.add_argument("--version", dest="version", action="store_true", help="Display the current version of pyoneGUI.")
    parser.add_argument("python_script", nargs="?", help="By default it starts as pyoneGUI, but if <python_script> is set, it starts as pyone without GUI and executes the <python_script>. <python_script> must end with .py")
    parser.add_argument("-lp", dest="plugin_directory", nargs=1, default=["plugin"], help=f"Load plugin from <PLUGIN_DIRECTORY> when pyoneGUI starts. For example, python {sys.argv[0]} -lp plugin")  #nargs=1 返回的是单元素的列表，而nargs="?"返回的是None或者字符串。
    parser.add_argument("-la", dest="appended_plugin_directory", nargs=1, default=[""], help=f"Load appended plugin from <APPENDED_PLUGIN_DIRECTORY>. For example, python {sys.argv[0]} -la dir1,dir2")
    parser.add_argument("-fp", dest="first_plugin", nargs=1, default=[None], help=f"<FIRST_PLUGIN> will be run first when the pyoneGUI is started. For non-text plugins, this can be used to specify the default view. For example, python {sys.argv[0]} -fp Fscan")
    
    args = parser.parse_args()
    if args.help:
        parser.print_help()
        os._exit(0)
    elif args.version:
        print(pyoneGUI_VERSION)
        os._exit(0)
    elif args.python_script and args.python_script.endswith(".py"):
        code=open(args.python_script, encoding="utf-8").read()
        exec(code, globals())
        os._exit(0)
        
    phub=PluginHub()
    phub.loadPlugin(plugin_directory=args.plugin_directory[0], appended_plugin_directory=args.appended_plugin_directory[0])
    app = Application(pluginhub=phub, first_plugin=args.first_plugin[0])
    app.mainloop()
    
if "__main__"==__name__:
    main()
