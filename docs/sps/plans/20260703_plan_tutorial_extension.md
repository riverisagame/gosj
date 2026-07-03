# 20260703 GOPL 教程纳米级扩展执行计划

## 1. 任务目标
对 `gopl-zh-tutorial` 目录下的 13 个章节 + 1 个附录进行无损物理追加，扩充底层原理及大厂 CTO 级面试题，保持白话与深度的性能对冲。

## 2. 子任务拆解与修改范围
为了确保改动的稳定性和代码的可维护性，我们将修改任务拆分为四个原子批次，并在每章尾部以追加形式增加 `底层原理纳米级精讲` 和 `大厂CTO级面试金典`。

---

### 批次 1: 基础起航篇（第 1 ~ 3 章）

#### [MODIFY] [ch01-introduction.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch01-introduction.md)
- **底层原理纳米级精讲**：
  - Go 程序的生命周期起点：从 `rt0_go` 汇编入口到 `runtime.main`，再到用户 `main.main` 的完整引导链路。
- **大厂CTO级面试金典**：
  - 面试题：`init` 函数与 `main` 函数的执行顺序是怎样的？多包依赖时 `init` 执行顺序？（配图及白话比喻）
  - 面试题：`go run` 与 `go build` 底层编译链接的区别是什么？（临时目录与静态链接）

#### [MODIFY] [ch02-program-structure.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch02-program-structure.md)
- **底层原理纳米级精讲**：
  - 编译器逃逸分析（Escape Analysis）：栈与堆的分配原理，静态判断逃逸的核心策略（指针传递、接口动态接收、超大对象）。
- **大厂CTO级面试金典**：
  - 面试题：什么是逃逸分析？Go 语言中变量是在栈上还是在堆上分配？（白话+CTO级黑话）
  - 面试题：`new` 和 `make` 的底层实现与本质区别是什么？（`newobject` 与复合类型的 runtime 构造函数）

#### [MODIFY] [ch03-basic-types.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch03-basic-types.md)
- **底层原理纳米级精讲**：
  - 字符串底层 `stringStruct` 结构，为什么是只读的，大厂如何通过 `unsafe.Pointer` 零拷贝转换 `[]byte` 和 `string`。
  - 浮点数 IEEE 754 存储结构，NaN 和 Inf 状态位底层解释，精度丢失原理。
- **大厂CTO级面试金典**：
  - 面试题：如何无痛且零拷贝实现 `string` 和 `[]byte` 的转换？（Go 1.20 前后 `unsafe` 魔法的演变）
  - 面试题：`iota` 的位移机制与编译期常量代换原理。

---

### 批次 2: 结构进阶篇（第 4 ~ 6 章）

#### [MODIFY] [ch04-composite-types.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch04-composite-types.md)
- **底层原理纳米级精讲**：
  - 切片底层 `slice` 结构（`array`, `len`, `cap`）。Go 1.22+ 最新的切片扩容算法计算细节（`cap < 256` 翻倍，否则按照扩容系数及内存对齐微调）。
  - Map 底层 `hmap` 与 `bmap`，溢出桶设计。渐进式扩容（等量扩容与双倍扩容）中旧桶（oldbuckets）向新桶（buckets）的搬迁细节。
- **大厂CTO级面试金典**：
  - 面试题：Map 并发读写崩溃的底层原因是什么？如何优雅解决？（RWMutex, sync.Map, runtime `hashWriting` 检查）
  - 面试题：为什么 Map 的迭代顺序是随机的？（随机数种子与随机起始桶）

#### [MODIFY] [ch05-functions.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch05-functions.md)
- **底层原理纳米级精讲**：
  - 闭包（Closure）的底层 `FuncVal` 结构，外部变量被捕获时的引用和值拷贝（局部变量逃逸到堆上）。
  - `defer` 的底层演进链路：堆 defer（`runtime._defer`）-> 栈 defer -> 开放编码（Open-coded defer）的性能对比。
- **大厂CTO级面试金典**：
  - 面试题：`panic` 和 `recover` 的执行链表，为什么可以在 recover 中拦截 panic？
  - 面试题：多个 `panic` 嵌套发生时，Go 是怎么处理的？（panic 链表状态流转）

#### [MODIFY] [ch06-methods.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch06-methods.md)
- **底层原理纳米级精讲**：
  - 方法表达式（Method Expression）与方法值（Method Value）在编译期的解糖（Desugaring）与闭包转化。
- **大厂CTO级面试金典**：
  - 面试题：指针接收者与值接收者的方法集（Method Set）判定规则是什么？（`T` 与 `*T`）
  - 面试题：用空结构体 `struct{}` 做 Receiver 有什么妙用和内存优化？

---

### 批次 3: 运行核心篇（第 7 ~ 9 章）

#### [MODIFY] [ch07-interfaces.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch07-interfaces.md)
- **底层原理纳米级精讲**：
  - `eface` (空接口) 和 `iface` (有方法接口) 的底层结构体定义。
  - `itab` 缓存机制，动态类型与动态值的比对过程。
- **大厂CTO级面试金典**：
  - 面试题：为什么 `var err error = (*MyError)(nil)` 不等于 `nil`？（接口内部 `type` 字段不为 nil）
  - 面试题：接口类型断言在运行时的性能开销和优化手段是什么？

#### [MODIFY] [ch08-goroutines-channels.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch08-goroutines-channels.md)
- **底层原理纳米级精讲**：
  - GMP 调度模型：G 状态流转，M 的系统线程映射，P 的本地队列与全局队列。Work Stealing 算法（如何随机窃取其他 P 队列中一半的 G）。
  - Channel 底层 `hchan` 与等待队列 `sudog`。带缓冲/无缓冲的物理操作路径（直接内存拷贝优化、锁开销）。
- **大厂CTO级面试金典**：
  - 面试题：Channel 的三种读取/写入物理路径是什么？怎么通过 sudog 挂起 G？
  - 面试题：GMP 中 sysmon 协程的作用是什么？如何实现非合作式抢占调度（异步信号抢占）？

#### [MODIFY] [ch09-shared-vars-concurrency.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch09-shared-vars-concurrency.md)
- **底层原理纳米级精讲**：
  - `sync.Mutex` 锁饥饿模式与自旋（Spinning）机制，自旋锁触发的底层条件（CPU 多核、活跃 P 等）。
  - `sync.Once` 的 DCL（Double Checked Locking）实现。
  - `sync.Map` 读写分离架构，无锁 `readOnly` 结构，`dirty` 映射提升与重建。
- **大厂CTO级面试金典**：
  - 面试题：自旋锁的物理原理是什么？为什么要限制自旋次数？
  - 面试题：大并发场景下如何优化 Mutex 锁冲突？（锁细粒度化、无锁 CAS、分段锁）

---

### 批次 4: 工具与黑魔法篇（第 10 ~ 13 章 + 附录A）

#### [MODIFY] [ch10-packages-tools.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch10-packages-tools.md)
- **底层原理纳米级精讲**：
  - Go Modules 的最小版本选择（MVS）算法的图论解析。
- **大厂CTO级面试金典**：
  - 面试题：Go 的编译链接器是如何处理包的循环依赖的？
  - 面试题：如何利用 Go 的静态链接优势在容器化部署中实现极简镜像（scratch 镜像与 Cgo 静态链接依赖解决）？

#### [MODIFY] [ch11-testing.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch11-testing.md)
- **底层原理纳米级精讲**：
  - Go 1.21+ `synctest` 虚拟时间机制的内部实现，用于高并发测试的逻辑。
- **大厂CTO级面试金典**：
  - 面试题：如何进行有效的并发安全检测与性能测试（Race Detector 的 ThreadSanitizer 机制原理）？

#### [MODIFY] [ch12-reflection.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch12-reflection.md)
- **底层原理纳米级精讲**：
  - `reflect.Type` 和 `reflect.Value` 的指针逃逸细节，运行时内存布局的动态解析。
- **大厂CTO级面试金典**：
  - 面试题：为什么反射会带来严重的性能开销？如何利用 `unsafe` 绕过反射修改私有结构体字段？

#### [MODIFY] [ch13-unsafe-cgo.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/ch13-unsafe-cgo.md)
- **底层原理纳米级精讲**：
  - Go 内存垃圾回收（GC）的演进史与完整状态机。三色标记法配合混合写屏障（Hybrid Write Barrier）的物理执行细节，插入屏障与删除屏障如何保证不漏标。
  - 强三色不变式和弱三色不变式。
- **大厂CTO级面试金典**：
  - 面试题：GC 调优的三板斧是什么？在高并发大对象场景下，如何避免 STW 物理耗时过高？（Pacer 调优、Memory Limit）
  - 面试题：Cgo 调用的底层代价是什么？（系统线程切换，Go 栈到 C 栈转换导致的调度器阻塞与资源损耗）

#### [MODIFY] [appendix-go-versions.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/appendix-go-versions.md)
- 追加近几个 Go 版本（Go 1.24, 1.25, 1.26, 1.27）关于运行时的重磅更新说明（如最新的 SwissTable Map 替换实现、Green Tea GC 内存屏障优化等）。

#### [MODIFY] [README.md](file:///d:/claudeprj/gosj/gopl-zh-tutorial/README.md)
- 对应更新各个文件的行数和大小、面试题总数（新增约 30 道顶级大厂 CTO 面试题）。

---

## 3. 验证与测试方案
- **自动测试**：通过脚本或命令验证生成的所有链接正确性，以及文本格式无误。
- **物理无损审计**：在最终提交前运行 `git diff` 确认原有的所有段落内容未发生任何误删、修改，仅仅是追加与目录文字更新。
