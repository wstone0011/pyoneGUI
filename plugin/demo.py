import json
import base64
import hashlib
import time
import re
import os
from urllib.parse import parse_qs, unquote

# 界面上的菜单顺序默认按照插件子类的定义顺序排列，优先找base.py文件，然后找其他py文件。
# 文件
class LoadFile(Plugin):
    menu="文件"
    name="加载文件"
    def run(self, text):
        #弹出对话框选择文件，在Plugin基类里实现
        file = self.filedialogAskopenfilename(initialdir=None)
        if file:
            text=self.readFile(file)
        return text
        
class LoadFile2Hex(Plugin):
    menu="文件"
    name="加载文件为Hex编码"
    def run(self, text):
        file = self.filedialogAskopenfilename(initialdir=None)
        if file:
            with open(file, 'rb') as f:
                binary_data = f.read()
                return binary_data.hex()
        return text
        
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
        
class RemoveSpace(Plugin):
    menu="文本处理"
    name="去除空格"
    def run(self, text):
        if not text:
            return ""
        return text.replace(" ", "")
        
class RemoveMultiLines(Plugin):
    menu="文本处理"
    name="去除多余换行符"
    def run(self, text):
        if not text:
            return ""
        text=text.replace("\r\n", "\n")
        text=re.sub(r"\n+", r"\n", text)
        return text
    
class RemoveNewline(Plugin):
    menu="文本处理"
    name="去除换行符"
    def run(self, text):
        if not text:
            return ""
        text=text.replace("\n", "")
        return text
        
class StringUnescaper(Plugin):
    menu="文本处理"
    name="字符串反转义"
    desc=r'''将字符串中的转义序列（如\\、\'、\n、\t）转换为实际字符。转换效果如下：

C:\\Windows\\System32  ->  C:\Windows\System32
{"a": "ab\'c"}         ->  {"a": "ab'c"}
'{"a": "ab\'c"}'       ->  {"a": "ab'c"}
'''
    def run(self, text):
        if not text:
            return ""
        if text.startswith("'"):
            text=text[1:]
        if text.endswith("'"):
            text=text[:-1]
        local_vars={}
        exec(r'''res='$$$TEXT$$' '''.replace('$$$TEXT$$', text), local_vars)
        return local_vars["res"]
    
class IpExtractor(Plugin):
    menu="文本处理"
    name="IP提取"
    def run(self, text):
        if not text:
            return ""
        REGEXP_IPV4 = r"(?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))"
        REGEXP_IPV4_MASK = r"(?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))/(?:[0-9]|[1-2][0-9]|3[0-2])"
        REGEXP_IPV4_RANGE = r"(?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))\-(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))"
        REGEXP_IPV4_RANGE2 = r"(?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))\-(?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))"
        pattern="((?:{REGEXP_IPV4_RANGE2})|(?:{REGEXP_IPV4_RANGE})|(?:{REGEXP_IPV4_MASK})|(?:{REGEXP_IPV4}))(?:[^0-9]|$)".format(REGEXP_IPV4=REGEXP_IPV4, REGEXP_IPV4_MASK=REGEXP_IPV4_MASK, REGEXP_IPV4_RANGE=REGEXP_IPV4_RANGE, REGEXP_IPV4_RANGE2=REGEXP_IPV4_RANGE2)  #要把REGEXP_IPV4_RANGE2放在前面，否则提前匹配结束，和预期不符。(?:XX)表示匹配但不捕获
        res=re.findall(pattern, text)
        return "\n".join(res)
        
class IpRemoveDuplicates(Plugin):
    menu="文本处理"
    name="IP去重"
    def run(self, text):
        if not text:
            return ""
        local_vars={}
        exec(self.readFile("plugin/lib/IPs.py"), local_vars)  #exec(code, globals()) 有效，但怕污染全局变量，尤其是插件多了之后；
        IPs=local_vars["IPs"]                                 #exec(code, locals())  只能修改局部变量副本，没什么用
        
        ips=IPs()  #IPs的实现在lib目录的IPs.py
        REGEXP_IPV4 = r"((?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5])))(?:[^0-9]|$)"  #^表示取反，即从数字开始，但最后要非数字
        res=re.findall(REGEXP_IPV4, text)
        for _ in res:
            ips|=IPs(_)
        REGEXP_IPV4_MASK = r"((?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))/(?:[0-9]|[1-2][0-9]|3[0-2]))(?:[^0-9]|$)"
        res=re.findall(REGEXP_IPV4_MASK, text)
        for _ in res:
            ips|=IPs(_)
        REGEXP_IPV4_RANGE = r"((?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))\-(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5])))(?:[^0-9]|$)"
        res=re.findall(REGEXP_IPV4_RANGE, text)
        for _ in res:
            ips|=IPs(_)
        REGEXP_IPV4_RANGE2 = r"((?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5]))\-(?:(?:(?:\d{1,2})|(?:1\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\.){3}(?:(?:1\d{2})|(?:\d{1,2})|(?:2[0-4]\d)|(?:25[0-5])))(?:[^0-9]|$)"
        res=re.findall(REGEXP_IPV4_RANGE2, text)
        for _ in res:
            ips|=IPs(_)
        return str(ips)
        
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
        
class Hex2CArray(Plugin):
    menu="编码解码"
    name="Hex转C数组"
    def run(self, text):
        if not text:
            return ""
            
        c_code = "unsigned char data[] = {\n"
        for i in range(0, len(text), 2):
            byte = text[i:i+2]
            c_code += f"0x{byte}"
            if i < len(text) - 2:
                c_code += ", "
            if (i + 2) % 32 == 0:
                c_code += "\n"
        c_code += "};"
        return c_code
        
class Hex2PythonArray(Plugin):
    menu="编码解码"
    name="Hex转Python数组"
    def run(self, text):
        if not text:
            return ""
        
        py_code = "data = [\n"
        for i in range(0, len(text), 2):
            byte = text[i:i+2]
            py_code += f"0x{byte}"
            if i < len(text) - 2:
                py_code += ", "
            if (i + 2) % 32 == 0:
                py_code += "\n"
        py_code += "]"
        return py_code

class XWwwFormUrlencoded2Json(Plugin):
    menu="编码解码"
    name="URL查询字符串转json格式"
    desc=r'''形如：a=1&b=2 -> {"a": "1", "b": "2"}'''
    def run(self, text):
        #从application/x-www-form-urlencoded转application/json格式
        if not text:
            return ""
            
        dic={}
        decoded_params = parse_qs(text)
        for key, values in decoded_params.items():
            decoded_values = [value for value in map(unquote, values)]
            #print(key, decoded_values)
            if len(decoded_values)==1:
                dic[key]=decoded_values[0]
            else:
                dic[key]=decoded_values
        return json.dumps(dic)
        
# 加密解密
class HashIdentifier(Plugin):
    menu="加密解密"
    name="哈希算法识别（hash-identifier）"
    desc=r'''参考 https://github.com/blackploit/hash-identifier/blob/master/hash-id.py'''
    def run(self, text):
        if not text:
            return ""
            
        python_path=sys.executable
        py_path=os.path.normpath(os.getcwd()+"/"+self.plugin_directory+"/_lib/hash-id.py")  #有对hash-id.py进行简单修改
        cmd=[python_path, py_path, text.strip()]
        logs=[]
        self.executeCommand(cmd, cwd=None, logfunc=lambda o:logs.append(o) )
        result =f"[!] {self.desc}\n\n"
        result+=os.path.normpath(f"[+] {' '.join(cmd)}\n")
        result+="".join(logs)+"\n"
        return result
        
class Md5(Plugin):
    menu="加密解密"
    name="md5"
    def run(self, text):
        if not text:
            return ""
        h = hashlib.md5()
        h.update(text.encode('utf-8'))
        return h.hexdigest()
        
class Sha1(Plugin):
    menu="加密解密"
    name="sha1"
    def run(self, text):
        if not text:
            return ""
        h = hashlib.sha1()
        h.update(text.encode('utf-8'))
        return h.hexdigest()
        
class Sha256(Plugin):
    menu="加密解密"
    name="sha256"
    def run(self, text):
        if not text:
            return ""
        h = hashlib.sha256()
        h.update(text.encode('utf-8'))
        return h.hexdigest()
        
# 代码执行
class ExecPython(Plugin):
    menu="代码执行"
    name="执行Python代码(exec执行)"
    def run(self, text):
        if not text:
            return ""
        try:
            def fn():
                local_vars={}
                exec(text, local_vars)  #虽然用了local_vars，但import的库仍然会影响全局。
                
            thread = threading.Thread(target=fn)
            thread.start()
        except Exception as e:
            print(e)
        return text
        
class ExecPython2(Plugin):
    menu="代码执行"
    name="执行Python代码(subprocess.Popen调用)"
    def run(self, text):
        if not text:
            return ""
        try:
            def fn():
                if sys.executable.endswith(r"\python.exe"):
                    command = sys.executable
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    output, _ = process.communicate(input=text)
                    if output:
                        print(output, end="")
                    
                else:
                    print(sys.executable)
                    print("[!] unsupported operation")
                
            thread = threading.Thread(target=fn)
            thread.start()
        except Exception as e:
            print(e)
        return text
        
class EvalPython(Plugin):
    menu="代码执行"
    name="数值计算（eval）"
    desc=r'''形如，(1+2)*3 -> 9=(1+2)*3'''
    def run(self, text):
        if not text:
            return ""
        answer = eval(text)
        return "{answer}={expression}".format(answer=answer, expression=text)
        
# 逆向分析
class Pyinstxtractor(Plugin):
    menu="逆向分析"
    name="pyinstaller解包（pyinstxtractor）"
    desc=r'''本功能源自: https://github.com/extremecoders-re/pyinstxtractor ，最后一次提交记录：Commits on Feb 22, 2025'''
    def run(self, text):
        result=f"[!] {self.desc}"
        result+="\n\n"
        
        file = self.filedialogAskopenfilename(initialdir=None)
        if not file:
            return text
            
        python_path=sys.executable
        py_path=os.path.normpath(os.getcwd()+"/"+self.plugin_directory+"/_lib/pyinstxtractor.py")
        cmd=[python_path, py_path, file]
        logs=[]
        self.executeCommand(cmd, cwd=os.path.dirname(file), logfunc=lambda o:logs.append(o) )
        result+=os.path.normpath(f"[+] {' '.join(cmd)}\n")
        result+="".join(logs)+"\n"
        return result
        
class Uncompyle6(Plugin):
    menu="逆向分析"
    name="pyc反编译（uncompyle6）"
    desc="本功能源自: https://github.com/rocky/python-uncompyle6"
    def run(self, text):
        result=f"[!] {self.desc}\n\n"
        file = self.filedialogAskopenfilename(initialdir=None, filetypes=[("Compiled Python Files", "*.pyc"), ("All Files", "*")])  #弹出对话框选择文件，在Plugin基类里实现
        if not file:
            return text
        
        uncompyle6_path=f"{os.path.dirname(sys.executable)}/Scripts/uncompyle6"
        cmd=[uncompyle6_path, "-o", "./", file]  # a.pyc -> a.pyc_dis
        logs=[]
        self.executeCommand(cmd, cwd=os.path.dirname(file), logfunc=lambda o:logs.append(o) )
        result+=os.path.normpath(f"[+] {' '.join(cmd)}\n")
        result+="".join(logs)+"\n"
        result+=file+" 反编译结束。"
        return result

# 系统管理
class InfoPythonVersion(Plugin):
    menu="系统管理"
    name="查看Python版本"
    def run(self, text):
        import sys
        return sys.version
        
class InfoSysPath(Plugin):
    menu="系统管理"
    name="查看sys.path"
    def run(self, text):
        import sys
        return "\n".join(sys.path)
        
class InfoModules(Plugin):
    menu="系统管理"
    name="查看依赖库信息"
    def run(self, text):
        import sys
        res=""
        for module_name in list(sys.modules):
            # 获取模块对象
            module = sys.modules.get(module_name)
            
            # 获取版本号（兼容不同模块的版本属性）
            version = ""
            if module:
                try:
                    # 优先尝试标准版本属性
                    version = getattr(module, '__version__', None)
                    
                    # 部分模块使用 VERSION 属性（如Django）
                    if version is None:
                        version = getattr(module, 'VERSION', None)
                        
                    # 部分模块使用 __version 属性（如deepspeed）
                    if version is None:
                        version = getattr(module, '__version', None)
                        
                    if version is None:
                        version = getattr(module, 'version', None)
                        
                    # 其他特殊情况处理
                    if version is None and module_name == 'sys':
                        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                        
                    version = version or ""  # 最终兜底
                except Exception as e:
                    version = f"Error: {str(e)}"
            
            if version:
                res += f"{module_name} ({version})\n"
            else:
                res += f"{module_name}\n"
        return res

class InfoPlugin(Plugin):
    menu="系统管理"
    name="查看插件列表"
    def run(self, text):
        res=""
        for _ in self.frame_args["pluginhub"]:
            obj=_["obj"]
            res+=f"{obj.menu}/{obj.name}{'' if obj.enable else f' （已禁用，类名: {obj.__class__.__name__}，路径: {obj.plugin_filepath} ）'}\n"
        return res
        