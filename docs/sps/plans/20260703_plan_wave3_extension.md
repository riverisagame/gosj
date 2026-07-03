# Wave 3 纳米级教程扩展执行计划 (IR 阶段)

- **任务ID**：TUTORIAL_EXT_W3
- **日期**：2026-07-03
- **出口准则**：输出 `[PLAN_LOCKED]`，等待评审。

## 1. 计划目标
在原有教程基础上，为 `ch01` 至 `ch13` 及附录 `appendix-go-versions.md` 全量追加第三波（Wave 3）硬核底层图解与最高级别大厂 CTO 面试真题。保证 **Deletions 始终为 0**，原有 Wave 1 & 2 数据毫发无损。

---

## 2. 物理执行步骤

### 2.1 依赖库更新
- **文件**：[patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)
- **修改逻辑**：在文件末尾定义 `wave3_data` 字典，针对每一个章节存储其 Wave 3 独有图解原理（`principles_w3`）与 CTO 面试真题（`interviews_w3`）。

### 2.2 注入引擎升级
- **文件**：[patch_tutorial_runner.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_runner.py)
- **修改逻辑**：
  1. 引入 `wave3_data`。
  2. 防重入 check：利用 Wave 3 原理部分的第一行标题进行判定。如果已存在则 skip。
  3. 注入定位：
     - **普通章节 (ch01-ch12)**：
       1. 读取内容，定位行 `### 🏆 大厂CTO级面试金典`，在其正上方插入 `principles_w3`；
       2. 定位行 `> **下一章**`，在其正上方插入 `interviews_w3`；
     - **特化章节 (ch13, 附录)**：
       直接在文件末尾增量追加 `principles_w3` 与 `interviews_w3`。

### 2.3 测试用例扩展 (TDD RED 阶段)
- **文件**：[test_tutorial_extensions.py](file:///d:/claudeprj/gosj/gopl-zh-tutorial/test_tutorial_extensions.py)
- **修改逻辑**：
  1. 增加 Wave 3 关键字断言，例如 `rt0_go`、`SP 寄存器`、`IEEE 754`、`SwissTable` 等。
  2. 增加对各章节是否含有 ASCII 流程图代码块（` ``` ` 形式包含的图解）的物理数量检查。

---

## 3. 逐章注入内容蓝图

### [MODIFY] [patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)

#### ch01-introduction.md
- **principles_w3**: `Go 编译链接全生命周期流程图`（显示 `go tool compile -> .o -> go tool link -> ELF/PE`）与 `rt0_go` 启动引导。
- **interviews_w3**: 从 ELF 载入到 runtime 初始化（`schedinit`）的机器级握手与二进制臃肿原因。

#### ch02-program-structure.md
- **principles_w3**: `逃逸分析 DAG 指针追溯图` 与 `栈帧分配 SP/BP 寄存器图`。
- **interviews_w3**: 指针流拓扑排序算法逻辑、栈空间在内核态与用户态的分配握手。

#### ch03-basic-types.md
- **principles_w3**: `IEEE 754 浮点数指数/尾数拆解图`。
- **interviews_w3**: 零拷贝切片的 GC 虚弱标记问题、float64 近似值的硬件舍入模式对冲。

#### ch04-composite-types.md
- **principles_w3**: `slice 扩容 roundupsize 物理内存对齐对比图`、`hmap & bmap 桶链表物理结构树状图`。
- **interviews_w3**: 缩容垃圾内存防泄露、溢出桶拉链法硬件对齐缓存行（Cache Line）。

#### ch05-functions.md
- **principles_w3**: `defer 堆/栈/开放编码控制流跳转图`、`gopanic / gorecover 异常恢复 CPU IP/SP 跳转图`。
- **interviews_w3**: 开放编码中 bitmask 标志位的寄存器对冲、recover 恢复指令现场物理恢复过程。

#### ch06-methods.md
- **principles_w3**: `method value/expression funcval 二进制解糖对比图`。
- **interviews_w3**: 接收者包装为闭包的堆分配边界、方法寻址优化。

#### ch07-interfaces.md
- **principles_w3**: `iface/eface 物理结构与 itab 字典序排序表图`。
- **interviews_w3**: itabTable 并发扩容时读写屏障的原子读写性能保证。

#### ch08-goroutines-channels.md
- **principles_w3**: `GMP 调度工作窃取与 G0 调度环图`、`hchan 环形缓冲区与 sudog 双向等待链表图`。
- **interviews_w3**: 窃取时自旋状态的对冲、跨栈拷贝栈屏障与 GC 并发屏障。

#### ch09-shared-vars-concurrency.md
- **principles_w3**: `sync.Mutex 饥饿/正常模式状态转移图`、`sync.Pool 的 poolLocal 双端无锁窃取队列图`。
- **interviews_w3**: CanSpin 硬件级判定条件（锁竞争与自旋开销对冲）、sync.Pool 的 victim 缓存区设计。

#### ch10-packages-tools.md
- **principles_w3**: `MVS 算法最小版本选择 DAG 依赖树计算图`。
- **interviews_w3**: 依赖图排序与包冲突动态剪枝过程。

#### ch11-testing.md
- **principles_w3**: `synctest 虚拟时钟沙箱隔离泡泡时间轴图`、`ThreadSanitizer 1:4 影子内存物理映射图`。
- **interviews_w3**: 虚拟时钟劫持原理、数据竞争中向量时钟合并与剪枝。

#### ch12-reflection.md
- **principles_w3**: `reflect.Value flag 二进制位布局图`。
- **interviews_w3**: 反射字段内存读写屏障越过方式与底层 flag 读写控制。

#### ch13-unsafe-cgo.md
- **principles_w3**: `混合写屏障三色标记堆写屏障插桩控制流图`、`Cgo 调用 Go 栈与 C 系统栈（G0）物理切换图`。
- **interviews_w3**: 混合写屏障新分配堆涂黑的 GC 必要性、Cgo 寄存器备份汇编切换现场分析。

#### appendix-go-versions.md
- **principles_w3**: `SwissTable 哈希查找 Slot 组控制图`。
- **interviews_w3**: SwissTable 组内 SIMD 并行指令查找与冲突平摊。

---

## 4. 自动化回归与验证计划
1. 在修改业务代码前，将测试文件 `test_tutorial_extensions.py` 升级，添加 Wave 3 所有关键字和 ASCII 图判定（RED 阶段）。
2. 运行测试，确保其因为“找不到 Wave 3 图解和关键字”而报错。
3. 升级内容和 runner，运行修补程序，并执行 `test_tutorial_extensions.py` 直至绿灯。
