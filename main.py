import tkinter as tk
from tkinter import ttk
from functools import partial
from tkinter import messagebox
import os
import sys
import argparse
from template import plugin_codes
#----框架中没有使用但在插件中有使用的库----
from tkinter import filedialog
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

pyoneGUI_VERSION="pyoneGUI v1.1"

class PluginHub(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.lst_py = []
        
    def __getitem__(self, index):
        if isinstance(index, str):
            for dic in self:
                if dic["class"]==index:
                    return dic
        else:
            return super().__getitem__(index)
        
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
        
    def traverseDirectory(self, path):
        for entry in os.scandir(path):
            if entry.is_file():
                if entry.path.endswith(".py"):
                    if entry.name=="base.py":
                        self.lst_py.insert(0, entry.path)
                    else:
                        self.lst_py.append(entry.path)
            elif entry.is_dir():
                if entry.name!="lib" and entry.name!="tool" and entry.name!="env":  #这几个目录避免全局调用exec，而是放在插件内部调用，尽量减少全局变量冲突
                    self.traverseDirectory(entry.path)

    def loadPlugin(self, plugin_path="plugin"):
        if not os.path.exists(plugin_path):
            print(f"[!] {plugin_path} is not found, default plugin will be created in the {plugin_path} directory.")
            os.makedirs(plugin_path)
            for py in plugin_codes:
                self.writeFile(plugin_path+"/"+py, plugin_codes[py])
            
        self.traverseDirectory(plugin_path)
        for path in self.lst_py:
            code=self.readFile(path)
            exec(code, globals())

        for v in globals().values():
            if Plugin in getattr(v, "__mro__", []):
                obj=v()
                if obj.__class__.__name__!="Plugin":
                    self.append({"class":obj.__class__.__name__, "obj":obj})  #不用排序，使用默认顺序挺好，方便控制菜单位置

class Application(tk.Tk):
    def __init__(self, pluginhub=[], first_plugin=None):
        super().__init__()
        self.TextItems={"num":10, "list":[]}  #统一管理tk.Text组件，其中list放{"obj":对象}数组
        self.frame_args={"text_tab_num":self.TextItems["num"], "cur_tab_id":0, "cur_text":"", "tab_laboratory":None}
        self.pluginhub=pluginhub
        
        self.title("常用工具")
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
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        menu_control={}
        for dic in self.pluginhub:
            obj=dic["obj"]
            if obj.enable:
                if obj.menu not in menu_control:
                    menu_control[obj.menu]=tk.Menu(menubar, tearoff=0)
                    menubar.add_cascade(label=obj.menu, menu=menu_control[obj.menu])
                cmd = partial(self.pluginRun, obj)  #创建新的函数，固定参数，使有参调用变无参调用。使用functools.partial函数创建了一个新的函数cmd，它会调用self.pluginRun方法并传递参数
                menu_control[obj.menu].add_command(label=obj.name, command=cmd)
        
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
            obj.pack(expand=1, fill="both")    # expand=1，组件会随着父容器的扩展而扩展；fill="both" 表示将组件填充满可用空间。两者配合，使得text0可以跟随窗口调整而变化。
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
        if plugin.type=="text":
            if self.frame_args["cur_tab_id"]>=self.frame_args["text_tab_num"]:
                #messagebox.showinfo(title="提示", message="当前窗口不支持此操作")
                text_obj=self.frame_args["laboratory_output_text_obj"]
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
            children = self.tab_laboratory.winfo_children()  # 获取子组件列表
            for child in children:
                child.destroy()
            self.frame_args["laboratory_output_text_obj"]=plugin.buildWindow()  #插件通过tab_laboratory操作界面，buildWindow函数会返回一个输出文本的tk.Text对象，方便其他插件更改文本
            self.tab_control.add(self.tab_laboratory, text=plugin.name)  #更改选项卡名称为当前插件的名称
            self.tab_control.select(self.tab_laboratory)    #主动切换到当前插件的选项卡上
            
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", dest="help", action="store_true", help="This help text")
    parser.add_argument("--version", dest="version", action="store_true", help="Show version number")
    parser.add_argument("python_script", nargs="?", help="By default it starts as pyoneGUI, but if <python_script> is set, it starts as pyone without GUI and executes the <python_script>. <python_script> must end with .py")
    parser.add_argument("-lp", dest="plugin_directory", nargs=1, default=["plugin"], help="Load plugin from <PLUGIN_DIRECTORY> when pyoneGUI starts")  #nargs=1 返回的是单元素的列表，而nargs="?"返回的是None或者字符串。
    parser.add_argument("-fp", dest="first_plugin", nargs=1, default=[None], help="<FIRST_PLUGIN> will be run first when the pyoneGUI is started. For non-text plugins, this can be used to specify the default view")
    
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
    phub.loadPlugin(plugin_path=args.plugin_directory[0])
    app = Application(pluginhub=phub, first_plugin=args.first_plugin[0])
    app.mainloop()
    
if "__main__"==__name__:
    main()
