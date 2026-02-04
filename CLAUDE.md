# 项目定位

功能：演示教学用途的正则表达式引擎。
技术栈：纯Python，不使用内置re库。

# 规范

* 禁止自动git提交
* 编码规范遵循PEP-8。
* 强制执行 Type Annotations。
* 公有函数必须包含详尽的 Docstrings (Args, Returns, Raises)。
* 使用 ruff 进行静态检查。
* 测试和构建过程使用Makefile控制
* 每次修改源码后，如果需要，更新README.md。
* 删除无用代码，删除头部无效import
* 使用logging处理日志。

# regex

regex引擎使用回朔法匹配。

# nfa

nfa引擎将正则表达式编译为NFA（非确定性有限状态自动机），通过图搜索算法来匹配。
