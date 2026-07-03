# Wave 7 纳米级教程扩展执行计划 (IR 阶段)

- **任务ID**：TUTORIAL_EXT_W7
- **日期**：2026-07-03
- **出口准则**：物理生成本文件后输出 `[PLAN_LOCKED]`，等待评审。

## 1. 计划目标
在原有教程（已含 Wave 1~6）基础上，为 `ch01` 至 `ch13` 及附录 `appendix-go-versions.md` 全量追加第七波（Wave 7）分布式高可用架构对冲与顶级大厂面试真题。保证 **Deletions 始终为 0**，原有 Wave 1~6 数据毫发无损。

---

## 2. 物理执行步骤

### 2.1 依赖库更新
- **文件**：[patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)
- **修改逻辑**：在文件末尾定义 `wave7_data` 字典，针对每一个章节存储其 Wave 7 分布式微服务高可用原理（`distributed_w7`）与顶级面试真题（`interviews_w7`）。

### 2.2 注入引擎升级
- **文件**：[patch_tutorial_runner.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_runner.py)
- **修改逻辑**：
  1. 引入 `wave7_data`，增加独立的 wave7 注入流程。
  2. 防重入 check：利用 Wave 7 真实场景部分的第一行标题进行判定。如果已存在则 skip。
  3. 注入定位：
     - **普通章节 (ch01-ch12)**：
       1. 读取内容，定位行 `### 🏆 大厂CTO级面试金典`，在其正上方插入 `distributed_w7`；
       2. 定位行 `> **下一章**`，在其正上方插入 `interviews_w7`；
     - **特化章节 (ch13, 附录)**：
       直接在文件末尾增量追加 `distributed_w7` 与 `interviews_w7`。

### 2.3 测试用例扩展 (TDD RED 阶段)
- **文件**：[test_tutorial_extensions.py](file:///d:/claudeprj/gosj/gopl-zh-tutorial/test_tutorial_extensions.py)
- **修改逻辑**：
  1. 增加 Wave 7 架构级关键字断言，例如 `优雅退出`、`一致性哈希`、`重试风暴`、`动态代理`、`看门狗`、`Wasm` 等。
  2. 保证原有 Wave 1~6 的所有测试依然 100% 通过。

---

## 3. 逐章注入分布式架构原理与大厂真题设计蓝图

### [MODIFY] [patch_tutorial_contents.py](file:///C:/Users/Administrator.BF-202604161409/.gemini/antigravity/brain/7beba9b4-0d0b-4ed0-b0b1-f1497d1ec295/scratch/patch_tutorial_contents.py)

#### ch01-introduction.md
- **distributed_w7**: 基于 Kubernetes 容器生命周期的优雅退出（Graceful Shutdown）与信号监听对冲。
- **interviews_w7**: 优雅退出机制、Go 如何监听 SIGTERM 信号安全清理连接。

#### ch02-program-structure.md
- **distributed_w7**: 配置中心动态热加载（Dynamic Config Hot-Reload）下的并发无锁原子指针替换对冲。
- **interviews_w7**: 如何在不使用互斥锁的前提下实现动态配置的安全热更新。

#### ch03-basic-types.md
- **distributed_w7**: 金融分布式账本高精度大数（BigDecimal）无损传输与计算精度雪崩对冲。
- **interviews_w7**: 为什么金融计算不能使用浮点数、大厂的精度对冲方案。

#### ch04-composite-types.md
- **distributed_w7**: 分布式一致性哈希（Consistent Hashing）环形数据分摊与虚节点抖动对冲。
- **interviews_w7**: 一致性哈希的顺时针检索实现、如何使用虚拟节点防范雪崩。

#### ch05-functions.md
- **distributed_w7**: 高频 RPC 调用的熔断限流与自适应重试（Adaptive Backoff）防抖对冲。
- **interviews_w7**: 熔断限流状态机设计、重试风暴防护。

#### ch06-methods.md
- **distributed_w7**: 分布式 RPC 框架底层的动态代理（Dynamic Proxy）与本地存根（Stub）反射解耦对冲。
- **interviews_w7**: 动态代理本地 Stub 劫持方法并动态封包发送到远程。

#### ch07-interfaces.md
- **distributed_w7**: 基于 Protocol Buffers 的 Any 动态类型解包与硬件加速序列化对冲。
- **interviews_w7**: Protobuf 紧凑字节码布局与 Fastpath 编码。

#### ch08-goroutines-channels.md
- **distributed_w7**: 高性能微服务网关中令牌桶与漏桶限流算法（Token/Leaky Bucket）的流量整形对冲。
- **interviews_w7**: 限流算法的 Go 原生并发锁开销对冲策略。

#### ch09-shared-vars-concurrency.md
- **distributed_w7**: 基于分布式锁（Redis Redlock / Etcd Lease）的一致性脑裂（Split-Brain）与看门狗自动续期对冲。
- **interviews_w7**: 看门狗（Watchdog）在分布式锁租约到期前的续期机理。

#### ch10-packages-tools.md
- **distributed_w7**: 利用 Go plugin / WebAssembly（Wasm）动态载入无侵入热插拔网关过滤器插件对冲。
- **interviews_w7**: Wasm 虚拟机沙箱在网关中的动态加载与隔离防护。

#### ch11-testing.md
- **distributed_w7**: 混沌工程（Chaos Engineering）注入测试下网络分区与分布式时钟偏移容灾对冲。
- **interviews_w7**: 网络分区测试演练、最终一致性对冲保障。

#### ch12-reflection.md
- **distributed_w7**: 高并发动态序列化结构体字段解析映射与 mapstructure 反序列化性能对冲。
- **interviews_w7**: 动态 map 到 struct 转换反射瓶颈平摊。

#### ch13-unsafe-cgo.md
- **distributed_w7**: 高性能 gRPC 网关直接调用 C+ASM 加速 AES-GCM 硬件加密以榨干 10G 网卡吞吐对冲。
- **interviews_w7**: 跨 Cgo 加密计算的微秒级时延规避。

#### appendix-go-versions.md
- **distributed_w7**: SwissTable 在 Go 1.26 中作为分布式路由表中数百万路由项极速比对的基石。
- **interviews_w7**: 服务发现路由缓存使用 SwissTable 后的物理提速性能数据。
