# Wave 6 纳米级教程扩展执行计划 (IR 阶段)

- **任务ID**：TUTORIAL_EXT_W6
- **日期**：2026-07-03
- **出口准则**：物理生成本文件后输出 `[PLAN_LOCKED]`，等待评审。

## 1. 计划目标
在原有教程（已含 Wave 1~5）基础上，为 `ch01` 至 `ch13` 及附录 `appendix-go-versions.md` 全量追加第六波（Wave 6）可观测性、运行时剖析与 eBPF 内核探测对冲与顶级大厂面试真题。保证 **Deletions 始终为 0**，原有 Wave 1~5 数据毫发无损。

---

## 2. 物理执行步骤

### 2.1 依赖库更新
- **文件**：[patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)
- **修改逻辑**：在文件末尾定义 `wave6_data` 字典，针对每一个章节存储其 Wave 6 可观测性与剖析对冲原理（`observability_w6`）与顶级面试真题（`interviews_w6`）。

### 2.2 注入引擎升级
- **文件**：[patch_tutorial_runner.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_runner.py)
- **修改逻辑**：
  1. 引入 `wave6_data`，增加独立的 wave6 注入流程。
  2. 防重入 check：利用 Wave 6 真实场景部分的第一行标题进行判定。如果已存在则 skip。
  3. 注入定位：
     - **普通章节 (ch01-ch12)**：
       1. 读取内容，定位行 `### 🏆 大厂CTO级面试金典`，在其正上方插入 `observability_w6`；
       2. 定位行 `> **下一章**`，在其正上方插入 `interviews_w6`；
     - **特化章节 (ch13, 附录)**：
       直接在文件末尾增量追加 `observability_w6` 与 `interviews_w6`。

### 2.3 测试用例扩展 (TDD RED 阶段)
- **文件**：[test_tutorial_extensions.py](file:///d:/claudeprj/gosj/gopl-zh-tutorial/test_tutorial_extensions.py)
- **修改逻辑**：
  1. 增加 Wave 6 调试与剖析关键字断言，例如 `时钟中断`、`uprobe`、`PMC`、`栈回溯`、`0xCC`、`调度器延迟` 等。
  2. 保证原有 Wave 1~5 的所有测试依然 100% 通过。

---

## 3. 逐章注入剖析原理与大厂真题设计蓝图

### [MODIFY] [patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)

#### ch01-introduction.md
- **observability_w6**: 基于 pprof 采样频率与 Linux 内核定时器时钟中断（Timer Interrupt）的物理采样对冲。
- **interviews_w6**: pprof 采样机制、高频时钟中断下的少量 CPU 损耗原理。

#### ch02-program-structure.md
- **observability_w6**: 利用 eBPF uprobe 动态探测用户态 Goroutine 栈逃逸的无侵入式监控对冲。
- **interviews_w6**: eBPF uprobe 拦截用户态函数逃逸参数的机制。

#### ch03-basic-types.md
- **observability_w6**: 基于 CPU 硬件性能计数器（PMC）对高并发下 Cache Miss 进行无损监控的物理对冲。
- **interviews_w6**: Linux perf 如何通过读取 PMU 硬件寄存器进行缓存分析。

#### ch04-composite-types.md
- **observability_w6**: 利用 pprof heap 内存剖析器追踪 MallocGC 分配链条与虚拟内存碎片对冲。
- **interviews_w6**: heap 火焰图中 `alloc_space` 与 `inuse_space` 在生产故障定位中的区别。

#### ch05-functions.md
- **observability_w6**: 利用 Frame Pointer 寄存器快速执行硬件级栈回溯（Stack Walkback）的 CPU 性能对冲。
- **interviews_w6**: Frame Pointer 硬件指针对性能剖析（Profiling）的低开销栈展开加速原理。

#### ch06-methods.md
- **observability_w6**: 基于 Delve/GDB 动态插桩（Dynamic Instrumentation）修改运行时机器指令实现无损调试对冲。
- **interviews_w6**: 调试器如何向进程内存插入 `0xCC`（`INT 3`）软中断指令实现协程挂起的原理。

#### ch07-interfaces.md
- **observability_w6**: 使用 pprof cpu 动态探测反射接口装箱带来的 CPU 周期消耗与微秒级时延震荡对冲。
- **interviews_w6**: 火焰图中识别由于 interface type assertion 导致的 CPU 耗时高耸波峰。

#### ch08-goroutines-channels.md
- **observability_w6**: 利用 eBPF 动态捕获用户态协程 gopark 耗时与调度器延迟（Scheduling Latency）的内核对冲。
- **interviews_w6**: 调度器延迟（Scheduling Latency）对微服务响应时间的影响与 eBPF 无损采集。

#### ch09-shared-vars-concurrency.md
- **observability_w6**: 基于 pprof mutex/block 探测锁持有时间与锁等待（Lock Contention）物理抖动的无损排查对冲。
- **interviews_w6**: block 剖析器与 mutex 剖析器的底层监控采样机制。

#### ch10-packages-tools.md
- **observability_w6**: 基于抽象语法树（AST）与 SSA 静态分析自动检测代码静默注入的安全防御对冲。
- **interviews_w6**: 编译期自定义静态分析器拦截安全风险的原理。

#### ch11-testing.md
- **observability_w6**: 测试执行中，基于 Linux cgroups 硬件隔离防范宿主机 CPU 抢占噪声的物理对冲。
- **interviews_w6**: 为什么在共享多租户宿主机跑 Benchmark 会失真，cgroups 核隔离价值。

#### ch12-reflection.md
- **observability_w6**: 基于 DWARF 调试符号规范自动映射反射内存字段地址的静态/动态对冲。
- **interviews_w6**: DWARF 段信息（如 `.debug_info`）对于反射寻址与运行时核心排错的关联。

#### ch13-unsafe-cgo.md
- **observability_w6**: 使用 Linux perf 工具直接捕获 C 侧函数和 G0 系统调度栈相互跳转引起的硬件指令丢失对冲。
- **interviews_w6**: 为什么普通的 pprof 无法透视 Cgo 内部，Linux perf 硬件采样的优势。

#### appendix-go-versions.md
- **observability_w6**: SwissTable 在 Go 1.26 中通过 pprof 核心指标观测哈希冲突比率以实现动态重新散列（Rehash）对冲。
- **interviews_w6**: 观测 SwissTable 动态 Rehash 带来的 CPU 周期与内存开销指标。
