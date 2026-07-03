# Wave 4 纳米级教程扩展执行计划 (IR 阶段)

- **任务ID**：TUTORIAL_EXT_W4
- **日期**：2026-07-03
- **出口准则**：物理生成本文件后输出 `[PLAN_LOCKED]`，等待评审。

## 1. 计划目标
在原有教程（已含 Wave 1、2、3）基础上，为 `ch01` 至 `ch13` 及附录 `appendix-go-versions.md` 全量追加第四波（Wave 4）工业级真实应用场景及大厂顶级真实面试题。保证 **Deletions 始终为 0**，原有 Wave 1~3 数据毫发无损。

---

## 2. 物理执行步骤

### 2.1 依赖库更新
- **文件**：[patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)
- **修改逻辑**：在文件末尾定义 `wave4_data` 字典，针对每一个章节存储其 Wave 4 真实应用场景（`scenarios_w4`）与顶级真实面试题（`interviews_w4`）。

### 2.2 注入引擎升级
- **文件**：[patch_tutorial_runner.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_runner.py)
- **修改逻辑**：
  1. 引入 `wave4_data` 并废弃或保留对 wave3_data 的操作（直接使用独立的 wave4 注入流程）。
  2. 防重入 check：利用 Wave 4 真实场景部分的第一行标题进行判定。如果已存在则 skip。
  3. 注入定位：
     - **普通章节 (ch01-ch12)**：
       1. 读取内容，定位行 `### 🏆 大厂CTO级面试金典`，在其正上方插入 `scenarios_w4`；
       2. 定位行 `> **下一章**`，在其正上方插入 `interviews_w4`；
     - **特化章节 (ch13, 附录)**：
       直接在文件末尾增量追加 `scenarios_w4` 与 `interviews_w4`。

### 2.3 测试用例扩展 (TDD RED 阶段)
- **文件**：[test_tutorial_extensions.py](file:///d:/claudeprj/gosj/gopl-zh-tutorial/test_tutorial_extensions.py)
- **修改逻辑**：
  1. 增加 Wave 4 关键字断言，例如 `automaxprocs`、`CPU 限流`、`Pointer-free`、`netpoller`、`CPU 占用率`、`XMM 寄存器`、`SIMD` 等。
  2. 保证原有 Wave 1~3 的所有测试依然 100% 通过。

---

## 3. 逐章注入真实场景与大厂真题设计蓝图

### [MODIFY] [patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)

#### ch01-introduction.md
- **scenarios_w4**: 大厂在 K8s 容器化部署中，Go 未感知物理核限制导致线程疯狂上下文切换（Context Switch）的线上故障对冲，引入 `automaxprocs`。
- **interviews_w4**: 容器环境下 CFS 限流原理、`automaxprocs` 动态读取 cgroups 伪文件的机制。

#### ch02-program-structure.md
- **scenarios_w4**: 支付网关系统高频反序列化 JSON，指针变量逃逸到堆引发频繁 GC 暂停（GC Pause），导致接口耗时从 10ms 抖动至 200ms。使用值对象与编译器指针追踪规避对冲。
- **interviews_w4**: 如何设计 Pointer-free 对象减少 GC 扫描压力、逃逸分析在接口（interface）调用时的隐式逃逸。

#### ch03-basic-types.md
- **scenarios_w4**: 广告系统在高频 Redis 键拼接中，因为 string 临时拷贝引发内存开销超限（Memory Swapping），改用字节指针零拷贝拼接。
- **interviews_w4**: []byte 与 string 在底层 runtime 层的物理转换转换异同与性能损耗。

#### ch04-composite-types.md
- **scenarios_w4**: 百亿级画像推荐系统，由于 map 的 Value 存放了大结构体，在拥有数百万个 Key 时导致 GC 并发标记阶段扫描了数百万个指针，CPU 占用率飙升 50%。改用扁平数组对冲。
- **interviews_w4**: 为什么 map[string]int32 的 GC 扫描成本低于 map[string]*int32？

#### ch05-functions.md
- **scenarios_w4**: 大厂核心消息队列中间件在循环体内高频执行 `defer` 关闭网络连接，QPS 达到 10w+ 时发生 `_defer` 链表抢占耗尽导致内存 OOM 崩溃。
- **interviews_w4**: defer 延迟调用的参数求值时机（L-value 与 R-value）、循环内 defer 的就地执行重构。

#### ch06-methods.md
- **scenarios_w4**: 分布式推送引擎在高并发事件分发中，使用方法值作为回调函数，因为隐式捕获了大变量导致的大面积内存泄露与碎片。
- **interviews_w4**: 方法值（Method Value）和方法表达式（Method Expression）在作为参数传递时的闭包包装与内存分配。

#### ch07-interfaces.md
- **scenarios_w4**: 动态路由组件在高频请求中频繁进行未命中的类型断言，导致不断退避到全局 `itabTable` 查找而引发全局锁竞争，QPS 暴跌 60%。
- **interviews_w4**: 如何通过自定义“类型静态哈希映射表”绕过接口断言的动态检索？

#### ch08-goroutines-channels.md
- **scenarios_w4**: 海量长连接推送网关中，由于下游系统阻塞导致百万个协程挂起，物理线程 M 暴涨至系统上限（10000），使用 `netpoller`（epoll）机制拦截对冲。
- **interviews_w4**: netpoller 内部 epoll 事件唤醒 GMP 协程的具体物理链路。

#### ch09-shared-vars-concurrency.md
- **scenarios_w4**: 瞬时高并发秒杀系统抢锁引发 Mutex 升级饥饿模式，自旋失效导致大量协程被挂起在 OS 信号量上，上下文切换占用了 80% CPU，使用 CAS 乐观锁或分段锁对冲。
- **interviews_w4**: 自旋锁与互斥锁的物理开销对比、为什么大厂核心高并发组件（如 sync.Map）尽量避开 Mutex？

#### ch10-packages-tools.md
- **scenarios_w4**: 供应链合规审计时，攻击者伪造了同版本的依赖文件静默投毒，团队在 CI/CD 中通过 Sumdb 和 Merkle Tree 校验拦截。
- **interviews_w4**: Merkle Tree（默克尔树）哈希链条的防伪机制。

#### ch11-testing.md
- **scenarios_w4**: 微服务压测时定时器模拟跑完测试需要 2 小时，通过 synctest 将其逻辑时钟虚拟化，压缩到 1 秒执行完。
- **interviews_w4**: 向量时钟（Vector Clock）在分布式系统及 race 检测中的计算复杂度。

#### ch12-reflection.md
- **scenarios_w4**: 大厂 ORM 框架在每秒数万次的 SQL 映射中，反射性能极差拖慢 CPU，改用 `unsafe` 获取结构体字段物理偏移实现零反射极速映射。
- **interviews_w4**: unsafe.Offsetof 物理寻址的内存越界防御机制。

#### ch13-unsafe-cgo.md
- **scenarios_w4**: 实时音视频转码系统调用 C 语言的 FFmpeg，因系统栈和 G0 栈频繁切换，且传递 Go 的堆指针触发 GC 误清扫导致核心转码服务概率性 Crash。
- **interviews_w4**: 为什么不能将含有 Go 堆指针的变量地址直接传给 C 语言？

#### appendix-go-versions.md
- **scenarios_w4**: 升级 Go 1.26 后，高并发存储引擎利用 SwissTable 的 SIMD 组内比对指令，实现哈希冲突下的长尾时延对冲。
- **interviews_w4**: CPU 向量寄存器（如 AVX2）的指令在 Go 编译器中的汇编级生成。
