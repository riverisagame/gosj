# Wave 5 纳米级教程扩展执行计划 (IR 阶段)

- **任务ID**：TUTORIAL_EXT_W5
- **日期**：2026-07-03
- **出口准则**：物理生成本文件后输出 `[PLAN_LOCKED]`，等待评审。

## 1. 计划目标
在原有教程（已含 Wave 1~4）基础上，为 `ch01` 至 `ch13` 及附录 `appendix-go-versions.md` 全量追加第五波（Wave 5）硬件微架构级对冲与顶级大厂面试真题。保证 **Deletions 始终为 0**，原有 Wave 1~4 数据毫发无损。

---

## 2. 物理执行步骤

### 2.1 依赖库更新
- **文件**：[patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)
- **修改逻辑**：在文件末尾定义 `wave5_data` 字典，针对每一个章节存储其 Wave 5 硬件微架构对冲原理（`hardware_w5`）与顶级硬件级面试真题（`interviews_w5`）。

### 2.2 注入引擎升级
- **文件**：[patch_tutorial_runner.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_runner.py)
- **修改逻辑**：
  1. 引入 `wave5_data`，增加独立的 wave5 注入流程。
  2. 防重入 check：利用 Wave 5 真实场景部分的第一行标题进行判定。如果已存在则 skip。
  3. 注入定位：
     - **普通章节 (ch01-ch12)**：
       1. 读取内容，定位行 `### 🏆 大厂CTO级面试金典`，在其正上方插入 `hardware_w5`；
       2. 定位行 `> **下一章**`，在其正上方插入 `interviews_w5`；
     - **特化章节 (ch13, 附录)**：
       直接在文件末尾增量追加 `hardware_w5` 与 `interviews_w5`。

### 2.3 测试用例扩展 (TDD RED 阶段)
- **文件**：[test_tutorial_extensions.py](file:///d:/claudeprj/gosj/gopl-zh-tutorial/test_tutorial_extensions.py)
- **修改逻辑**：
  1. 增加 Wave 5 硬件级关键字断言，例如 `NUMA`、`伪共享`、`分支预测`、`内存屏障`、`AVX-512`、`Prefetching` 等。
  2. 保证原有 Wave 1~4 的所有测试依然 100% 通过。

---

## 3. 逐章注入硬件原理与大厂真题设计蓝图

### [MODIFY] [patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)

#### ch01-introduction.md
- **hardware_w5**: NUMA（非一致内存访问）多处理器架构亲和性物理排布与 CPU 核绑定（Thread Affinity）对冲。
- **interviews_w5**: 本地与远程内存（Remote Memory）访问延迟差、Go 调度器如何对冲这一硬件缺陷。

#### ch02-program-structure.md
- **hardware_w5**: 内存对齐边界与 CPU 内存条存取周期（Memory Access Cycles）物理对冲。
- **interviews_w5**: 结构体字段物理排序对 CPU 寻址周期的优化。

#### ch03-basic-types.md
- **hardware_w5**: 高并发数值修改下，多核 CPU 的 Cache Line 伪共享（False Sharing）与 MESI 一致性协议对冲。
- **interviews_w5**: 缓存行伪共享的本质、Go 中如何使用指针补齐（Cache Line Padding）进行性能对冲。

#### ch04-composite-types.md
- **hardware_w5**: Go 内存分配器的多级物理虚拟分页（mspan/mcache）与 TLB 缓存未命中（TLB Miss）硬件对冲。
- **interviews_w5**: 什么是 TLB 缓存未命中、Go 内存分配器如何平摊 TLB 检索成本。

#### ch05-functions.md
- **hardware_w5**: CPU 分支预测（Branch Prediction）指令预取失效与无分支代码（Branchless Code）逻辑对冲。
- **interviews_w5**: 为什么无分支代码的计算速度会大幅度超越包含 if-else 的代码。

#### ch06-methods.md
- **hardware_w5**: 方法动态分发（Dynamic Dispatch）与 CPU 指令缓存（I-Cache）未命中的物理对冲。
- **interviews_w5**: 动态接口方法分发对 CPU I-Cache 会产生怎样的污染。

#### ch07-interfaces.md
- **hardware_w5**: 堆分配与 Linux 的 OS 页表缺页中断（Page Fault）物理耗时的硬件对冲。
- **interviews_w5**: 缺页中断的硬件级物理开销、高频小堆分配对页表的影响。

#### ch08-goroutines-channels.md
- **hardware_w5**: 并发 Channel 读写下的多核心缓存线无效（Cache Line Invalidation）与锁自由无锁环对冲。
- **interviews_w5**: 高竞争下的 Channel 引发 L1/L2 缓存线抖动的底层原因。

#### ch09-shared-vars-concurrency.md
- **hardware_w5**: CPU 指令重排（Instruction Reordering）与 Go 编译器内存屏障（Memory Barrier）汇编级对冲。
- **interviews_w5**: 多核并发读写为什么需要内存屏障、Go 底层是如何插入 Read/Write Barrier 的。

#### ch10-packages-tools.md
- **hardware_w5**: 链接器做死代码剪枝（Dead Code Elimination）的静态符号图有向图剪枝算法。
- **interviews_w5**: 链接阶段剔除未使用的包函数的有向图剪枝实现。

#### ch11-testing.md
- **hardware_w5**: 基准测试（Benchmark）在硬件层面的 CPU 频率抖动（CPU Frequency Scaling）与 Turbo Boost 物理对冲。
- **interviews_w5**: 为什么基准测试时需要锁定 CPU 频率、如何防范硬件动态调频干扰。

#### ch12-reflection.md
- **hardware_w5**: 物理内存直达寻址下的指针安全与硬件缺页段错误防御。
- **interviews_w5**: 越过反射进行 unsafe 强转时，如何计算 CPU 缓存行的对齐物理边界。

#### ch13-unsafe-cgo.md
- **hardware_w5**: 利用 CPU SIMD 向量寄存器（AVX-512）执行超大块数据并行内存拷贝（memcpy）的极速对冲。
- **interviews_w5**: 向量指令拷贝与普通 for 循环拷贝在硬件吞吐上的本质不同。

#### appendix-go-versions.md
- **hardware_w5**: SwissTable 哈希槽组在多核 CPU 上的二级缓存（L2/L3 Cache）预取（Prefetching）物理机制。
- **interviews_w5**: Cache Prefetching 预取机制、SwissTable 查找是如何指导 CPU 预取冷数据的。
