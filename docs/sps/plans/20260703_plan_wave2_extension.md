# 20260703 GOPL 教程 Wave 2 纳米级深度扩展计划

## 1. 任务目标
在 Wave 1 的基础上，进一步对 13 个章节文件和 1 个附录进行马力全开的纳米级追加扩充。扩展计算机底层（如 CPU 汇编、操作系统内核机制、SIMD 硬件加速）以及大厂 CTO 高频面试题。

## 2. 细化追加内容规划（逐章细化）

---

### 批次 1: 基础起航篇（第 1 ~ 3 章）

#### [MODIFY] [ch01-introduction.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch01-introduction.md)
- **底层原理纳米级精讲**：
  - Go 系统调用（Syscall）底层拦截与调度器协同：当 G 调用阻塞系统调用时，从汇编 `Syscall` 陷入内核，到 runtime 如何触发 `entersyscall` 和 `exitsyscall`。
- **大厂CTO级面试金典**：
  - 面试题：Go 是如何防止阻塞系统调用把操作系统线程池拖垮的？（P 与 M 分离，sysmon 主动剥离并重新关联新 M 的原理）

#### [MODIFY] [ch02-program-structure.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch02-program-structure.md)
- **底层原理纳米级精讲**：
  - 未命名常量（Untyped Constants）的编译期延迟推导与任意精度表示（编译期高精度浮点数字面量）。
  - 空结构体（`struct{}`）作为结构体尾部字段时的特殊对齐边界（多占用 1 字节防止指向结构体外的野指针）。
- **大厂CTO级面试金典**：
  - 面试题：为什么未命名常量可以表示像 `1<<100` 这样远超常规整型上限的值？
  - 面试题：为什么空结构体作为结构体的最后一个字段时会多占 1 字节（或 8 字节）内存？

#### [MODIFY] [ch03-basic-types.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch03-basic-types.md)
- **底层原理纳米级精讲**：
  - UTF-8 变长解码在标准库中的快速查表优化原理（`utf8.DecodeRune` 里的字节掩码与位移运算）。
- **大厂CTO级面试金典**：
  - 面试题：Go 标准库 `unicode/utf8` 是如何实现高性能解码的？为什么不使用大循环判断字节？

---

### 批次 2: 结构进阶篇（第 4 ~ 6 章）

#### [MODIFY] [ch04-composite-types.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch04-composite-types.md)
- **底层原理纳米级精讲**：
  - Map 桶内 `tophash` 的快速过滤原理；哈希碰撞时的链表检索与 key 查找触发的 `reflect.toyface` 判定。
- **大厂CTO级面试金典**：
  - 面试题：Map 为什么不是并发安全的？写冲突发生时，runtime 究竟是如何在 1ns 内检测并强制 Panic 的？（`flags` 的 `hashWriting` 位操作与多核 CPU 检测）

#### [MODIFY] [ch05-functions.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch05-functions.md)
- **底层原理纳米级精讲**：
  - 闭包在逃逸分析中的反向优化边界：为什么有些捕获了外部变量的闭包并没有发生堆逃逸？（只读/立即执行）。
- **大厂CTO级面试金典**：
  - 面试题：嵌套 Defer 时的 `_defer` 链表状态复用是怎么做的？（Go 1.14 开放编码下的嵌套优化）

#### [MODIFY] [ch06-methods.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch06-methods.md)
- **底层原理纳米级精讲**：
  - 方法集的编译期决议与接口动态调用的虚函数表（itab）方法指针物理对齐流程。
- **大厂CTO级面试金典**：
  - 面试题：如何利用 Go 方法集的编译决议设计零拷贝的接口代理？

---

### 批次 3: 运行核心篇（第 7 ~ 9 章）

#### [MODIFY] [ch07-interfaces.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch07-interfaces.md)
- **底层原理纳米级精讲**：
  - 类型断言（Type Assertion）在汇编指令层面的 `assertE2I`、`assertE2T` 的底层运行过程。
- **大厂CTO级面试金典**：
  - 面试题：接口类型断言在汇编层是怎么执行的？它的分支判断对 CPU 缓存友好吗？

#### [MODIFY] [ch08-goroutines-channels.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch08-goroutines-channels.md)
- **底层原理纳米级精讲**：
  - 栈分裂与栈复制的物理实现。当栈空间不足触发 `runtime.morestack` 时，`copystack` 内部是如何递归搜索并更新整个调用栈上所有指针的物理地址（包括 `**T` 的指针偏移动态修正）。
- **大厂CTO级面试金典**：
  - 面试题：当 Goroutine 进行栈拷贝时，如果有指针指向别处（甚至指向自己的栈），底层是如何保证指针不会失效并正确指向新内存地址的？

#### [MODIFY] [ch09-shared-vars-concurrency.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch09-shared-vars-concurrency.md)
- **底层原理纳米级精讲**：
  - `sync.Pool` 的物理架构与多级缓存：`poolLocal` 中的 `private` 私有插槽与 `shared` 双向链表。GC 触发时的清理步骤以及跨 P 工作窃取（Steal）机制。
- **大厂CTO级面试金典**：
  - 面试题：高并发场景下使用 `sync.Pool` 为什么能有效防止 GC 抖动？它的底层是如何规避锁竞争与数据盗用的？

---

### 批次 4: 工具与黑魔法篇（第 10 ~ 13 章 + 附录A）

#### [MODIFY] [ch10-packages-tools.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch10-packages-tools.md)
- **底层原理纳米级精讲**：
  - Go Modules `go.sum` 的全局校验和数据库（Checksum Database，Sumdb）的默克尔树（Merkle Tree）防篡改防劫持校验流程。
- **大厂CTO级面试金典**：
  - 面试题：`go.sum` 怎么防范黑客通过篡改 Git 仓库发布木马？Sumdb 的默克尔树防篡改底层逻辑是什么？

#### [MODIFY] [ch11-testing.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch11-testing.md)
- **底层原理纳米级精讲**：
  - `-race` 竞争检测插桩底层的 ThreadSanitizer（TSan）状态机检测模型原理（内存块分配影子内存 shadow memory 记录最后 4 次访问的物理时间线）。
- **大厂CTO级面试金典**：
  - 面试题：大厂在高并发微服务压测时，是如何利用 Race Detector 的影子内存数据发现隐藏的数据竞争的？

#### [MODIFY] [ch12-reflection.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch12-reflection.md)
- **底层原理纳米级精讲**：
  - `reflect.Value.Set` 写入时的动态类型匹配与只读 `flag` 安全位检查，反射对只读字段写入的安全阻断。
- **大厂CTO级面试金典**：
  - 面试题：如何通过反射修改只读字段并绕过安全检查（反射的 flag 物理破解机制）？

#### [MODIFY] [ch13-unsafe-cgo.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch13-unsafe-cgo.md)
- **底层原理纳米级精讲**：
  - 汇编函数与 Go 的接口交互：为什么向 Go 汇编函数（Assembly Function）传递指针必然会导致堆逃逸？
- **大厂CTO级面试金典**：
  - 面试题：大厂高性能零拷贝库设计时，为什么手写汇编函数反而可能引发 GC 性能退化？（汇编无法静态分析指针生命周期导致一律判定为堆逃逸）

---

## 3. 验证与测试方案
- **自动化关键字测试**：升级 `test_tutorial_extensions.py`，新增对 Wave 2 关键技术短语（如 `entersyscall`，`copystack`，`sync.Pool` 等）的强校验。
- **物理无损审计**：运行 Git 状态确认，保证不对原有内容发生任何物理损减。
