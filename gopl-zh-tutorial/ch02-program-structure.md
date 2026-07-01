# 第2章 程序结构

> 深入Go程序的构建块：命名规范、声明语句、变量生命周期、类型系统、包组织和作用域规则。这些是编写任何Go程序的基础。

---

## 目录

- [2.1 命名](#21-命名)
- [2.2 声明](#22-声明)
- [2.3 变量](#23-变量)
- [2.4 赋值](#24-赋值)
- [2.5 类型](#25-类型)
- [2.6 包和文件](#26-包和文件)
- [2.7 作用域](#27-作用域)

---

## 2.1 命名

### 核心规则

1. **命名必须以字母或下划线开头**，后跟任意数量的字母、数字或下划线
2. **大小写敏感**：`Hello`和`hello`是不同的名字
3. **驼峰式**：Go推荐驼峰命名，不使用下划线（`CamelCase`，不是`camel_case`）
4. **首字母大小写决定可见性**：
   - 大写字母开头 = **导出（exported/public）**：对包外可见
   - 小写字母开头 = **未导出（unexported/private）**：仅包内可见
   - 此规则适用于变量、常量、类型、函数、方法、结构体字段

### 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 包名 | 小写，单数 | `fmt`, `http`, `strings` |
| 变量 | 驼峰，短 | `count`, `req`, `w` (Writer) |
| 常量 | 驼峰 | `MaxSize`, `StatusOK` |
| 接口名 | 加-er后缀 | `Reader`, `Writer`, `Handler` |
| 类型 | 首字母大写 | `Request`, `Response` |
| 测试函数 | TestXxx | `TestParse` |

### 关键字（不能用作标识符）

```
break      default       func     interface   select
case       defer         go       map         struct
chan       else          goto     package     switch
const      fallthrough   if       range       type
continue   for           import   return      var
```

### 预定义标识符（可被重新声明，但不建议）

```
内建类型:  bool byte complex64 complex128 error float32 float64
           int int8 int16 int32 int64 rune string
           uint uint8 uint16 uint32 uint64 uintptr
内建函数:  append cap close complex copy delete imag len
           make new panic print println real recover
常量:      true false iota
零值:      nil
```

### 🔥 面试扩展

**高频题1：为什么Go推荐短变量名（`i`, `r`, `w`等）？**
> Go认为**变量的作用域越小，名字应该越短**。局部变量生命周期短，短名可读性高（不影响理解和搜索）。包级变量则应有描述性名称。例如HTTP handler中`w`（ResponseWriter）和`r`（*Request）是标准惯例。

**高频题2：Go包命名为什么用小写单数？**
> 因为导入后通过包名访问，长名字增加调用负担。`strings.Compare`好于`string_utilities.Compare`。包名是命名空间，且应简洁到供客户端愉快使用。

**高频题3：`new`和`make`是关键字还是函数？被重定义会发生什么？**
> `new`和`make`是**预定义标识符**（不是关键字），可以在局部作用域重新声明。但重新声明后，在作用域内无法使用原本的内建功能，极易造成混淆，**绝对不要这么做**。

---

## 2.2 声明

### 四种声明

| 声明 | 关键字 | 用途 |
|------|--------|------|
| 变量声明 | `var` | 创建一个变量 |
| 常量声明 | `const` | 创建一个编译期常量 |
| 类型声明 | `type` | 定义新的命名类型 |
| 函数声明 | `func` | 声明一个函数 |

### 声明示例

```go
// 包级别声明
package main

import "fmt"

const PI = 3.14159    // 常量
var version = "1.0"   // 变量

type Celsius float64    // 类型
type Fahrenheit float64

func main() {           // 函数
    fmt.Println("Go version:", version)
}
```

### 🔥 面试扩展

**高频题1：包级别变量声明和函数内部声明的初始化时机？**
> 包级变量在程序启动时（`init`函数运行前）初始化；局部变量在**函数执行到声明时**初始化。

**高频题2：多个文件中的`init`函数执行顺序？**
> 同一个包内按文件名顺序；导入的包先于当前包的`init`执行。多个`init`按源文件编译顺序执行，**不要依赖多个init之间的执行顺序**。

---

## 2.3 变量

### 零值初始化

Go中所有变量声明时自动初始化为零值：

| 类型 | 零值 |
|------|------|
| 数值类型 | `0` |
| bool | `false` |
| string | `""`（空字符串） |
| 指针/接口/slice/channel/map/函数类型 | `nil` |
| 数组 | 所有元素为零值 |
| 结构体 | 所有字段为零值 |

### 变量声明形式

```go
// 1. 完整声明
var name string = "Alice"

// 2. 类型推断
var name = "Alice"   // string

// 3. 短声明（仅函数内）
name := "Alice"

// 4. 多变量声明
var i, j, k int
var a, b, c = 1, 2, "hello"

// 5. 声明分组
var (
    name    string
    age     int
    active  bool
)
```

### new函数

```go
p := new(int)    // *int类型，值为0的指针
fmt.Println(*p)  // 输出 0
*p = 2
fmt.Println(*p)  // 输出 2
```

`new(T)`等价于 `&T{}`，但`new(int)`返回`*int`指向零值，而`&T{}`可初始化非零值。

### 变量的生命周期

- **包级变量**：程序整个运行期间
- **局部变量**：从声明到函数返回（或被闭包引用时逃逸到堆上）
- **逃逸分析**：编译器决定变量分配在栈还是堆

### 🔥 面试扩展

**高频题1：`var a int` 和 `a := 0` 有何区别？**
> - `var a int`：声明+零值初始化，可读性更好
> - `a := 0`：短声明+类型推断，更简洁
> - 包级别不能用`:=`
> - 对于零值，`var a int`更明确表达了"初始化为零值"的意图

**高频题2：短变量声明`:=`的"至少一个新变量"规则是什么？**
> 在多重赋值中，`:=`左边**至少有一个变量是未声明的**。已有变量会被赋值而非重新声明：
```go
a, b := 1, 2    // 声明a和b
a, c := 3, 4    // a被赋值（已存在），c是新声明
// a, b := 5, 6 // ❌ 编译错误：没有新变量
```

**高频题3：什么情况下变量会逃逸到堆上？**
> 1. 函数返回了局部变量的指针
> 2. 变量被闭包捕获并在函数返回后使用
> 3. 变量太大无法放入栈
> 4. 编译器不确定变量大小（如`interface{}`）
> 可以用`go build -gcflags=-m`查看逃逸分析结果。

**高频题4：Go的栈和goroutine栈有何关系？**
> 每个goroutine初始有一个**小栈（~2KB）**，动态增长（最大1GB，64位系统）。Go的栈是连续栈（早期版本为分段栈），不够时通过`stack copying`扩容——将所有栈帧复制到更大的连续内存区域。这是goroutine比线程廉价的核心原因之一。

**高频题5：`new`和`make`的区别？**
> - `new(T)`：返回`*T`（指针），分配零值内存，适用于任意类型
> - `make(T, args)`：仅用于slice/map/channel，返回初始化后的引用类型（非指针），会初始化内部数据结构
> - `new(map[string]int)`返回`*map[string]int`（nil map指针），而`make(map[string]int)`返回一个可用的map

---

## 2.4 赋值

### 赋值形式

```go
// 简单赋值
x = 1
*p = true
person.name = "Alice"

// 元组赋值（多重赋值）
x, y = y, x           // 交换值
a, b = 1, 2

// 增量赋值
count++
count--
count += 10
count *= 2
```

### 可赋值性

赋值时必须满足：**值的类型必须和变量类型兼容**。Go没有隐式类型转换，不同类型间赋值或比较必须显式转换。

```go
var i int = 42
var f float64 = float64(i)  // 必须显式转换
var u uint = uint(f)         // 必须显式转换
```

### 🔥 面试扩展

**高频题1：Go为什么不支持隐式类型转换？**
> 隐式类型转换是大量bug的来源（如C语言中int到unsigned int的陷阱）。Go要求显式转换，牺牲了短期"便利"，换来了长期可靠性和代码清晰度。

**高频题2：两个值交换的元组赋值在Go中如何实现？**
> 编译器生成临时变量保存原值，然后分别赋值。`a, b = b, a`等价于：
> ```go
> tmp1, tmp2 = b, a
> a, b = tmp1, tmp2
> ```

**高频题3：Go的`++`和`--`有什么限制？**
> - `++`和`--`是语句不是表达式，不能用在赋值语句中：
>   ```go
>   x = a++  // ❌ 编译错误
>   ```
> - 只有后缀形式，没有前缀`++a`
> - 仅用于数值类型

---

## 2.5 类型

### 类型声明

```go
// 定义新的命名类型
type Celsius float64
type Fahrenheit float64

// 类型的方法
func (c Celsius) String() string {
    return fmt.Sprintf("%.2f°C", c)
}
```

### 类型别名（Go 1.9+）

```go
type MyInt = int  // 别名，MyInt和int是同一类型
type MyInt2 int   // 新类型，和int不是同一类型
```

### 类型转换

```go
var c Celsius = 100.0
var f Fahrenheit = Fahrenheit(c)  // 显式转换

// 数值类型转换
var i int = 42
var f float64 = float64(i)  // 42.0
var u uint = uint(f)        // 42
```

### 🔥 面试扩展

**高频题1：`type Celsius float64`定义的类型和`float64`的关系？**
> `Celsius`是一个**新类型**，有区别于`float64`的类型系统：
> - 底层类型仍是`float64`（可以进行算术运算）
> - 需要**显式转换**`float64(c)`才能用于需要`float64`参数的地方
> - 可以为`Celsius`定义方法（如上面的`String()方法`）
> - `type MyInt = int`才是真正的类型别名（类型相同）

**高频题2：类型声明有什么实际用途？**
> 1. **语义化**：`Celsius`和`Fahrenheit`比`float64`有更强的语义
> 2. **类型安全**：不小心混用不同类型会编译错误
> 3. **方法绑定**：自定义类型可以添加方法
> 4. **接口实现**：新类型可以隐式实现接口

---

## 2.6 包和文件

### 包的结构

```go
// $GOPATH/src/github.com/user/project/
//   main.go          → package main
//   utils/
//     helper.go      → package utils
```

### 导入

```go
// 标准导入
import "fmt"
import "net/http"

// 分组导入
import (
    "fmt"
    "net/http"
    "os"
)

// 重命名导入
import f "fmt"
import "crypto/rand"
import rand2 "math/rand"  // 避免名字冲突

// 匿名导入（仅初始化）
import _ "image/png"  // 注册PNG解码器
```

### 包的初始化顺序

```
程序入口 → import的包初始化（递归）→ 包级变量初始化 → init函数运行
```

```go
var a = b + c  // a第三个初始化
var b = f()    // b第二个初始化
var c = 1      // c第一个初始化

func f() int { return c + 1 }
```

### 🔥 面试扩展

**高频题1：循环导入（import cycle）如何处理？**
> Go禁止循环导入。如果A导入B，B导入A，编译会报错`import cycle not allowed`。解决方式：
> 1. **提取公共接口**到第三个包C
> 2. A只导入C（接口），B通过参数传递
> 3. 使用包级别的回调函数
> 4. 合并两个包

**高频题2：包的匿名导入`import _ "pkg"`的常见用途？**
> 1. **注册数据库驱动**：`import _ "github.com/go-sql-driver/mysql"`
> 2. **注册图片编解码器**：`import _ "image/png"`，`import _ "image/jpeg"`
> 3. **初始化时注册插件**：某些框架通过匿名导入注册组件
> 实现机制：包被初始化（调用init函数），但标识符不暴露给当前包。

**高频题3：`init`函数可以有多少个？有什么限制？**
> - 一个文件可以有多个`init`函数
> - `init`不能显式调用，不能有参数和返回值
> - 不建议依赖多个init的执行顺序
> - 通常用于：注册插件、初始化全局状态、检查配置

---

## 2.7 作用域

### 作用域 vs 生命周期

| 概念 | 说明 |
|------|------|
| 作用域（Scope） | 声明在源代码中可见的范围（**编译时**概念） |
| 生命周期（Lifetime） | 变量在运行时存在的时间段（**运行时**概念） |

### 作用域规则

```go
var x = "package level"  // 包级别作用域

func f() {
    x := "function level"  // 函数级别，遮蔽包级x
    fmt.Println(x)         // 输出 "function level"
    if true {
        x := "block level" // 块级别，遮蔽函数级x
        fmt.Println(x)     // 输出 "block level"
    }
    fmt.Println(x)         // 输出 "function level"
}
```

### 隐式作用域块

Go有多种隐式作用域块：

1. **宇宙块（Universe Block）**：所有Go源码共享，包含预定义标识符
2. **包块（Package Block）**：包内所有源文件共享
3. **文件块（File Block）**：单个源文件内
4. **if/for/switch/select块**：每个控制结构创建自己的作用域

```go
if x := f(); x > 0 {
    fmt.Println(x)    // 可访问x
}
// x在这里不可访问

if x, err := f(); err != nil {
    fmt.Println(x)    // 可访问x
} else {
    fmt.Println(x)    // 同一作用域，也可访问
}
// x和err在这里都不可访问
```

### 🔥 面试扩展

**高频题1：下面的代码输出什么？**

```go
var a = "G"

func main() {
    n()
    m()
    n()
}

func n() { fmt.Print(a) }
func m() {
    a := "O"
    fmt.Print(a)
}
```

> 输出：`GOG`。`n()`访问包级变量`a`（"G"），`m()`用自己的局部变量`a`遮蔽了包级变量（"O"），`n()`再次访问包级变量（仍是"G"）。

**高频题2：for循环中的变量作用域陷阱**

```go
var rmdirs []func()
for _, dir := range tempDirs() {
    os.MkdirAll(dir, 0755)
    rmdirs = append(rmdirs, func() {
        os.RemoveAll(dir)  // ❌ 闭包捕获的是dir变量，不是值
    })
}
// 执行时所有闭包都看到最后一个dir值
```

> 修复：`dir := dir`创建副本，或传参。

**高频题3：if语句中声明变量的作用域**

```go
if v, err := doSomething(); err != nil {
    return err
} else {
    // v和err在此可见
    fmt.Println(v)
}
// v和err不可见
```

> 这种模式是Go的惯用写法，在if中处理函数返回值和错误，else块中处理成功情况。

**高频题4：包级变量的可见性如何确定？**
> 包级变量遵循**包内所有文件可见**（同一包任何文件都可访问）。对外，**首字母大写**的标识符是导出的，其他包可访问。这构成了Go的封装机制——不需要`public/private`关键字，大小写就够了。

## ⚡ 超级扩展

### ⚡ 2.0 命名规则的字节级分析

#### Go标识符的Unicode支持细节

Go对标识符的支持不仅限于ASCII——它完整支持Unicode标识符（包括中文变量名）：

```go
package main

import "fmt"

func main() {
    变量 := 42
    fmt.Println(变量)  // 42
}
```

**底层规则：** Go的标识符定义在 `unicode.IsLetter` 和 `unicode.IsDigit` 两个函数中。标识符首字符必须是Letter类，后续字符可以是Letter或Digit。

**Unicode类别覆盖：**
```
Letter (L): Lu(大写), Ll(小写), Lt(标题), Lm(修饰符), Lo(其他)
Digit (Nd): 十进制数字
连接符 (Pc): 下划线_（仅此一个）
```

#### 空白标识符 `_` 的底层实现

```go
// 1. 丢弃函数返回值
_, err := doSomething()

// 2. for range时丢弃key或value
for _, v := range slice {}
for k, _ := range slice {}  

// 3. 包级别声明类型声明
var _ io.Writer = &MyWriter{}  // 编译期检查接口实现

// 4. import时触发init
import _ "image/png"
```

---

### ⚡ 2.1 声明系统的编译时深度分析

#### Go的四种声明语句完整对比

| 声明 | 关键字 | 作用域 | 编译时/运行时 |
|------|--------|--------|---------------|
| 变量 | `var` | 函数/包 | 运行时分配内存 |
| 常量 | `const` | 函数/包 | 编译时求值 |
| 类型 | `type` | 包 | 编译时注册 |
| 函数 | `func` | 包 | 编译时生成代码 |

#### 常量编译时求值机制

```go
const (
    a = 1 + 2           // 编译时 → 3（constant folding）
    b = a * 3           // → 9
    c = 1 << (10 * 2)   // → 1 << 20 = 1048576
)
// 运行时零开销，就像直接写 const c = 1048576
```

#### 声明顺序无关的真正原因

Go的编译器**先收集所有声明**，建立符号表，然后才进行类型检查和代码生成。所以声明的顺序不影响编译结果（和C语言不同）。

---

### ⚡ 2.2 变量体系完全解析

#### var 声明的六种形式

```go
// 形式1: 基础类型+零值
var count int                    // 0

// 形式2: 类型推断
var name = "Alice"              // string

// 形式3: 显式类型
var port int64 = 8080

// 形式4: 多变量
var x, y int                     // 0, 0

// 形式5: 分组声明
var (
    home   = os.Getenv("HOME")
    user   = os.Getenv("USER")
)

// 形式6: 短变量声明（仅函数内）
count := 0
name, err := os.Hostname()
```

#### 零值初始化完整表格

| 类型 | 零值 | 内部二进制表示 |
|------|------|---------------|
| bool | false | 0x00 |
| 所有整数类型 | 0 | 全0 |
| float32/float64 | 0.0 | IEEE 754全0 |
| complex64/128 | 0+0i | 实部虚部全0 |
| string | "" | (ptr=nil, len=0) |
| pointer | nil | 0x0 |
| function | nil | 0x0 |
| interface | nil | (tab=nil, data=nil) |
| slice | nil | (array=nil, len=0, cap=0) |
| map | nil | nil指针 |
| channel | nil | nil指针 |
| struct | 所有字段零值 | 递归清零 |
| array | 所有元素零值 | 固定长度填充0 |

#### nil slice vs empty slice 底层差异

```go
var s []int             // nil slice
s2 := []int{}           // empty slice

// 底层结构
// nil slice:   {array: 0x0,         len: 0, cap: 0}
// empty slice: {array: 0x123456,    len: 0, cap: 0}
// empty slice的array指向全局zerobase地址

json.Marshal(s)          // "null"
json.Marshal(s2)         // "[]"
```

---

### ⚡ 2.3 new() 函数的完整源码分析

#### new(T) 的编译器和运行时调用链

```go
p := new(int)

// 编译后变成调用 runtime.newobject
// 源码: runtime/malloc.go
func newobject(typ *_type) unsafe.Pointer {
    return mallocgc(typ.size, typ, true)  // true=清零
}
```

**内存分配路径：**
```
new(int)
  → runtime.newobject
    → mallocgc(8, typ, true)
      → 小对象(<32KB): 从P的mcache分配
        → 有空闲: mcache.alloc[sizeClass].next
        → 无空闲: mcache.refill → mheap.alloc
      → 大对象(>=32KB): mheap.allocLarge
    → 内存清零
    → 返回 unsafe.Pointer
```

#### new(T) vs &T{} 对比

```go
p1 := new(int)       // *int, 指向0
p2 := &int{}         // *int, 指向0

// 区别
p3 := new(Point)          // &Point{X:0, Y:0} — 只能零值
p4 := &Point{X: 1}        // &Point{X:1, Y:0} — 可指定字段
```

---

### ⚡ 2.4 逃逸分析的完整机制

#### 逃逸分析是什么？

编译器在编译时决定变量分配在栈还是堆。目标是：能放栈的尽量放栈（栈分配零GC开销）。

#### 逃逸条件汇总

| 条件 | 示例 | 结果 |
|------|------|------|
| 返回局部指针 | `return &x` | 逃逸 |
| 闭包捕获 | `func() { x++ }` | 逃逸 |
| 接口装箱 | `fmt.Println(x)` | 逃逸 |
| 大对象 | `[1000000]int{}` | 逃逸 |
| 类型不确定 | `make([]int, n)` (n为变量) | 逃逸 |
| defer引用 | `defer func() { _ = x }()` | 逃逸 |

#### 查看逃逸分析

```bash
$ go build -gcflags='-m -l' main.go
# 输出如:
# ./main.go:5:2: moved to heap: x
```

#### 避免逃逸的技巧

```go
// ❌ 接口参数导致逃逸
func printVal(v interface{}) {}
printVal(42)  // 42逃逸

// ✅ Go 1.18泛型可以避免
func printVal[T int | int64](v T) {}
printVal(42)  // 不逃逸
```

---

### ⚡ 2.5 赋值完整解析

#### 元组赋值的底层实现

```go
x, y = y, x  // Go原生支持交换

// 编译器生成的伪代码
// tmp1 := y
// tmp2 := x
// x = tmp1
// y = tmp2
```

#### Go不支持的赋值类型

```go
// 1. 链式赋值
// a = b = 0     // ❌

// 2. 自增作为表达式
// if i++ > 0 {}  // ❌ i++是语句不是表达式

// 3. 不同类型隐式转换
// var i int = 3.14  // ❌
```

---

### ⚡ 2.6 类型声明深度分析

#### 命名类型 vs 非命名类型

```go
type MyInt int         // 命名类型
var x int              // 预定义命名类型
var y []int            // 非命名类型（复合字面量）
```

**关键区别：**
- 只有命名类型可以有方法
- `[]int`、`*int`、`map[string]int` 不能直接定义方法

#### 底层类型（Underlying Type）完整规则

```go
type Celsius float64      // 底层类型: float64
type Fahrenheit float64   // 底层类型: float64

// 命名类型间必须显式转换
var c Celsius = 100.0
var f Fahrenheit = Fahrenheit(c)  // 必须显式

// 但结构体底层类型相同（匿名字段相同）可转换
type Point struct { X, Y float64 }
type MyPoint struct { X, Y float64 }
var p1 Point
var p2 MyPoint
p2 = MyPoint(p1)  // ✅ 底层类型相同
```

#### 类型别名的实际应用场景

```go
// 场景1: 大型重构逐步迁移
type OldConfig = NewConfig

// 场景2: 给跨包类型添加方法（通过别名再定义新类型）
type HandlerFunc = http.HandlerFunc

// 场景3: 简化泛型代码
type Slice[T any] = []T
```

---

### ⚡ 2.7 包的初始化顺序

#### 完整的初始化流程

```
1. 导入的包递归初始化（深度优先）
2. 包级变量的零值初始化
3. 包级变量按依赖顺序初始化
4. 所有init()函数按文件名字典序运行
5. 如果包是main，执行main()
```

#### init() 详细规则

```go
// 一个文件可以有多个init
func init() { fmt.Print("A ") }
func init() { fmt.Print("B ") }
// 输出: A B

// init不能手动调用
// init()    // ❌

// init没有参数和返回值
```

**循环导入解决方案：**

```go
// 方案1: 提取公共接口到第三个包
// 方案2: 回调模式
package a
var OnEvent func()

package b
import "a"
func init() { a.OnEvent = handleEvent }
```

---

### ⚡ 2.8 作用域深度分析

#### 作用域 vs 生命周期

| 概念 | 定义 | 类型 |
|------|------|------|
| 作用域（Scope） | 标识符在源代码中可见的区域 | 编译时 |
| 生命周期（Lifetime） | 变量在运行时存活的时间段 | 运行时 |

#### 8层作用域层次

```
1. 宇宙作用域 (Universe) — 预定义类型/函数/常量
2. 包作用域 (Package) — 包级声明
3. 文件作用域 (File) — Cgo导入作用域
4. 函数作用域 (Function) — 函数参数和局部变量
5. if/for/switch/select块 — 控制结构隐式块
6. 函数体块 — 显式 {} 代码块
```

#### 宇宙作用域可被遮蔽的危险

```go
func main() {
    string := "shadow"  // 遮蔽了string类型！
    var x string         // 编译错误：string现在是变量
}
```

#### Go 1.22的for循环变量修复

```go
// Go 1.22之前: 每次迭代复用同一变量
for i := 0; i < 3; i++ {
    defer fmt.Print(i)  // 输出: 2 1 0 (defer LIFO, i是同一地址)
}

// Go 1.22: 每次迭代创建新变量
for i := 0; i < 3; i++ {
    defer fmt.Print(i)  // 输出: 2 1 0 (虽然地址不同，但值已被defer捕获)
}
```

---

---

### ⚡ 2.9 大厂面试题全集（程序结构篇）

**面试题1：下面代码的输出是什么？**
```go
var x = 10

func main() {
    x := 20     // 注意：这是短声明，创建了新的局部变量x
    fmt.Println(x)  // 输出？
}
// 输出：20
// 函数内部的 x 遮蔽（shadow）了包级别的 x
```

**面试题2：变量遮蔽（Variable Shadowing）是什么？怎么检测？**
```go
func main() {
    x := 10
    if true {
        x := 20  // 这个x是新变量，遮蔽了外部的x
        fmt.Println(x)  // 20
    }
    fmt.Println(x)  // 10（外层的x没变）
    
    // 检测工具：
    // go install golang.org/x/tools/go/analysis/passes/shadow/cmd/shadow
    // go vet -vettool=$(which shadow) main.go
}
```

**面试题3：变量的作用域和生命周期有什么区别？**
```
作用域（Scope）= 我能看到它的范围（编译时的概念）
生命周期（Lifetime）= 它活着的时间（运行时的概念）

想象你在教室：
  作用域 = 我坐在第3排（我能看到第3排的同学）
  生命周期 = 同学从进教室到出教室的这段时间

Go例子：
func f() *int {
    x := 42  // 作用域：f函数内
    return &x  // x的生命周期：逃逸到堆上，直到没人用为止
}
```

**面试题4：new(int) 和 &int{} 返回的都是*int，有什么区别？**
```go
// new(int)：返回指向0的指针（只能做零值）
p1 := new(int)  // *int，指向0

// &int{}：Go 1.17+，也是指向0
p2 := &int{}  // *int，指向0

// 区别：&T{} 可以初始化非零值
// type Point struct { X, Y int }
p3 := &Point{X: 1, Y: 2}  // ✅ 不是零值
// p4 := new(Point)  // 只能得到 {0, 0}
```

**面试题5：包作用域和函数作用域的初始化顺序？**
```go
var a = b + c  // 3. a = 3
var b = f()    // 2. b = 2  
var c = 1      // 1. c = 1

func f() int { return c + 1 }

func init() {  // 4. init最后执行
    fmt.Println(a, b, c)  // 3 2 1
}

// 知识点：包级变量按"依赖顺序"初始化
// 不是按代码顺序！
```

**面试题6：Go的iota是什么？怎么用？**
```go
// iota = 在const块中从0开始自动递增的计数器

const (
    _  = iota             // 0（丢弃）
    KB = 1 << (10 * iota) // 1 << (10*1) = 1024
    MB                    // 1 << (10*2) = 1048576
    GB                    // 1 << (10*3) = 1073741824
)

// 也可以用在位运算：
const (
    Read  = 1 << iota  // 1
    Write              // 2
    Exec               // 4
    Admin              // 8
)
```

**面试题7：什么是逃逸分析（Escape Analysis）？**
```
逃逸分析 = 编译器决定变量是放在栈上还是堆上

栈（Stack）  = 自动整理，速度极快，
堆（Heap）   = 需要GC清理，速度稍慢

变量什么时候"逃逸"到堆上？
1. 返回局部变量的指针
2. 闭包中使用了外部变量
3. 变量太大（> 64KB）
4. 把值赋给了 interface{} 类型
5. 在 defer 中使用了变量

查看逃逸：go build -gcflags='-m' main.go
```

**面试题8：Go的初始化顺序（终极版）**
```
╔═══════════════════════════════════════╗
║          Go程序启动流程               ║
║ 1. 导入包的init（深度优先）           ║
║    ↓                                ║
║ 2. 包级常量初始化                    ║
║    ↓                                ║
║ 3. 包级变量初始化（按依赖顺序）       ║
║    ↓                                ║
║ 4. init()函数运行（按文件名字典序）   ║
║    ↓                                ║
║ 5. main()函数执行                   ║
╚═══════════════════════════════════════╝

例子：
// a.go
var X = Y + 1      // 第3步
var Y = 1          // 第2步
func init() { fmt.Print("A ") }  // 第4步

// b.go
func init() { fmt.Print("B ") }  // 第4步（b.go在a.go后面）
```

---

---

### ⚡ 2.10 Go作用域的完整图解（给初中生）

#### 作用域就像你的"可见范围"

```
想象你在学校的不同地方：

【宇宙作用域】= 全世界
  ├── 每个人都认识的东西（true, false, nil, int, string...）
  
【包作用域】= 你的班级
  ├── 班级里所有人都认识的同学
  
【函数作用域】= 你的小组
  ├── 小组里大家互相认识
  
【块作用域】= 你和同桌的秘密
  ├── 只有你们两个人知道
```

```go
package main

import "fmt"

var schoolName = "第一中学"  // 包作用域：全班都知道

func classOne() {
    className := "一班"     // 函数作用域：这个函数里的人知道
    
    if true {
        secret := "秘密"    // 块作用域：只有这个if块里的人知道
        fmt.Println(secret)  // ✅ 能看到
    }
    
    // fmt.Println(secret)  // ❌ 看不到！在if外面
    fmt.Println(className)   // ✅ 能看到（同一个函数）
    fmt.Println(schoolName)  // ✅ 能看到（同一个包）
}
```

#### 遮蔽（Shadowing）的完整图解

```go
var x = "我是包级x"  // 第1层：包作用域

func main() {
    fmt.Println(x)  // "我是包级x"
    
    x := "我是函数级x"  // 第2层：遮蔽包级x
    fmt.Println(x)    // "我是函数级x"
    
    if true {
        x := "我是块级x"  // 第3层：遮蔽函数级x
        fmt.Println(x)    // "我是块级x"
    }
    
    fmt.Println(x)  // "我是函数级x"（块级的不影响外面）
}
```

**遮蔽就是"里层挡住了外层"：**
```
包作用域  [x = "包级"]
  ↓ 看不到包级x了
函数作用域 [x = "函数级"]  ← 遮蔽了包级
  ↓ 看不到函数级x了  
块作用域   [x = "块级"]   ← 遮蔽了函数级
```

#### 作用域检查方法

```bash
# 安装遮蔽检查工具：
go install golang.org/x/tools/go/analysis/passes/shadow/cmd/shadow@latest
# 运行检查：
go vet -vettool=$(which shadow) ./...
# 会报告所有变量遮蔽的地方
```

---

### ⚡ 2.11 再补3道大厂面试题

**面试题9：Go包级变量的初始化顺序？**
```go
var a = b + 1   // 3. a = 3
var b = c + 1   // 2. b = 2
var c = 1       // 1. c = 1

// Go编译器按"依赖图"排序
// c没有依赖 → 最先初始化
// b依赖c → 然后初始化b
// a依赖b → 最后初始化a
```

**面试题10：Go的iota是什么？**
```go
// iota = "自动递增的计数器"
// 只在const块中有效

const (
    Monday = iota     // 0
    Tuesday           // 1（自动+1）
    Wednesday         // 2
    Thursday          // 3
    Friday            // 4
    Saturday          // 5
    Sunday            // 6
)

// 用iota定义二进制标志：
const (
    Read  = 1 << iota  // 1 << 0 = 1
    Write              // 1 << 1 = 2
    Exec               // 1 << 2 = 4
)
```

**面试题11：Go中哪些类型不可比较？**
```go
// 不可比较（不能使用 ==）：
// slice, map, function

var s1 = []int{1, 2}
var s2 = []int{1, 2}
// fmt.Println(s1 == s2)  // ❌ 编译错误！

// 可以用 reflect.DeepEqual
fmt.Println(reflect.DeepEqual(s1, s2))  // true
```

---

---

### ⚡ 2.12 泛型（Generics）——写一次，到处用

#### 为什么需要泛型？（给初中生）

```
没有泛型的世界：
  你想写一个"反转数组"的函数
  给int写一个：func ReverseInt(s []int) []int
  给string写一个：func ReverseStr(s []string) []string
  给float64写一个：func ReverseFloat(s []float64) []float64
  ...无穷无尽！

有泛型的世界：
  写一个反转函数，所有类型都能用
  func Reverse[T any](s []T) []T { ... }
  传int→给[]int反转
  传string→给[]string反转
```

#### 类型参数（Type Parameter）

```go
// [T any] = 类型参数列表
// T 是类型参数的名字
// any 是类型约束（T必须满足的条件）

func Reverse[T any](s []T) []T {
    result := make([]T, len(s))
    for i, v := range s {
        result[len(s)-1-i] = v
    }
    return result
}

// 使用：
ints := Reverse([]int{1, 2, 3})          // [3, 2, 1]
strs := Reverse([]string{"a", "b", "c"}) // ["c", "b", "a"]
```

#### any 和 comparable

```go
// any = 任何类型（是 interface{} 的别名）
func Print[T any](v T) { fmt.Println(v) }

// comparable = 可以用 == 比较的类型
func Find[T comparable](s []T, v T) int {
    for i, item := range s {
        if item == v { return i }  // == 要求 T 是 comparable
    }
    return -1
}
```

#### 类型约束（Constraint）

```go
// 自定义约束
// 用 interface 定义

type Number interface {
    ~int | ~int64 | ~float64  // ~表示底层类型
    // 比如 type MyInt int 也符合 ~int
}

func Sum[T Number](s []T) T {
    var sum T
    for _, v := range s {
        sum += v
    }
    return sum
}

// 使用：
type MyInt int
fmt.Println(Sum([]MyInt{1, 2, 3}))  // 6（MyInt的底层类型是int）
```

#### 为什么用 `~int` 而不是 `int`？

```go
// int：只有int本身符合
// ~int：底层类型是int的都符合（int, MyInt, MyScore...）

type MyInt int

// 如果约束是 int：MyInt 不符合
// 如果约束是 ~int：MyInt 符合（因为MyInt的底层类型是int）
```

---

---

### ⚡ 2.13 iota、nil、类型声明、短声明——完整用法大全

#### iota的完整用法大全（给初中生）

```go
// iota = "自动递增的计数器"
// 只在 const 块中有效

// 基本用法：
const (
    A = iota  // 0
    B        // 1
    C        // 2
)

// 跳过值：
const (
    _ = iota  // 0（丢弃）
    X         // 1
    Y         // 2
)

// 位运算标志（经典面试题）：
const (
    Read  = 1 << iota  // 1 << 0 = 1
    Write              // 1 << 1 = 2
    Exec               // 1 << 2 = 4
    Admin              // 1 << 3 = 8
)

// 字节单位：
const (
    _  = iota
    KB = 1 << (10 * iota)  // 1 << 10 = 1024
    MB                     // 1 << 20 = 1048576
    GB                     // 1 << 30 = 1073741824
)

// iota在每个const块中重置：
const (
    A = iota  // 0
    B        // 1
)
const (
    C = iota  // 0（重新从0开始！）
    D        // 1
)
```

#### nil用法大全

```go
// nil 在Go中有多重含义，取决于用在什么类型上

// 1. nil指针
var p *int = nil
fmt.Println(p == nil)  // true

// 2. nil切片
var s []int = nil
fmt.Println(s == nil)  // true
s = append(s, 1)        // nil切片可以append！

// 3. nil map
var m map[string]int = nil
// m["key"] = 1        // ❌ panic!
_ = m["key"]            // ✅ 读nil map返回零值
len(m)                   // ✅ 0
delete(m, "key")         // ✅ no-op

// 4. nil channel
var ch chan int = nil
// ch <- 1              // ❌ 永远阻塞
// <-ch                 // ❌ 永远阻塞

// 5. nil函数
var fn func() = nil
// fn()                 // ❌ panic!
fn = func() { fmt.Println("hi") }
fn()                     // ✅ hi

// 6. nil接口
var iface interface{} = nil
fmt.Println(iface == nil)  // true

// 但注意：存了nil指针的接口不是nil！
var buf *bytes.Buffer = nil
iface = buf
fmt.Println(iface == nil)  // false！经典面试陷阱
```

#### 类型声明详解

```go
// Go有5种声明，类型声明是其中之一

// 1. 新类型（type NewType OldType）
type Celsius float64  // 创建一个新类型
var c Celsius = 100.0
// float64(c)  // 需要显式转换

// 2. 类型别名（type Alias = OldType）
type MyInt = int  // MyInt和int是同一类型
var x MyInt = 42
var y int = x     // ✅ 不需要转换！

// 3. 结构体类型
type Person struct {
    Name string
    Age  int
}

// 4. 接口类型
type Writer interface {
    Write([]byte) (int, error)
}

// 5. 函数类型
type Handler func(http.ResponseWriter, *http.Request)

// 6. map/slice/channel类型
type IntSlice []int
type StringMap map[string]string
type DoneChan chan struct{}
```

#### 短变量声明规则（必考面试题）

```go
// 规则1：至少有一个新变量
x := 10      // ✅ x是新变量
x, y := 20, 30  // ✅ x已有（赋值），y是新变量
// x := 30    // ❌ 编译错误：左边没有新变量

// 规则2：只能在函数内部使用
var a = 10    // ✅ 包级别
// b := 20    // ❌ 包级别不能使用:=

// 规则3：短声明的变量类型由初始化值决定
name := "Alice"  // string
count := 42       // int
pi := 3.14       // float64

// 规则4：短声明可以和函数返回值配合
f, err := os.Open("file.txt")
// f 是 *os.File, err 是 error

// 规则5：短声明在多重赋值中有特殊行为
// 如果:=左边有多个变量，只要至少一个是新变量，其他可以是已存在的

x := 1
y := 2
x, z := 3, 4  // x被重新赋值（已存在），z是新变量
```

---

---

### ⚡ 2.14 内存对齐——给初中生的超级详解

#### 什么是内存对齐？

```
CPU读取内存时，一次读8字节（64位系统）
就像你一次搬8块砖

如果int64在地址0：
  一次读0~7 → 拿到全部8字节  ✅ 快！

如果int64在地址3：
  第一次读0~7 → 得到前5字节
  第二次读8~15 → 得到后3字节
  拼在一起 → 慢！多读了一次

内存对齐 = 把数据放到"合适"的地址
  保证CPU一次就能读完
  不用分两次读
```

#### 各类型的对齐要求

```go
type T struct {
    a bool    // 对齐1字节（可以放任何地址）
    b int32   // 对齐4字节（地址必须是4的倍数）
    c int64   // 对齐8字节（地址必须是8的倍数）
}

// 实际内存布局：
// 偏移0:  a (1字节)
// 偏移1~3: 填充（padding，为了让b对齐到4）
// 偏移4~7:  b (4字节)
// 偏移8~15: c (8字节)
// 总大小: 16字节（不是1+4+8=13！有3字节填充）

fmt.Println(unsafe.Sizeof(T{}))    // 16
fmt.Println(unsafe.Alignof(T{}))   // 8（最大字段的对齐）
fmt.Println(unsafe.Offsetof(T{}.b)) // 4（b的偏移）
```

#### 优化结构体字段顺序节省内存

```go
// ❌ 不好：16字节
type Bad struct {
    a bool    // 1 + 3填充
    b int32   // 4
    c bool    // 1 + 7填充（因为int64对齐到8）
}

// ✅ 好：12字节（省4字节）
type Good struct {
    b int32   // 4
    a bool    // 1
    c bool    // 1 + 2填充
}

// 如果是100万个这样的结构体：
// Bad: 16MB
// Good: 12MB
// 省了4MB！
```

**对齐规则总结：**
```
1. 每个字段的起始地址必须是对齐值的倍数
2. 结构体总大小必须是最大对齐值的倍数
3. 把大字段放前面可以节省填充
4. unsafe.Alignof(T)返回T类型的对齐值
5. unsafe.Offsetof(T.f)返回字段f的偏移量
```

**面试题：下面这个结构体占多少字节？**
```go
type Example struct {
    a int32    // 4字节
    b bool     // 1字节
    c string   // 16字节
}
// 思考过程：
// a: 偏移0（4字节对齐）
// b: 偏移4（1字节对齐）
// c: 偏移8（8字节对齐？不对，string对齐是8字节）
// 但b占据了偏移4~5，从偏移5开始有3个填充到偏移8
// c: 偏移8~23
// 总大小: 24字节
```

---

---

### ⚡ 2.15 变量、类型、包和作用域的纳米级图解

#### 变量的完整生命周期图

```
         var x = 42
            │
            ▼
    ┌──────────────────────┐
    │ 编译阶段：            │
    │ 逃逸分析决定放哪     │
    └──────────┬───────────┘
               │
         ╭─────┴────────╮
       栈↓              ↓堆
         │              │
    ┌────┴────┐   ┌────┴──────────┐
    │ x在栈上  │   │ x在堆上       │
    │ 函数返回  │   │ GC管理生命周期  │
    │ 自动回收  │   │ 没人引用时回收  │
    └─────────┘   └───────────────┘

什么情况放栈？                              什么情况放堆？
  ✅ 局部变量，不返回指针                        ❌ 返回指针 &x
  ✅ 小变量（< 64KB）                          ❌ 闭包捕获 x
  ✅ 大小编译时可知                            ❌ 变量太大
  ✅ 不逃逸（不被函数外使用）                    ❌ 赋给 interface{}
```

#### 变量声明形式完整对照图

```
四种声明方式对比

┌──────────────────────────────────────────────────────────────────┐
│ 方式1：var name type = value（完整声明）                         │
│   var name string = "Alice"                                     │
│   适用所有地方：包级别、函数内                                   │
│   明确指定类型，可读性最好                                       │
├──────────────────────────────────────────────────────────────────┤
│ 方式2：var name = value（类型推断）                              │
│   var name = "Alice"  → string                                  │
│   适用所有地方                                                   │
│   类型由初始化值决定                                              │
├──────────────────────────────────────────────────────────────────┤
│ 方式3：name := value（短声明）                                   │
│   name := "Alice"                                               │
│   ❌ 只能在函数内使用                                            │
│   最简洁                                                       │
├──────────────────────────────────────────────────────────────────┤
│ 方式4：分组声明 var (...)                                       │
│   var (                                                         │
│       name = "Alice"                                            │
│       age  = 18                                                 │
│   )                                                             │
│   适用于多个相关的包级变量                                        │
└──────────────────────────────────────────────────────────────────┘
```

#### 包导入的完整查找流程图

```
         import "fmt"
              │
              ▼
    ┌─────────────────────┐
    │ 检查GOROOT/src/fmt   │ ← 标准库优先
    └──────────┬──────────┘
               │
               找到→用标准库
               │
               没找到→
               ▼
    ┌─────────────────────┐
    │ 检查vendor/fmt       │ ← 项目vendor目录
    └──────────┬──────────┘
               │
               找到→用vendor的
               │
               没找到→
               ▼
    ┌─────────────────────┐
    │ 检查module cache     │ ← GOPATH/pkg/mod
    └──────────┬──────────┘
               │
               找到→用缓存
               │
               没找到→
               ▼
    ┌─────────────────────┐
    │ 从GOPROXY下载        │ ← 最后尝试
    └─────────────────────┘
```

#### init() 函数的执行顺序图

```
程序启动
   │
   ▼
┌──────────────────────┐
│ 1. 导入的包递归初始化  │
│    ├── 包A的init()     │
│    ├── 包B的init()     │
│    └── 按导入顺序      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. 当前包的常量初始化  │
│    const a = 1       │
│    const b = a + 1   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. 当前包变量初始化    │
│    （按依赖顺序）      │
│    var c = d + 1      │
│    var d = 1          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 4. init()函数执行     │
│    （按文件名字典序）   │
│    a.go的init先执行    │
│    b.go的init后执行    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 5. 如果包是main       │
│    → 执行main()      │
│    如果不是main       │
│    → 初始化完成       │
└──────────────────────┘
```

#### 作用域遮蔽层次图

```
                宇宙作用域
      ┌──────────────────────────┐
      │ int, string, true, nil.. │
      └────────────┬─────────────┘
                    │ 被遮蔽
                    ▼
                包作用域
      ┌──────────────────────────┐
      │ var x = "包级"          │
      └────────────┬─────────────┘
                    │ 被遮蔽
                    ▼
                函数作用域
      ┌──────────────────────────┐
      │ x := "函数级"            │
      └────────────┬─────────────┘
                    │ 被遮蔽
                    ▼
                if/for块作用域
      ┌──────────────────────────┐
      │ x := "块级"             │
      └──────────────────────────┘

嵌套多层时，里层的变量"遮住"外层的同名变量
就像你前面的同学挡住你看黑板
```

#### 变量声明 vs 短声明选择图

```
要声明变量
    │
    ▼
┌─────────────────────┐
│ 在包级别（函数外）？ │
└──────────┬──────────┘
      是↓  │  ↓否
         │ │
   ┌─────┴─┴──────┐
   │ 用 var       │
   └──────┬──────┘
          │
          ▼
┌──────────────────────────┐
│ 需要明确指定类型？        │
└──────────┬───────────────┘
      是↓  │  ↓否
         │ │
   ┌─────┴─┴──────┐
   │ var x int = 42│
   └──────────────┘
          │
          ▼
┌──────────────────────────┐
│ 简洁优先？                │
└──────────┬───────────────┘
      是↓
         │
   ┌─────┴──────────┐
   │ x := 42         │
   └────────────────┘
```

---

---

### ⚡ 2.16 作用域和声明的纳米级图解

#### 嵌套作用域的查找规则图

```
当代码中引用一个变量时，Go按以下顺序查找：

                   查找变量名 "x"
                        │
                        ▼
              ┌──────────────────┐
              │ 最内层代码块      │  ← 先找这里
              │ （{}里面的）      │
              └────────┬─────────┘
                       │
                  找到↓│  ↓没找到
                       │ │
                  ┌────┴─┴──────┐
                  │ 外层代码块   │
                  │ （函数级）    │
                  └────┬─────────┘
                       │
                  找到↓│  ↓没找到
                       │ │
                  ┌────┴─┴──────┐
                  │ 包作用域     │
                  │ （全局）     │
                  └────┬─────────┘
                       │
                  找到↓│  ↓没找到
                       │ │
                  ┌────┴─┴──────────┐
                  │ 宇宙作用域       │
                  │ （预定义类型）    │
                  └─────────────────┘
                       │
                       ▼
              如果还没找到 → 编译错误！

就像你在学校里找人：
  先看自己座位上 → 没有
  再看自己班级 → 没有
  再看全校 → 没有
  → 查无此人（编译错误）
```

#### 变量的声明位置和使用范围图

```
包级别变量（var在函数外声明）：
┌────────────────────────────────────────────┐
│ package main                                │
│                                             │
│ var version = "1.0"  ← 包内所有函数都能访问  │
│ var debug = false    ← 全局变量             │
│                                             │
│ func main() {                               │
│     fmt.Println(version)  ← ✅ 能访问       │
│ }                                            │
│                                             │
│ func helper() {                             │
│     fmt.Println(debug)    ← ✅ 也能访问      │
│ }                                            │
└────────────────────────────────────────────┘

函数级别变量（var/:=在函数内）：
┌────────────────────────────────────────────┐
│ func outer() {                              │
│     x := 10         ← 只在outer里有效       │
│     if x > 0 {                              │
│         y := 20     ← 只在if块里有效        │
│         fmt.Println(x, y)  ← ✅             │
│     }                                       │
│     fmt.Println(x)    ← ✅                  │
│     // fmt.Println(y) ← ❌ y不在这里！      │
│ }                                            │
└────────────────────────────────────────────┘
```

#### 类型转换的完整规则图

```
var i int = 42
var f float64

f = i                     ← ❌ 编译错误！不同类型
f = float64(i)            ← ✅ 显式转换

i = int(f)                ← ✅ 显式转换（可能丢失小数）


数值类型之间的转换规则：
┌──────────┐     ┌──────────┐
│  int32   │────→│  int64   │  ✅ 小→大，安全
└──────────┘     └──────────┘

┌──────────┐     ┌──────────┐
│  int64   │────→│  int32   │  ⚠️ 大→小，可能溢出
└──────────┘     └──────────┘

┌──────────┐     ┌──────────┐
│  int     │────→│ float64  │  ⚠️ 可能精度丢失（大整数）
└──────────┘     └──────────┘

┌──────────┐     ┌──────────┐
│ float64  │────→│  int     │  ⚠️ 丢失小数部分
└──────────┘     └──────────┘

┌──────────┐     ┌──────────┐
│  string  │────→│  int     │  ❌ 不能！必须用strconv
└──────────┘     └──────────┘
```

#### const声明完整分类图

```
const 声明
    │
    ├── 无类型常量（可以给任何兼容类型赋值）
    │     const Pi = 3.14159
    │     var f32 float32 = Pi  ← ✅ 自动转换
    │     var f64 float64 = Pi  ← ✅ 自动转换
    │
    ├── 有类型常量（只能给特定类型赋值）
    │     const Port int = 8080
    │     // var x int32 = Port  ← ❌ 类型不匹配
    │
    └── iota枚举生成器
          const (
              A = iota   // 0
              B          // 1——自动递增
              C          // 2
          )

无类型常量的好处：
  const Big = 1 << 100  ← 编译期精确值
  // 虽然int放不下1<<100
  // 但const保留精确值
  // 赋给float64时再转换
```

#### Go程序启动到结束的完整流程图

```
          操作系统执行程序
                │
                ▼
      ┌────────────────────┐
      │ 运行时初始化         │
      │ 创建main goroutine  │
      │ 分配栈(2KB)        │
      └──────────┬─────────┘
                │
                ▼
      ┌────────────────────┐
      │ 导入包递归初始化    │
      │ ├── 包A的init()    │
      │ ├── 包B的init()    │
      │ └── ...           │
      └──────────┬─────────┘
                │
                ▼
      ┌────────────────────┐
      │ 当前包的变量初始化  │
      │（按依赖顺序）      │
      └──────────┬─────────┘
                │
                ▼
      ┌────────────────────┐
      │ init()函数执行     │
      │（按文件名字典序）   │
      └──────────┬─────────┘
                │
                ▼
      ┌────────────────────┐
      │ main()函数开始执行  │
      └──────────┬─────────┘
                │
                ▼
      ┌────────────────────┐
      │ main()返回         │
      │ 所有goroutine结束  │
      │ 程序退出           │
      └────────────────────┘
```

---

---

### ⚡ 2.17 大厂面试题扩展（程序结构篇·10道）

**面试题1：var和:=声明变量有什么区别？**
```
var：可以声明在任何地方（包级别+函数内）
  :=：只能在函数内使用
  var：可以不初始化（使用零值）
  :=：必须初始化
  var：可以显式指定类型
  :=：只能类型推断

包级别：只能用var
函数内：优先用:=
```

**面试题2：什么是变量遮蔽（Variable Shadowing）？**
```go
var x = 10  // 包级变量

func main() {
    x := 20  // 遮蔽了包级x
    fmt.Println(x)  // 20
    
    if true {
        x := 30  // 遮蔽了函数级x
        fmt.Println(x)  // 30（在if块里）
    }
    
    fmt.Println(x)  // 20（函数级x，没被if影响）
}
```

**面试题3：new(T)和&T{}有什么区别？**
```go
// new(T)：只能得到零值
p1 := new(int)  // *int → 0
p2 := new(Person)  // *Person → {Name:"", Age:0}

// &T{}：可以指定字段值
p3 := &Person{Name: "Alice"}  // Name="Alice", Age=0

// 对于简单类型，Go 1.17+支持&T{}
p4 := &int(42)  // *int → 42（Go 1.26+用new(int(42))）
```

**面试题4：Go有枚举类型吗？怎么实现枚举？**
```go
// Go没有专门的enum关键字
// 用const + iota实现

type Color int

const (
    Red Color = iota  // 0
    Green             // 1
    Blue              // 2
)

func (c Color) String() string {
    return [...]string{"红色","绿色","蓝色"}[c]
}

fmt.Println(Red)  // 红色
```

**面试题5：iota在同一个const块里怎么重置？**
```go
// iota在每个const块里从0开始

const (
    A = iota  // 0
    B        // 1
    C        // 2
)

const (
    D = iota  // 0（重新开始！）
    E        // 1
)

// 实用的位运算枚举：
const (
    Read  = 1 << iota  // 1
    Write              // 2
    Exec               // 4
    Admin              // 8
)
```

**面试题6：包级变量的初始化顺序是什么样的？**
```go
var a = b + c  // 3. a=3（最后）
var b = f()    // 2. b=2
var c = 1      // 1. c=1（最先，因为没依赖）

func f() int { return c + 1 }

// 编译器按依赖图排序
// c没有依赖 → 最先
// b依赖c → 然后b
// a依赖b → 最后a
```

**面试题7：init函数有什么用？可以有几个？**
```go
// init在main之前执行
// 每个文件可以有多个init
// 不能手动调用

func init() { fmt.Print("A ") }
func init() { fmt.Print("B ") }

func main() { fmt.Println("main") }
// 输出：A B main

// init的使用场景：
// 1. 注册插件/数据库驱动
// 2. 初始化全局状态
// 3. 解析配置文件
```

**面试题8：循环导入（import cycle）怎么解决？**
```go
// 错误：a → b → a（循环依赖）
package a
import "b"

package b
import "a"  // ❌ 编译错误！

// 解决方案：
// 1. 提取公共接口到第三个包c
// 2. 把双向依赖改为单向
// 3. 使用回调函数
package a
var OnEvent func()

package b
import "a"
func init() {
    a.OnEvent = func() { /* 处理 */ }
}
```

**面试题9：Go中哪些类型可以做map的key？**
```
可以（可用==比较）：
  bool, 整数, 浮点数, string, 指针, channel
  只包含可比较字段的结构体
  只包含可比较元素的数组

不可以：
  slice ❌
  map ❌
  function ❌
  （因为不能使用 == 比较）
```

**面试题10：逃逸分析是什么？怎么查看？**
```
逃逸分析 = 编译器决定变量放栈还是堆

查看逃逸：
  go build -gcflags='-m' main.go

什么情况会逃逸到堆：
  1. 返回局部变量指针：return &x
  2. 闭包捕获外部变量：func() { x++ }
  3. 变量太大：> 64KB
  4. 赋给interface{}：fmt.Println(x)

逃逸到堆的代价：
  需要GC回收，性能比栈低
```

---

> **下一章**：[第3章 基础数据类型](./ch03-basic-types.md) —— 深入Go的整型、浮点数、复数、布尔、字符串和常量系统。

---

### 🔬 2.18 底层原理：Go程序在内存里长什么样？

#### 编译后的exe文件结构

```
你写的Go代码 → go build → 可执行文件（exe）

一个可执行文件由多个"段"（Segment/Section）组成：

┌──────────────────────────────────┐
│ 可执行文件头部（Header）          │
│ ├── 入口地址（从哪里开始执行）     │
│ ├── 段表（有哪些段、在哪）        │
│ └── 平台信息（Windows/Linux/Mac） │
├──────────────────────────────────┤
│ 代码段（.text）    ← 你的函数指令  │
│ 只读！不能改！                    │
├──────────────────────────────────┤
│ 数据段（.data）    ← 全局变量     │
│ ├── 初始化了的全局变量            │
│ └── var x = 42 存在这里          │
├──────────────────────────────────┤
│ BSS段（.bss）      ← 零值全局变量  │
│ ├── var y int （=0）存在这里      │
│ └── 不占文件空间，运行时分配       │
├──────────────────────────────────┤
│ 只读数据段（.rodata） ← 常量      │
│ ├── const msg = "hello"          │
│ └── 字符串字面量                  │
├──────────────────────────────────┤
│ 其他段：调试信息、符号表...        │
└──────────────────────────────────┘
```

#### 程序加载到内存的过程

```
你在终端输入：./myprogram
              │
              ▼
     ┌────────────────────────┐
     │ 1. Shell调用操作系统    │
     │    exec()系统调用       │
     └──────────┬─────────────┘
                │
                ▼
     ┌────────────────────────┐
     │ 2. 加载器（Loader）分析  │
     │    exe文件格式          │
     │    读取段表             │
     └──────────┬─────────────┘
                │
                ▼
     ┌────────────────────────┐
     │ 3. 分配虚拟内存空间      │
     │    把各段加载到内存      │
     │    代码段→代码区        │
     │    数据段→数据区        │
     │    BSS段→零初始化       │
     └──────────┬─────────────┘
                │
                ▼
     ┌────────────────────────┐
     │ 4. 动态链接（如果有的话）│
     │    解析符号：fmt.Println │
     │    指向标准库代码        │
     └──────────┬─────────────┘
                │
                ▼
     ┌────────────────────────┐
     │ 5. 跳转到入口地址       │
     │    _rt0_amd64_linux   │
     │    → runtime初始化     │
     │    → main goroutine   │
     │    → 你的main()       │
     └────────────────────────┘
```

#### 符号表和链接——你的程序怎么找到fmt.Println的？

```
当你写 import "fmt" 时：

你的代码里有 fmt.Println
但fmt.Println的代码不在你的exe里（初始阶段）

符号表（Symbol Table） → "谁在哪里的地图"
┌───────────────────────────────┐
│ 符号名         地址            │
├───────────────────────────────┤
│ main          0x1234          │ ← 你自己写的
│ fmt.Println   0x?（未知）      │ ← 需要链接才知道
│ runtime.main  0x?（未知）      │
└───────────────────────────────┘

链接器（Linker）的工作：
  1. 找到fmt包的代码（从标准库或go.mod）
  2. 把fmt.Println的地址填進符号表
  3. 把所有需要的代码拼成一个大文件

Go是静态链接：
  所有代码（包括标准库）都打包到exe里
  → exe比较大（~10MB）
  → 到哪都能跑

C可以是动态链接：
  exe里只记"谁在哪"，运行时才找dll
  → exe比较小（~100KB）
  → 换了系统可能找不到dll
```

#### 变量存在内存的哪个区？

```
Go程序运行时，内存分成多个区域：

┌──────────────────────┐ ← 高地址
│       栈（Stack）      │
│ goroutine的调用栈     │
│ 存局部变量、函数参数  │
│ 自动增长（2KB→最大1GB）│
├──────────────────────┤
│         ↕            │
├──────────────────────┤
│       堆（Heap）      │
│ new/make出来的对象    │
│ GC管理生命周期        │
│ 存逃逸的变量          │
├──────────────────────┤
│       数据段          │
│ 全局变量              │
│ 初始化过的→.data       │
│ 零值的→.bss           │
├──────────────────────┤
│       代码段          │
│ 你的函数指令          │
│ fmt.Println的指令     │
│ runtime的指令         │
│ 只读！                │
├──────────────────────┤
│       常量区          │
│ 字符串字面量           │
│ const常量值           │
│ 只读！                │
└──────────────────────┘ ← 低地址

变量存哪里取决于：
  1. 全局变量 → 数据段
  2. 局部变量（不逃逸）→ 栈
  3. new/逃逸 → 堆
  4. 常量/字符串字面量 → 只读区
```

#### BSS段为什么不需要在文件里占空间？

```
代码段：需要有指令（占文件空间）
数据段：需要有初始值（占文件空间）
  var x = 42  → 文件里存着"42"

BSS段：初始值都是0
  var y int   → 就是0，不需要存
  操作系统加载时：分配一块全是0的内存

就像：
  你订了一批教材（数据段已经有内容了）
  还要一批空白练习本（BSS段）
  练习本都是空白的，
  不需要提前写好"空白"两个字——本来就是空白
```

---

> **下一章**：[第3章 基础数据类型](./ch03-basic-types.md) —— 深入Go的整型、浮点数、复数、布尔、字符串和常量系统。
