# 第8章 Goroutines和Channels

> goroutine和channel是Go并发模型的核心，基于CSP（Communicating Sequential Processes）理论。掌握它们的原理和最佳实践是写出高效并发Go程序的关键。

---

## 目录

- [8.1 Goroutines](#81-goroutines)
- [8.2 示例: 并发的Clock服务](#82-示例-并发的clock服务)
- [8.3 示例: 并发的Echo服务](#83-示例-并发的echo服务)
- [8.4 Channels](#84-channels)
- [8.5 并发的循环](#85-并发的循环)
- [8.6 示例: 并发的Web爬虫](#86-示例-并发的web爬虫)
- [8.7 基于select的多路复用](#87-基于select的多路复用)
- [8.8 示例: 并发的目录遍历](#88-示例-并发的目录遍历)
- [8.9 并发的退出](#89-并发的退出)
- [8.10 示例: 聊天服务](#810-示例-聊天服务)

---

## 8.1 Goroutines

### goroutine的本质

```go
go f()    // 启动一个新的goroutine来执行f()
```

goroutine是Go运行时管理的**用户态线程**（协程），不是OS线程。

### Goroutine vs 系统线程

| 特性 | Goroutine | 系统线程 |
|------|-----------|----------|
| 创建成本 | 约2KB栈 | 约1MB栈 |
| 调度方式 | Go运行时调度器（协作式+抢占式） | 内核调度器（抢占式） |
| 切换成本 | ~50ns（用户态保存3个寄存器） | ~1μs（内核态切换，上下文切换） |
| 数量级 | 数十万到百万 | 数千后性能严重下降 |
| 栈增长 | 动态增缩（stack copying） | 固定大小 |

### 🔥 面试扩展

**高频题1：GMP调度模型是什么？**
> Go的调度器基于GMP模型：
> - **G**（Goroutine）：包含栈、PC、SP等信息的执行上下文
> - **M**（Machine）：代表OS线程，负责执行G
> - **P**（Processor）：逻辑处理器，数量由`GOMAXPROCS`决定（默认CPU核数）
>
> 调度流程：全局队列 → P的本地队列 → M从P取G执行
> 当P的本地队列空时，从其他P或全局队列"偷取"G（work stealing）

**高频题2：goroutine的栈为什么可以很小且可以增长？**
> Go 1.3之前用的是**分段栈（segmented stacks）**，后来改为**连续栈（contiguous stacks）**：
> - 每个goroutine初始分配2KB栈空间
> - 栈空间不够时，Go运行时分配一个更大的新栈（通常是2倍），将原栈内容复制过去
> - 所有栈帧的指针都需要更新（通过stack copying实现，是GC的一部分）
> - 这就是goroutine数量可达百万级的原因——初始化成本极低

**高频题3：goroutine什么时候被挂起（yield/suspend）？**
> 1. channel操作（发送/接收）
> 2. 系统调用（如文件读写、网络IO）——M会和其他P绑定或休眠
> 3. sync操作（Lock、WaitGroup.Wait等）
> 4. time.Sleep
> 5. 主动调用`runtime.Gosched()`
> 6. GC周期
> Go 1.14引入了**基于信号的抢占式调度**（非协作式），确保长时间执行的计算密集型goroutine不会饿死其他goroutine。

---

## 8.2 示例: 并发的Clock服务

```go
// Clock服务器
func main() {
    listener, _ := net.Listen("tcp", "localhost:8000")
    for {
        conn, _ := listener.Accept()
        go handleConn(conn)  // 每个连接一个goroutine
    }
}

func handleConn(c net.Conn) {
    defer c.Close()
    for {
        _, err := io.WriteString(c, time.Now().Format("15:04:05\n"))
        if err != nil {
            return
        }
        time.Sleep(1 * time.Second)
    }
}
```

### 🔥 面试扩展

**高频题1：`net.Listen`的第二个参数为什么是`"tcp"`？Go支持哪些网络协议？**
> `net`包支持：tcp、tcp4、tcp6、udp、udp4、udp6、ip、unix（Unix域socket）等。

**高频题2：如果多个客户端连接时`net.Listen`的backlog参数？**
> Go的`net.Listen`底层调用了C的`listen(fd, backlog)`，backlog在Go中是硬编码为`syscall.SOMAXCONN`的，由操作系统决定连接等待队列的大小。

---

## 8.3 示例: 并发的Echo服务

```go
func echo(c net.Conn, shout string, delay time.Duration) {
    fmt.Fprintln(c, "\t", strings.ToUpper(shout))
    time.Sleep(delay)
    fmt.Fprintln(c, "\t", shout)
    time.Sleep(delay)
    fmt.Fprintln(c, "\t", strings.ToLower(shout))
}

func handleConn(c net.Conn) {
    input := bufio.NewScanner(c)
    for input.Scan() {
        go echo(c, input.Text(), 1*time.Second)  // 每个输入启动一个goroutine
    }
}
```

---

## 8.4 Channels

### 创建和基本操作

```go
// 无缓冲channel
ch := make(chan int)

// 有缓冲channel
ch := make(chan int, 10)

// 操作
ch <- v   // 发送
v = <-ch  // 接收
close(ch) // 关闭

// 单向channel类型
func f(ch chan<- int) {}  // 只发送
func g(ch <-chan int) {}  // 只接收
```

### 无缓冲channel

```go
// 无缓冲channel：发送和接收必须同时准备好，否则阻塞
ch := make(chan int)
go func() {
    ch <- 42  // 阻塞直到数据被接收
}()
value := <-ch  // 阻塞直到有数据发送
fmt.Println(value)
```

### 有缓冲channel

```go
ch := make(chan int, 3)
ch <- 1  // ✅ 不阻塞
ch <- 2  // ✅ 不阻塞
ch <- 3  // ✅ 不阻塞
// ch <- 4  // ❌ 阻塞！缓冲区满了

fmt.Println(<-ch)  // 1
fmt.Println(<-ch)  // 2
fmt.Println(<-ch)  // 3
// fmt.Println(<-ch)  // ❌ 阻塞！缓冲区空了
```

### 关闭channel

```go
ch := make(chan int, 3)
ch <- 1
ch <- 2
close(ch)

// 接收直到channel关闭
for v := range ch {
    fmt.Println(v)
}

v, ok := <-ch
fmt.Println(v, ok)  // 0, false（channel已关闭）
```

### 🔥 面试扩展

**高频题1：无缓冲channel和有缓冲channel的使用场景？**
> - **无缓冲**：同步通信，发送方和接收方都需要等待对方（goroutine间同步）
> - **有缓冲**：异步通信，解耦发送和接收（工作池、限流）
> 无缓冲channel = `channel`，有缓冲channel = `buffer` + `channel`

**高频题2：向已关闭的channel发数据会发生什么？**
> **panic：** `send on closed channel`。channel关闭后发送立即panic。

**高频题3：从已关闭的channel收数据会发生什么？**
> 返回**零值**（不阻塞），`v, ok := <-ch`中ok为false。

**高频题4：关闭一个已经关闭的channel会怎样？**
> **panic：** `close of closed channel`。关闭channel只能做一次。

**高频题5：`len(ch)`和`cap(ch)`在channel上的行为？**
> - `len(ch)`：缓冲区中当前元素个数（无缓冲时为0）
> - `cap(ch)`：缓冲区容量（无缓冲时返回0）
> 注意：`len(ch)`返回的是瞬时值，不能用于精确判断

**高频题6：channel作为函数参数，如何控制读写权限？**
> 通过**单向类型**实现类型级别控制：
```go
// 只写（发送端）
func producer(out chan<- int) {
    for i := 0; i < 10; i++ {
        out <- i
    }
    close(out)  // 可以关闭只写channel
}

// 只读（接收端）
func consumer(in <-chan int) {
    for v := range in {
        fmt.Println(v)
    }
    // in <- 1  // ❌ 编译错误：不能向只读channel发送
}
```
> 编译器保证单向channel的类型安全，这是Go类型系统的重要特性。

---

## 8.5 并发的循环

```go
func processFiles(files []string) {
    type result struct {
        name string
        size int64
    }

    results := make(chan result)
    var wg sync.WaitGroup

    for _, f := range files {
        wg.Add(1)
        go func(file string) {
            defer wg.Done()
            // 处理文件...
            results <- result{file, size}
        }(f)
    }

    // 等待goroutine完成并关闭result channel
    go func() {
        wg.Wait()
        close(results)
    }()

    // 处理结果
    for r := range results {
        fmt.Printf("%s: %d\n", r.name, r.size)
    }
}
```

### 🔥 面试扩展

**高频题1：`sync.WaitGroup`必须`Add`在`go`之前吗？**
> **是的。** `Add`必须在启动goroutine之前调用，否则goroutine可能在`Wait`之前执行并调用`Done`，导致`Wait`返回过早。也有一种模式是提前知道总数后一次性Add：
```go
wg.Add(len(files))
for _, f := range files {
    go func(file string) {
        defer wg.Done()
        // ...
    }(f)
}
```

**高频题2：在goroutine中使用`recover`保护单个goroutine不崩溃？**
```go
go func() {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("goroutine panicked: %v", r)
        }
    }()
    // 可能panic的代码
}()
```

---

## 8.6 示例: 并发的Web爬虫

```go
func crawl(url string) []string {
    fmt.Println(url)
    list, err := links.Extract(url)
    if err != nil {
        log.Print(err)
    }
    return list
}

func main() {
    worklist := make(chan []string)
    var n int  // 等待队列中的任务数

    // 初始URL
    n++
    go func() { worklist <- os.Args[1:] }()

    seen := make(map[string]bool)
    for ; n > 0; n-- {
        list := <-worklist
        for _, link := range list {
            if !seen[link] {
                seen[link] = true
                n++
                go func(link string) {
                    worklist <- crawl(link)
                }(link)
            }
        }
    }
}

// 限制并发数：使用计数信号量（token bucket）
var tokens = make(chan struct{}, 20)

func crawl(url string) []string {
    tokens <- struct{}{}  // 获取令牌
    list, _ := links.Extract(url)
    <-tokens               // 释放令牌
    return list
}
```

### 🔥 面试扩展

**高频题1：用channel做信号的两种常见模式？**
> 1. **令牌桶（Token Bucket）**：限制并发数
```go
sem := make(chan struct{}, maxConcurrent)
go func() {
    sem <- struct{}{}  // 获取
    defer func() { <-sem }()  // 释放
    // 执行任务
}()
```
> 2. **通知信号（signal）**：goroutine完成通知
```go
done := make(chan struct{})
go func() {
    // 执行任务
    close(done)  // 广播完成
}()
<-done  // 等待完成
```

---

## 8.7 基于select的多路复用

### select基础

```go
select {
case <-ch1:
    // 从ch1收到数据
case v := <-ch2:
    // 从ch2收到数据
case ch3 <- v:
    // 向ch3发送数据
default:
    // 所有channel操作都阻塞时执行
}
```

### select特性

- 同时检查所有case
- 如果多个case都满足，随机选择一个执行
- 没有满足的case时：有default则执行default，否则阻塞

### 超时控制

```go
select {
case v := <-ch:
    fmt.Println(v)
case <-time.After(5 * time.Second):
    fmt.Println("timeout")
}
```

### 🔥 面试扩展

**高频题1：select中多个channel同时ready时，Go如何选择？**
> Go运行时**随机公平选择**其中一个可执行的case。这是有意为之——防止开发者的代码依赖选择顺序，导致某种case被"饿死"。

**高频题2：select中nil channel的行为？**
> 对nil channel的发送和接收**永远阻塞**，所以对应case永远不会被执行。这个特性可以用来在运行时动态禁用某个case：
```go
var ch1, ch2 chan int
select {
case v := <-ch1:  // ch1为nil时永远不会执行
case v := <-ch2:  // ch2为nil时永远不会执行
}
```

**高频题3：select的空操作——`select{}`？**
> `select{}`会永远阻塞（因为没有case，没有default）。常用于main函数中让程序不退出：
```go
func main() {
    // 启动后台goroutine
    go server()
    select{}  // 永久阻塞
}
```

---

## 8.8 示例: 并发的目录遍历

```go
// 统计目录大小
func main() {
    // 根据flag确定根目录
    roots := os.Args[1:]
    if len(roots) == 0 {
        roots = []string{"."}
    }

    // 遍历目录
    fileSizes := make(chan int64)
    var wg sync.WaitGroup
    for _, root := range roots {
        wg.Add(1)
        go walkDir(root, &wg, fileSizes)
    }
    go func() {
        wg.Wait()
        close(fileSizes)
    }()

    var nfiles, nbytes int64
    for size := range fileSizes {
        nfiles++
        nbytes += size
    }
    printDiskUsage(nfiles, nbytes)
}
```

---

## 8.9 并发的退出

```go
var done = make(chan struct{})

// 当用户按下Ctrl+C时关闭done channel
func setupSignalHandler() {
    c := make(chan os.Signal, 1)
    signal.Notify(c, os.Interrupt)
    go func() {
        <-c
        close(done)
    }()
}

// 检查是否应该退出
func cancelled() bool {
    select {
    case <-done:
        return true
    default:
        return false
    }
}
```

### 🔥 面试扩展

**高频题1：close(done)的广播机制原理？**
> 关闭channel时，所有正在或将来要从该channel接收的goroutine都会立即收到零值。这就是**广播（broadcast）**。一次关闭，所有监听者都收到通知，不需要逐一通知。

**高频题2：如何优雅退出多个goroutine？**
> 几种模式：
> 1. **close channel广播**：如上所示，最简单
> 2. **context取消**：`ctx, cancel := context.WithCancel(context.Background())`
> 3. **传递done channel**：手动传递退出信号

**高频题3：Context包如何优雅管理goroutine生命周期？**
```go
func worker(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            // 继续工作
        }
    }
}

ctx, cancel := context.WithCancel(context.Background())
go worker(ctx)
// 当需要停止时：
cancel()
```

---

## 8.10 示例: 聊天服务

```go
type client chan<- string  // 对外发送消息的channel

var (
    entering = make(chan client)
    leaving  = make(chan client)
    messages = make(chan string)  // 所有收到的消息
)

func broadcaster() {
    clients := make(map[client]bool)  // 所有连接
    for {
        select {
        case msg := <-messages:
            for cli := range clients {
                cli <- msg  // 广播给所有客户端
            }
        case cli := <-entering:
            clients[cli] = true
        case cli := <-leaving:
            delete(clients, cli)
            close(cli)
        }
    }
}
```

### 🔥 面试扩展

**高频题1：聊天服务的并发架构是什么模式？**
> **Reactor模式** + **CSP管道**：
> - `broadcaster`是中央goroutine（reactor），所有操作通过它串行化
> - 客户端goroutine只和broadcaster通过channel通信
> - 不存在共享变量，没有锁，完全通过通信实现并发安全

**高频题2：如果客户端数量非常大（10万+），上述架构有什么问题？**
> 1. `broadcaster`单点瓶颈：每个消息要发送给所有客户端，耗时O(N)
> 2. 每个客户端共享channel，可能因为一个慢客户端阻塞所有人
> 3. 改进方案：扇出（fan-out）模式、每个客户端独立goroutine
> 4. 生产环境用Redis Pub/Sub或消息队列

## ⚡ 超级扩展

### ⚡ 8.1 GMP调度器的完整源码分析

#### GMP 三要素详解

```go
// G = Goroutine — 执行栈和执行上下文
// runtime/g.go
type g struct {
    stack       stack       // 当前栈 [lo, hi]
    stackguard0 uintptr     // 栈增长检测
    m           *m          // 当前绑定的M
    sched       gobuf       // 调度上下文（SP, PC, BP等）
    atomicstatus uint32     // 状态
    goid         int64      // goroutine ID
    waitreason   waitReason // 等待原因
    ...
}

// M = Machine — OS线程
type m struct {
    g0      *g     // 调度goroutine（执行调度代码用）
    curg    *g     // 当前运行的用户goroutine
    p       *p     // 关联的P
    tls     [6]uintptr  // 线程本地存储
    ...
}

// P = Processor — 逻辑处理器
type p struct {
    id          int32
    status      uint32      // _Pidle/_Prunning/_Psyscall等
    m           muintptr    // 关联的M（反向指针）
    // 本地goroutine队列
    runqhead    uint32
    runqtail    uint32
    runq        [256]guintptr  // 本地队列（最多256个G）
    // 下一步可运行的goroutine
    runnext     guintptr
    ...
}
```

#### 完整的调度循环

```go
// runtime/proc.go

func schedule() {
    _g_ := getg()
    
    // 每调度61次检查一次全局队列（防止全局队列饿死）
    if _g_.m.p.ptr().schedtick%61 == 0 {
        // 从全局队列获取G
        if gp := globrunqget(_g_.m.p.ptr()); gp != nil {
            execute(gp)
        }
    }
    
    // 1. 从本地队列获取
    if gp := runqget(_g_.m.p.ptr()); gp != nil {
        execute(gp)
    }
    
    // 2. 尝试窃取（work stealing）
    if gp := findRunnable(); gp != nil {
        execute(gp)
    }
    
    // 3. 都找不到，停止M
    stopm()
}
```

#### Work Stealing（工作窃取）算法

```go
func findRunnable() *g {
    // 1. 从全局队列获取
    // 2. 从网络轮询器获取
    // 3. 从其他P的队列偷取（steal）
    //    从其他P的后半段随机取
    //    每个P尝试偷取
    //    (在Go 1.22中，steal的顺序是随机化的)
    // 4. 从GC标记队列获取
    
    // 偷取策略：
    for _, pp := range allp {
        if pp == _g_.m.p.ptr() {
            continue
        }
        // 尝试偷取pp的一半任务
        if gp := runqsteal(_g_.m.p.ptr(), pp, false); gp != nil {
            return gp
        }
    }
    return nil
}
```

#### 系统调用阻塞的处理

```go
// goroutine发起系统调用时：
// 1. M和P解绑（M被操作系统阻塞）
// 2. P寻找新的M来执行本地队列中的G
// 3. 系统调用完成时，M尝试找P接管
// 4. 找不到P时，G放入全局队列，M休眠

// 进入系统调用的状态转换：
// g + m + p (运行中)
//   → 系统调用
//   → p.status = _Psyscall
//   → 其他P发现系统调用时间过长
//   → p.Status = _Pidle（系统调用被劫持）
//   → 系统调用完成时发现P已被回收
//   → m将g放入全局队列，m尝试找新P或睡眠
```

#### goroutine状态机

```
_Gidle       — 新创建
_Grunnable   — 可运行，等待调度
_Grunning    — 正在M上执行
_Gsyscall    — 系统调用中
_Gwaiting    — 等待（channel/mutex/time.Sleep等）
_Gpreempted  — 被抢占
_Gdead       — 死亡/已回收
```

**状态转换：**
```
_Gidle → newproc → _Grunnable → schedule → _Grunning
  → 主动让出(channel/sleep) → _Gwaiting → 唤醒 → _Grunnable
  → 系统调用 → _Gsyscall → 完成 → _Grunnable
  → 被抢占 → _Gpreempted → 重调度 → _Grunnable
  → 执行完毕 → _Gdead → 回收
```

#### 抢占式调度（Go 1.14+）

```go
// 基于信号的抢占式调度
// 1. OS定时器发送SIGURG信号（Go 1.14+）
// 2. 信号处理函数调用 gopreempt_m
// 3. 目标goroutine被标记为可抢占
// 4. 下一次安全检查时，goroutine让出CPU
//
// 解决了以下问题：
// - 纯计算密集型goroutine不主动yield会饿死其他goroutine
// - GC等待goroutine停止的延迟过长
```

---

### ⚡ 8.2 channel的完整底层实现

#### hchan结构体源码

```go
// runtime/chan.go
type hchan struct {
    qcount   uint           // 队列中元素个数
    dataqsiz uint           // 环形队列大小
    buf      unsafe.Pointer // 指向环形缓冲区
    elemsize uint16         // 元素大小
    closed   uint32         // 是否关闭
    elemtype *_type         // 元素类型
    sendx    uint           // 发送索引
    recvx    uint           // 接收索引
    recvq    waitq          // 接收等待队列（sudog链表）
    sendq    waitq          // 发送等待队列
    
    lock mutex  // 保护所有字段的互斥锁
}
```

#### 无缓冲channel的完整流程

```go
ch := make(chan int)

// goroutine A:
ch <- 42
// 1. 加锁
// 2. 检查 recvq 是否有等待的接收者
// 3. 有 → 直接将42拷贝到接收者的栈上
// 4. 唤醒接收者goroutine
// 5. 解锁

// goroutine B:
val := <-ch
// 1. 加锁
// 2. 检查 sendq 是否有等待的发送者
// 3. 有 → 从发送者拷贝数据到接收者栈
// 4. 解锁

// 如果发送时没有接收者等待：
// 1. 获取一个sudog（goroutine的等待结构体）
// 2. 将当前goroutine封装到sudog中
// 3. 将sudog放入sendq
// 4. 调用 gopark() 将当前goroutine挂起
// 5. 当接收者到来时，goready() 唤醒
```

#### 有缓冲channel的完整流程

```go
ch := make(chan int, 3)

// 发送：
ch <- 1
// 1. 加锁
// 2. 检查 recvq 是否有等待者（有→直接传递）
// 3. 检查缓冲区是否还有空间（qcount < dataqsiz）
// 4. 有 → 将值复制到buf[sendx]
// 5. sendx++，qcount++
// 6. 解锁

// 接收：
val := <-ch
// 1. 加锁
// 2. 检查缓冲区是否有数据（qcount > 0）
// 3. 有 → 从buf[recvx]读取
// 4. recvx++，qcount--
// 5. 如果sendq有等待者，将发送者的数据放到缓冲区
// 6. 解锁
```

#### select的底层实现

```go
// select { case <-ch1: ... case ch2 <- v: ... }

// 编译后调用 runtime.selectgo()

func selectgo(cas0 *scase, order0 *uint16, pc0 *uintptr, nsels int) int {
    // 1. 加锁所有channel
    // 2. 随机打乱case顺序（保证公平性）
    // 3. 依次检查每个case是否就绪
    //    - 可立即执行 → 解锁所有channel，执行case
    //    - 没有一个就绪
    //    - 有default → 执行default
    //    - 无default → 注册到所有channel的等待队列，挂起goroutine
    // 4. 被唤醒后，确定是哪个case就绪
    // 5. 从其他channel的等待队列中注销
    // 6. 解锁所有channel
    // 7. 返回就绪的case索引
}
```

---

### ⚡ 8.3 并发模式的完整集合

#### 模式1: Pipeline（流水线）

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用
for n := range sq(sq(gen(2, 3))) {
    fmt.Println(n)  // 16, 81
}
```

#### 模式2: Fan-out / Fan-in

```go
// Fan-out: 多个函数从同一个channel读取
func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// Fan-in: 从多个channel合并到一个
func merge(cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)
    
    output := func(c <-chan int) {
        for n := range c {
            out <- n
        }
        wg.Done()
    }
    
    wg.Add(len(cs))
    for _, c := range cs {
        go output(c)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}

// 使用：并行计算
nums := gen(2, 3, 4, 5)
c1 := sq(nums)
c2 := sq(nums)
out := merge(c1, c2)
for n := range out {
    fmt.Println(n)  // 4, 9, 16, 25 (无序)
}
```

#### 模式3: Worker Pool（工作池）

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("worker %d processing job %d\n", id, j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func main() {
    const numJobs = 10
    const numWorkers = 3
    
    jobs := make(chan int, numJobs)
    results := make(chan int, numJobs)
    
    // 启动worker
    for w := 0; w < numWorkers; w++ {
        go worker(w, jobs, results)
    }
    
    // 发送任务
    for j := 0; j < numJobs; j++ {
        jobs <- j
    }
    close(jobs)
    
    // 收集结果
    for r := 0; r < numJobs; r++ {
        <-results
    }
}
```

#### 模式4: 超时控制

```go
// 带超时的channel操作
func doWithTimeout(d time.Duration) error {
    result := make(chan error, 1)  // 缓冲1防止goroutine泄露
    
    go func() {
        result <- doSomething()
    }()
    
    select {
    case err := <-result:
        return err
    case <-time.After(d):
        return fmt.Errorf("timeout after %v", d)
    }
}
```

#### 模式5: context超时和取消

```go
func slowOperation(ctx context.Context) (string, error) {
    result := make(chan string, 1)
    
    go func() {
        // 模拟慢操作
        time.Sleep(5 * time.Second)
        result <- "done"
    }()
    
    select {
    case r := <-result:
        return r, nil
    case <-ctx.Done():
        return "", ctx.Err()
    }
}

// 使用
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

val, err := slowOperation(ctx)
if err == context.DeadlineExceeded {
    fmt.Println("操作超时")
}
```

#### 模式6: 信号量（Semaphore）模式

```go
// 控制并发数：使用带缓冲channel作为计数信号量
type Semaphore chan struct{}

func NewSemaphore(max int) Semaphore {
    return make(Semaphore, max)
}

func (s Semaphore) Acquire() {
    s <- struct{}{}
}

func (s Semaphore) Release() {
    <-s
}

// 使用
sem := NewSemaphore(3)
for _, task := range tasks {
    sem.Acquire()
    go func(t Task) {
        defer sem.Release()
        process(t)
    }(task)
}
```

---

### ⚡ 8.4 Goroutine泄漏的检测和预防

#### 常见泄漏场景

```go
// 场景1: channel永不关闭
func leak() {
    ch := make(chan int)
    go func() {
        val := <-ch  // 永远阻塞
    }()
    // ch永远不会被关闭或发送数据
}

// 场景2: 发送到无人接收的channel
func leak2() {
    ch := make(chan int)
    go func() {
        ch <- 42  // 永远阻塞（无人接收）
    }()
}

// 场景3: select导致goroutine永久阻塞
func leak3() {
    done := make(chan struct{})
    go func() {
        select {
        case <-done:  // 如果done永远不会被close
        case <-time.After(10 * time.Minute):
        }
    }()
    // 10分钟内done如果不close，goroutine保持10分钟
}
```

#### 泄漏检测

```go
// 使用runtime.NumGoroutine监控
func TestNoLeak(t *testing.T) {
    before := runtime.NumGoroutine()
    
    doSomething()
    
    time.Sleep(100 * time.Millisecond)  // 等待goroutine结束
    after := runtime.NumGoroutine()
    
    if after > before {
        t.Errorf("goroutine leak: %d -> %d", before, after)
    }
}

// 使用pprof
// import _ "net/http/pprof"
// http://localhost:6060/debug/pprof/goroutine
```

---

### ⚡ 8.5 Channel和Goroutine的完整基准测试

```go
// channel发送/接收的性能数据（近似值）
//
// 无缓冲channel:           ~50-100ns/次
// 有缓冲channel（空）:      ~30-80ns/次
// 有缓冲channel（满）:      ~50-100ns/次
// close(channel):           ~60ns
// select一个case:           ~20ns
// select两个case同时就绪:   ~100ns
//
// goroutine创建:            ~200-400ns
// goroutine切换:            ~50-200ns（取决于上下文）
//
// sync.Mutex Lock/Unlock:   ~20-50ns
// atomic.AddInt64:           ~5-10ns
```

---

---

### ⚡ 8.6 大厂面试题全集（并发篇）

**面试题1：goroutine的最小栈大小是多少？为什么这么小？**
```
goroutine初始栈：2KB
    系统线程栈：1MB（大了500倍！）

为什么goroutine的栈可以这么小？
因为Go用了"动态栈"技术：
  不够用了就自动扩容（通过stack copying）
  
就像你用行李箱：
  系统线程 = 带一个大行李箱（1MB），不管用不用都扛着
  goroutine = 带一个小背包（2KB），装不下了再换大包

所以：10万个goroutine ≈ 200MB
      10万个线程    ≈ 100GB（不可能！）
```

**面试题2：有缓冲channel和无缓冲channel有什么不同？**
```go
// 无缓冲 channel：
//  发送方和接收方必须同时准备好
//  就像打乒乓球：你扔过来，我立刻接住
ch := make(chan int)
ch <- 42  // 一直等，直到有人取走

// 有缓冲 channel：
//  发送方扔到缓冲区就走
//  接收方可以从缓冲区拿
//  就像发快递：你放快递柜里，别人有空来拿
ch := make(chan int, 3)
ch <- 1  // ✅ 不阻塞（有空位）
ch <- 2  // ✅ 不阻塞
ch <- 3  // ✅ 不阻塞
// ch <- 4  // ❌ 阻塞（满了，等别人拿）
```

**面试题3：goroutine泄漏怎么发生？怎么避免？**
```go
// goroutine泄漏 = goroutine永远结束不了
// 就像租了房子永远不退房

// 泄漏案例1：channel没人读
func leak() {
    ch := make(chan int)
    go func() {
        <-ch  // 永远没人发数据 → 永远阻塞
    }()
}

// 泄漏案例2：channel没人写
func leak2() {
    ch := make(chan int)
    go func() {
        ch <- 42  // 永远没人取 → 永远阻塞
    }()
}

// ✅ 修复方案：有缓冲channel
func safe() {
    ch := make(chan int, 1)  // 缓冲1个
    ch <- 42  // 即使没人取，也能放进去
    close(ch)
}

// ✅ 修复方案：超时控制
func safe2() {
    ch := make(chan int)
    go func() {
        time.Sleep(10 * time.Second)
        ch <- 42
    }()
    
    select {
    case v := <-ch:
        fmt.Println(v)
    case <-time.After(1 * time.Second):
        fmt.Println("超时了，不等了")
        // goroutine虽然没结束，但不会阻塞主流程
    }
}
```

**面试题4：goroutine和线程的对应关系（GMP模型）**
```
G = Goroutine（你的代码）
M = Machine（系统线程）
P = Processor（处理器，默认=CPU核数）

关系：
  G 运行在 M 上
  M 需要绑定 P 才能运行 G
  P 的数量 = GOMAXPROCS

形象理解：
  G = 工人（做任务）
  M = 工位（需要位置才能干活）
  P = 工厂的许可证（有多少个位置）

场景：
  你有10000个工人（G），但只有4个工位（P=4）
  → 每次4个人干活
  → 有人的时候4个人干，有人睡觉（被block）了就换人
  → 这就是Go的调度！
```

**面试题5：如何限制goroutine并发数？**
```go
// 使用channel做"信号量"（Semaphore）
sem := make(chan struct{}, 10)  // 最多10个并发

for i := 0; i < 100; i++ {
    sem <- struct{}{}  // 获取令牌（满了就阻塞）
    
    go func(id int) {
        defer func() { <-sem }()  // 释放令牌
        
        // 干活...
        fmt.Println(id)
        time.Sleep(time.Second)
    }(i)
}

// 或者用 WaitGroup 等待所有完成
var wg sync.WaitGroup
for i := 0; i < 100; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        fmt.Println(id)
    }(i)
}
wg.Wait()
```

**面试题6：select 的用法和原理**
```go
// select = 多个channel中，哪个有数据就处理哪个
// 就像你在多个外卖窗口前：
//   哪个窗口喊你的号，你就去哪个窗口取餐

ch1 := make(chan string)
ch2 := make(chan string)

go func() {
    time.Sleep(1 * time.Second)
    ch1 <- "从ch1来了"
}()

go func() {
    time.Sleep(2 * time.Second)
    ch2 <- "从ch2来了"
}()

select {
case msg := <-ch1:
    fmt.Println(msg)  // 1秒后执行这个
case msg := <-ch2:
    fmt.Println(msg)
case <-time.After(3 * time.Second):
    fmt.Println("超时了")
default:
    fmt.Println("没有一个channel准备好")  // 非阻塞
}
```

**面试题7：context.Context 是干什么的？**
```go
// Context = 管理goroutine生命周期的工具
// 就像家长给孩子的定时电话：
//   "5分钟后必须回家"（超时）
//   "现在回家！"（取消）

func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():  // 检查是否被取消了
            fmt.Println("被要求停止了")
            return
        default:
            fmt.Println("工作中...")
            time.Sleep(500 * time.Millisecond)
        }
    }
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()
    
    go worker(ctx)
    
    time.Sleep(3 * time.Second)
    fmt.Println("主程序结束")
}
```

**终极并发面试题8：实现一个"发布-订阅"模式**
```go
// Publisher-Subscriber（发布-订阅）
// 就像微信公众号：
//   作者发文章（发布）
//   所有关注者收到（订阅）

type PubSub struct {
    mu     sync.RWMutex
    subs   map[string][]chan string
}

func (ps *PubSub) Subscribe(topic string) <-chan string {
    ch := make(chan string, 1)
    ps.mu.Lock()
    ps.subs[topic] = append(ps.subs[topic], ch)
    ps.mu.Unlock()
    return ch
}

func (ps *PubSub) Publish(topic, msg string) {
    ps.mu.RLock()
    for _, ch := range ps.subs[topic] {
        ch <- msg
    }
    ps.mu.RUnlock()
}

// 使用：
ps := &PubSub{subs: make(map[string][]chan string)}

// 订阅
ch1 := ps.Subscribe("golang")
ch2 := ps.Subscribe("golang")

// 发布
ps.Publish("golang", "Go 1.22发布了！")

fmt.Println(<-ch1)  // Go 1.22发布了！
fmt.Println(<-ch2)  // Go 1.22发布了！
```

---

---

### ⚡ 8.7 context.Context的完整详解

#### 为什么需要Context？（给初中生）

```
假设你在等外卖：
  ❌ 没有Context：你傻等，外卖员不来了你也不知道
  ✅ 有Context：你设了30分钟超时，到了就去干别的事

Context是Go中管理goroutine生命周期的工具：
  1. 取消（Cancel）：告诉goroutine"别干了，回家！"
  2. 超时（Timeout）："给你5秒，干不完就拉倒"
  3. 传递值："这是你的工牌（token），带上干活"
```

#### Context的创建

```go
ctx := context.Background()
// 根Context，一般在main函数或请求入口创建

ctx := context.TODO()
// 和Background一样，但表示"还没想好用什么Context"
```

#### Context的派生

```go
// 1. 手动取消
ctx, cancel := context.WithCancel(context.Background())
defer cancel()  // 记得调用！

if somethingWrong {
    cancel()  // 发送取消信号
}

// 2. 超时取消
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 3. 截止时间取消
ctx, cancel := context.WithDeadline(context.Background(), time.Now().Add(5*time.Second))
defer cancel()

// 4. 附带值
ctx := context.WithValue(context.Background(), "userID", 123)
```

#### 标准用法：在goroutine中检查取消

```go
func doWork(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():  // 检查是否被取消了
            fmt.Println("被取消了，退出")
            return ctx.Err()  // 为什么被取消？
        default:
            // 正常工作
            fmt.Println("工作中...")
            time.Sleep(500 * time.Millisecond)
        }
    }
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()
    
    go doWork(ctx)  // 把Context传给goroutine
    
    time.Sleep(3 * time.Second)
    fmt.Println("主程序结束")
}
// 输出：
// 工作中...
// 工作中...
// 工作中...
// 工作中...
// 被取消了，退出  ← 2秒后准时取消！
// 主程序结束
```

**Context的传递规则：**
```
1. Context必须作为函数的第一个参数（约定）
2. 不要把Context放在结构体里
3. 不要传递nil Context
4. WithValue只用于传递请求范围的数据（userID, traceID）
   不要用它传函数的可选参数
```

---

---

### ⚡ 8.8 再补3道大厂面试题

**面试题9：goroutine和线程的M:N模型是什么？**
```
M:N = M个goroutine在N个OS线程上运行

比如：10000个goroutine（M=10000）在4个线程（N=4）上

Go运行时负责调度：
  哪个goroutine在哪个线程上跑
  什么时候切换goroutine
  
就像10000个员工（goroutine）抢4个工位（线程）
  工位不够了 → 排队
  有人去喝水了（阻塞）→ 下一个人上
```

**面试题10：for range channel 和普通的 for+索引 有什么区别？**
```go
ch := make(chan int, 3)
ch <- 1; ch <- 2; ch <- 3
close(ch)

// for range channel：自动从channel接收，直到channel关闭
for v := range ch {
    fmt.Println(v)  // 1, 2, 3
}

// 等价于：
for {
    v, ok := <-ch
    if !ok { break }  // channel关闭就退出
    fmt.Println(v)
}

// for range channel 的好处：
// 1. 自动处理关闭
// 2. 代码更简洁
// 3. 不会panic（即使channel是nil，也会永远阻塞，而不是panic）
```

**面试题11：context.WithValue 传值的正确用法**
```go
type contextKey string

const userIDKey contextKey = "userID"

// 存值
ctx := context.WithValue(context.Background(), userIDKey, 123)

// 取值
if uid, ok := ctx.Value(userIDKey).(int); ok {
    fmt.Println("用户ID:", uid)
}

// 为什么key要用自定义类型而不是字符串？
// 防止不同包之间key冲突！
// 如果用字符串，两个不同包都可能用"userID"这个key
```

---

### ⚡ 8.9 Goroutine泄漏检测（Go 1.26+）

#### 什么是goroutine泄漏？

```
goroutine泄漏 = goroutine永远结束不了，一直占着内存

就像你借书不还：
  goroutine借了2KB栈空间，用完了不还
  越来越多的goroutine占着内存
  最终内存耗尽，程序崩溃
```

#### 用runtime.NumGoroutine检测泄漏

```go
func main() {
    // 启动前
    before := runtime.NumGoroutine()
    
    // 做一些可能泄漏的事
    go func() {
        time.Sleep(10 * time.Minute)
    }()
    
    time.Sleep(time.Second)
    
    // 启动后
    after := runtime.NumGoroutine()
    
    if after > before {
        fmt.Printf("⚠️ 可能有泄漏：%d → %d\n", before, after)
    }
}
```

#### context.AfterFunc 和 context.Cause（Go 1.21+）

```go
// context.AfterFunc：当context取消时，自动执行一个函数
// 像"手机欠费自动停机"

ctx, cancel := context.WithCancel(context.Background())

// 注册"如果ctx取消，就打印"
stop := context.AfterFunc(ctx, func() {
    fmt.Println("ctx被取消了，清理资源！")
})

// 取消ctx时，AfterFunc自动执行
cancel()
// 输出：ctx被取消了，清理资源！
```

```go
// context.Cause：知道context为什么被取消
// 像知道"为什么手机停机了"——欠费？还是主动关的？

ctx, cancel := context.WithCancelCause(context.Background())

cancel(errors.New("超时了"))  // 取消时带上原因

fmt.Println(context.Cause(ctx))  // "超时了"
```

#### range-over-function迭代器（Go 1.23）

```go
import "iter"

// Go 1.23：for range 支持函数迭代器！

// 写一个迭代器：遍历目录下的所有文件
func Files(dir string) iter.Seq[string] {
    return func(yield func(string) bool) {
        entries, _ := os.ReadDir(dir)
        for _, e := range entries {
            if !yield(e.Name()) {  // yield返回false=要停止
                return
            }
        }
    }
}

// 使用
for name := range Files(".") {
    fmt.Println(name)
}
```

---

### ⚡ 8.10 goroutine泄漏检测（用pprof）

#### 什么是goroutineleak？

```
goroutineleak = goroutine泄漏
  你启动了一个goroutine，但它永远不会结束
  它占用的内存永远不会被释放
  越来越多的泄漏 → 内存耗尽 → 程序崩溃

就像你打开水龙头不关：
  水一直流（goroutine一直在运行）
  水费越来越高（内存越用越多）
  最终水漫金山（程序崩溃）
```

#### 检测goroutine泄漏的4种方法

```go
// 方法1：runtime.NumGoroutine 看数量变化
func main() {
    before := runtime.NumGoroutine()
    
    // 启动一些goroutine
    for i := 0; i < 1000; i++ {
        go func() {
            time.Sleep(time.Minute)  // 模拟工作
        }()
    }
    
    after := runtime.NumGoroutine()
    fmt.Printf("goroutine: %d → %d\n", before, after)
    
    // 如果after一直不回落到before，就有泄漏
}

// 方法2：pprof查看goroutine堆栈
// 在代码中引入：
import _ "net/http/pprof"

// 然后浏览器访问：
// http://localhost:6060/debug/pprof/goroutine
// 可以看到所有goroutine的堆栈
// 如果看到很多goroutine都在同一行代码等待 → 泄漏了

// 方法3：Go 1.26实验性goroutineleak profile
// GOEXPERIMENT=goroutineleakprofile
// 专门检测哪些goroutine泄漏了

// 方法4：测试中检测
func TestNoGoroutineLeak(t *testing.T) {
    before := runtime.NumGoroutine()
    
    // 执行可能泄漏的代码
    myFunction()
    
    // 等待goroutine结束
    time.Sleep(100 * time.Millisecond)
    
    after := runtime.NumGoroutine()
    if after > before {
        t.Errorf("goroutine泄漏！%d → %d", before, after)
    }
}
```

**常见的泄漏场景和修复：**

```go
// 场景1：channel没人读（发送者阻塞）
func leak1() {
    ch := make(chan int)
    go func() {
        ch <- 42  // 永远没人读 → 永远阻塞
    }()
    // 没把ch的值取走
}

// 修复：有缓冲channel
func fix1() {
    ch := make(chan int, 1)  // 缓冲1个
    go func() {
        ch <- 42  // 即使没人读也能放进去
    }()
}

// 场景2：for-select没退出条件
func leak2() {
    go func() {
        for {  // 没有退出条件
            select {
            case <-time.After(time.Second):
                fmt.Println("工作中...")
            }
        }
    }()
}

// 修复：用context控制退出
func fix2(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():  // 可以退出了
                return
            case <-time.After(time.Second):
                fmt.Println("工作中...")
            }
        }
    }()
}
```

---

> **下一章**：[第9章 基于共享变量的并发](./ch09-shared-vars-concurrency.md) —— 竞争条件、Mutex、RWMutex、内存同步、sync.Once和竞争检测。
