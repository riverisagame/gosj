# Wave 8 纳米级教程扩展执行计划 (IR 阶段)

- **任务ID**：TUTORIAL_EXT_W8
- **日期**：2026-07-03
- **出口准则**：物理生成本文件后输出 `[PLAN_LOCKED]`，等待评审。

## 1. 计划目标
对原有教程的 14 个 Markdown 文件进行词法健全性静态审计。确保经过 Wave 1~7 的多轮定位拼接注入后，没有任何未闭合的 ``` 代码块和未闭合的 HTML 注释，防止渲染排版大面积塌陷。保证 **Deletions 始终为 0**。

---

## 2. 物理执行步骤

### 2.1 静态审计逻辑升级 (TDD RED/GREEN 阶段)
- **文件**：[test_tutorial_extensions.py](file:///d:/claudeprj/gosj/gopl-zh-tutorial/test_tutorial_extensions.py)
- **修改逻辑**：
  1. 新建 `check_markdown_syntax(file_path)` 方法；
  2. 读取文本内容，按行或按字符扫描：
     - **代码围栏校验**：统计 ``` 出现次数，非偶数抛出异常。
     - **注释完备校验**：统计 `<!--` 与 `-->`，不匹配抛出异常。
     - **行内单字对齐校验**：校验行内公式或特定语法锚点闭合。
  3. 如果发现异常，输出具体的行号和上下文，保障零渲染故障交付。
