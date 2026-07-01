# 第5章 函数

> Go函数是一等公民（first-class citizen），可以作为值传递、闭包捕获变量、defer确保清理、panic/recover作为异常机制。理解函数的设计哲学是掌握Go的关键。

---

## 目录

- [5.1 函数声明](#51-函数声明)
- [5.2 递归](#52-递归)
- [5.3 多返回值](#53-多返回值)
- [5.4 错误](#54-错误)
- [5.5 函数值](#55-函数值)
- [5.6 匿名函数](#56-匿名函数)
- [5.7 可变参数](#57-可变参数)
- [5.8 Deferred函数](#58-deferred函数)
- [5.9 Panic异常](#59-panic异常)
- [5.10 Recover捕获异常](#510-recover捕获异常)

---

## 5.1 函数声明

### 语法

```go
func name(parameter-list) (result-list) {
    body
}

// 示例
func add(x int, y int) int {
    return x + y
}

// 类型相同的参数可合并
func add(x, y int) int { return x + y }

// 多返回值
func div(x, y int) (int, error) {
    if y == 0 {
        return 0, errors.New("division by zero")
    }
    return x / y, nil
}

// 命名返回值
func f(x, y int) (sum int, err error) {
    sum = x + y  // 可直接使用
    return       // 裸返回（naked return）
}
```

### 函数签名

Go的函数由**参数类型**和**返回值类型**唯一标识（函数名不参与签名），可作为map的key吗？**不能**（函数类型不可比较，除非是nil）。

```go
func(x int) bool  // 函数类型
```

### 🔥 面试扩展

**高频题1：值传递和引用传递？**
> Go所有都是**值传递**。slice/map/channel/function/interface/指针传递的是header的副本，但这些header内部有指向底层数据的指针，所以函数内修改可能影响外部。没有真正的引用传递。

**高频题2：命名返回值的裸返回（naked return）是好实践吗？**
> 在短函数中可以（提升可读性），但长函数中不好（容易忘记哪些返回值已赋值）。很多Go风格指南推荐短函数才用。

**高频题3：函数类型赋值需要满足什么条件？**
> 参数和返回值类型完全一致（函数名无关）。包括参数名称无关：
```go
func f1(x int) int { return x }
func f2(y int) int { return y }
var fn func(int) int = f1
fn = f2  // ✅ 签名一致
```

---

## 5.2 递归

### 标准示例

```go
// HTML解析：递归遍历DOM树
func outline(stack []string, n *html.Node) {
    if n.Type == html.ElementNode {
        stack = append(stack, n.Data)
        fmt.Println(stack)
    }
    for c := n.FirstChild; c != nil; c = c.NextSibling {
        outline(stack, c)
    }
}

// 递归遍历目录
func walkDir(dir string) {
    files, _ := os.ReadDir(dir)
    for _, file := range files {
        if file.IsDir() {
            walkDir(filepath.Join(dir, file.Name()))
        } else {
            fmt.Println(file.Name())
        }
    }
}
```

### 🔥 面试扩展

**高频题1：Go中递归调用的栈安全吗？goroutine栈的自动增长如何处理递归？**
> goroutine初始栈很小（~2KB），但Go运行时使用**动态栈**技术——栈空间不够时自动扩容（通过`stack copying`将整个栈复制到更大的连续内存空间）。但无限递归最终会耗尽内存（`runtime: goroutine stack exceeds 1000000000-byte limit`），和C语言的固定栈溢出不同。

**高频题2：递归和迭代如何选择？**
> - 递归：代码更简洁（树遍历、图遍历），但可能有额外函数调用开销
> - 迭代：性能更好（避免栈操作），但代码复杂度可能增加
> - Go编译器不进行尾调用优化（TCO），深递归需谨慎

---

## 5.3 多返回值

### 基本用法

```go
func findLinks(url string) ([]string, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    doc, err := html.Parse(resp.Body)
    if err != nil {
        return nil, err
    }
    return visit(nil, doc), nil
}
```

### 🔥 面试扩展

**高频题1：多返回值和命名返回值的性能差异？**
> 编译后无差异。命名返回值只是在源码层面声明了返回值变量名，编译器自动生成return语句。功能和性能上没有区别，只是可读性差异。

**高频题2：Go为什么不像Java那样用异常，而用多返回值传error？**
> 这是Go的设计哲学：**错误是值（errors are values）**。错误应由调用者显式处理而不是抛到上层。这种设计：
> 1. 让错误处理路径清晰可见
> 2. 避免try-catch控制流的混入
> 3. 错误在性能路径上零开销（不抛出异常时）

---

## 5.4 错误

### 错误处理策略

```go
// 策略1：传播错误（最常用）
if err != nil {
    return fmt.Errorf("read config: %w", err)
}

// 策略2：重试
for attempts := 0; attempts < 3; attempts++ {
    if err := doSomething(); err == nil {
        break
    }
    time.Sleep(time.Second)
}

// 策略3：输出日志后继续
if err != nil {
    log.Printf("skipping %s: %v", name, err)
    continue
}

// 策略4：程序退出
if err != nil {
    log.Fatal(err)  // 记录日志并os.Exit(1)
}

// 策略5：忽略（谨慎使用）
_ = doSomething()
```

### 自定义错误

```go
// 方式1：errors.New
err := errors.New("something went wrong")

// 方式2：fmt.Errorf
err := fmt.Errorf("user %d not found", id)

// 方式3：自定义错误类型
type ValidationError struct {
    Field string
    Value interface{}
    Msg   string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed: %s = %v (%s)", e.Field, e.Value, e.Msg)
}
```

### 错误包装（Go 1.13+）

```go
// 包装错误（加上下文）
if err != nil {
    return fmt.Errorf("open file %s: %w", filename, err)
}

// 解包检查
if errors.Is(err, os.ErrNotExist) { ... }

// 类型断言检查
var valErr *ValidationError
if errors.As(err, &valErr) { fmt.Println(valErr.Field) }
```

### 🔥 面试扩展

**高频题1：`%w`（Wrap）和`%v`的区别？**
> - `%w`：**包装**错误，可通过`errors.Is`/`errors.As`解包
> - `%v`：**格式化**错误信息，不保留原始错误，不能解包
> - 一个链上只能用一次`%w`（多次`%w`只有一个能解包）

**高频题2：`errors.Is`和`errors.As`的区别？**
> - `errors.Is(err, target)`：判断错误链上**是否有等于target的错误**（基于`==`）
> - `errors.As(err, &target)`：判断错误链上**是否有类型匹配的错误**（赋值给target）

**高频题3：什么时候不应该用`%w`？**
> 1. 不希望调用者依赖特定错误类型（封装抽象）
> 2. 添加多层上下文时（只包装最重要的下层错误）
> 3. 外部API层：避免暴露内部实现细节

**高频题4：Go 1.20+的新错误处理特性？**
> - `errors.Join(err1, err2)`：合并多个错误
> - 多个`%w`支持（Go 1.20+）：`fmt.Errorf("context: %w, %w", err1, err2)`在`errors.Is`/`errors.As`中会检查每个包装

---

## 5.5 函数值

### 函数是一等公民

```go
// 函数作为变量
var f func(int) int
f = func(x int) int { return x * 2 }

// 函数作为参数
func mapStr(arr []string, f func(string) string) []string {
    result := make([]string, len(arr))
    for i, s := range arr {
        result[i] = f(s)
    }
    return result
}

// 函数作为返回值
func getAdder() func(int) int {
    sum := 0
    return func(x int) int {
        sum += x
        return sum
    }
}
```

### 🔥 面试扩展

**高频题1：函数值的底层实现？**
> 函数值本质上是一个**指向函数代码的指针**（类似C的函数指针）。闭包则包含函数代码指针 + 捕获的变量。

**高频题2：函数值的零值是什么？**
> `nil`。调用nil函数值会导致panic。

---

## 5.6 匿名函数

### 闭包

```go
// 闭包：捕获外部变量
func squares() func() int {
    var x int
    return func() int {
        x++
        return x * x
    }
}

func main() {
    f := squares()
    fmt.Println(f())  // 1
    fmt.Println(f())  // 4
    fmt.Println(f())  // 9
}
```

### 循环变量陷阱（经典面试题）

```go
var fns []func()
for i := 0; i < 5; i++ {
    fns = append(fns, func() { fmt.Println(i) })
}
for _, f := range fns {
    f()  // 输出？ 5 5 5 5 5 （不是0 1 2 3 4！）
}

// 修复1：传参
for i := 0; i < 5; i++ {
    fns = append(fns, func(n int) { fmt.Println(n) }(i))
}

// 修复2：局部副本
for i := 0; i < 5; i++ {
    i := i  // 创建副本
    fns = append(fns, func() { fmt.Println(i) })
}
```

### 🔥 面试扩展

**高频题1：闭包捕获的是变量还是值？**
> 闭包捕获的是**变量引用**（指针），不是值快照。所有闭包共享同一个变量，当变量值改变时，闭包看到的是最新值。这是循环变量陷阱的根本原因。

**高频题2：Go的闭包在内存泄漏上有什么风险？**
> 闭包导致被捕获的变量逃逸到堆上。如果闭包被长期持有（如回调注册），大变量即使闭包只用了一小部分，整个变量也无法释放。这就是**闭包内存泄漏**。

**高频题3：Go 1.22修复了这个循环变量陷阱吗？**
> Go 1.22在`for range`循环中修复了——每次迭代创建新的循环变量。但传统的`for i := 0; i < n; i++`形式不变。

---

## 5.7 可变参数

```go
// 声明
func sum(vals ...int) int {
    total := 0
    for _, v := range vals {
        total += v
    }
    return total
}

// 调用
sum(1, 2, 3)       // 6
sum()              // 0（空切片）

// 展开切片
values := []int{1, 2, 3}
sum(values...)     // 展开为1, 2, 3
```

### 🔥 面试扩展

**高频题1：可变参数的本质是什么？**
> `...T`本质上是在函数内部创建一个`[]T`切片。调用时如果没有参数，传入nil切片。展开切片时传递的是**底层数组指针**不是副本，但函数内修改切片元素会影响原切片。

**高频题2：`interface{}`作为可变参数的特殊性？**
```go
func Printf(format string, args ...interface{})
```
> 这是使用最广的可变参数。任何类型的值都可传入（因为所有类型都实现了`interface{}`），但编译器会为每个参数创建`interface{}`值，涉及装箱（boxing）开销。

---

## 5.8 Deferred函数

### defer的用途

```go
// 1. 资源清理
f, err := os.Open(filename)
if err != nil {
    return err
}
defer f.Close()

// 2. 解锁
mu.Lock()
defer mu.Unlock()

// 3. 打印跟踪
func trace(funcName string) func() {
    start := time.Now()
    log.Printf("enter: %s", funcName)
    return func() { log.Printf("exit: %s (%s)", funcName, time.Since(start)) }
}
defer trace("main")()

// 4. 恢复panic
defer func() {
    if r := recover(); r != nil {
        log.Printf("panic: %v", r)
    }
}()
```

### defer的执行顺序

```go
func main() {
    defer fmt.Println(1)
    defer fmt.Println(2)
    defer fmt.Println(3)
}
// 输出: 3 2 1（LIFO：后进先出）
```

### defer和返回值

```go
// defer修改命名返回值
func f() (result int) {
    defer func() {
        result++  // 在return之后执行，但可以修改返回值
    }()
    return 0  // 实际返回1！
}
```

执行逻辑：
1. result设置为0
2. 执行defer（result变为1）
3. 返回result的值（1）

### 🔥 面试扩展

**高频题1：defer的执行时机（return语句的执行顺序）？**
```
1. 设置返回值（对命名返回值赋值或将值拷贝到匿名返回值）
2. 执行defer（LIFO顺序）
3. 真正的RET指令返回
```
所以defer可以修改命名返回值，但不能修改匿名返回值。

**高频题2：性能考量——defer有开销吗？**
> Go 1.13之前defer有显著开销（堆分配defer结构体），Go 1.14优化为**栈分配**大部分defer。Go 1.17+进一步优化为**内联defer**（在函数末尾直接执行defer代码）。现在defer的开销已经非常小，不必为性能避免使用。

**高频题3：defer中能否修改循环变量？**
```go
for i := 0; i < 3; i++ {
    defer fmt.Println(i)  // 输出？ 2 1 0（LIFO顺序）
}
```
> 因为defer的参数在声明时求值（`i`作为参数传入），所以defer记录的是当前i的值。

**高频题4：循环中defer会导致什么问题？**
```go
for _, file := range files {
    f, err := os.Open(file)
    defer f.Close()  // ❌ 所有f.Close()在函数返回时才执行
}
```
> 所有文件句柄在整个函数执行期间保持打开，直到函数返回才一次性关闭。可能导致文件句柄耗尽。
> **修复**：将循环体提取为单独函数，或直接`f.Close()`不用defer。

---

## 5.9 Panic异常

### 触发panic

```go
// 运行时panic（越界、空指针等）
var s []int
_ = s[0]  // panic: index out of range

// 显式panic
func assert(cond bool, msg string) {
    if !cond {
        panic(msg)
    }
}
```

### 🔥 面试扩展

**高频题1：panic发生后程序的执行流程？**
> 1. 当前函数停止正常执行，开始执行defer
> 2. 当前函数的defer执行完后，panic向调用栈上层传播
> 3. 每层都执行defer后继续向上传播
> 4. 直到main函数或者被recover捕获
> 5. 未被recover → 程序崩溃，打印stack trace

**高频题2：哪些情况会导致panic（常见运行时panic）？**
> - 索引/切片越界（`index out of range`）
> - 空指针解引用（`nil pointer dereference`）
> - 向nil map赋值（`assignment to entry in nil map`）
> - 类型断言失败（未使用ok模式）
> - 向已关闭的channel发送数据
> - 关闭已关闭的channel
> - 并发读写map
> - 栈溢出（无限递归）

**高频题3：Go为什么不推荐使用panic作为常规错误处理？**
> panic是**不可控的**，会展开调用栈执行所有defer，开销大。更重要的是，调用方无法通过错误返回链处理panic（除非recover）。Go的哲学是：**库代码绝不应该panic**（除非极端情况），用error返回可预测的错误。

---

## 5.10 Recover捕获异常

### 基本用法

```go
func safeDiv(x, y int) (result int, err error) {
    defer func() {
        if p := recover(); p != nil {
            err = fmt.Errorf("panic: %v", p)
        }
    }()
    return x / y, nil
}
```

### 最佳实践

```go
// 只恢复自己产生的panic，不恢复其他人的
func recoverPanic() {
    if r := recover(); r != nil {
        // 记录日志、转换为error返回
        log.Printf("recovered from panic: %v", r)
    }
}
```

### 🔥 面试扩展

**高频题1：`recover()`只有在defer中才有用，为什么？**
> 如果不在defer中调用，panic发生后执行的`recover()`永远在正常函数返回后执行（panic往上传播时只执行defer），所以`recover()`只有在defer上下文中才有意义。

**高频题2：recover后程序的状态？**
> recover后程序从defer函数返回继续执行（不是从panic发生处继续）。panic未发生时，recover返回nil，不应做任何处理。

**高频题3：`net/http`服务器如何处理handler中的panic？**
> Go的每个HTTP请求在独立goroutine中处理。`net/http`服务器为每个连接设定了recover，某个handler的panic不会导致整个服务器崩溃，只会导致当前请求返回500。

**面试实战题：下面代码的输出是什么？**
```go
func main() {
    defer func() {
        fmt.Println(recover())
    }()
    defer func() {
        fmt.Println(recover())
    }()
    panic("oops")
}
```
> 输出：`oops`（第一个defer recover了，第二个defer recover返回nil）。defer LIFO顺序，后注册的defer（第一个recover）先执行，recover到了panic。第二个defer执行时已经没有panic了，返回nil，输出`<nil>`。输出顺序：先"oops"，后"<nil>"。

## ⚡ 超级扩展

### ⚡ 5.1 函数调用栈完整解析

#### Go函数调用的底层汇编

```go
// 简单函数
func add(a, b int) int {
    return a + b
}

// 编译后的AMD64汇编 (go tool compile -S main.go)
// ""·add STEXT size=45 args=0x18 locals=0x0
// 0x0000 00000 (main.go:3)  TEXT    "".add(SB), ABIInternal, $0-24
// 0x0000 00000 (main.go:3)  MOVQ    a+0(FP), AX    // 第一个参数a
// 0x0005 00005 (main.go:3)  MOVQ    b+8(FP), CX    // 第二个参数b
// 0x000a 00010 (main.go:3)  ADDQ    CX, AX         // a + b
// 0x000d 00013 (main.go:3)  MOVQ    AX, ""~r2+16(FP)  // 返回值
// 0x0012 00018 (main.go:3)  RET                     // 返回
```

**栈帧布局：**
```
高地址 ←
 [返回值]   ← FP + 16 (24-8)
 [arg b]    ← FP + 8  (16-8)
 [arg a]    ← FP + 0  (8-0)
 [返回地址] ← SP当前
 [局部变量] 
低地址 →
```

#### 函数参数全部通过栈传递

```go
func f(a, b, c, d, e, f int) int {
    return a + b + c + d + e + f
}

// Go将所有参数放在栈上（不像C语言用寄存器传参）
// 这简化了goroutine栈的操作，但付出了一些性能代价
```

#### 闭包捕获变量的内存模型

```go
func incrementer() func() int {
    x := 0  // 逃逸到堆上
    return func() int {
        x++
        return x
    }
}

// 闭包在底层是一个结构体：
// type Closure struct {
//     F uintptr   // 函数代码指针
//     X *int      // 捕获的变量指针
// }
```

---

### ⚡ 5.2 defer 的完整生命周期

#### defer在Go不同版本的演进

| 版本 | defer实现 | 性能 |
|------|-----------|------|
| Go 1.0-1.13 | 堆分配defer结构体 | 慢 (~200ns) |
| Go 1.14 | 栈分配defer（大部分情况） | 快 (~30ns) |
| Go 1.17+ | 内联defer（open coded defer） | 极快 (~2ns) |

**Go 1.17+ 内联defer的实现：**

```go
func example() {
    defer fmt.Println(1)
    fmt.Println(2)
}

// Go 1.17+编译后等价于：
func example() {
    deferBits := 0  // 用于跟踪哪些defer需要执行
    deferBits |= 1 << 0  // 标记第一个defer
    
    fmt.Println(2)
    
    // 函数返回前：
    if deferBits & (1 << 0) != 0 {
        deferBits &^= 1 << 0
        fmt.Println(1)
    }
}
```

**内联defer的限制：**
- 如果defer在循环中 → 使用标准defer
- 如果defer数量超过8个 → 使用标准defer
- 如果defer在显式的条件分支中嵌套很深 → 使用标准defer

#### defer参数求值时机

```go
func main() {
    x := 1
    defer fmt.Println(x)  // 此时x=1被记录
    x = 2
}
// 输出: 1 （defer记录的是声明时的值，不是执行时的值）

// 闭包方式捕获的是变量引用
func main() {
    x := 1
    defer func() {
        fmt.Println(x)  // 闭包捕获x的地址
    }()
    x = 2
}
// 输出: 2 （闭包看到的是最终值）
```

#### defer和return的执行顺序完整演示

```go
func f1() (r int) {
    r = 0
    defer func() {
        r++  // 修改命名返回值
    }()
    return 1  // r被设为1，然后defer执行r++，最终返回2
}
// 返回值: 2

func f2() int {
    var r int
    defer func() {
        r++  // 匿名返回值，修改的是局部变量r，不影响返回值
    }()
    r = 1
    return r  // r=1被复制到返回值，然后defer执行r++
}
// 返回值: 1 (不是2!)

func f3() (r int) {
    defer func(r int) {
        r++  // 值传递，修改的是副本
    }(r)  // r=0被传入
    return 1  // r被设为1，defer执行r副本++，不影响返回值
}
// 返回值: 1
```

#### defer与panic/recover的交互

```go
func main() {
    defer func() {
        fmt.Println(recover())  // 捕获panic
    }()
    
    defer func() {
        fmt.Println("before panic")
    }()
    
    panic("oops")
    
    // 这里永远不会执行
    defer func() {
        fmt.Println("after panic")  // 不会执行
    }()
}
// 输出:
// before panic
// oops
```

**完整执行流程：**
```
1. 注册两个defer
2. 执行 panic("oops")
3. 停止正常执行
4. 执行栈中所有注册的defer（LIFO）
5. 第二个defer输出 "before panic"
6. 第一个defer执行recover()，返回"oops"
7. recover()后panic被抑制
8. 函数正常返回
```

#### 循环中defer的文件句柄泄露

```go
// ❌ 危险：所有文件直到函数返回才关闭
func processFiles(files []string) error {
    for _, file := range files {
        f, err := os.Open(file)
        if err != nil {
            return err
        }
        defer f.Close()  // 文件句柄堆积！
        // 处理文件...
    }
    return nil
}

// ✅ 修复：包裹在defer中或直接关闭
func processFiles(files []string) error {
    for _, file := range files {
        if err := func() error {
            f, err := os.Open(file)
            if err != nil {
                return err
            }
            defer f.Close()  // 在匿名函数返回时关闭
            // 处理文件...
            return nil
        }(); err != nil {
            return err
        }
    }
    return nil
}
```

---

### ⚡ 5.3 闭包循环变量陷阱的完整分析

#### 经典问题的所有层面

```go
// 问题：所有goroutine共享同一个i
func main() {
    for i := 0; i < 5; i++ {
        go func() {
            fmt.Print(i)  // 可能输出 "01234" 但通常输出 "55555" 或类似
        }()
    }
    time.Sleep(time.Second)
}

// 原因：goroutine调度延迟，当它们实际执行时，i已经递增到5
```

**四种修复方案：**

```go
// 方案1: 传参（推荐）
for i := 0; i < 5; i++ {
    go func(n int) {
        fmt.Print(n)
    }(i)
}

// 方案2: 创建局部副本（经典）
for i := 0; i < 5; i++ {
    i := i  // 每次迭代创建新变量
    go func() {
        fmt.Print(i)
    }()
}

// 方案3: 在局部作用域中声明新变量
for i := 0; i < 5; i++ {
    {
        n := i
        go func() {
            fmt.Print(n)
        }()
    }
}

// 方案4: Go 1.22+ 自动修复
// for i := 0; i < 5; i++ {  ← Go 1.22每次迭代创建新i
//     go func() {
//         fmt.Print(i)
//     }()
// }
```

---

### ⚡ 5.4 错误处理的完整最佳实践

#### 错误包装的完整链

```go
// Go 1.13错误链
func loadConfig(path string) (*Config, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, fmt.Errorf("open config: %w", err)  // 包装
    }
    defer f.Close()
    
    var cfg Config
    if err := json.NewDecoder(f).Decode(&cfg); err != nil {
        return nil, fmt.Errorf("parse config %s: %w", path, err)
    }
    return &cfg, nil
}

// 错误链的结构
// loadConfig → "parse config /etc/app.json: unexpected end of JSON input"
// errors.Is(err, io.ErrUnexpectedEOF)  → true

// 自定义错误类型的errors.As
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println("Path:", pathErr.Path)  // 获取路径信息
}
```

#### 静默错误和nil检查

```go
// ⚠️ 不要忽略错误
resp, _ := http.Get(url)  // 忽略错误！
// 如果Get失败，resp为nil，resp.Body会panic

// ✅ 正确处理
resp, err := http.Get(url)
if err != nil {
    return fmt.Errorf("fetch failed: %w", err)
}
defer resp.Body.Close()

if resp.StatusCode != http.StatusOK {
    return fmt.Errorf("unexpected status: %s", resp.Status)
}
```

#### Go 1.20 errors.Join 的使用

```go
// 合并多个错误
func validate(v interface{}) error {
    var errs []error
    if v == nil {
        errs = append(errs, errors.New("is nil"))
    }
    if s, ok := v.(string); ok && s == "" {
        errs = append(errs, errors.New("is empty"))
    }
    return errors.Join(errs...)  // 如果没有错误，返回nil
}
```

---

### ⚡ 5.5 panic/recover的生产级使用模式

#### 生产级recover

```go
// 在net/http服务器中的使用
func recoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                // 获取堆栈
                stack := debug.Stack()
                
                // 记录错误（包括堆栈）
                log.Printf(
                    "panic recovered: %v\n%s",
                    err, stack,
                )
                
                // 返回500
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

#### goroutine中的panic隔离

```go
// goroutine中的panic如果不处理，会导致整个进程崩溃
func main() {
    go func() {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("goroutine panicked: %v", r)
            }
        }()
        // 可能panic的代码
        panic("something went wrong")
    }()
    
    time.Sleep(time.Second)
    fmt.Println("main continues")  // ✅ 正常运行
}
```

---

### ⚡ 5.6 函数的完整性能分析

#### 函数调用的性能开销

```go
// 基准测试：直接调用 vs 函数值调用 vs 反射调用

// 直接调用:            ~2ns
// 函数值（变量）:       ~2ns
// 接口方法:             ~4ns
// 通过闭包:             ~3ns (闭包结构体间接引用)
// reflect.Call:         ~500ns (动态分配、类型检查、参数打包)
// reflect.Method.Call:  ~300ns
```

#### 内联优化的条件

```go
// 小函数会被内联（inline）
// 条件：函数体小、不包含复杂语句

// 会被内联:
func min(a, b int) int {
    if a < b { return a }
    return b
}

// 不会被内联:
func heavy() {
    for i := 0; i < 1000; i++ {
        doSomething()
    }
}

// 查看内联: go build -gcflags='-m' main.go
// ./main.go:3:6: can inline min
// ./main.go:10:6: cannot inline heavy: function too complex
```

---

---

### ⚡ 5.7 大厂面试题全集（函数篇）

**面试题1：defer函数的执行顺序是什么？**
```go
func main() {
    defer fmt.Println(1)
    defer fmt.Println(2)
    defer fmt.Println(3)
    fmt.Println("start")
}
// 输出：
// start
// 3
// 2
// 1

// 原因：defer是"后进先出（LIFO）"
// 就像叠盘子：
//   先放1号，再放2号，再放3号
//   拿的时候：先拿3号，再拿2号，再拿1号
```

**面试题2：defer + return 的执行顺序**
```go
func f() (r int) {
    defer func() {
        r++  // 修改返回值
    }()
    return 0  // r先被设为0，然后defer++，返回1
}

// 实际上分为三步：
// 1. r = 0（设置返回值）
// 2. r++（执行defer）
// 3. return r（返回1）
```

**面试题3：匿名函数（闭包）捕获的是值还是引用？**
```go
func main() {
    x := 10
    
    f1 := func() { fmt.Println(x) }
    
    x = 20
    f1()  // 输出：20（捕获的是引用，不是值）
}

// 如果想捕获当前值：
func main() {
    x := 10
    
    f1 := func(v int) { fmt.Println(v) }
    f1(x)  // 传参：把x的值拷贝进去
    
    x = 20
    // f1还是10，因为10已经被拷贝了
}
```

**面试题4：什么是"循环变量陷阱"？**
```go
// 经典问题：
func main() {
    var fns []func()
    
    for i := 0; i < 3; i++ {
        fns = append(fns, func() { fmt.Print(i) })
    }
    
    for _, fn := range fns {
        fn()
    }
}
// 输出（Go 1.21之前）：3 3 3（不是0 1 2！）
// 原因：所有闭包捕获的是同一个i，i最后的值是3

// Go 1.22 修复了这个问题
// （for range 每次迭代创建新变量）
```

**面试题5：Panic和Recover的用法**
```go
// panic = 程序出大问题了（比如数组越界）
// recover = 抢救程序

func safeDiv(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    
    if b == 0 {
        panic("除数不能为0")
    }
    return a / b, nil
}

// 使用：
result, err := safeDiv(10, 0)
if err != nil {
    fmt.Println(err)  // panic: 除数不能为0
}
```

**面试题6：Go的错误处理为什么比Java的异常好？**
```
Go的哲学："错误就是值（errors are values）"

Go的方式——显式：
  函数返回error，你看到了就必须处理
  就像快递员送到你面前，你得签字

Java的方式——隐式：
  try-catch-finally
  异常可能被忽略，你不知道哪里会抛出异常
  就像快递员把快递扔你门口，你可能没看到
```

**面试题7：函数的参数是值传递还是引用传递？**
```go
// Go全部是值传递！没有引用传递！

func changeVal(x int) {
    x = 100  // 修改的是副本
}

func changePtr(p *int) {
    *p = 100  // 通过指针修改原值
}

func main() {
    a := 10
    changeVal(a)
    fmt.Println(a)  // 10（没变！）
    
    changePtr(&a)
    fmt.Println(a)  // 100（变了）
    
    // 注意：slice、map、channel也是值传递！
    // 但它们内部有指针，所以能修改底层数据
}
```

**面试题8：什么是"裸返回"（Naked Return）？好坏？**
```go
// 裸返回：函数有命名返回值，return时不写变量名
func div(a, b int) (result int, err error) {
    if b == 0 {
        err = errors.New("÷0")
        return  // 裸返回
    }
    result = a / b
    return  // 裸返回
}

// 优点：短函数中更简洁
// 缺点：长函数中不知道return了什么
// 建议：只有短函数（<10行）才用
```

**面试题9：Go支持默认参数吗？怎么模拟？**
```go
// Go不支持函数默认参数（"少即是多"）

// 模拟方式1：可变参数
func Connect(addr string, opts ...Option) { ... }

// 模拟方式2：配置结构体
func NewServer(addr string, cfg *Config) (*Server, error) {
    if cfg == nil {
        cfg = &Config{Port: 8080, Timeout: 30}  // 默认值
    }
    // ...
}

// 模拟方式3：函数选项模式（Functional Options）
type Option func(*Config)

func WithPort(port int) Option {
    return func(c *Config) { c.Port = port }
}

func NewServer(addr string, opts ...Option) *Server {
    cfg := &Config{Port: 8080}  // 默认
    for _, opt := range opts {
        opt(cfg)
    }
    return &Server{Addr: addr, Config: cfg}
}
```

---

---

### ⚡ 5.8 错误处理超级详解：errors.Is和errors.As

#### 什么是错误链？（给初中生）

```
错误链 = 错误像包礼物一样，一层包一层

函数A出错："打开文件失败"
  └── 原因："找不到文件"
    └── 根本原因："路径不对"

errors.Is 问：这个错误链里有没有"找不到文件"这个错误？
  → 有！

errors.As 问：这个错误链里有没有"路径错误"这个类型的错误？
  → 有！让我把它的详细信息给你
```

#### errors.Is 的完整用法

```go
import "errors"

func openConfig() error {
    _, err := os.Open("/etc/config.yaml")
    if err != nil {
        return fmt.Errorf("打开配置失败: %w", err)  // %w 包装
    }
    return nil
}

func main() {
    err := openConfig()
    
    // errors.Is 检查错误链
    if errors.Is(err, os.ErrNotExist) {
        fmt.Println(\✅ 文件不存在，创建默认配置")
    } else if err != nil {
        fmt.Println("其他错误:", err)
    }
}
```

#### errors.As 的完整用法

```go
// 自定义错误类型
type ValidationError struct {
    Field string
    Value interface{}
    Msg   string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %v (%s)", e.Field, e.Value, e.Msg)
}

func validateAge(age int) error {
    if age < 0 {
        return &ValidationError{"age", age, "不能为负"}
    }
    if age > 150 {
        return &ValidationError{"age", age, "太大了吧"}
    }
    return nil
}

func main() {
    err := validateAge(-5)
    
    var valErr *ValidationError
    if errors.As(err, &valErr) {
        fmt.Printf("字段: %s\n", valErr.Field)
        fmt.Printf("值: %v\n", valErr.Value)
        fmt.Printf("信息: %s\n", valErr.Msg)
    }
}
```

#### %w 和 %v 的区别

```go
err := os.ErrNotExist

// %w：包装（保留原始错误）
f1 := fmt.Errorf("额外信息: %w", err)
fmt.Println(errors.Is(f1, os.ErrNotExist))  // true！可以找到

// %v：不包装（只保留文字）
f2 := fmt.Errorf("额外信息: %v", err)
fmt.Println(errors.Is(f2, os.ErrNotExist))  // false！找不到
```

---

### ⚡ 5.9 函数的完整性能指南

#### 函数调用的开销

```
直接调用普通函数：~2ns
调用接口方法：~4ns
通过函数值调用：~2ns（编译后可内联）
通过闭包调用：~3ns
通过reflect调用：~500ns

结论：
  普通函数、接口方法、函数值，性能差距很小
  不要为了"性能"避免使用接口或函数值
  但反射真的很慢，能不用就不用
```

#### 内联优化（Inline）

```
Go编译器会自动把小函数"内联"
内联 = 把函数代码直接"复制"到调用处
     = 省掉了函数调用的开销

会被内联的函数：
  - 函数体很小（一般< 80行）
  - 没有复杂语句（如for/range）
  - 没有闭包

查看内联：go build -gcflags='-m' main.go
输出：可以内联（can inline）
```

---

---

### ⚡ 5.10 defer性能分析和函数选项模式

#### defer到底有多慢？

```go
// Go 1.14之前：defer很慢（堆分配），约200ns
// Go 1.14~1.16：defer优化为栈分配，约30ns
// Go 1.17+：内联defer（open coded defer），约2ns！
//
// 直接调用：~2ns
// 内联defer：~2ns（几乎没有额外开销！）
// 栈defer：~30ns
//
// 结论：Go 1.17+之后，不用为性能担心defer！
// 用defer的开销几乎为零
```

**什么情况下defer不会内联？**
```
1. defer在for循环中
2. 同一个函数中有超过8个defer
3. defer嵌套在深层条件分支中
4. defer涉及闭包
```

#### 内置函数min、max、clear（Go 1.21+）

```go
// 不需要import，可直接使用

// min：取最小值
min(1, 2, 3)              // 1
min(1.5, 2.5)            // 1.5
min("a", "b")            // "a"

// max：取最大值
max(1, 2, 3)              // 3

// clear：清空map或slice元素归零
m := map[string]int{"a": 1}
clear(m)                  // m 空了

s := []int{1, 2, 3}
clear(s)                  // s = [0, 0, 0]

// 可以和defer配合吗？可以！
func safeSum(values []int) int {
    defer func() {
        if r := recover(); r != nil {
            log.Println("求和出错:", r)
        }
    }()
    var sum int
    for _, v := range values {
        sum = max(sum, sum+v)  // 用max确保不会负数越界
    }
    return sum
}
```

---

### ⚡ 5.11 函数选项模式（Functional Options Pattern）

函数选项模式是Go中非常流行的设计模式，用来替代其他语言的"默认参数"或"Builder模式"。

```go
type Server struct {
    addr    string
    port    int
    timeout time.Duration
    verbose bool
}

// Option 是一个函数类型
type Option func(*Server)

// 各种选项函数
func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func WithTimeout(t time.Duration) Option {
    return func(s *Server) { s.timeout = t }
}

func WithVerbose() Option {
    return func(s *Server) { s.verbose = true }
}

// 构造函数——接受可变数量的选项
func NewServer(addr string, opts ...Option) *Server {
    // 默认值
    s := &Server{
        addr:    addr,
        port:    8080,
        timeout: 30 * time.Second,
    }
    // 应用选项
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// 使用：
s1 := NewServer("localhost")                                   // 全默认
s2 := NewServer("localhost", WithPort(9090))                    // 自定义端口
s3 := NewServer("localhost", WithPort(9090), WithVerbose())     // 自定义端口+详细日志
```

**为什么函数选项模式好？**
```
1. 不需要改构造函数签名就能增加选项
2. 调用者只设置关心的选项
3. 可以随意扩展
4. 组合灵活（比Builder模式更简洁）
5. Go的标准库也在用（gRPC、etcd等）
```

---

---

### ⚡ 5.12 泛型函数完整指南（Go 1.18+）

#### 什么是泛型函数？（给初中生）

```
普通函数：只能处理一种类型
func DoubleInt(n int) int { return n * 2 }
func DoubleFloat(n float64) float64 { return n * 2 }

泛型函数：可以处理多种类型
func Double[T int | float64](n T) T { return n * 2 }

Double(3)       // T=int, 返回6
Double(3.5)     // T=float64, 返回7.0

同一份代码，适用于多种类型！
```

#### 完整的泛型函数例子

```go
// 泛型反转切片
func Reverse[T any](s []T) []T {
    result := make([]T, len(s))
    for i, v := range s {
        result[len(s)-1-i] = v
    }
    return result
}

// 泛型查找
func Find[T comparable](s []T, target T) int {
    for i, v := range s {
        if v == target { return i }  // comparable保证可以用==
    }
    return -1
}

// 泛型过滤
func Filter[T any](s []T, keep func(T) bool) []T {
    var result []T
    for _, v := range s {
        if keep(v) {
            result = append(result, v)
        }
    }
    return result
}

// 使用：
ints := []int{1, 2, 3, 4, 5}
evens := Filter(ints, func(n int) bool { return n%2 == 0 })
fmt.Println(evens)  // [2, 4]
```

#### 泛型函数的性能

```go
// Go的泛型通过"模板实例化"实现
// 不是通过反射或接口装箱

// 也就是说：
// Double[int](3)  → 编译器生成一个 func DoubleInt(n int) int
// Double[float64](3.5) → 编译器生成一个 func DoubleFloat(n float64) float64

// 运行时：和手写的类型特定版本一样快！
// 没有性能损失（不像Java泛型有装箱开销）
```

---

---

### ⚡ 5.13 再补5道大厂面试题（函数篇）

**面试题10：map作为函数参数，是传值还是传引用？**
```go
func modifyMap(m map[string]int) {
    m["key"] = 42  // 会影响外面的map
}

// map是引用类型，但传的是"map header"的副本
// header里有指向底层哈希表的指针
// 所以函数内修改会影响外部

// 但：如果函数内 m = make(map[string]int) 重新赋值
// 不会影响外部！（因为m是副本）
```

**面试题11：可变参数的底层是什么样的？**
```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {  // nums实际上是个[]int
        total += n
    }
    return total
}

// ...int 在函数内部被编译为 []int
// 编译器在调用处：
//   sum(1, 2, 3) → sum([]int{1, 2, 3})
//
// 区别：
// nums := []int{1, 2, 3}
// sum(nums...)  // 展开，不创建新切片
```

**面试题12：什么是"函数类型"？可以当map的key吗？**
```go
// 函数类型 = 函数的签名
// func(int, int) int 这是一个类型

var fn func(int, int) int
fn = func(a, b int) int { return a + b }

// 函数不能做map的key（因为函数不可比较）
// var m map[func()]int  // ❌ 编译错误
```

**面试题13：多个defer的执行顺序和参数求值？**
```go
func main() {
    x := 1
    defer fmt.Println("defer1:", x)  // 此时x=1被记录
    
    x = 2
    defer fmt.Println("defer2:", x)  // 此时x=2被记录
    
    x = 3
}
// 输出：
// defer2: 2  ← 后进的先出
// defer1: 1  ← 先记录的值
```

**面试题14：defer能修改函数返回值吗？**
```go
// 只有命名返回值才可以！

func f1() (result int) {
    defer func() {
        result += 10  // 修改命名返回值
    }()
    return 1  // result先设为1，defer改成11
}
// 返回11

func f2() int {
    var result int
    defer func() {
        result += 10  // 修改局部变量，不影响匿名返回值
    }()
    return 1  // 1被复制到匿名返回值，defer改的是result
}
// 返回1
```

---

---

### ⚡ 5.14 函数调用的完整流程图集合

#### 函数调用栈流程图

```
         main() 调用 add(3, 4)
              │
              ▼
      ┌─────────────────┐    ← 高地址
      │ main的局部变量   │
      ├─────────────────┤
      │ add的参数 a=3    │  ← 入栈
      ├─────────────────┤
      │ add的参数 b=4    │  ← 入栈
      ├─────────────────┤
      │ 返回地址        │  ← 保存回到哪
      ├═════════════════┤
      │ add的局部变量    │  ← SP栈指针
      └─────────────────┘    ← 低地址

      add执行完毕
              │
              ▼
      ┌─────────────────┐
      │ main继续执行    │  ← SP回到main的栈
      └─────────────────┘
```

#### 递归调用的栈变化图

```
factorial(5) 的调用栈：

Step 1: factorial(5)          ┌─┐
          ↓                    │5│  ← 栈顶
Step 2: factorial(5)→5*factorial(4)  ┌─┐
          ↓                      │4│
                                  │5│
Step 3: ...继续到factorial(1)   ┌─┐
                                 │1│
                                 │2│
                                 │3│
                                 │4│
                                 │5│

开始返回：
  factorial(1) = 1  → 弹出1
  factorial(2) = 2*1 = 2  → 弹出2
  factorial(3) = 3*2 = 6  → 弹出3
  factorial(4) = 4*6 = 24  → 弹出4
  factorial(5) = 5*24 = 120  → ⭐最终结果

如果递归太深（比如100000次）：
  → 栈溢出！程序崩溃
  goroutine栈可以增长到1GB，但终究有限
```

#### defer的执行顺序图

```
         ┌──────────────────────┐
         │  注册defer1          │  ①
         │  注册defer2          │  ②
         │  注册defer3          │  ③
         │  ...                 │
         │  正常执行代码         │
         │  return              │
         ├══════════════════════┤
         │  ⭐ 执defer3（后进） │  ③
         │  ⭐ 执行defer2       │  ②
         │  ⭐ 执行defer1（先出）│  ① ← LIFO!
         └──────────────────────┘

就像叠盘子：
  放上1号盘 → 放上2号盘 → 放上3号盘
  拿走3号盘 → 拿走2号盘 → 拿走1号盘
  后放上去的先拿走（后进先出 LIFO）
```

#### defer + return 的执行顺序图

```go
func example() (result int) {
    result = 0          // 1. result设为0
    defer func() {       // 2. 注册defer
        result += 10    // 4. 修改result为10
    }()
    return result       // 3. return把result的值返回
                        // 5. 函数结束，返回10
}

时间线：
step1: result = 0
step2: defer 注册（不执行）
step3: return 0 → result准备返回
step4: defer 执行 → result += 10
step5: 函数结束 → 返回 result(final) = 10
```

#### panic/recover流程图

```
           panic("出错了")
               │
               ▼
      ┌────────────────┐
      │ 当前函数立刻停止  │
      └───────┬────────┘
              │
              ▼
      ┌────────────────┐
      │ 执行当前函数的   │
      │ 所有defer       │
      └───────┬────────┘
              │
              ▼
      ┌────────────────┐
      │ panic向上层传播 │
      └───────┬────────┘
              │
              ▼
      ┌──────────────────────┐
      │ 上层执行它的defer    │
      │ 有recover吗？        │
      └───────┬──────┬──────┘
          有/│      │无
             │      ▼
        ╔════╧══╗  ┌────────────────┐
        ║恢复!  ║  │ 继续向上传播   │
        ║继续执 ║  │ 直到main      │
        ║行程序 ║  │ 程序崩溃      │
        ╚═══════╝  └────────────────┘
```

#### 闭包的完整图解

```go
func adder() func(int) int {
    sum := 0                ← sum在堆上（逃逸）
    return func(x int) int {
        sum += x            ← 闭包捕获sum的地址
        return sum
    }
}

在内存里：
┌──────────────────────┐
│ adder()调用后的结果：  │
│                      │
│ 闭包结构体：          │
│ ┌────────────────┐   │
│ │ 函数代码指针    │   │
│ │ sum的地址 ──────┼───┼──→ 堆上的sum变量
│ └────────────────┘   │
└──────────────────────┘

f := adder()
f(10)  → sum = 10
f(5)   → sum = 15（sum还在！没有被销毁）
f(3)   → sum = 18

为什么sum不消失？
  因为闭包还握着对sum的引用
  GC检测到sum还被使用者 → 不回收
```

---

> **下一章**：[第6章 方法](./ch06-methods.md) —— 方法声明、指针接收器、嵌入扩展、封装。
