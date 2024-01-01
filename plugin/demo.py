import json
import base64
import hashlib
import time
import re
import os

# 界面上的菜单顺序默认按照插件子类的定义顺序排列，优先找base.py文件，然后找其他py文件。
# 文件
class loadFile(Plugin):
    menu="文件"
    name="加载文件"
    def run(self, text):
        file = self.filedialogAskopenfilename(initialdir=os.getcwd())  #弹出对话框选择文件，在Plugin基类里实现
        return self.readFile(file)
        
class saveFile(Plugin):
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
        id=self.frame_args["cur_text_id"]
        if id not in self.orders:
            self.orders[id]=False  #reverse  False 升序；True 降序
        else:
            self.orders[id]=not self.orders[id]
            
        words = text.strip().replace("\r\n", "\n").split("\n")
        words.sort(reverse=self.orders[id])
        return "\n".join(words)
        
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
        ips=IPs()  #plugin下的所有类都在globals里，所以可以直接用。IPs的实现在lib目录下的IPs.py
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
        