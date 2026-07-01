# 第9章 基于共享变量的并发

> **大白话版：** 当多个人（多个goroutine）同时用同一个东西（变量）时，就会打架！
> 这一章就是教你怎么防止它们打架的——用"锁"。

---

## 零基础小课堂：为什么要加锁？

想象你和你的朋友共用一个存钱罐：

你："存钱罐里有100块，我要放10块进去"
1. 你看了一眼：有100块
2. 你去拿钱
3. **就在这时**你的朋友也来看了："100块啊，我拿20块"
4. 他拿走了20块
5. 你放进去10块 → 你记的是110块，但实际只有90块！

**这就是"数据竞争"——两个人同时动同一个东西，乱套了！**

怎么解决？用一个"锁"：
- 你拿钱时，锁上存钱罐（其他人不能动）
- 你放完钱，打开锁
- 朋友再来拿 → 至少有正确数据

```go
var 锁 sync.Mutex

func 存钱(金额 int) {
    锁.Lock()      // 锁上！别人不能动
    余额 = 余额 + 金额
    锁.Unlock()    // 打开！别人可以动了
}
```

**锁 = 让同时只能一个人操作，不乱！**

---

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

### 大白话竞争条件

两个人同时动一个东西=竞争条件。前面用存钱罐例子：

你：看一下余额100 → 你朋友也看到100 → 他取20 → 你存10
你记：100+10=110
实际：100-20+10=90
账不对了！

这就是竞争条件：两人同时操作一个数据，结果乱了。

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

### 大白话Mutex

Mutex=互斥锁。一次只能一个人持有。

就像厕所门锁：
你进去→锁门→别人进不来→你用完了→开门→别人用

var mu sync.Mutex
mu.Lock()   // 锁！别人不能进
余额++
mu.Unlock() // 开锁！别人可以进了

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

### 大白话RWMutex

RWMutex=读写锁。读可以一起读，写只能一个人写。

就像图书馆的书：
- 读：100个人可以同时看同一本书（不冲突）
- 写：只能一个人往书上写笔记（别人不能同时写）

var rw sync.RWMutex
rw.RLock() // 读锁：可以多人同时读
rw.RUnlock()
rw.Lock() // 写锁：只能一个人
rw.Unlock()

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

### 大白话内存同步

两个goroutine之间"你的修改我能看到"。

就像对讲机：
你说了一句话→要等1秒→对方才能听到

内存同步=保证你说的对方一定能听到，不会漏！

锁不止保护数据，还保证"你改的我能看到"。

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

---

### ⚡ 9.11 并发同步的纳米级图解大全

#### 竞条件产生的完整时序图

```
时间 →

Goroutine A              count         Goroutine B
    │                      │                │
    │  LOAD count(=0)      │                │
    │ ←──── 0 ───────     │                │
    │                      │                │
    │  ADD 1               │    LOAD count(=0)
    │                      │ ←──── 0 ────  │
    │  STORE count(=1)     │                │
    │ ──── 1 ──────→      │                │
    │                      │    ADD 1       │
    │                      │                │
    │                      │    STORE count(=1) ← 覆盖了！
    │                      │ ──── 1 ────→  │
    │                      │                │
    ▼                      ▼                ▼
  期望结果：2              count=1 ❌      期望结果：2
  （悲局：A的计算被B覆盖了）

解决方法：让LOAD-ADD-STORE变成原子操作
  → sync.Mutex
  → atomic.AddInt64
```

#### Mutex实现互斥的完整流程图

```
多个goroutine竞争锁：

          ┌────┐ ┌────┐ ┌────┐
          │ G1 │ │ G2 │ │ G3 │
          └─┬──┘ └─┬──┘ └─┬──┘
            │      │      │
            ▼      ▼      ▼
      ┌────────────────────────┐
      │     mu.Lock()          │
      │    谁先拿到锁？        │
      └──────────┬─────────────┘
                 │
            ╔════╧════╗
            ▼         ▼
      ┌────────┐  等待队列
      │ G1拿到锁 │  ┌────────┐
      │ 执行临界 │  │ G2     │
      │ 区代码  │  ├────────┤
      │ balance │  │ G3     │
      │ += amt  │  └────────┘
      └───┬────┘
          │
          │ mu.Unlock()
          ▼
      ┌──────────────────────┐
      │ 从等待队列唤醒一个人  │
      │ → G2拿到锁           │
      └──────────────────────┘
```

#### Mutex的正常模式 vs 饥饿模式对比

```
正常模式（公平竞争）：
  等待者被唤醒后，和当前正在CPU上跑的goroutine一起抢锁
  
  等待者（刚睡醒）     新来的goroutine（正在CPU上跑）
  ┌─────────┐           ┌─────────────┐
  │慢半拍   │    VS     │ 反应更快    │
  │抢不到锁 │           │ 总是抢赢    │
  └─────────┘           └─────────────┘
  
  问题：等待者可能永远抢不到锁 → 饿死

饥饿模式（排队公平）：
  当一个等待者等了超过1ms就进入饥饿模式
  
  锁直接交给队首的等待者
  新来的goroutine必须排队，不能抢
  
  就像医院挂号：
    正常模式：谁跑得快谁先看医生
    饥饿模式：先来后到，排队
```

#### RWMutex的应用场景对比图

```
               RWMutex
                  │
          ┌───────┴────────┐
          │                │
      🔓 RLock()       🔒 Lock()
      (读锁)            (写锁)
          │                │
      ┌───┴───┐        ┌──┴──┐
      │多个goro│        │只有  │
      │可以同时│        │一个  │
      │读     │        │能写  │
      └───┬───┘        └──┬───┘
          │                │
      适合读多写少的场景：

  场景A：配置热更新
    读取配置：100次/秒 ✅ 全部RLock
    更新配置：1次/小时 ✅ 偶尔Lock
    → RWMutex最适合

  场景B：高频计数器
    读取：50次/秒
    写入：50次/秒
    → 直接用Mutex（RWMutex的开销不划算）

  场景C：缓存
    读取：9999次/秒
    写入：1次/秒
    → RWMutex完美
```

#### sync.Once执行流程图（双重检查锁定）

```
              once.Do(f)
                  │
                  ▼
        ┌──────────────────┐
        │ atomic.LoadUint32│  ← 快速检查（不加锁）
        │ &once.done       │
        │  == 1 ?          │
        └──────┬───────────┘
              │
           是↓│  ↓否（=0）
              │ │
        ┌─────┴─┴──────────┐
        │ 直接返回          │
        │（已经执行过了）    │
        └──────────────────┘
              │
              ▼
        ┌──────────────────┐
        │ 加锁             │
        │ mu.Lock()        │
        └──────┬───────────┘
              │
              ▼
        ┌──────────────────┐
        │ 再次检查 done    │  ← 双重检查
        │ == 0 ?           │
        └──────┬───────────┘
              │
           是↓│  ↓否
              │ │
              │ └──→ 直接返回（另一goroutine已经执行了）
              ▼
        ┌──────────────────┐
        │ 执行 f()          │  ← 真的只执行一次！
        │ atomic.StoreUint32│
        │ &once.done = 1   │
        │ 解锁             │
        └──────────────────┘

就像：
  第一次：开门前先看看门锁了吗（快速检查）
         如果没锁，掏出钥匙锁门（加锁）
         再看看是不是已经锁了（双重检查）
         确实没锁 → 锁门（执行）
```

#### 竞争检测器工作原理图

```
        go run -race main.go
                 │
                 ▼
       ┌──────────────────┐
       │ 编译器在所有内存   │
       │ 访问前插入检测代码  │
       └────────┬─────────┘
                 │
                 ▼
       ┌──────────────────┐
       │ 运行时维护"访问历史" │
       │ shadow memory    │
       │ 每个内存位置记录：  │
       │ - 哪个goroutine  │
       │ - 读还是写        │
       │ - 时间戳          │
       └────────┬─────────┘
                 │
                 ▼
       ┌──────────────────┐
       │ 检测到冲突：      │
       │ G1写x时 G2也在写x│
       │ 没有同步保护     │
       │ → REPORT!       │
       └──────────────────┘

输出示例：
  ==================
  WARNING: DATA RACE
  Read at 0x... by goroutine 5:
    main.main() main.go:10
  Previous write at 0x... by goroutine 6:
    main.main() main.go:10
  ==================
```

#### Deadlock（死锁）的流程图

```
死锁的4个必要条件（同时满足就死锁）：

1. 互斥：资源一次只能一个人用
2. 持有等待：拿着一个资源等另一个
3. 不可剥夺：别人不能强行拿走你的资源
4. 循环等待：你等我，我等她，她等你

Go经典死锁例子：

Goroutine A:                     Goroutine B:
  mu1.Lock() ← 拿到锁1             mu2.Lock() ← 拿到锁2
     │                                │
     │ time.Sleep                   │ time.Sleep
     │                                │
     │ mu2.Lock() ← 等锁2            │ mu1.Lock() ← 等锁1
     │    锁2被B拿着！           │    锁1被A拿着！
     ▼                                ▼
  ⚠️ A等B释放锁2                  ⚠️ B等A释放锁1
  B等A释放锁1                      A等B释放锁2
  → 互相等待 → 永远卡住 → 死锁！

Go运行时会检测到死锁：
  fatal error: all goroutines are asleep - deadlock!
```

---

---

### ⚡ 9.12 大厂面试题扩展（共享并发篇·10道）

**面试题1：Mutex和RWMutex有什么区别？**
```
Mutex（互斥锁）：
  Lock：只有一个goroutine能拿到
  Unlock：释放锁
  适合：读写差不多的场景

RWMutex（读写锁）：
  RLock：多个goroutine可以同时读
  Lock：写的时候只能一个人
  适合：读远多于写的场景

选择：
  读1万次/写1次 → RWMutex
  读1次/写1次 → Mutex（RWMutex有额外开销）
```

**面试题2：什么是自旋锁？Go的Mutex是自旋锁吗？**
```
自旋锁：反复检查锁是否释放（CPU空转）
  适合：锁等待时间极短

Go的Mutex不是纯自旋锁
  先尝试自旋几次
  如果不行 → goroutine挂起（不浪费CPU）
  这样结合了自旋和阻塞的优点
```

**面试题3：Go的Mutex是可重入的吗？**
```go
var mu sync.Mutex

func f() {
    mu.Lock()
    g()      // g也Lock → 死锁！
    mu.Unlock()
}

func g() {
    mu.Lock()  // ❌ 同一个goroutine再锁一次
    mu.Unlock()
}
// Go的Mutex不是可重入的！
// 防止你在同一个goroutine里重复加锁
```

**面试题4：什么是数据竞争？怎么检测？**
```go
var count int

// 两个goroutine同时写count → 数据竞争
go func() { count++ }()
go func() { count++ }()

// 检测：go run -race main.go
// 输出：WARNING: DATA RACE

// 修复：加锁
var mu sync.Mutex
go func() { mu.Lock(); count++; mu.Unlock() }()
```

**面试题5：sync.Once是怎么保证只执行一次的？**
```go
var once sync.Once
var config *Config

func GetConfig() *Config {
    once.Do(func() {
        config = loadConfig()  // 只执行一次
    })
    return config
}

// 原理：双重检查锁定
// 1. 先原子读once.done（不加锁）
// 2. 如果为0（没执行过），加锁
// 3. 再检查一次done是否为0
// 4. 还是0 → 执行函数，设done=1
// 5. 解锁
// 后续调用：直接检查done=1 → 不执行
```

**面试题6：atomic.Value和sync.RWMutex哪个快？**
```go
// atomic.Value：无锁读取
var config atomic.Value
config.Store(&Config{Addr: ":8080"})
cfg := config.Load().(*Config)  // ~5ns

// RWMutex：有锁读取
var mu sync.RWMutex
var cfg *Config
mu.RLock()
c := cfg  // ~15ns
mu.RUnlock()

// atomic.Value适合：配置热更新
// RWMutex适合：需要同时保护多个变量
```

**面试题7：map的并发读写为什么会panic？**
```go
m := make(map[int]int)

// 两个goroutine同时读写
// 即使一个读一个写也会panic！
go func() {
    for { _ = m[1] }  // 读
}()
go func() {
    for { m[2] = 2 }  // 写
}()
// fatal error: concurrent map read and map write

// 修复方案：
// 1. map + sync.RWMutex
// 2. sync.Map（读多写少场景）
// 3. 改为channel通信
```

**面试题8：sync.Map适合什么场景？**
```
适合：
  读远多于写
  多个goroutine读不同的key
  key相对稳定（很少增删）
  如：配置表、缓存

不适合：
  写很多
  key频繁变化
  存大量数据（有内存开销）
```

**面试题9：什么是ABA问题？CAS操作有什么坑？**
```go
// CAS：Compare And Swap
// 比较旧值，如果没变就更新

// ABA问题：
// 1. goroutine A读x = 1
// 2. goroutine B把x改成2
// 3. goroutine C把x改回1
// 4. goroutine A: CAS(x, 1, 3) 成功
//   但x已经不是原来的x了（中间变过）

// Go中CAS的使用：
swapped := atomic.CompareAndSwapInt64(&x, old, new)
// 返回是否成功
```

**面试题10：如何写一个并发安全的生产者-消费者？**
```go
func main() {
    ch := make(chan int, 10)
    done := make(chan bool)
    
    // 生产者
    go func() {
        for i := 0; i < 20; i++ {
            ch <- i
            fmt.Println("生产:", i)
        }
        close(ch)
    }()
    
    // 消费者
    go func() {
        for v := range ch {
            fmt.Println("消费:", v)
            time.Sleep(100 * time.Millisecond)
        }
        done <- true
    }()
    
    <-done
}
// 用channel实现生产者-消费者
// 天然并发安全！不需要锁
```

---

> **下一章**：[第10章 包和工具](./ch10-packages-tools.md) —— 包的组织、导入路径、初始化、go工具链。

---

### 🔬 9.13 底层原理：CPU缓存一致性、内存屏障和原子指令

#### 多核CPU的缓存一致性问题

```
         CPU 0           CPU 1
        ┌──────┐        ┌──────┐
        │ L1   │        │ L1   │
        │ x=42 │        │ x=?  │← CPU1的缓存里可能有旧的x
        └──┬───┘        └──┬───┘
           │               │
           ▼               ▼
        ┌────────────────────────┐
        │      主存（RAM）       │
        │      x=42             │
        └────────────────────────┘

问题：
  CPU0修改x=42（在缓存里）
  CPU1读x → 读的是自己缓存里的旧值
  → 各位CPU看到的数据不一致！

这就是为什么需要"缓存一致性协议"（MESI）
```

#### MESI缓存一致性协议

```
每个缓存行（64字节）有4种状态：

M = Modified（已修改）
  CPU独享，数据已改，但还没写回主存
  ┌──────┐
  │ M    │ ← 这是我的缓存，别人没有
  │ x=42 │     而且我改过了
  └──────┘

E = Exclusive（独占）
  CPU独享，数据和主存一致
  ┌──────┐
  │ E    │ ← 这是我的缓存，别人没有
  │ x=42 │     但我没改过
  └──────┘

S = Shared（共享）
  多个CPU都有这份数据，且一致
  ┌──────┐    ┌──────┐
  │ S    │    │ S    │
  │ x=42 │    │ x=42 │
  └──────┘    └──────┘

I = Invalid（无效）
  数据过期了，需要重新读
  ┌──────┐
  │ I    │ ← 别人改了，我的作废
  │ x=?  │
  └──────┘

状态转换：
  CPU0读x → 发消息给其他CPU："你有x吗？"
  → 没有 → E状态（独占）
  → 有 → S状态（共享）
  
  CPU0写x → 通知其他CPU："你们的x作废！"
  → 其他CPU的x → I状态
  → 自己的x → M状态
```

#### 内存屏障（Memory Barrier）——为什么需要它？

```
为了提高性能，CPU和编译器会重排指令：

代码顺序：
  x = 1
  y = 1
  
实际执行可能：
  y = 1  ← 先执行（因为y的缓存准备好了）
  x = 1  ← 后执行
  
这在单线程下没问题（结果一样）
但在多线程下会导致bug！

Goroutine A：              Goroutine B：
  x = 1                      if y == 1 {
  y = 1                          fmt.Println(x)
                              }

可能的结果：
  1. A先执行x=1 → y=1 → B看到y=1 → x也是1 ✅
  2. CPU重排：A执行y=1 → B看到y=1 → 打印x
     → x还是0！❌

内存屏障（Memory Barrier）：
  告诉CPU和编译器：
  这条指令前后的顺序不能重排！
  
Go中的内存屏障：
  sync.Mutex.Lock/Unlock
  atomic.Load/Store
  channel发送/接收
  这些操作自带内存屏障
```

#### 总线锁——原子指令是怎么保证不被打断的？

```
atomic.AddInt64(&x, 1)

这一行编译成：
  LOCK XADDQ [addr], 1

LOCK前缀的作用：
  ┌─────────────────────────────────┐
  │ 在执行这条指令时：               │
  │ 1. CPU发出LOCK#信号            │
  │ 2. 锁住内存总线                 │
  │ 3. 其他CPU不能访问内存          │
  │ 4. 这条指令执行完→释放总线      │
  └─────────────────────────────────┘

就像：
  你在ATM上取钱时
  ATM机把你关在隔间里（锁总线）
  别人不能同时操作你的账户
  你取完→开门→下一个人
```

#### CAS（Compare And Swap）操作

```go
atomic.CompareAndSwapInt64(&x, old, new)

功能：
  如果 x == old，就把 x = new
  返回是否成功

底层实现（一条CPU指令）：
  LOCK CMPXCHGQ [addr], new
  比较→交换→一条指令完成！

用法——无锁更新：
  for {
      old := atomic.LoadInt64(&x)
      new := old + 1
      if atomic.CompareAndSwapInt64(&x, old, new) {
          break  // 成功
      }
      // 失败 → 重试（别的goroutine改了x）
  }

好处：不需要锁，不会阻塞goroutine
坏处：循环可能空转（高竞争时）
```

#### Go中各种同步机制的性能对比

```
1秒内能执行多少次操作（近似值）：

无锁访问变量：         ~500,000,000次（5亿）
atomic.AddInt64：      ~200,000,000次（2亿）
Mutex Lock/Unlock：    ~50,000,000次（5千万）

channel发送/接收：     ~10,000,000次（1千万）
RWMutex.RLock/RUnlock：~30,000,000次（3千万）

实际的goroutine创建：   ~5,000,000次（5百万）

结论：
  atomic 比 Mutex 快4倍
  Mutex 比 channel 快5倍
  能用atomic用atomic
  不行用Mutex
  channel用于goroutine通信，不是用于保护数据
```

---

### 🧠 9.14 纳米级知识点：锁粒度、Once实现、内存序

#### 锁粒度——锁越大还是越小越好

```
粗粒度锁：一把锁保护所有数据（简单但并发低）
细粒度锁：每个数据自己的锁（并发高但复杂）

Go中：大多数用粗粒度，性能敏感时分片

分片例子：32个map各有一把锁
  不同key用不同map→不同锁→32倍并发
```

#### sync.Once源码——双重检查锁定

```go
func (o *Once) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 0 { // 第一重（无锁）
        o.doSlow(f)
    }
}
func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done == 0 { // 第二重（有锁）
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}
```

#### 内存序——为什么需要happens-before

```
Goroutine A: x=1; y=1
Goroutine B: if y==1 { print(x) }

CPU可能重排→y先执行→B看到y=1时x还是0

happens-before保证：
  Mutex.Unlock() happen-before 下一个Lock()
  channel发送 happen-before 接收
  atomic.Store happen-before 看到新值
```

---

> **下一章**：[第10章 包和工具](./ch10-packages-tools.md) —— 包的组织、导入路径、初始化、go工具链。

### 🎤 Q&A 共享并发篇

**Q: Mutex vs RWMutex？** A: Mutex互斥。RWMutex读共享写互斥。读远多写时用RWMutex。

**Q: atomic vs Mutex哪个快？** A: atomic快约4倍(5ns vs 20ns)。简单计数用atomic，复杂用Mutex。

**Q: 死锁4条件？** A: 互斥、持有等待、不可剥夺、循环等待。破坏任一就能解。

**Q: sync.Once保证只执行一次？** A: 双重检查锁定。原子读→加锁→再检→执行→设done=1。
