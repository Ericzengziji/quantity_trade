[toc]
# 前言
个人理解代码规范的好处：
+ 便于运维。
+ 便于交流。
+ 提升质量。

让自己和别人都看得懂，并快速定位和解决问题，在大项目维护上更能体现价值

# 风格规范
### 命名规则
* protected/private名字解释：
  * 单/双下划线开头的函数或类不会被from module import *导入
  * 双下划线开头的类成员函数/变量会被python内部改写，加上类名前缀，以避免与派生类同名成员冲突
  * 单/双下划线都不能真正意义上阻止用户访问，只是module开发者与使用者之间的”约定”
* 双下划线开头、结尾的名字对python解释器有特殊意义，可能与内部关键字冲突

+ [强制] 类(包括异常)名使用首字母大写驼峰式命名
+ [强制] 常量使用全大写字母，单词间用下划线分隔
+ [强制] 其它情况(目录/文件/package/module/function/method/variable/parameter)一律使用全小写字母，单词间用下划线分隔
+ [建议] protected成员使用单下划线前缀，private成员使用双下划线前缀
+ [建议] 禁止使用双下划线开头，双下划线结尾的名字(类似__init__)

> 示例
```
ClassName, ExceptionName

GLOBAL_CONSTANT_NAME, CLASS_CONSTANT_NAME,

module_name, package_name, method_name, function_name, global_var_name, instance_var_name, function_parameter_name, local_var_name

_InternalClassName, _INTERNAL_CONSTANT_NAME, _internal_function_name, _protected_member_name, __private_member_name
```


# 编程实践
### python解释器
* python的安装位置在不同服务器上可能有差异，所以建议用env python的方式启动，使用当前环境下的默认python
* 百度不同服务器上安装的python版本可能有差异，如果对python程序的可移植性要求很高，可以自带python环境发布

+ [建议] 模块的主程序必须以`#!/usr/bin/env python`开头。如果明确只支持某个python版本，请带上python版本号
+ [建议] 模块可以自带某个特定版本的python环境一起发布。需要在程序的启动脚本中指定具体使用的python解释器程序
+ [建议] 推荐使用2.7版本(含)以上的python解释器

### 文件编码
* python默认使用ASCII编码解析代码文件。若代码中含有非ASCII字符，无论在字符串中还是注释中，都会导致python异常。必须在文件头标明，告知python解释器正确的字符编码
* UTF8编码是自同步编码，进行字符串处理更方便、通用。

+ [强制] 如果文件包含非ASCII字符，必须在文件前两行标明字符编码。
+ [强制] 只能使用UTF-8或GB18030编码。推荐使用UTF-8编码，如果项目确有需要，可以使用GB18030
+ [建议] 如非必要，应尽量避免使用reload(sys); sys.setdefaultencoding('utf-8')

### 类继承
若不继承自object，property将不能正常工作，且与python3不兼容。
+ [建议] 如果一个类没有基类，必须继承自object类
> YES
```buildoutcfg
class SampleClass(object):
    pass

class OuterClass(object):

    class InnerClass(object):
        pass

class ChildClass(ParentClass):
    """Explicitly inherits from another class already."""
```
> NO 
```
class SampleClass:
        pass

class OuterClass:

    class InnerClass:
        pass
```

### 字符串拼接
python中字符串是不可修改对象。每次+=会创建一个新的字符串，性能较差。
+ [建议] 不要使用+=拼接字符串列表，应该使用join。但需确保列表中全是Strings类型，如果有Numbers等其它类型，会报TypeError错误，当不确定时建议仍使用+=拼接字符串
> YES
```
items = ['<table>']
for last_name, first_name in employee_list:
    items.append('<tr><td>%s, %s</td></tr>' % (last_name, first_name))
    items.append('</table>')
employee_table = ''.join(items)
```
>NO
```buildoutcfg
employee_table = '<table>'
for last_name, first_name in employee_list:
    employee_table += '<tr><td>%s, %s</td></tr>' % (last_name, first_name)
employee_table += '</table>'
```

### 主程序
若模块不可导入会导致pydoc或单测框架失败
+ [建议] 所有module都必须可导入。如需要执行主程序，必须检查__name__ == '__main__'
> YES
```buildoutcfg
def main():
      ...

if __name__ == '__main__':
    main()
```

### 单元测试
+ [建议] 推荐使用UnitTests做单元测试。是否需要做单元测试以及目标单测覆盖率 **自行决定**。
+ [建议] 推荐测试代码放在单独的test目录中。如果被测试代码文件名为xxx.py，那么测试代码文件应该被命名为xxx_test.py
> EXAMPLE
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import math

class MathTestCase(unittest.TestCase):
    def test_sqrt(self):
        self.assertEqual(math.sqrt(4) * math.sqrt(4), 4)

if __name__ == "__main__":
    unittest.main()
```

### 日志输出
+ 日志格式尽量与百度传统的ullog/comlog保持一致。方便统一日志处理
+ 独立的warning/error/critical日志方便发现、追查线上问题

+ [建议] 推荐使用python自带的logging库打印日志。
+ [建议] 推荐默认日志格式："%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s", 时间格式："%Y-%m-%d%H:%M:%S"
+ [建议] 推荐线上程序使用两个日志文件：一个专门记录warning/error/critical日志，另一个记录所有日志。
> EXAMPLE
```
import os
import logging
import logging.handlers

def init_log(log_path, level=logging.INFO, when="D", backup=7,
             format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
             datefmt="%m-%d %H:%M:%S"):
    """
    init_log - initialize log module

    Args:
    log_path - Log file path prefix.
    Log data will go to two files: log_path.log and log_path.log.wf
    Any non-exist parent directories will be created automatically
    level - msg above the level will be displayed
    DEBUG < INFO < WARNING < ERROR < CRITICAL
    the default value is logging.INFO
    when - how to split the log file by time interval
    'S' : Seconds
    'M' : Minutes
    'H' : Hours
    'D' : Days
    'W' : Week day
    default value: 'D'
    format - format of the log
    default format:
    %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
    INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
    backup - how many backup file to keep
    default value: 7

    Raises:
    OSError: fail to create log directories
    IOError: fail to open log file
    """

    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger()
    logger.setLevel(level)

    dir = os.path.dirname(log_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.wf",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

你可以把上面的代码拷贝到自己的项目中。在程序初始化时，调用init_log即可使日志打印符合规范
```buildoutcfg
import log def main(): 
    log.init_log("./log/my_program") # 日志保存到./log/my_program.log和./log/my_program.log.wf，按天切割，保留7天 
    logging.info("Hello World!!!")
```


# 语言规范

### 全局变量
全局变量破坏程序封装性，使代码维护困难
+ [强制] 禁止使用全局变量。除了以下例外：脚本默认参数模块级常量
+ [强制] 如果定义全局变量，必须写在文件头部。

### import
1. 避免冲突。调用关系简单明了，x.obj表示obj对象定义在模块x中
2. 避免模块名冲突，查找包更容易。部署时保持项目结构，使用virtualenv等创建隔离的Python环境，并配置需要的PYTHONPATH
+ [建议] 禁止使用from xxx import yyy语法直接导入类或函数(即yyy只能是module或package，不能是类或函数)
+ [建议] 禁止使用from xxx import *
+ [建议] import时必须使用package全路径名(相对PYTHONPATH)，禁止使用相对路径(相对当前路径)，禁止使用sys.path.append('../../')等类似操作改变当前环境变量
> YES
```
from Crypto.Cipher import AES
import os
os.unlink(path)
```

> NO
```
# os已经是最底下的模块了
from os import unlink
unlink(path)
```





# python的婵
```
The Zen of Python

 Beautiful is better than ugly.
 Explicit is better than implicit.
 Simple is better than complex.
 Complex is better than complicated.
 Flat is better than nested.
 Sparse is better than dense.
 Readability counts.
 Special cases aren't special enough to break the rules.
 Although practicality beats purity.
 Errors should never pass silently.
 Unless explicitly silenced.
 In the face of ambiguity, refuse the temptation to guess.
 There should be one-- and preferably only one --obvious way to do it.
 Although that way may not be obvious at first unless you're Dutch.
 Now is better than never.
 Although never is often better than |right| now.
 If the implementation is hard to explain, it's a bad idea.
 If the implementation is easy to explain, it may be a good idea.
 Namespaces are one honking great idea -- let's do more of those!

-- by Tim Peters
```