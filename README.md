# pyregex

一个用 Python 实现的简单正则表达式引擎，包含两种不同的实现方式：基于回溯的匹配器和基于 NFA 的匹配器。这个项目展示了正则表达式引擎的内部工作原理。

## 两种实现

### 1. Regex（基于回溯）

`regex` 包提供了传统的基于回溯的正则表达式引擎，支持捕获组功能。

**特性：**
- 基于回溯的模式匹配
- 量词：`*`、`+`、`?`、`{m,n}`（贪婪和非贪婪）
- 字符类：`[]`、`[^]`
- 特殊字符类：`\d`、`\D`、`\s`、`\S`、`\w`、`\W`
- 捕获组：`()`、`(?P<name>...)`
- 命名组和匿名组
- 捕获组位置跟踪

**支持的模式：**
- `.` - 匹配任意单个字符
- `*` - 匹配零次或多次（贪婪）
- `+` - 匹配一次或多次（贪婪）
- `?` - 匹配零次或一次（贪婪）
- `{m,n}` - 匹配 m 到 n 次（贪婪）
- `*?`、`+?`、`??`、`{m,n}?` - 非贪婪版本
- `[]` - 字符类（如 `[a-z]`、`[0-9]`）
- `[^]` - 否定字符类（如 `[^0-9]`）
- `\d`、`\D`、`\s`、`\S`、`\w`、`\W` - 特殊字符类
- `()` - 捕获组
- `(?P<name>...)` - 命名捕获组
- `|` - 分支（有限支持）

#### 已知限制（Regex）
- 不支持对捕获组直接使用量词（如 `(ab)*`、`(a)+`、`(x){2,3}`）。
  这类模式会直接抛错，目前暂不处理。

### 2. NFA（非确定性有限自动机）

`nfa` 包提供了基于 NFA 的正则表达式引擎，使用 Thompson 构造算法。

**特性：**
- Thompson 构造算法生成 NFA
- 广度优先搜索进行模式匹配
- 支持 epsilon 转换（ε-moves）
- 反向解析实现高效的 NFA 构建
- 正确处理嵌套和多个括号组
- 支持图可视化（DOT 格式）

**支持的模式：**
- `.` - 匹配任意单个字符
- `*` - 匹配零次或多次（贪婪）
- `+` - 匹配一次或多次（贪婪）
- `?` - 匹配零次或一次（贪婪）
- `*?`、`+?`、`??` - 非贪婪版本
- `{n}` - 精确匹配 n 次
- `{n,}` - 匹配至少 n 次
- `{n,m}` - 匹配 n 到 m 次
- `[]` - 字符类（如 `[a-z]`、`[0-9]`）
- `[^]` - 否定字符类（如 `[^0-9]`）
- `\d`、`\D`、`\s`、`\S`、`\w`、`\W` - 特殊字符类
- `\c` - 转义特殊字符（如 `\.`、`\*`）
- `()` - 分组（不支持捕获）
- `|` - 分支

**主要区别：**
- **NFA**：不支持捕获组，简单匹配更快，生成显式的状态机
- **Regex**：完整的捕获组支持，复杂模式较慢，使用回溯算法

## 使用方法

### 使用 Regex 实现

```python
import regex

# 简单匹配
result = regex.match('abc.*def', 'abcXYZdef')
print(bool(result))  # True

# 使用捕获组
result = regex.match('abc(.*)def', 'abczzdef')
if result:
    print(result.groups[1])  # 第1组的内容

# 命名组
result = regex.match('abc(?P<content>.*)def', 'abc123def')
if result:
    print(result.groups[1].name)   # 'content'
    print(result.groups[1].start)  # 起始位置
    print(result.groups[1].end)    # 结束位置
```

### 使用 NFA 实现

```python
import nfa

# 编译模式为 NFA
pattern = nfa.compile('abc.*def')

# 匹配字符串
result = pattern.match('abcXYZdef')
print(result)  # True

# NFA 可以可视化
dot_graph = pattern.graph2dot()
print(dot_graph)  # Graphviz DOT 格式
```

## 项目结构

```
pyregex/
├── regex/              # 基于回溯的正则引擎
│   ├── __init__.py
│   ├── regex.py        # 主正则编译器和匹配器
│   ├── matcher.py      # 核心匹配逻辑和数据结构
│   ├── regex_test.py   # 正则编译器测试
│   └── matcher_test.py # 匹配器组件测试
├── nfa/                # 基于 NFA 的正则引擎
│   ├── __init__.py
│   ├── compile.py      # Thompson 构造编译器
│   ├── nodes.py        # NFA 节点和匹配算法
│   ├── edges.py        # 边类型（Empty、Char、Any、Charset）
│   ├── compile_test.py # 编译器测试
│   ├── nodes_test.py   # 节点和匹配测试
│   └── edges_test.py   # 边类型测试
├── test.py             # 快速验证测试套件
├── main.py             # 使用示例
└── README.md           # 本文件
```

## 运行测试

### 运行所有单元测试：
```bash
make unittest
# 或
python3 -m unittest discover . "*_test.py"
```

### 运行快速验证测试：
```bash
make test
# 或
python3 test.py
```

### 针对特定实现运行测试：
```bash
# 仅测试 regex 实现
python3 test.py --impl regex

# 仅测试 NFA 实现
python3 test.py --impl nfa
```

### 静态代码检查：
```bash
make lint
# 或
ruff check .
```

## 测试覆盖率

- **总测试数**：218
  - Regex 实现：43 个测试
  - NFA 边类型：39 个测试
  - NFA 节点（包括匹配）：39 个测试
  - NFA 编译器：97 个测试
    - scan_brackets（括号匹配）：14 个测试
    - tokenizer（词法分析）：22 个测试
    - tok_to_set（字符集解析）：10 个测试
    - compile（编译器）：51 个测试
      - 限定数量量词 {n,m}：15 个测试

## 示例

### 示例 1：邮箱模式（Regex）
```python
import regex

pattern = '[a-z]+@[a-z]+\\.com'
result = regex.match(pattern, 'user@example.com')
print(bool(result))  # True
```

### 示例 2：数字提取（Regex 带捕获组）
```python
import regex

pattern = '(\\d+)\\.(\\d+)'
result = regex.match(pattern, '123.456')
if result:
    print(f"整数部分: {result.groups[1]}")   # 第1组
    print(f"小数部分: {result.groups[2]}")   # 第2组
```

### 示例 3：模式匹配（NFA）
```python
import nfa

# 编译并匹配
pattern = nfa.compile('a(b|c)*d')
print(pattern.match('ad'))      # True
print(pattern.match('abd'))     # True
print(pattern.match('acd'))     # True
print(pattern.match('abcd'))    # True
print(pattern.match('abbd'))    # True
```

### 示例 4：限定数量量词（NFA）
```python
import nfa

# 精确匹配 - 匹配 3 位数字
pattern = nfa.compile('\\d{3}')
print(pattern.match('123'))     # True
print(pattern.match('12'))      # False
print(pattern.match('1234'))    # False

# 范围匹配 - 密码长度验证（6-12 个字母或数字）
pattern = nfa.compile('[a-zA-Z0-9]{6,12}')
print(pattern.match('pass'))       # False (太短)
print(pattern.match('password'))   # True
print(pattern.match('pass1234'))   # True
print(pattern.match('verylongpassword123'))  # False (太长)

# 最少匹配 - 至少 2 个重复字符
pattern = nfa.compile('a{2,}')
print(pattern.match('a'))       # False
print(pattern.match('aa'))      # True
print(pattern.match('aaaa'))    # True
```

### 示例 5：可视化 NFA
```python
import nfa

pattern = nfa.compile('ab*c')
dot = pattern.graph2dot()

# 保存到文件并使用 Graphviz 可视化
with open('nfa.dot', 'w') as f:
    f.write(dot)

# 然后运行：dot -Tpng nfa.dot -o nfa.png
```

## 实现细节

### Regex 实现
- 使用递归下降解析进行模式编译
- 基于回溯的匹配算法
- 在匹配过程中捕获组位置
- 支持贪婪和非贪婪量词

### NFA 实现
- 使用 Thompson 构造算法
- 反向解析实现高效的 NFA 构建
- `scan_brackets` 函数正确处理嵌套和多个括号
  - 使用层级计数处理任意深度的嵌套括号
  - 从后向前扫描，支持多个连续的括号组
  - 可以正确处理 `(a(b)c)`、`((a)(b))`、`(a)(b)(c)` 等复杂模式
- 限定数量量词 `{n,m}` 通过节点克隆实现
  - `Node.clone()` 方法执行深度拷贝并保持图拓扑结构
  - 使用映射字典处理共享节点和循环引用
  - 支持 `{n}`（精确）、`{n,}`（最少）、`{n,m}`（范围）三种格式
- 使用带历史记录跟踪的广度优先搜索进行匹配
- epsilon 闭包处理状态转换
- 解耦的边和节点设计提供灵活性

## 许可证

详见 LICENSE 文件。

## 贡献

这是一个教育项目，用于演示正则表达式引擎的实现。欢迎探索和学习代码！
