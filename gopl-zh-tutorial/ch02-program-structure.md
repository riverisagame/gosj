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

> **下一章**：[第3章 基础数据类型](./ch03-basic-types.md) —— 深入Go的整型、浮点数、复数、布尔、字符串和常量系统。
