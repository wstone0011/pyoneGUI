# 常用工具

# 环境依赖
```
这些版本下有效，其他版本未测试
Python 3.12.0
tkinter.TkVersion 8.6
pyinstaller 6.2.0
```

# 其他说明
```
打包出来的程序会有命令行窗口，其实留着命令行窗口也挺好，方便看报错日志。
pyinstaller -F main.py --noupx

把py脚本后缀改为pyw，再打包，运行时就没有命令行窗口了。
pyinstaller -F main.pyw --noupx

```
