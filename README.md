# pyregex

`pyregex` 是一个用 Python 实现的简单正则表达式引擎。它演示了正则表达式的工作原理，并提供了基本的正则表达式功能。

## 特性

- 基本的正则表达式模式匹配
- 支持量词 (*, +, ?, {m,n})
- 贪婪和非贪婪匹配
- 字符类和特殊转义 (\d, \D, \s, \S, \w, \W)
- 捕获组，包括命名组和匿名组
- 模式编译和匹配

## 使用方法

该模块导出了 `match` 函数，可用于将正则表达式模式与字符串进行匹配：

```python
import regex

# 简单匹配
result = regex.match('abc.*def', 'abcdef')
print(bool(result))  # True

# 带捕获组的匹配
result = regex.match('abc(.*)def', 'abczzdef')
if result:
    print(result.groups[1])  # 'zz'
```

## 模块

### regex.py

主模块，包含 `Regex` 类和 `match` 函数，用于模式编译和匹配。

主要函数：
- `Regex(exp)` - 编译正则表达式模式
- `match(exp, s)` - 将模式与字符串进行匹配

### matcher.py

包含核心匹配逻辑和数据结构：

- `Context` - 保存匹配上下文信息
- `Str` - 字符串字面量匹配器
- `Any` - 匹配任意单个字符 (.)
- `Charset` - 字符类匹配器
- `Group` - 组匹配处理
- `GroupMatch` - 存储组匹配信息

## 支持的模式

- `.` - 匹配任意单个字符
- `*` - 匹配前面元素的零次或多次（贪心）
- `+` - 匹配前面元素的一次或多次（贪心）
- `?` - 匹配前面元素的零次或一次（贪心）
- `{m,n}` - 匹配前面元素 m 到 n 次（贪心）
- `*?`, `+?`, `??`, `{m,n}?` - 非贪心版本
- `[]` - 字符类
- `\d`, `\D`, `\s`, `\S`, `\w`, `\W` - 特殊字符类
- `()` - 捕获组
- `(?P<name>...)` - 命名捕获组

## 运行测试

运行测试套件：

```bash
python3 -m unittest regex_test.py
```

## 示例

```python
import regex

# 匹配带捕获组的模式
match_result = regex.match('abc(?P<content>.*)def', 'abc123def')
if match_result:
    print(match_result.groups[1].start)  # 第1组的起始位置
    print(match_result.groups[1].end)    # 第1组的结束位置
    print(match_result.groups[1].name)   # 第1组的名称 ('content')
```