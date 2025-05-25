from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageGrab
from pyzbar import pyzbar

class DecodeQRcode(Plugin):
    menu="图文处理"
    name="二维码识别"
    type="laboratory"
    desc=r'''二维码识别，支持拖拽和粘贴。'''
    def buildWindow(self):
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame0 = tk.Frame(tab_laboratory)
        frame0.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        img_label = tk.Label(frame0, text="图片路径：")
        img_label.grid(row=0, column=nexti(i=0))
        self.img_entry = tk.Entry(frame0, width=100)
        self.img_entry.grid(row=0, column=nexti())
        tk.Label(frame0, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_open = tk.Button(frame0, text="打开", command=self.onOpen)
        button_open.grid(row=0, column=nexti(), padx=5)
        button_recognize = tk.Button(frame0, text="识别", command=self.onRecognize)
        button_recognize.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame0, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_help = tk.Button(frame0, text="查看帮助文档", command=self.showHelp)
        button_help.grid(row=0, column=nexti(), padx=5)
        
        # 绑定回车事件
        self.img_entry.bind('<Return>', self.onOpen)

        frame1 = tk.Frame(tab_laboratory)
        frame1.grid(row=1, column=0, pady=5, sticky=tk.NSEW)
        frame1.grid_columnconfigure(0, weight=1, minsize=200) # 图片区
        frame1.grid_columnconfigure(1, weight=1) # 文本区
        frame1.grid_rowconfigure(0, weight=1)
        
        # 图片显示区 (左侧)
        image_display_frame = tk.Frame(frame1, relief=tk.SUNKEN, borderwidth=1, bg="lightgrey")
        image_display_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0,5))
        self.image_label = tk.Label(image_display_frame, text="拖拽图片到此\n或Ctrl+V粘贴截图", bg="lightgrey", takefocus=1)
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # 绑定拖拽事件到图片显示Label
        self.image_label.drop_target_register(DND_FILES)
        self.image_label.dnd_bind('<<Drop>>', self.onDropImage)
        
        # 绑定Ctrl+V用于粘贴
        self.image_label.bind("<Button-1>", lambda event: self.image_label.focus_set())
        self.image_label.bind("<Control-v>", self.onPasteImage)  #先选中image_label，再Ctrl+V
        
        # 文本输出区 (右侧)
        text_output_frame = tk.Frame(frame1) # 用于容纳文本框和滚动条
        text_output_frame.grid(row=0, column=1, sticky=tk.NSEW)
        text_output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = tk.Text(text_output_frame)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y = ttk.Scrollbar(text_output_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.configure(command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scroll_y.set)
        
        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(1, weight=1)
        
        self.current_pil_image = None
        # 设置options
        self.options=Options()
        dic={"Name":"IMAGE_PATH", "Current Setting":"", "Required":"no", "Description":"图片路径", "obj":self.img_entry }
        self.options.append(dic)
        dic={"Name":"IMAGE_DATA", "Current Setting":"", "Required":"yes", "Description":"图片数据", "obj":"(image data)" }
        self.options.append(dic)
        return self.output_text
        
    def onOpen(self, event=None):
        filepath = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=(("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"), ("所有文件", "*.*"))
        )
        if filepath:
            pil_image = Image.open(filepath)
            self.img_entry.delete(0, tk.END)
            self.img_entry.insert(0, os.path.normpath(filepath))
            self.displayImage(pil_image)
    
    def onRecognize(self, event=None):
        if not self.current_pil_image:
            return
            
        decoded_objects = pyzbar.decode(self.current_pil_image)
        msg=""
        if decoded_objects:
            msg += (f"\n从图片中识别到的二维码信息：\n")
            for obj in decoded_objects:
                # 将解码后的数据从 bytes 转换为 string (通常是 utf-8)
                decoded_data = obj.data.decode('utf-8')
                msg+=f"类型 (Type): {obj.type}\n"
                msg+=f"内容 (Data): {decoded_data}\n"
                msg+=f"位置 (Rect): {obj.rect}\n"
                msg+="-" * 20+"\n"
        else:
            msg += "\n未识别到二维码信息。\n"
            
        self.log(msg)
            
    def showHelp(self, event=None):
        super().showHelp()

    def onDropImage(self, event):
        # event.data 通常是包含文件路径的字符串，可能包含花括号和空格
        # 使用 TkinterDnD 提供的 splitlist 方法处理更安全
        #print(event.data)
        filepaths = self.image_label.tk.splitlist(event.data)
        if filepaths:
            filepath = filepaths[0] # 取第一个文件
            # 简单检查下是否是常见图片后缀 (可选)
            if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                pil_image = Image.open(filepath)
                self.img_entry.delete(0, tk.END)
                self.img_entry.insert(0, os.path.normpath(filepath))
            
                self.displayImage(pil_image)
            else:
                self.log(f"拖拽了不支持的文件类型: {os.path.normpath(filepath)}\n")
        else:
            self.log("拖拽事件未获取到文件路径。\n")
            
    def onPasteImage(self, event):
        try:
            pil_image = ImageGrab.grabclipboard()
            if pil_image:
                if not isinstance(pil_image, Image.Image):
                    # ImageGrab.grabclipboard() 在某些情况下可能返回文件路径列表 (例如从文件管理器复制文件)
                    # 这里我们主要处理位图数据
                    if isinstance(pil_image, list) and pil_image:
                        try:
                            # 尝试打开列表中的第一个路径 (如果它是图片)
                            filepath = pil_image[0]
                            pil_image = Image.open(pil_image[0])
                            self.img_entry.delete(0, tk.END)
                            self.img_entry.insert(0, os.path.normpath(filepath))
                        except Exception:
                            self.log("剪贴板内容不是直接的图像数据，也无法作为图片文件打开。\n")
                            return
                    else:
                        self.log("剪贴板内容不是有效的图像数据。\n")
                        return
                else:
                    self.img_entry.delete(0, tk.END)
                    self.img_entry.insert(0, "来自剪贴板")
                self.displayImage(pil_image)
            else:
                self.log("剪贴板中没有图片。\n")
                
        except Exception as e:
            self.log(f"粘贴操作失败或剪贴板无图片: {e}\n")
            
    def displayImage(self, pil_image):
        """
        显示图片到image_label。
        参数: pil_image 是PIL.Image对象。
        """
        try:
            self.current_pil_image = pil_image
            
            # 获取Label的当前尺寸以缩放图片
            # 需要延迟一下获取，否则winfo_width/height可能为1
            self.image_label.update_idletasks()
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()

            if label_width <= 1 or label_height <= 1: # 如果窗口还未完全绘制，给个默认值
                label_width = 300
                label_height = 300
            
            img_copy = self.current_pil_image.copy()
            img_copy.thumbnail((label_width-5, label_height-5), Image.Resampling.LANCZOS) # 减去一点边距

            self.current_photo_image = ImageTk.PhotoImage(img_copy)  # 保留对PhotoImage的引用，否则会被回收，导致无法显示图片
            self.image_label.config(image=self.current_photo_image, text="") # 清空文字
            self.log(f"图片已加载。尺寸: {self.current_pil_image.width}x{self.current_pil_image.height}\n")
            
            self.onRecognize()

        except FileNotFoundError:
            self.log("错误: 图片文件未找到。\n")
        except Exception as e:
            self.log(f"错误: 无法加载图片 - {e}\n")
            
class WeChatOCR1(DecodeQRcode):
    menu="图文处理"
    name="微信OCR（kanadeblisst00版本）"
    type="laboratory"
    is_initialized = False
    desc=r'''
源自 https://github.com/kanadeblisst00/wechat_ocr
本插件使用的微信版本为3.9.12.51，WeChatOCR版本为7079。

相关项目：
https://github.com/EEEEhex/QQImpl
https://github.com/swigger/wechat-ocr
'''
    def onRecognize(self, event=None):
        if not self.current_pil_image:
            return
            
        def ocr_result_callback(img_path, results):
            lines=[]
            for dic in results["ocrResult"]:
                lines.append( dic["text"])
            
            self.content="\n".join(lines)
            #self.log("\n".join(lines))  # 对象都在，但直接调用会卡住
            
        OCR_MAX_TASK_ID=32
        self.content=""
        
        if not self.is_initialized:
            self.is_initialized=True
            wechat_path = f"{self.plugin_directory}/_dependencies/WeChat/[3.9.12.51]"
            wechatocr3_path = f"{self.plugin_directory}/_dependencies/WeChatOCR/7079/extracted/WeChatOCR.exe"
            load_py_module(name="wechat_ocr", location=f"{self.plugin_directory}/_dependencies/kanadeblisst00/wechat_ocr/__init__.py")
            from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
            
            self.ocr_manager = OcrManager(wechat_path)
            # 设置WeChatOcr目录
            self.ocr_manager.SetExePath(wechatocr3_path)
            # 设置微信所在路径
            self.ocr_manager.SetUsrLibDir(wechat_path)
            # 设置ocr识别结果的回调函数
            self.ocr_manager.SetOcrResultCallback(ocr_result_callback)
            # 启动ocr服务
            self.ocr_manager.StartWeChatOCR()
            
        output_dir="output"
        os.makedirs(output_dir, exist_ok=True)
        now=int(time.time())
        tmpfile=f"{output_dir}/tmp_{now}.png"
        self.current_pil_image.save(tmpfile, format="png")    #通通转成png
        
        #图片识别
        self.ocr_manager.DoOCRTask(tmpfile)
        while self.ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
             time.sleep(0.1)
        
        # 识别输出结果
        #self.ocr_manager.KillWeChatOCR()
        
        self.clearLog()
        self.log(self.content)    #self.content在ocr_result_callback里被设置
        self.log("\n")
        
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
        
class WeChatOCR2(DecodeQRcode):
    menu="图文处理"
    name="微信OCR（swigger版本）"
    type="laboratory"
    is_initialized = False
    desc=r'''
源自 https://github.com/swigger/wechat-ocr
本插件使用的微信版本为3.9.12.51，WeChatOCR版本为7079。

相关项目：
https://github.com/EEEEhex/QQImpl
https://github.com/kanadeblisst00/wechat_ocr
'''
    def onRecognize(self, event=None):
        if not self.current_pil_image:
            return
            
        if not self.is_initialized:
            self.is_initialized=True
            wechat_path = f"{self.plugin_directory}/_dependencies/WeChat/[3.9.12.51]"
            wechatocr3_path = f"{self.plugin_directory}/_dependencies/WeChatOCR/7079/extracted/WeChatOCR.exe"
            self.wcocr = load_py_module(name="wcocr", location=f"{self.plugin_directory}/_dependencies/swigger/wcocr.pyd")
            self.wcocr.init(wechatocr3_path, wechat_path)
        
        output_dir="output"
        os.makedirs(output_dir, exist_ok=True)
        now=int(time.time())
        tmpfile=f"{output_dir}/tmp_{now}.png"
        self.current_pil_image.save(tmpfile, format="png")    #通通转成png
        
        res = self.wcocr.ocr(tmpfile)
        #self.log(json.dumps(res))
        
        lines=[]
        for dic in res["ocr_response"]:
            lines.append( dic["text"])
            
        self.clearLog()
        self.log("\n".join(lines))
        self.log("\n")
        
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
        
class WeChatOcrBatch(Plugin):
    menu="图文处理"
    name="OCR批量扫描（swigger版本）"
    type="laboratory"
    is_initialized = False
    is_running = False
    
    def buildWindow(self):
        if not self.is_initialized:
            self.is_initialized=True
            wechat_path = f"{self.plugin_directory}/_dependencies/WeChat/[3.9.12.51]"
            wechatocr3_path = f"{self.plugin_directory}/_dependencies/WeChatOCR/7079/extracted/WeChatOCR.exe"
            self.wcocr = load_py_module(name="wcocr", location=f"{self.plugin_directory}/_dependencies/swigger/wcocr.pyd")
            self.wcocr.init(wechatocr3_path, wechat_path)
            
        tab_laboratory = self.frame_args["tab_laboratory"]
        frame0 = tk.Frame(tab_laboratory)
        frame0.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        imgs_label = tk.Label(frame0, text="图片目录：")
        imgs_label.grid(row=0, column=nexti(i=0))
        self.imgs_entry = tk.Entry(frame0, width=100)
        self.imgs_entry.grid(row=0, column=nexti())
        tk.Label(frame0, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_open = tk.Button(frame0, text="打开", command=self.onOpen)
        button_open.grid(row=0, column=nexti(), padx=5)
        button_recognize = tk.Button(frame0, text="批量识别", command=self.onRecognize)
        button_recognize.grid(row=0, column=nexti(), padx=5)
        tk.Label(frame0, width=5).grid(row=0, column=nexti(), padx=5)  #占位
        button_help = tk.Button(frame0, text="查看帮助文档", command=self.showHelp)
        button_help.grid(row=0, column=nexti(), padx=5)

        frame1 = tk.Frame(tab_laboratory)
        frame1.grid(row=1, column=0, pady=5, sticky=tk.NSEW)
        self.output_text = tk.Text(frame1)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y = ttk.Scrollbar(frame1, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.configure(command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scroll_y.set)
        
        # 绑定回车事件
        self.imgs_entry.bind('<Return>', self.onRecognize)

        # 设置网格布局列和行权重
        tab_laboratory.grid_columnconfigure(0, weight=1)
        tab_laboratory.grid_rowconfigure(1, weight=1)
        
        # 设置options
        self.options=Options()
        dic={"Name":"IMAGE_DIR", "Current Setting":"", "Required":"yes", "Description":"图片目录", "obj":self.imgs_entry }
        self.options.append(dic)
        return self.output_text
        
    def onOpen(self, event=None):
        dir_path = filedialog.askdirectory(
            title="选择图片目录"
        )
        if dir_path:
            self.imgs_entry.delete(0, tk.END)
            self.imgs_entry.insert(0, os.path.normpath(dir_path))
        
    def onRecognize(self, event=None):
        options=self.getOptions()
        imgs_dir=options["IMAGE_DIR"]
        
        if self.is_running:
            self.log("[!] 正在运行中，请等待任务完成或者终止任务。\n")
            return
        
        self.is_running=True
        outfile="out_{now}.txt".format(now=int(time.time()))
        self.log(f"[+] {imgs_dir}\n")
        self.log(f"save to {outfile}\n\n")
        
        def fn():
            try:
                def _callback_ocr(entry):
                    self.log(f"[+] {entry.path}\n")
                    try:
                        content = self.ocrOneImg(entry.path)
                        with open(outfile, "a", encoding="utf-8") as fout:
                            fout.write(content)
                        #self.log(res)
                    except Exception as e:
                        print(e)
                    #self.log("\n\n")
                    
                Utils.traverseDirectory(path=imgs_dir, find=r'(?i)^.*\.(png|jpe?g|bmp|tiff?|webp)$', ignore_dir=set([""]), callback=_callback_ocr)
                # 正则表达式解释：
                # (?i)      -> 不区分大小写
                # \.(...)   -> 匹配扩展名点符号
                # png       -> 匹配.png
                # jpe?g     -> 匹配.jpg或.jpeg
                # bmp       -> 匹配.bmp
                # tiff?     -> 匹配.tif或.tiff
                # webp      -> 匹配.webp
                # $         -> 确保扩展名在字符串末尾
                
                self.log("[*] over")
                
            except Exception as e:
                print(e)
            self.is_running=False
            
        self.thread = threading.Thread(target=fn)
        self.thread.start()
        
    def onStop(self, event=None):
        self.log("[*] onStop\n")
        #self.thread._stop()  #无效
        
    def ocrOneImg(self, imgs_path):
        res = self.wcocr.ocr(imgs_path)
        #self.log(json.dumps(res))
        
        lines=[]
        for dic in res["ocr_response"]:
            lines.append( dic["text"] )
            
        return "\n".join(lines)
        