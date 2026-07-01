# 第9章 基于共享变量的并发

> 当多个goroutine通过共享变量通信时（而非channel），需要同步机制保证正确性。本章深入竞争条件、互斥锁、读写锁、内存模型、惰性初始化和竞争检测。

---

## 目录

- [9.1 竞争条件](#91-竞争条件)
- [9.2 sync.Mutex互斥锁](#92-syncmutex互斥锁)
- [9.3 sync.RWMutex读写锁](#93-syncrwmutex读写锁)
- [9.4 内存同步](#94-内存同步)
- [9.5 sync.Once惰性初始化](#95-synconce惰性初始化)
- [9.6 竞争条件检测](#96-竞争条件检测)
- [9.7 示例: 并发的非阻塞缓存](#97-示例-并发的非阻塞缓存)
- [9.8 Goroutines和线程](#98-goroutines和线程)

---

## 9.1 竞争条件

### 数据竞争

当多个goroutine并发访问同一变量，且至少一个是写操作，就产生了**数据竞争**：

```go
var balance int

func Deposit(amount int) {
    balance = balance + amount  // 非原子操作！
}

func Balance() int {
    return balance
}

// goroutine A: Deposit(200) — 执行到一半被抢占
// goroutine B: Balance() — 读到了中间值
```

### 三种竞争条件

| 类型 | 定义 | 示例 |
|------|------|------|
| 数据竞争（Data Race） | 并发读写同一变量 | 上面示例 |
| 竞态条件（Race Condition） | 执行顺序影响结果 | 缺乏同步的转账 |
| 原子性违反 | 本应原子的操作被中断 | `balance = balance + 100` |

### 避免数据竞争的三种方法

```go
// 1. 不写变量（immutable）
var readonly = []string{...}  // 构造后不再修改

// 2. 不共享变量（channel通信）
ch := make(chan int)
go func() { ch <- work() }()
result := <-ch

// 3. 加锁访问
var mu sync.Mutex
func Deposit(amount int) {
    mu.Lock()
    defer mu.Unlock()
    balance += amount
}
```

### 🔥 面试扩展

**高频题1：`balance = balance + amount`不是原子的，那具体拆分为哪些指令？**
> 在处理器层面，这行代码通常拆分为：
> 1. **LOAD**：从内存读取`balance`到寄存器
> 2. **ADD**：寄存器中的值和`amount`相加
> 3. **STORE**：将结果写回内存
> 如果goroutine A执行LOAD后被抢占，goroutine B修改了`balance`，A接着用旧值做ADD并STORE，导致B的更新被覆盖。这就是经典的**读-改-写（Read-Modify-Write）竞争**。

**高频题2：为什么`map`并发读写会panic而不是返回错误值？**
> Go在map的底层实现中内置了**并发检测**。当检测到并发读写时，直接`fatal error: concurrent map read and map write`。这是为了防止更难以调试的数据损坏（如指针损坏、哈希表结构损坏）。这是Go语言特有的安全设计——宁可崩溃也不静默损坏。

---

## 9.2 sync.Mutex互斥锁

### 基本使用

```go
var mu sync.Mutex  // 零值可直接使用

func Deposit(amount int) {
    mu.Lock()
    balance += amount
    mu.Unlock()
}

func Balance() int {
    mu.Lock()  // 也可以使用mu.TryLock()（Go 1.18+）
    b := balance
    mu.Unlock()
    return b
}
```

### 可重入性

Go的`sync.Mutex`**不是可重入的**，即同一个goroutine不能对已加锁的Mutex再次Lock：

```go
func f() {
    mu.Lock()
    g()     // 如果g也Lock同一mutex → ❌ deadlock
    mu.Unlock()
}

func g() {
    mu.Lock()   // ❌ fatal error: all goroutines are asleep - deadlock!
    mu.Unlock()
}
```

### 🔥 面试扩展

**高频题1：为什么Go选择不可重入的Mutex？**
> 1. **实现简单**：不需要追踪"谁是锁的持有者"
> 2. **强制良好设计**：不可重入迫使你清晰地划分加锁边界，避免锁状态混乱
> 3. **性能更好**：可重入锁（递归锁）需要跟踪锁的持有者和递归深度
> 4. 如果确实需要递归锁定，可通过**信号量实现**或使用`sync.Mutex`配合条件重新组织代码

**高频题2：Mutex在goroutine中是否能跨协程解锁？**
> **可以但不能保证安全。** Mutex允许一个goroutine Lock，另一个goroutine Unlock。但不推荐这样做——违反了谁加锁谁解锁的原则。

**高频题3：Go 1.18+的`TryLock`的用途和风险？**
```go
if mu.TryLock() {
    defer mu.Unlock()
    // 获得了锁，可以操作
} else {
    // 未获得锁，做其他事情
}
```
> TryLock用于**非阻塞尝试**。风险是可能导致锁获取的不公平性，不建议常规使用。

**高频题4：Mutex的底层实现？**
> Go 1.18+的Mutex实现：
> 1. **正常模式**：等待者按FIFO排队，被唤醒的goroutine和刚来的goroutine竞争
> 2. **饥饿模式**：当一个goroutine等待超过1ms，进入饥饿模式，Mutex直接交给队首的goroutine
> 这种设计避免了"刚来的goroutine总是抢到锁，老等待者被饿死"的问题。

---

## 9.3 sync.RWMutex读写锁

```go
var mu sync.RWMutex
var balance int

func Balance() int {
    mu.RLock()       // 读锁：多个goroutine可同时获取
    defer mu.RUnlock()
    return balance
}

func Deposit(amount int) {
    mu.Lock()        // 写锁：互斥
    defer mu.Unlock()
    balance += amount
}
```

### 性能特征

- 读操作（RLock）可以并发多个
- 写操作（Lock）必须互斥
- 有写等待时，新读操作被阻塞（防止写饥饿）

### 🔥 面试扩展

**高频题1：RWMutex适合什么场景？不适合什么场景？**
> 适合：
> - 读远多于写的场景（如配置快照、缓存查询）
> - 需要频繁读取但很少修改的共享数据
>
> 不适合：
> - 读写相当或写多的场景（RWMutex开销比Mutex大）
> - 读操作非常快（Mutex的锁竞争时间很短，RWMutex的额外开销不划算）

**高频题2：RWMutex的写饥饿问题？**
> 新读操作不断加入，导致写锁永远得不到执行。Go的RWMutex有解决机制：
> 当有写操作在等待时，新来的读操作RLock**不会直接成功**，而是排队在后面。这确保写操作不会无限等待。

---

## 9.4 内存同步

### 编译器/硬件重排

没有同步的情况下，不同goroutine对内存的修改顺序可能不同：

```go
var x, y int

// goroutine A
x = 1
y = 1

// goroutine B
fmt.Println(y)
fmt.Println(x)
// 可能输出 "0 1" 或 "1 0" 甚至 "0 0"！
// 因为A中x=1可能在y=1之后才被B看到（CPU重排或编译器重排）
```

### happens-before关系

- 在一个goroutine内，代码按顺序happens-before
- `sync.Mutex.Lock()` happens-before Unlock后下一个Lock
- `close(ch)` happens-before `<-ch`收到零值
- `ch <- v` happens-before `v = <-ch`

### 🔥 面试扩展

**高频题1：Go的内存模型（Memory Model）是什么？**
> Go的内存模型定义了goroutine之间对变量读写的可见性保证：
> - 一个goroutine内部的读写按程序顺序执行（单线程语义保证）
> - 不同goroutine间的同步通过**同步原语**建立happens-before关系
> - 没有同步的并发读写是**未定义行为**（Go的竞争检测器可以发现）

**高频题2：为什么会有CPU指令重排？**
> CPU为了优化性能，会乱序执行指令。关键点是保证**单线程语义**不变：
> - 在单线程中，重排不影响最终结果（程序员看不到）
> - 在多线程中，重排导致其他线程看到不一致的修改顺序
> 现代CPU通过**内存屏障（memory barrier）**指令强制顺序。

---

## 9.5 sync.Once惰性初始化

```go
var (
    once   sync.Once
    config *Config
)

func LoadConfig() *Config {
    once.Do(func() {
        config = loadConfigFromFile()  // 只执行一次
    })
    return config
}
```

### 🔥 面试扩展

**高频题1：`sync.Once`的源码实现？**
```go
type Once struct {
    done uint32  // 0=未执行，1=已执行
    m    Mutex
}

func (o *Once) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 0 {  // 快速路径
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done == 0 {
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}
```
> 核心思路：先原子读检查（快速路径），再加锁执行（慢路径）。双重检查锁定（Double-checked Locking）模式的Go版本。

**高频题2：`sync.Once`的`done`为什么用`atomic`操作而不用普通变量？**
> 如果用普通变量，goroutine A执行完`f()`设置`done=1`时，goroutine B可能看不到这个写入（没有happens-before关系）。`atomic.StoreUint32`和`atomic.LoadUint32`保证可见性。

**高频题3：`sync.Once`中`f`如果panic了会怎样？**
> `sync.Once`不处理panic——如果`f` panic了，`once.done`不会被设为1，下次调用`Do`时会重新执行`f`。这个行为在Go 1.x中一直存在争议。

---

## 9.6 竞争条件检测

```go
// 使用 -race 标志运行
$ go test -race mypkg
$ go run -race myserver.go
$ go build -race mycmd

// race detector实际输出
var counter int
go func() {
    counter++          // 写入
}()
fmt.Println(counter)  // 读取
// WARNING: DATA RACE
// Read at ...
// Previous write at ...
```

### 🔥 面试扩展

**高频题1：race detector的工作原理？**
> 基于**ThreadSanitizer（TSan）**技术：
> 1. 编译器在所有内存访问处插入检测代码
> 2. 运行时维护一个"访问历史"的阴影内存（shadow memory）
> 3. 当检测到冲突访问（一个写和一个读/写之间没有happens-before），报告race
> 缺点：程序运行慢5-10倍，内存占用高（2-5x），且只能检测运行时出现的race

**高频题2：为什么race detector不能保证发现所有race？**
> 1. **运行时**：只检测当前执行路径上的访问
> 2. **非确定性**：race是否触发依赖于调度器决策
> 3. **不同的输入/并发模式**会导致不同的race
> 结论：race detector是调试工具，不是证明工具。**确保没有race需要严格的设计**（如CSP模式）。

---

## 9.7 示例: 并发的非阻塞缓存

```go
// 缓存系统的演进
// 版本1：使用Mutex（简单但串行化）
type Memo struct {
    f     Func
    mu    sync.Mutex
    cache map[string]result
}

func (memo *Memo) Get(key string) (value interface{}, err error) {
    memo.mu.Lock()
    defer memo.mu.Unlock()
    if res, ok := memo.cache[key]; ok {
        return res.value, res.err
    }
    res := memo.f(key)
    memo.cache[key] = res
    return res.value, res.err
}

// 版本2：使用duplicate suppression（避免重复计算）
type entry struct {
    res   result
    ready chan struct{}  // 当result准备好时关闭
}

func (memo *Memo) Get(key string) (value interface{}, err error) {
    memo.mu.Lock()
    e := memo.cache[key]
    if e == nil {
        // 第一个请求，创建entry
        e = &entry{ready: make(chan struct{})}
        memo.cache[key] = e
        memo.mu.Unlock()

        e.res.value, e.res.err = memo.f(key)
        close(e.ready)  // 广播完成
    } else {
        memo.mu.Unlock()
        <-e.ready  // 等待完成
    }
    return e.res.value, e.res.err
}
```

### 🔥 面试扩展

**高频题1：`close(e.ready)`广播和`sync.WaitGroup`的工作有何异同？**
> - 相同：都能等待多个goroutine完成
> - 不同：`close(ch)`是**一次性广播**，所有等待者同时收到通知；`WaitGroup`可**多次使用**（Add/Wait）。
> 这里的`ready chan struct{}`本质上是"一次性事件"。

---

## 9.8 Goroutines和线程

### Goroutine栈

- 初始栈：~2KB（远小于线程的1MB）
- 动态增长：通过stack copying实现（Go 1.4+使用连续栈）
- 最大栈：64位系统上1GB

### 调度

| 特性 | Go运行时调度 | OS线程调度 |
|------|-------------|-----------|
| 调度方式 | M:N调度（M个goroutine在N个OS线程上） | 1:1（一个线程对应一个内核线程） |
| 切换成本 | 低（仅保存/恢复少量寄存器） | 高（完整的上下文切换） |
| 调度点 | channel操作、系统调用、主动yield | 时间片中断 |
| 亲和性 | 不保证 | 可通过sched_setaffinity设置 |

### GOMAXPROCS

```go
runtime.GOMAXPROCS(0)  // 获取当前值
runtime.GOMAXPROCS(4)  // 设置为4
```

### 🔥 面试扩展

**高频题1：goroutine和OS线程的对应关系？**
> M:N调度模型：
> - 程序启动时创建和GOMAXPROCS相等数量的P
> - 每个P绑定一个M（OS线程）
> - 一个M上可运行多个G
> - 当G阻塞（系统调用、channel操作），M被释放去执行其他G
> - 当所有M都阻塞时，Go运行时创建新的M

**高频题2：goroutine阻塞在系统调用时会发生什么？**
> 1. 当前M（线程）和P解绑
> 2. P去寻找另一个M（从休眠队列或新建）
> 3. M继续执行P的本地队列中的其他G
> 4. 原来的系统调用完成后，M尝试找P接管；找不到则将G放入全局队列
>
> 这就是Go并发模型处理阻塞系统调用的方式——**不浪费线程，P始终在工作**

**高频题3：network poller（网络轮询器）的作用？**
> Go对非阻塞网络IO使用了特殊的处理：
> 1. goroutine发起网络读/写时，如果操作暂不可用，goroutine被挂起
> 2. M可以继续执行其他goroutine（不会被阻塞）
> 3. 网络轮询器（netpoller）在后台监控所有已注册的描述符
> 4. 当数据准备好时，对应的goroutine被唤醒
> 这是goroutine在IO密集型场景下比线程优越的核心原因。

## ⚡ 超级扩展

### ⚡ 9.1 sync.Mutex 的完整内部实现

#### Mutex的自旋锁和信号量

```go
// runtime/lock_futex.go (Linux)
// sync.Mutex 不是用自旋锁实现的，而是用信号量：

// sync.Mutex内部结构
// src/sync/mutex.go
type Mutex struct {
    state int32   // 32位状态（4个字段打包）
    sema  uint32  // 信号量
}

// state 各比特位的含义：
// mutexLocked:     第0位 — 是否被锁定
// mutexWoken:      第1位 — 是否有goroutine被唤醒
// mutexStarving:   第2位 — 是否处于饥饿模式
// mutexWaiterShift: 第3位+ — 等待者的数量
```

#### 正常模式 vs 饥饿模式

```go
// 正常模式：
// - 等待者按FIFO顺序排队
// - 被唤醒的goroutine和CPU上正在运行的goroutine竞争锁
// - 新来的goroutine已有CPU，更容易抢到锁（因为被唤醒的需要调度）
// - 可能导致等待者长时间无法获取锁（被"饿死"）

// 饥饿模式（Go 1.9+引入）：
// - 当等待者等待超过1ms时进入饥饿模式
// - 锁直接交给队首的等待者
// - 新来的goroutine不再试图抢锁，直接排队
// - 当队首等待者获得锁后，如果等待时间<1ms或有其他等待者，退出饥饿模式
// - 防止"枪手"goroutine饿死"排队"goroutine
```

#### Mutex拷贝保护

```go
type Counter struct {
    mu sync.Mutex
    val int
}

func (c Counter) Inc() {  // ❌ 值接收器！
    c.mu.Lock()  // 拷贝了Mutex
    c.val++
    c.mu.Unlock()
}

// 使用go vet检测：
// $ go vet ./
// ./main.go:6:9: Inc passes lock by value: Counter

// 修复：使用指针接收器
func (c *Counter) Inc() {
    c.mu.Lock()
    c.val++
    c.mu.Unlock()
}
```

---

### ⚡ 9.2 原子操作的完整详解

#### sync/atomic 包的底层实现

```go
// atomic.AddInt64(&x, 1)
// 编译为LOCK XADDQ指令（x86_64）

// 底层代码（src/sync/atomic/doc.go）
func AddInt64(addr *int64, delta int64) (new int64)

// 常用原子操作
atomic.LoadInt64(&x)       // 原子读取
atomic.StoreInt64(&x, 42)  // 原子写入
atomic.AddInt64(&x, 1)     // 原子加减
atomic.SwapInt64(&x, 42)   // 原子交换
atomic.CompareAndSwapInt64(&x, old, new)  // CAS

// 原子指针（Go 1.19+）
type Config struct{}
var ptr atomic.Pointer[Config]
cfg := &Config{}
ptr.Store(cfg)
loaded := ptr.Load()
```

#### Mutex vs 原子操作的性能

```go
// 原子操作: ~5ns（CPU指令级）
// Mutex:
//   - 无竞争: ~20ns
//   - 竞争激烈: ~数百ns到μs
// RWMutex (读): ~15-25ns
// Channel: ~50-100ns
```

---

### ⚡ 9.3 内存模型的完整规则

#### happens-before 保证

```go
// Go的内存模型定义了以下 happens-before 规则：

// 1. 同一个goroutine内：程序顺序保证
x := 1
fmt.Println(x)  // 保证看到x=1

// 2. Mutex: Unlock() happens-before 下一次Lock()
var mu sync.Mutex
var x int

// goroutine A
mu.Lock()
x = 42
mu.Unlock()  // 同步点

// goroutine B
mu.Lock()    // 读取A的写入
_ = x         // 保证看到42
mu.Unlock()

// 3. Channel: 发送 happens-before 接收完成
ch := make(chan int, 1)

// goroutine A
x = 42
ch <- 1  // 同步点

// goroutine B
<-ch     // 保证看到x=42
_ = x

// 4. close(channel) happens-before 从已关闭channel接收
// 5. sync.Once.Do(f) 中的f() happens-before 所有Do()返回
// 6. sync.WaitGroup.Add(n) happens-before Wait()返回
// 7. goroutine创建 happens-before goroutine开始执行

// 没有同步的并发读写 = 数据竞争（undefined behavior）
```

---

---

### ⚡ 9.4 sync.Cond条件变量

#### 什么是条件变量——给初二小白

```

想象你在餐厅点餐：
  ❌ 轮询（忙等待）：每隔1秒问服务员"我的饭好了吗？"
     → 浪费你和服务员的时间
  
  ✅ 条件变量：告诉服务员"饭好了喊我"
     → 你可以玩手机，好了自然有人叫你
     → 什么也不浪费
```

#### sync.Cond的使用

```go
// 一个生产者-消费者例子
var (
    mu    sync.Mutex
    cond  = sync.NewCond(&mu)
    ready = false
)

// 消费者（等待者）
func consumer() {
    mu.Lock()
    for !ready {           // 用for不是if！（重要）
        cond.Wait()        // 等待，自动释放锁，被唤醒后重新加锁
    }
    fmt.Println("消费！")
    mu.Unlock()
}

// 生产者（通知者）
func producer() {
    time.Sleep(time.Second)
    mu.Lock()
    ready = true
    cond.Signal()  // 通知一个等待者
    // cond.Broadcast()  // 通知所有等待者
    mu.Unlock()
}
```

#### Wait()的内部工作原理

```go
func (c *Cond) Wait() {
    c.L.Unlock()      // 1. 释放锁（让其他人能拿到锁）
    // 2. 把自己加入等待队列
    // 3. 挂起（gopark）直到被Signal/Broadcast唤醒
    c.L.Lock()        // 4. 重新获取锁（等待唤醒后）
}
```

**为什么Wait()必须用for而不是if？**
```go
// ❌ 错误：虚假唤醒（spurious wakeup）
// 操作系统可能无缘无故唤醒goroutine
if !ready {
    cond.Wait()  // 被唤醒后，!ready可能是false！
}

// ✅ 正确：再次检查条件
for !ready {
    cond.Wait()  // 唤醒后自动检查条件
}
```

#### Signal vs Broadcast

```go
// Signal: 唤醒一个等待者（像"下一个"）
cond.Signal()    // 叫醒队首的一个

// Broadcast: 唤醒所有等待者（像"全场起立"）
cond.Broadcast() // 叫醒全部

// 用哪个？
// 只有一个等待者：Signal
// 所有等待者都要干活：Broadcast
// 不确定：Broadcast（安全但可能浪费）
```

---

### ⚡ 9.5 原子操作的超级详解

#### 为什么需要原子操作？

```go
var counter int64

// 在多核CPU上，counter++ 实际上分三步：
// 1. 从内存读取counter到CPU寄存器    ← goroutine A
// 2. CPU中加1                         ← goroutine B 可能在这步修改了内存的counter
// 3. 写回内存                         ← goroutine A写的是旧值+1，覆盖了B的修改

// 这就是数据竞争！
// 即使只加一行代码：counter++ 也是不安全的
```

#### atomic包的完整使用

```go
var counter int64

// ✅ 原子递增
atomic.AddInt64(&counter, 1)

// ✅ 原子读取
val := atomic.LoadInt64(&counter)

// ✅ 原子写入
atomic.StoreInt64(&counter, 100)

// ✅ 原子交换
old := atomic.SwapInt64(&counter, 200)  // 返回旧值

// ✅ 比较并交换（Compare And Swap）
swapped := atomic.CompareAndSwapInt64(&counter, 200, 300)
// 如果 counter == 200，就设为 300
// 返回是否成功
```

#### 原子操作的底层原理——CPU指令级别

```go
// atomic.AddInt64(&x, 1) 在 x86 CPU上编译为：
// LOCK XADDQ [addr], 1
// └──── 锁住内存总线，其他CPU不能干扰
//      这个操作是一个完整的CPU指令，不会被中断

// 与之对比：
// counter++ 编译为：
//   MOV  [addr], %RAX   ← 读
//   ADD  $1, %RAX       ← 加
//   MOV  %RAX, [addr]   ← 写
// 三步，中间可能被打断
//
// 原子操作 = 一次完成，不可分割（希腊语atomos=不可分割）
```

#### atomic.Value——原子存储任意类型

```go
// Go 1.4+ 引入的 atomic.Value
// 可以原子地读/写任意类型

var config atomic.Value

// 写入（Store原子地替换）
cfg := &Config{Addr: ":8080", Timeout: 30}
config.Store(cfg)

// 读取（Load原子地获取）
cfg := config.Load().(*Config)
fmt.Println(cfg.Addr)  // :8080

// 优点：读操作完全无锁
// 缺点：只能Store整个对象，不能修改内部字段
// 适合：配置热更新、共享快照
```

#### 原子操作的性能（纳秒级）

```go
// 在自己的电脑上测试（结果会不同，但相对比例差不多）
//
// 无锁访问:        ~2ns
// atomic.Add:       ~5ns   ← 比Mutex快10倍
// Mutex.Lock:       ~40ns  ← 有goroutine调度开销
// Mutex（竞争激烈）: ~数μs  ← 可能发生goroutine挂起
// Channel:          ~80ns  ← Channel包含Mutex+拷贝
//
// 结论：
// 简单计数器 → atomic
// 复杂逻辑    → Mutex
// goroutine通信 → Channel
```

---

### ⚡ 9.6 sync.Map——并发安全的map

#### 普通map的问题

```go
m := map[string]int{"a": 1}

go func() {
    for i := 0; i < 10000; i++ {
        m["a"] = i  // 写入
    }
}()

go func() {
    for i := 0; i < 10000; i++ {
        _ = m["a"]   // 读取
    }
}()

// ❌ fatal error: concurrent map read and map write
// Go 运行时检测到并发读写，直接让程序崩溃！
```

#### sync.Map的用法

```go
var m sync.Map

// 写入
m.Store("key", 42)

// 读取
val, ok := m.Load("key")
if ok {
    fmt.Println(val.(int))
}

// 不存在才写入（原子操作）
actual, loaded := m.LoadOrStore("key", 100)
// 如果key存在，返回已有的值和true
// 如果key不存在，存入100，返回100和false

// 删除
m.Delete("key")

// 遍历
m.Range(func(k, v interface{}) bool {
    fmt.Println(k, v)
    return true  // 返回false停止遍历
})
```

#### sync.Map的内部原理（给初中生）

```
sync.Map 内部实际上有 "两个map"：
  read map  — 用于读（不需要加锁！）
  dirty map — 用于写（需要加锁）

工作原理：
1. 读取时先查read map
   → 找到了 → 直接返回（不需要锁）
   → 没找到 → 加锁查dirty map

2. 写入时先加锁
   → 写到dirty map
   → 当dirty map变大的时候，"提升"为read map
   → 查询miss次数超过dirty长度时触发提升

就像商店里的商品：
  read = 货架上的（顾客直接拿，不用问店员）
  dirty = 仓库里的（需要店员去拿）
  每天晚上把仓库的货补到货架上
```

#### sync.Map vs map+sync.RWMutex

```
| 场景                    | sync.Map | map+RWMutex |
|------------------------|----------|-------------|
| 读远多于写              | ✅ 最快  | ❌ 有锁竞争  |
| key很少变化             | ✅ 优化  | ✅ 也可以   |
| 写很多                 | ❌ 慢    | ✅ 更快     |
| key太多（百万级）       | ❌ 内存多 | ✅ 内存少   |
| 不需要并发              | ❌ 慢    | ✅ 更快     |
| 存不同类型的value       | ✅ 可以  | ❌ 必须统一 |

结论：
  sync.Map 在 "写少、读多、key不重复" 的场景最快
  一般场景用 map + RWMutex 更通用
```

---

### ⚡ 9.7 大厂面试题全集（并发篇）

**面试题1：数据竞争的检测方法有哪些？**
```
1. go run -race：运行时检测（推荐）
   运行慢5-10倍，但能发现实际发生的race

2. go vet：静态检查（不能发现所有）

3. 代码审查：人工检查
   - 有并发访问吗？
   - 有同步（Mutex/channel）保护吗？
   - 写操作有锁吗？

4. 压力测试：高并发下更容易触发race
```

**面试题2：这段代码有数据竞争吗？**
```go
var count int

func main() {
    for i := 0; i < 1000; i++ {
        go func() {
            count++  // 有竞争！1000个goroutine同时读写
        }()
    }
    time.Sleep(time.Second)
    fmt.Println(count)  // 不是1000！可能是998、999
}

// 修复方式：
// 方案1: atomic.AddInt64
// 方案2: sync.Mutex
// 方案3: channel
```

**面试题3：死锁的条件（银行家算法简化版）**
```go
// 死锁的4个必要条件（全部满足才会死锁）：
// 1. 互斥：资源一次只能给一个线程
// 2. 持有等待：线程拿着一个资源，还等待另一个
// 3. 不可剥夺：资源不能被强制拿走
// 4. 循环等待：A等B的资源，B等A的资源

// Go中经典的死锁：
func main() {
    ch := make(chan int)
    ch <- 1  // ⚠️ 死锁！向无缓冲channel发送，但没人接收
    <-ch     // 这行永远不会执行到
}
// fatal error: all goroutines are asleep - deadlock!
```

**面试题4：为什么Go map的并发读也会panic？**
```go
m := map[int]int{1: 10}

// goroutine A
for i := 0; i < 1000; i++ {
    _ = m[1]  // 读
}

// goroutine B
for i := 0; i < 1000; i++ {
    m[1] = i  // 写
}
// 运行时：fatal error: concurrent map read and map write

// Go为什么设计成这样？
// 回答：读可能导致map内部结构变化（如"发现需要扩容"）
// 所以map设计成完全不能并发
// 这叫"不是警告，是错误"——Go的设计哲学
```

**面试题5：写一个无锁的计数器**
```go
type Counter struct {
    value int64
}

func (c *Counter) Inc() {
    atomic.AddInt64(&c.value, 1)
}

func (c *Counter) Value() int64 {
    return atomic.LoadInt64(&c.value)
}

// 使用：
var c Counter
var wg sync.WaitGroup

for i := 0; i < 1000; i++ {
    wg.Add(1)
    go func() {
        c.Inc()
        wg.Done()
    }()
}
wg.Wait()
fmt.Println(c.Value())  // 一定是1000
```

**面试题6：RWMutex的读锁能递归加吗？**
```go
var mu sync.RWMutex

func Read() {
    mu.RLock()
    defer mu.RUnlock()
    
    ReadSub()  // 调用另一个读函数
}

func ReadSub() {
    mu.RLock()  // ❌ 死锁！同一goroutine不能递归加读锁
    defer mu.RUnlock()
    // 不是可重入锁！
}

// 修复：需要重构代码避免递归加锁
```

**面试题7：sync.Once的两个goroutine同时调用会怎样？**
```go
var once sync.Once

func setup() {
    fmt.Println("只执行一次")
}

func main() {
    go once.Do(setup)  // goroutine A
    go once.Do(setup)  // goroutine B
    time.Sleep(time.Second)
}
// 输出："只执行一次"（只打印一次！）
// 
// 内部机制：
// goroutine A：看到done=0，加锁，执行setup，设done=1，解锁
// goroutine B：看到done=0也进来，加锁时发现已锁，等A释放
//            然后看到done=1，不执行setup，直接解锁返回
```

---

---

### ⚡ 9.8 原子类型和Once的新用法（Go 1.19+）

#### atomic.Int64、atomic.Bool、atomic.Pointer（Go 1.19+）

Go 1.19引入了类型安全的原子操作！

```go
import "sync/atomic"

// 以前：用函数（容易搞混类型）
var val int64
atomic.AddInt64(&val, 1)

// 现在：用类型安全的方法（推荐！）
var val atomic.Int64
val.Add(1)             // 不用传指针！
val.Store(42)
n := val.Load()        // 42
val.Swap(100)          // 返回旧值：42
swapped := val.CompareAndSwap(100, 200)  // 如果=100就改成200

// atomic.Bool
var flag atomic.Bool
flag.Store(true)
fmt.Println(flag.Load())  // true

// atomic.Pointer[T]——类型安全的原子指针
type Config struct {
    Addr  string
    Port  int
}

var cfg atomic.Pointer[Config]
cfg.Store(&Config{Addr: "localhost", Port: 8080})
c := cfg.Load()
fmt.Println(c.Addr)  // localhost

// 对比以前的 unsafe.Pointer 方式：
// 旧：需要 unsafe.Pointer 强制转换，容易错
// 新：泛型保证类型安全，编译期检查
```

#### OnceFunc、OnceValue、OnceValues（Go 1.21+）

```go
// sync.Once：确保函数只执行一次
// 但Go 1.21给了更方便的变体！

var once sync.Once
var result int
once.Do(func() {
    result = expensive()
})

// OnceFunc：返回一个"只执行一次"的函数
loadOnce := sync.OnceFunc(func() {
    fmt.Println("只执行一次！")
})
loadOnce()  // 打印
loadOnce()  // 不打印
loadOnce()  // 不打印

// OnceValue：返回一个"只计算一次的值"
getConfig := sync.OnceValue(func() *Config {
    fmt.Println("加载配置...")
    return &Config{Addr: ":8080"}
})

cfg1 := getConfig()  // 加载配置...
cfg2 := getConfig()  // 不打印（直接返回缓存的结果）
fmt.Println(cfg1 == cfg2)  // true（同一个指针）

// OnceValues：返回两个值（常用于返回值和error）
getDB := sync.OnceValues(func() (*sql.DB, error) {
    return sql.Open("sqlite3", ":memory:")
})

db, err := getDB()  // 第一次：执行
_, _ = getDB()      // 第二次：直接返回缓存的结果
```

---

---

### ⚡ 9.9 再补3道大厂面试题

**面试题8：写一个并发安全的计数器**
```go
type SafeCounter struct {
    val atomic.Int64
}

func (c *SafeCounter) Inc()  { c.val.Add(1) }
func (c *SafeCounter) Dec()  { c.val.Add(-1) }
func (c *SafeCounter) Val() int64 { return c.val.Load() }

var c SafeCounter
var wg sync.WaitGroup
for i := 0; i < 1000; i++ {
    wg.Add(1)
    go func() { c.Inc(); wg.Done() }()
}
wg.Wait()
fmt.Println(c.Val())  // 1000
```

**面试题9：RWMutex什么时候比Mutex好？**
```
RWMutex = 读写锁
  读锁（RLock）：多个goroutine同时加读锁
  写锁（Lock）：互斥

读远多于写时RWMutex快
读1万次/写1次 → RWMutex
读写相当 → Mutex
```

**面试题10：Cond条件变量用法**
```go
var mu sync.Mutex
cond := sync.NewCond(&mu)
var ready bool

// 等待者
func waiter() {
    mu.Lock()
    for !ready { cond.Wait() }
    fmt.Println("条件满足，继续")
    mu.Unlock()
}

// 通知者
func notifier() {
    mu.Lock()
    ready = true
    cond.Signal()  // 叫醒一个
    mu.Unlock()
}
```

---

---

### ⚡ 9.10 Mutex、原子操作和内存模型的完整流程图

#### 数据竞争的产生流程图

```
两个goroutine同时修改同一变量

Goroutine A                Goroutine B
    │                          │
    │ count++                  │ count++
    │                          │
    ├─LOAD count(=0)           │
    │                          ├─LOAD count(=0)←读到了旧值！
    │ ADD 1                    │
    │                          │ ADD 1
    ├─STORE count(=1)          │
    │                          ├─STORE count(=1)←覆盖了A的修改
    ▼                          ▼
  结果：count=1（而不是2！）——数据竞争！
```

#### Mutex加锁/解锁的完整流程

```
         ┌────────────────────┐
         │  Goroutine A       │
         │  mu.Lock()         │
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │ 有锁冲突？        │
         └─────────┬──────────┘
              是↓  │  ↓否
                │  │
          ┌─────┴──┴──────┐
          │ 进入等待队列    │←─── Goroutine B
          │ (gopark挂起)   │      mu.Lock()—等在这里
          └───────┬────────┘
                  │
            被唤醒↓
                  │
          ┌───────┴──────────┐
          │ 获得锁，执行临界区│      ← 只有一个Goroutine能进
          │ balance += amount │
          └───────┬──────────┘
                  │
          ┌───────┴──────────┐
          │ mu.Unlock()       │
          │ 唤醒等待队列中的  │
          │ 下一个goroutine   │
          └──────────────────┘
```

#### 饥饿模式 vs 正常模式流程图

```
正常模式：
  ┌─────┐  Lock ┌─────────────┐  ┌──────┐
  │新来的│──────→│ 和排队中的   │←─│队列  │
  │goro │  抢占 │ 一起抢锁    │  │等待者│
  └─────┘       └─────────────┘  └──────┘
                → 新来的往往抢赢（已在CPU上跑）
                → 等待者可能"饿死"

饥饿模式（一个等待者等待超过1ms后进入）：
  ┌─────┐       ┌─────────────┐  ┌──────┐
  │新来的│──────→│  排队！      │→│队列  │
  └─────┘ 排队   │  锁直接交给  │  │等待者│
                   │  队首等待者  │  └──────┘
                   └─────────────┘
                   → 公平了
```

#### RWMutex读写锁流程图

```
         RWMutex
         ┌────┬────┐
         │ 读 │ 写 │
         └─┬──┴──┬─┘
           │    │
     ┌─────┘    └──────┐
     ▼                 ▼
  RLock()            Lock()
     │                 │
     ▼                 ▼
┌──────────┐    ┌──────────────┐
│多个goro  │    │只允许一个    │
│可以同时  │    │获得写锁      │
│获得读锁  │    └──────┬───────┘
└────┬─────┘           │
     │                 ▼
     ▼         ┌──────────────┐
读1 读2 读3    │写操作进行中…  │
     │         │写时不能读     │
     │         │读时不能写     │
     ▼         └──────────────┘
  ┌───────┐
  │解锁    │
  │RUnlock│
  └───────┘
```

#### 原子操作的CPU指令级图

```
count++（非原子，3步）：
┌──────┐  ┌──────┐  ┌──────┐
│ LOAD │→│ ADD  │→│STORE │  ← 中间可能被中断
└──────┘  └──────┘  └──────┘

atomic.AddInt64（原子，1指令）：
┌──────────────────────────┐
│   LOCK XADDQ [addr], 1   │ ← CPU锁住内存总线
│   一个指令，不可分割      │ ← 不能被其他CPU中断
└──────────────────────────┘

就像：
  count++ = "拿起杯子→喝水→放下杯子"（三步，中间会被打断）
  atomic.Add = "一口闷！"（一步完成，不可中断）
```

#### sync.Once的执行流程图

```
         once.Do(f)
             │
             ▼
    ┌────────────────┐
    │ atomic.Load     │
    │ done == 1 ?     │
    └───┬──────┬─────┘
      是│      │否
        │      ▼
    直接返回┌────────────┐
           │ 加锁       │
           └────┬───────┘
                ▼
        ┌────────────────┐
        │ done == 0 ?    │（双重检查）
        └───┬──────┬─────┘
          是│      │否→直接返回
            │
            ▼
        ┌────────────┐
        │ 执行 f()    │← 只执行一次！
        │ atomic.Store│
        │ done = 1    │
        └────────────┘
```

---

> **下一章**：[第10章 包和工具](./ch10-packages-tools.md) —— 包的组织、导入路径、初始化、go工具链。
