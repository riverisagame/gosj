# 第3章 基础数据类型

> Go语言提供丰富的基础数据类型：整数（有符号/无符号/特殊类型）、浮点数、复数、布尔、字符串和常量。理解它们的底层表示、边界行为和性能特性是写出正确高效Go代码的前提。

---

## 目录

- [3.1 整型](#31-整型)
- [3.2 浮点数](#32-浮点数)
- [3.3 复数](#33-复数)
- [3.4 布尔型](#34-布尔型)
- [3.5 字符串](#35-字符串)
- [3.6 常量](#36-常量)

---

## 3.1 整型

### Go的整型体系

```
有符号（补码表示）：
  int8    (-128 ~ 127)
  int16   (-32,768 ~ 32,767)
  int32   (-2,147,483,648 ~ 2,147,483,647)
  int64   (-9,223,372,036,854,775,808 ~ 9,223,372,036,854,775,807)
  int     (32位系统=32bit，64位系统=64bit)

无符号：
  uint8   (0 ~ 255)
  uint16  (0 ~ 65,535)
  uint32  (0 ~ 4,294,967,295)
  uint64  (0 ~ 18,446,744,073,709,551,615)
  uint    (32位系统=32bit，64位系统=64bit)

特殊：
  rune    = int32（Unicode码点）
  byte    = uint8（原始字节）
  uintptr （足够保存指针的整数，用于unsafe包）
```

### 运算符

```go
// 算术：+ - * / %（取模，仅整数）
// 比较：== != < <= > >
// 位运算：& | ^ &^ << >>
// 赋值：= += -= *= /= %= &= |= ^= <<= >>=
```

### 位运算详解

```go
&   // 按位与（AND）
|   // 按位或（OR）
^   // 按位异或（XOR，一元时取反）
&^  // 位清除（AND NOT）：a&^b = a & (^b)
<<  // 左移
>>  // 右移（无符号逻辑右移，有符号算术右移）
```

### 类型转换

```go
var a int32 = 1000
var b int8 = int8(a)  // 截断：高位丢失
// b = -24 (二进制: 0b11111000)

// 算术运算要求相同类型
var x int32 = 10
var y int64 = 20
// fmt.Println(x + y)  // ❌ 编译错误：类型不匹配
fmt.Println(int64(x) + y)  // ✅ 显式转换
```

### 🔥 面试扩展

**高频题1：`int`和`int64`在64位系统上是同一类型吗？**
> **不是。** `int`是平台相关的别名（64位系统上`int`是64bit，但和`int64`是不同的类型）。需要`int64`的地方不能直接传`int`，必须显式转换。

**高频题2：有符号整数溢出的行为？**
> Go中**有符号整数溢出是已定义的环绕行为**（Two's complement wrap-around），但Go编译器不会报错也不会panic。如果关心溢出，用`math.MaxInt`/`math.MinInt`检查或使用`math/bits`包。

**高频题3：`byte`和`rune`的本质区别？**
> - `byte = uint8`：一个字节，用于原始数据/ASCII字符
> - `rune = int32`：一个Unicode码点，用于Unicode文本处理
> ```go
> s := "Hello, 世界"
> fmt.Println(len(s))             // 13 (UTF-8字节数)
> fmt.Println(len([]rune(s)))     // 9 (字符数)
> fmt.Println(len([]byte(s)))     // 13
> ```

**高频题4：`a&^b`位清除操作的数学意义？**
> `a &^ b` = `a & (^b)`，清除a中对应b为1的位。常用于位标志操作：
```go
const (
    Read  = 1 << iota  // 1
    Write              // 2
    Exec               // 4
)
perm := Read | Write  // 3
perm &^= Write        // 清除Write位，perm = 1 (Read only)
```

**高频题5：Go为什么不支持隐式整数提升（如C语言的int提升）？**
> 为了防止精度丢失和跨平台不一致。C语言中`short + int`会自动提升，但在不同平台表现不同。Go要求开发者显式处理类型转换，确保行为明确。

---

## 3.2 浮点数

### 两种浮点类型

| 类型 | 位数 | 精度 | 最大值 |
|------|------|------|--------|
| `float32` | 32bit | ≈6位小数 | 3.4e38 |
| `float64` | 64bit | ≈15位小数 | 1.8e308 |

### 特殊值

```go
var z float64
fmt.Println(z, -z, 1/z, -1/z, z/z)
// 输出: 0 -0 +Inf -Inf NaN
```

### 浮点数陷阱

```go
// ❌ 不要用==比较浮点数
fmt.Println(0.1 + 0.2 == 0.3)  // false!

// ✅ 用epsilon比较
const epsilon = 1e-9
fmt.Println(math.Abs((0.1+0.2)-0.3) < epsilon)  // true
```

### NaN的特性

```go
nan := math.NaN()
fmt.Println(nan == nan)  // false！NaN不等于自身
fmt.Println(nan < nan)   // false
fmt.Println(nan > nan)   // false
```

### 🔥 面试扩展

**高频题1：为什么`0.1 + 0.2 != 0.3`？**
> 因为0.1和0.2在二进制浮点数中无法精确表示（类似十进制无法精确表示1/3）。IEEE 754的表示误差导致求和结果略小于0.3。

**高频题2：如何格式化浮点数输出？**
```go
fmt.Printf("%f\n", math.Pi)     // 3.141593（默认6位）
fmt.Printf("%.2f\n", math.Pi)  // 3.14
fmt.Printf("%e\n", math.Pi)    // 3.141593e+00（科学计数法）
fmt.Printf("%g\n", math.Pi)    // 3.141592653589793（根据情况选择格式）
```

**高频题3：为什么Go推荐默认使用`float64`？**
> `float32`的精度（~7位有效数字）在很多场景不够用，累加误差快速累积。`float64`提供~15位有效数字，内存开销从4字节增加到8字节，但对大多数应用可接受。只有内存或带宽极度敏感时（如图形处理、大规模数据），才会选`float32`。

**高频题4：NaN的比较特性在Go中可能造成哪些坑？**
> `NaN != NaN`意味着map以NaN做key时会永远找不到；`if x != x`是检测NaN的技巧。序列化/反序列化时NaN可能"变"成其他值（如JSON不支持NaN）。

---

## 3.3 复数

### 两种复数类型

```go
var x complex64   = 1 + 2i   // float32实部和虚部
var y complex128 = 3 + 4i    // float64实部和虚部

// 构造复数
var z = complex(5, 6)  // 5+6i
real(z)  // 5.0
imag(z)  // 6.0
```

### 复数的应用

```go
// 复数运算
a := 1 + 2i
b := 3 + 4i
fmt.Println(a + b)  // (4+6i)
fmt.Println(a * b)  // (-5+10i)
```

### 🔥 面试扩展

**高频题1：Go的复数在什么场景下使用最合适？**
> 信号处理（FFT）、分形图形（Mandelbrot集）、量子力学模拟。日常业务开发极少用到，但Go标准库内置复数支持，体现了Go在科学计算领域的考虑。

**高频题2：复数可以和普通数值混用吗？**
> 不能。`1 + 2i`是复数字面量，不是整数1+虚数2i。`complex64`和`float32`之间的类型转换必须显式进行。

---

## 3.4 布尔型

### bool

```go
var a bool = true
var b bool = false

// 短路求值
if a && b { /* 如果a为false，b不会被计算 */ }
if a || b { /* 如果a为true，b不会被计算 */ }
```

### 🔥 面试扩展

**高频题1：Go中bool和int不能互转的意义？**
> C语言中`if (x = 1)`是常见bug，因为赋值表达式的值（1）被当做true。Go强制bool类型，`if x = 1 {`编译错误，杜绝了此类问题。

**高频题2：如何将bool转为string？**
```go
s := strconv.FormatBool(true)     // "true"
b, _ := strconv.ParseBool("true") // true
```

---

## 3.5 字符串

### 字符串的本质

Go字符串是**不可变的字节序列**，底层是一个结构体：

```go
type stringStruct struct {
    str unsafe.Pointer  // 指向底层字节数组的指针
    len int             // 字节长度
}
```

### 字符串操作

```go
s := "hello, 世界"

// 长度（字节数，不是字符数）
len(s)          // 13

// 索引（取字节，不是字符）
s[0]            // 'h' (104)
s[7]            // 第一个字节 of '世'

// 切片（产生新字符串，共享底层）
s[0:5]          // "hello"
s[:5]           // "hello"
s[7:]           // "世界"

// 字符串拼接
"hello" + ", " + "world"
strings.Join([]string{"hello", "world"}, ", ")

// 高效拼接
var b strings.Builder
b.WriteString("hello")
b.WriteString(", ")
b.WriteString("world")
b.String()  // "hello, world"
```

### 字符串和UTF-8

```go
s := "Hello, 世界"

// 遍历字节
for i := 0; i < len(s); i++ {
    fmt.Printf("%x ", s[i])
}
// 48 65 6c 6c 6f 2c 20 e4 b8 96 e7 95 8c

// 遍历rune（Unicode码点）
for i, r := range s {
    fmt.Printf("%d\t%q\t%x\n", i, r, r)
}
// 0       'H'     48
// 1       'e'     65
// ...
// 7       '世'    4e16
// 10      '界'    754c
```

### Unicode/UTF-8/rune关系

```
Unicode: 字符集，每个字符一个码点（code point）
UTF-8:   变长编码方案（1-4字节），Go源码默认编码
rune:    Go类型（int32别名），表示一个Unicode码点
```

### strings包常用函数

```go
strings.Contains(s, substr)
strings.Count(s, substr)
strings.HasPrefix(s, prefix)
strings.HasSuffix(s, suffix)
strings.Index(s, substr)
strings.Join([]string, sep)
strings.Replace(s, old, new, n)
strings.Split(s, sep)
strings.ToLower(s)
strings.ToUpper(s)
strings.Trim(s, cutset)
strings.Fields(s)       // 按空白字符分割
```

### strconv包

```go
strconv.Itoa(42)              // "42"
strconv.Atoi("42")            // 42, nil
strconv.FormatInt(42, 16)     // "2a"
strconv.ParseInt("2a", 16, 0) // 42, nil
strconv.FormatFloat(3.14, 'f', 2, 64)
strconv.ParseFloat("3.14", 64)
```

### 🔥 面试扩展

**高频题1：Go字符串为什么是不可变的？**
> 不可变性带来以下好处：
> 1. **安全**：多个变量可安全共享底层字节数组，不会相互影响
> 2. **高效**：子串切片操作（`s[1:5]`）不用复制，直接指向原内存
> 3. **map key**：只有不可变类型才能作为map的key
> 4. **并发安全**：多个goroutine可安全读取同一个字符串

**高频题2：字符串拼接的性能对比**

| 方法 | 性能 | 适用场景 |
|------|------|----------|
| `+` | 最慢（O(n²)） | 少量拼接 |
| `fmt.Sprintf` | 中 | 格式化拼接 |
| `strings.Join` | 快（O(n)） | 已知切片 |
| `strings.Builder` | 最快 | 大量动态拼接 |
| `bytes.Buffer` | 快 | 类似Builder |

**高频题3：`range`遍历字符串时为什么返回`rune`而非`byte`？**
> Go设计者认为遍历字符串最常见需求是处理每个字符（rune），而非每个字节。`for i, r := range s`自动解码UTF-8序列。如果非法UTF-8序列，`r`返回`\uFFFD`（替换字符）。

**高频题4：`[]byte(s)`和`[]rune(s)`转换的内存开销？**
> - `[]byte(s)`：**共享底层数据**（不复制），零开销
> - `[]rune(s)`：**必须解码每个UTF-8序列为新数组**，O(n)时间和内存
> - `string([]rune(runes))`：同样必须编码

**高频题5：如何高效地修改字符串中的字符？**
```go
// 方法1：转[]byte修改后转回string
b := []byte(s)
b[0] = 'H'
s = string(b)

// 方法2：使用strings.Builder
var sb strings.Builder
sb.WriteString(s[:i])
sb.WriteRune(newChar)
sb.WriteString(s[i+1:])
```

**高频题6：什么是字符串的内部布局，为什么取地址不能直接修改？**
> 字符串结构体`reflect.StringHeader`包含`Data`（*byte指针）和`Len`（int）。虽然可以拿到底层字节数组的指针，但Go编译器禁止通过常规方式修改`string`（被声明为immutable）。如果通过`unsafe`绕过，会产生未定义行为，因为字符串可能存在于只读内存段或与其他字符串共享。

---

## 3.6 常量

### 常量声明

```go
// 单常量
const pi = 3.14159
const e float64 = 2.71828  // 指定类型

// 多常量
const (
    a = 1
    b = 2
    c = 3
)

// 隐式重复
const (
    a = 1
    b          // = 1（隐式重复上一个表达式）
    c          // = 1
)
```

### iota常量生成器

```go
const (
    Monday = iota        // 0
    Tuesday              // 1
    Wednesday            // 2
    Thursday             // 3
    Friday               // 4
    Saturday             // 5
    Sunday               // 6
)

// 跳过和复杂使用
const (
    _  = iota             // 0（丢弃）
    KB = 1 << (10 * iota) // 1 << 10
    MB                    // 1 << 20
    GB                    // 1 << 30
    TB                    // 1 << 40
    PB                    // 1 << 50
    EB                    // 1 << 60
)
```

### 无类型常量

Go的常量是**无类型**的，直到使用时才确定具体类型：

```go
const Big = 1 << 100     // 无类型整数常量
// var i int = Big       // ❌ 溢出int
var f float64 = Big      // ✅ 转换为float64（可能有精度损失）
```

### 常量类型

```
无类型布尔
无类型整数
无类型浮点数
无类型复数
无类型字符串
无类型rune
```

### 🔥 面试扩展

**高频题1：无类型常量为什么重要？**
> 1. **更大的精度**：编译期可保留任意精度（`1<<100`编译期正确，运行时才转换）
> 2. **更少的显式转换**：`const PI = 3.14`可以直接赋值给`float32`或`float64`，不需要转换
> 3. **iota的语义**：`KB = 1 << (10 * iota)`利用了编译期求值能力

**高频题2：`iota`在`const`块中的重置规则？**
> `iota`在每个`const`块中从0开始，每遇到一个常量声明就+1。不同`const`块**重置**为0：
```go
const (
    A = iota  // 0
    B         // 1
)
const (
    C = iota  // 0（重置！）
    D         // 1
)
```

**高频题3：`const`和`var`的性能差异？**
> `const`在**编译期**求值，直接替换为字面量，零运行时开销。`var`在运行时分配。尽可能使用const。

**高频题4：常量可以实现枚举类型吗？**
> Go没有专门的枚举类型，通常用`const`+`iota`模拟枚举：
```go
type Color int
const (
    Red Color = iota
    Green
    Blue
)
func (c Color) String() string {
    return [...]string{"Red", "Green", "Blue"}[c]
}
```

**高频题5：无类型浮点常量赋值给不同类型的行为？**
```go
const X = 1.5
var a float32 = X  // ✅ 精确表示
var b float64 = X  // ✅ 精确表示
// 但如果常量的值超出float32范围则编译错误
const Y = 1e300
// var c float32 = Y  // ❌ 编译错误：溢出
var d float64 = Y  // ✅
```

## ⚡ 超级扩展

### ⚡ 3.1 整数类型完整深度分析

#### 各整数类型的二进制补码表示

Go的有符号整数使用**二进制补码（Two's Complement）**表示：

```go
var a int8 = 127   // 0111 1111
var b int8 = -128  // 1000 0000 (补码)
var c int8 = -1    // 1111 1111 (补码)

// 溢出的环绕行为
var x int8 = 127
x++  // -128 (环绕)
// 0111 1111 → 1000 0000

var y uint8 = 255
y++  // 0 (无符号环绕)
// 1111 1111 → 0000 0000
```

#### 有符号数为什么负数比正数多一个？

对于int8：范围是 -128 ~ 127，-128比127多一个。
原因：补码表示中，1000 0000 表示 -128，0000 0000 表示 0，没有 "负零"。

```
127 = 0111 1111
  1 = 0000 0001
  0 = 0000 0000
 -1 = 1111 1111
-128 = 1000 0000
```

#### 整数溢出的真实生产事故案例

```go
// 经典案例：时间计算溢出
var seconds int32 = 2147483647  // math.MaxInt32
seconds++  // 变成了 -2147483648 !
// 导致时间倒流！

// Go 1.17引入的math.MaxInt等常量
fmt.Println(math.MaxInt8)   // 127
fmt.Println(math.MaxInt16)  // 32767
fmt.Println(math.MaxInt32)  // 2147483647
fmt.Println(math.MaxInt64)  // 9223372036854775807
```

#### 位运算的实战模式大全

```go
// 1. 检查第n位是否为1
func isBitSet(x uint64, n uint) bool {
    return x & (1 << n) != 0
}

// 2. 设置第n位为1
func setBit(x uint64, n uint) uint64 {
    return x | (1 << n)
}

// 3. 清除第n位
func clearBit(x uint64, n uint) uint64 {
    return x &^ (1 << n)
}

// 4. 翻转第n位
func toggleBit(x uint64, n uint) uint64 {
    return x ^ (1 << n)
}

// 5. 权限控制经典模式
const (
    Read  = 1 << iota  // 1
    Write              // 2
    Exec               // 4
)
perm := Read | Write  // 3
hasExec := perm&Exec != 0  // false
perm |= Exec           // 添加执行权限
perm &^= Write         // 移除写权限
```

---

### ⚡ 3.2 浮点数完整深度分析

#### IEEE 754 标准的Go实现

```go
// float32: 1位符号 + 8位指数 + 23位尾数
// float64: 1位符号 + 11位指数 + 52位尾数
```

**查看浮点数的二进制表示：**

```go
import "math"

func floatBits(f float64) string {
    bits := math.Float64bits(f)
    sign := bits >> 63
    exp := (bits >> 52) & 0x7FF
    mant := bits & 0xFFFFFFFFFFFFF
    return fmt.Sprintf("sign=%b exp=%d mant=%b", sign, exp-1023, mant)
}

func main() {
    fmt.Println(floatBits(1.0))
    // sign=0 exp=0 mant=0  (1.0 = 1.0000... × 2^0)
    
    fmt.Println(floatBits(0.1))
    // 0.1在二进制中无限循环：0.00011001100110011...
    // 这就是 0.1 + 0.2 != 0.3 的根本原因
}
```

#### 浮点数精度陷阱大全

```go
// 陷阱1: 累加误差
var sum float64
for i := 0; i < 1000; i++ {
    sum += 0.001
}
fmt.Println(sum)  // 0.9999999999999998 (不是1.0!)

// 陷阱2: 大数+小数
var big = 1e16
var small = 1.0
fmt.Println(big + small)  // 10000000000000000 (small被吃掉)

// 陷阱3: 减法灾难
var a = 1.0000000000000001
var b = 1.0
fmt.Println(a - b)  // 1.1102230246251565e-16 (精度损失严重)
```

#### 正确比较浮点数的完整方案

```go
// 方法1: 绝对误差
func almostEqual(a, b, epsilon float64) bool {
    return math.Abs(a-b) < epsilon
}

// 方法2: 相对误差（适合数量级差异大的情况）
func relEqual(a, b, epsilon float64) bool {
    diff := math.Abs(a - b)
    mag := math.Max(math.Abs(a), math.Abs(b))
    if mag == 0 {
        return diff < epsilon
    }
    return diff/mag < epsilon
}

// 方法3: 单位末尾比较（ULP - Units in the Last Place）
import "math"

func ulpEqual(a, b float64) bool {
    if math.IsNaN(a) || math.IsNaN(b) {
        return false
    }
    if math.Signbit(a) != math.Signbit(b) {
        return a == b  // 零值处理
    }
    diff := math.Float64bits(a) - math.Float64bits(b)
    if diff > math.Float64bits(0) {
        return diff <= 4  // 允许4个ULP误差
    }
    return -diff <= 4
}
```

#### NaN、Inf、-0 的完整语义

```go
var z float64

// Inf的产生
posInf := 1.0 / z   // +Inf
negInf := -1.0 / z  // -Inf

// Inf的比较
fmt.Println(posInf > 1e308)  // true
fmt.Println(posInf == posInf) // true

// NaN的产生 — 0/0 或 Inf-Inf
nan := z / z

// NaN的特性：不等于任何值，包括自己
fmt.Println(nan == nan) // false!
fmt.Println(nan < nan)  // false
fmt.Println(nan > nan)  // false

// 检查NaN
fmt.Println(math.IsNaN(nan))  // true

// NaN在map中作key
m := map[float64]int{}
m[nan] = 1  // ✅ 合法，但永远取不到
fmt.Println(m[nan])  // 0 (找不到！因为nan != nan)
```

---

### ⚡ 3.3 字符串的终极深度分析

#### 字符串的完整内部结构

```go
// runtime/string.go

type stringStruct struct {
    str unsafe.Pointer  // 指向底层字节数组的指针
    len int             // 字节长度（不是字符数！）
}
```

**完整内存布局：**
```
stringStruct {
    str -----------> [104] [101] [108] [108] [111] [44] [32] [228] [184] [150] [231] [149] [140]
                      H     e     l     l     o     ,         世             界
    len = 13
}
```

#### UTF-8 编码的完整细节

UTF-8是一种**变长编码**，每个Unicode码点用1-4字节表示：

```
U+0000 ~ U+007F:   0xxxxxxx (1字节)  — ASCII范围
U+0080 ~ U+07FF:   110xxxxx 10xxxxxx (2字节)  — 拉丁字母扩展
U+0800 ~ U+FFFF:   1110xxxx 10xxxxxx 10xxxxxx (3字节)  — CJK基本区
U+10000 ~ U+10FFFF: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx (4字节)  — 表情符号等
```

```go
// 手动解码UTF-8
func decodeRune(s string) (rune, int) {
    if len(s) == 0 {
        return -1, 0
    }
    b := s[0]
    if b < 0x80 {  // 1字节
        return rune(b), 1
    } else if b < 0xE0 {  // 2字节
        return rune(b&0x1F)<<6 | rune(s[1]&0x3F), 2
    } else if b < 0xF0 {  // 3字节
        return rune(b&0x0F)<<12 | rune(s[1]&0x3F)<<6 | rune(s[2]&0x3F), 3
    } else {  // 4字节
        return rune(b&0x07)<<18 | rune(s[1]&0x3F)<<12 | rune(s[2]&0x3F)<<6 | rune(s[3]&0x3F), 4
    }
}

func main() {
    s := "Hello, 世界"
    // UTF-8编码详解:
    // H = 0x48 (1字节)
    // e = 0x65 (1字节)
    // 世 = 0xE4 0xB8 0x96 (3字节)
    // 界 = 0xE7 0x95 0x8C (3字节)
    fmt.Println(len(s))  // 13 (字节数)
    fmt.Println(utf8.RuneCountInString(s))  // 9 (字符数)
}
```

#### strings.Builder 完整源码分析

```go
// Go 1.10+引入的strings.Builder

// 内部结构
// src/strings/builder.go
type Builder struct {
    addr *Builder  // 用于拷贝检查
    buf  []byte    // 底层缓冲区
}

func (b *Builder) WriteString(s string) (int, error) {
    b.copyCheck()  // 检查是否被复制
    b.buf = append(b.buf, s...)
    return len(s), nil
}

func (b *Builder) Grow(n int) {
    b.copyCheck()
    if b.buf == nil {
        b.buf = make([]byte, 0, n)
    } else if cap(b.buf)-len(b.buf) < n {
        // 预分配
        b.buf = append(b.buf[:cap(b.buf)], make([]byte, n)...)[:len(b.buf)]
    }
}

func (b *Builder) String() string {
    return string(b.buf)  // 不逃逸（编译器优化）
}
```

**strings.Builder vs bytes.Buffer vs += 性能对比：**

```go
// Benchmark
func BenchmarkPlus(b *testing.B) {
    var s string
    for i := 0; i < b.N; i++ {
        s += "x"
    }
    _ = s
}

func BenchmarkBuilder(b *testing.B) {
    var sb strings.Builder
    for i := 0; i < b.N; i++ {
        sb.WriteString("x")
    }
    _ = sb.String()
}

// N=1000时:
// +=:          ~8μs (多次分配拷贝)
// Builder:     ~0.5μs (一次分配)
// bytes.Buffer: ~0.6μs (类似)
// strings.Join: ~0.4μs (已知切片长度的最优解)
```

#### Go 1.22 对字符串的改进：字符串不可变但可切片的细节

```go
s := "hello"
// s[0] = 'H'  // ❌ 编译错误：字符串不可变

// 但可以切片
sub := s[1:4]  // "ell"，共享底层内存

// 切片为什么不需要复制？
// 因为字符串的不可变性保证了切片安全——子串永远不会修改底层数组

// 修改字符串的正确方式
b := []byte(s)
b[0] = 'H'
s = string(b)
```

#### 字符串转换的内存开销

```go
// string → []byte: 如果编译器可以证明[]byte不会被修改，零拷贝
s := "hello"
b := []byte(s)  // 可能复制，也可能共享（取决于编译器分析）

// string → []rune: 总是O(n)解码
r := []rune(s)  // 每个字符解码为rune

// []byte → string: 总是分配新字符串（不可变保证）
s2 := string(b)  // 必须复制，因为[]byte可能被修改
```

---

### ⚡ 3.4 大厂面试题全集（基础数据类型篇）

**面试题1：“0.1 + 0.2 != 0.3” 是怎么回事？
```
// 这是因为计算机用二进制存小数
// 0.1 在二进制中是无限循环小数：0.00011001100110011...
// 就像 1/3 在十进制中是 0.3333... 永远写不完
// 计算机只能存有限位（float32存23位，float64存52位）
// 所以存的是近似值，加起来就有误差
```

**面试题2：“NaN != NaN” 是什么意思？**
```go
nan := math.NaN()
fmt.Println(nan == nan)  // false!
// NaN = Not a Number
// 表示"不是数字"的结果（比如 0/0）
// NaN不等于任何东西，甚至不等于自己
// 
// 坑：在map里用NaN做key，永远取不到值
m := map[float64]string{}
m[math.NaN()] = "hello"
fmt.Println(m[math.NaN()])  // ""（找不到！）
```

**面试题3：int 和 int64 在64位系统上是同一类型吗？**
```
不是！虽然它们都占8字节，但Go认为它们是不同的类型

var a int = 10
var b int64 = 20
// a = b     // ❌ 编译错误：类型不匹配
// a + b     // ❌ 编译错误

// 必须显式转换：
a = int(b)
b = int64(a)
```

**面试题4：为什么Go没有隐式类型转换？**
```
安全！安全！安全！（重要的事情说三遍）

C语言有隐式转换，经常导致bug：
  unsigned int a = 1;
  int b = -2;
  if (a > b) { ... }  // 实际上 a < b！因为b被转成了无符号数

Go强制你显式写转换，虽然多了几行代码，但不会出这种bug
```

**面试题5：rune和byte有什么区别？**
```go
// byte = uint8（1字节，存ASCII字符）
// rune = int32（4字节，存Unicode字符）

s := "Hello, 世界"

for i := 0; i < len(s); i++ {
    fmt.Printf("%c ", s[i])  // H e l l o ,   ä  ̖ ! (乱码！)
}

for _, r := range s {
    fmt.Printf("%c ", r)    // H e l l o ,   世 界 （正确）
}

// 因为"世"在UTF-8中占3个字节：0xE4 0xB8 0x96
// 所以用byte索引会看到3个乱码字符
```

**面试题6：string的底层结构是什么？**
```go
// 底层是一个结构体：
// type stringStruct struct {
//     str unsafe.Pointer  // 指向字节数组的指针
//     len int             // 字节数
// }

// 所以：
s := "hello"
p1 := &s   // 取string的地址（16字节的地址）
p2 := &s[0] // 取第一个字节的地址
fmt.Println(unsafe.Sizeof(s))  // 16

// string切片不复制（因为只有指针和长度，超快）
sub := s[1:4]  // "ell"，零成本！
```

**面试题7：strings.Builder和bytes.Buffer有什么区别？**
```go
// strings.Builder 专门用来拼接字符串
// bytes.Buffer 可以拼接任意字节

var sb strings.Builder
sb.WriteString("hello")
sb.WriteString(" ")
sb.WriteString("world")
s := sb.String()  // "hello world"

// strings.Builder 的好处：
// 1. 自动扩容（内部[]byte自动增长）
// 2. String()方法不分配内存（直接返回内部[]byte转string）
// 3. 比 + 快了将近100倍
```

---

### ⚡ 3.5 Go的运算符优先级（完整表格）

```
优先级（高→低）：
  5  *  /  %  <<  >>  &  &^
  4  +  -  |  ^
  3  ==  !=  <  <=  >  >=
  2  &&
  1  ||

简单记法：
  * / % > + - > 比较 > && > ||
  
例子：
a + b * c    → a + (b * c)    // 乘法优先
x < 10 && y > 5    → (x < 10) && (y > 5)  // 比较优先

a := 1 << 2 + 3    // 1 << (2+3) = 32 （移位低于加减）
```

---

---

### ⚡ 3.6 字符串操作大全（给初中生）

#### 字符串的完整操作方法

```go
s := "Hello, 世界"

// 1. 长度（字节数，不是字符数！）
fmt.Println(len(s))  // 13

// 2. 索引（取第i个字节）
fmt.Println(s[0])     // 72（'H'的ASCII码）

// 3. 切片（取子串）
fmt.Println(s[0:5])  // "Hello"
fmt.Println(s[:5])   // "Hello"
fmt.Println(s[7:])   // "世界"

// 4. 字符串拼接
s2 := s + "!!!"
fmt.Println(s2)  // "Hello, 世界!!!"

// 5. for range（遍历每一个字符，不是字节）
for i, r := range s {
    fmt.Printf("位置%d: %c\n", i, r)
}
// 位置0: H
// 位置1: e
// ...
// 位置7: 世
// 位置10: 界
```

#### strings包常用函数大全

```go
import "strings"

s := "  hello world  "

strings.Contains(s, "hello")        // true
strings.Count(s, "l")               // 3
strings.HasPrefix(s, "  hello")     // true
strings.HasSuffix(s, "world  ")     // true
strings.Index(s, "world")           // 7
strings.LastIndex(s, "l")           // 9
strings.Repeat("ha", 3)            // "hahaha"
strings.Replace("foo", "o", "x", 1) // "fxo"
strings.Split("a,b,c", ",")        // ["a", "b", "c"]
strings.Join([]string{"a","b"}, "-") // "a-b"
strings.ToUpper("hello")           // "HELLO"
strings.ToLower("HELLO")           // "hello"
strings.Trim(s, " ")               // "hello world"
strings.TrimSpace(s)                // "hello world"
strings.Fields("a b  c")          // ["a", "b", "c"]
```

#### strconv包（字符串和数字互转）

```go
import "strconv"

// 数字 → 字符串
s := strconv.Itoa(42)            // "42"
s = strconv.FormatInt(42, 16)     // "2a"（16进制）
s = strconv.FormatFloat(3.14, 'f', 2, 64)  // "3.14"

// 字符串 → 数字
n, _ := strconv.Atoi("42")       // 42
n, _ := strconv.ParseInt("ff", 16, 0)  // 255
f, _ := strconv.ParseFloat("3.14", 64) // 3.14

// 注意：转换失败时会返回错误
n, err := strconv.Atoi("hello")
fmt.Println(n, err)  // 0, strconv.Atoi: parsing "hello": invalid syntax
```

---

### ⚡ 3.7 常量完整的超级详解

#### 什么是常量？（给初中生）

```
常量 = 永远不会变的值
就像圆周率 π = 3.14159...
世界上所有人都知道π是多少
而且π永远不会变

Go中的常量也一样：
  const Pi = 3.14159
  Pi 永远等于 3.14159
  你不能改它
```

#### 常量和变量的对比

```go
// 变量：可以改
var age = 18
age = 19  // ✅ 可以改

// 常量：不能改
const PI = 3.14159
// PI = 3.14  // ❌ 编译错误！
```

#### 常量可以在编译时计算

```go
const (
    a = 1 + 2       // 3（编译时就算好了）
    b = a * 3       // 9
    c = 1 << 10     // 1024
)

// 运行时：a, b, c 已经是"直接写死的数字"了
// 不需要任何计算！
```

#### 无类型常量的好处

```go
// 无类型常量：可以给任何兼容的类型赋值
const Big = 1000000

var a int32 = Big    // ✅ 转换
var b int64 = Big    // ✅ 转换
var c float64 = Big  // ✅ 转换

// 如果是有类型常量：
const BigInt int64 = 1000000
// var a int32 = BigInt  // ❌ 编译错误：类型不匹配！
```

---

---

### ⚡ 3.8 max、min、clear——Go 1.21+内置函数

#### max：取最大值

```go
// max 可以传任意多个参数
max(1, 2, 3)             // 3
max(3.14, 2.5, 1.0)     // 3.14
max("apple", "banana")  // "banana"（字典序）

// 可以传切片吗？不行，max接收的是可变参数
nums := []int{1, 4, 2}
// max(nums...)   // ❌ 不可以
m := nums[0]
for _, v := range nums[1:] { m = max(m, v) }
```

#### min：取最小值

```go
min(1, 2, 3)         // 1
min(3.14, 2.5)       // 2.5
```

#### clear：清空map或slice

```go
// 清空map
m := map[string]int{"a": 1, "b": 2}
clear(m)
fmt.Println(len(m))  // 0

// 清空slice（不是删除元素，是把元素归零）
s := []int{1, 2, 3}
clear(s)
fmt.Println(s)        // [0, 0, 0]（长度不变！）
```

**clear的底层原理：**
```
clear map：把map的元素全部删除（重新分配内存）
clear slice：把每个元素设为该类型的零值（长度和容量不变）

以前清空map要这样：
  for k := range m { delete(m, k) }
现在一行就行：
  clear(m)
```

#### float32精度的详细分析

```go
// float32 精度：约7位有效数字
// float64 精度：约15位有效数字

var f32 float32 = 123456789  // 123456792（最后几位不对！）
var f64 float64 = 123456789  // 123456789（准确）

// 什么时候用float32？
// 1. 图形学（OpenGL顶点数据）
// 2. 机器学习（大量浮点数时省一半内存）
// 3. 嵌入式系统（内存紧张）

// 什么时候用float64？
// 1. 大多数情况（默认选择）
// 2. 金融计算（虽然最好用decimal）
// 3. 科学计算（需要精度）
```

---

---

### ⚡ 3.9 再补5道大厂面试题（基础数据类型篇）

**面试题8：为什么Go的string是不可变的？**
```
1. 安全：多个变量可以共享底层字节数组，不会互相影响
2. 高效：子串切片（s[1:5]）零拷贝，直接指向原内存
3. map key：只有不可变类型才能做key
4. 并发安全：多个goroutine可同时读同一字符串

就像一张收据：你可以看，但不能改
```

**面试题9：'rune'到底是什么？为什么需要它？**
```go
// rune = int32的别名，表示一个Unicode码点
// 
// 为什么需要？
// 因为一个中文字符在UTF-8中占3个字节
// 如果按byte遍历，会看到乱码

s := "Hello, 世界"

// byte遍历（错误）：
for i := 0; i < len(s); i++ {
    fmt.Printf("%c", s[i])  // H e l l o ,   ä ̖ !乱码
}

// rune遍历（正确）：
for _, r := range s {
    fmt.Printf("%c", r)  // H e l l o ,   世 界
}
```

**面试题10：0.1 + 0.2 != 0.3 怎么修复？**
```go
// 方法1：用误差比较
const epsilon = 1e-9
if math.Abs((0.1+0.2)-0.3) < epsilon {
    fmt.Println("相等")
}

// 方法2：用整数
// 比如计算金额时用分而不是元
a := 10  // 0.1元 = 10分
b := 20  // 0.2元 = 20分
if a + b == 30 {  // 30分 = 0.3元
    fmt.Println("相等")
}

// 方法3：用第三方包
// github.com/shopspring/decimal
```

**面试题11：uintptr和unsafe.Pointer的区别？**
```go
// unsafe.Pointer：指针类型，GC能跟踪
// uintptr：整数类型，GC不能跟踪

x := 42
p := unsafe.Pointer(&x)  // GC知道p指向x
addr := uintptr(p)        // 只是一个数字，GC不知道它指向x

// 如果x被GC移动了：
// p → 指向x的新地址 ✅
// addr → 还是旧地址 ❌（野指针！）
```

**面试题12：iota在const块中如何重置？**
```go
// iota在每个const块中从0开始

const (
    A = iota  // 0
    B        // 1
)

const (
    C = iota  // 0（从0重新开始！）
    D        // 1
)
```

### ⚡ 3.10 整型的完整流程图

#### int类型的取值范围流程图

```
                    ┌──────────────────────┐
                    │    int8 (-128~127)    │
                    ├──────────────────────┤
                    │    int16 (-32768~32767)  │
                    ├──────────────────────┤
                    │    int32 (-21亿~21亿)    │
                    ├──────────────────────┤
                    │    int64 (极大!)        │
                    └──────────────────────┘
                        ║ int = 平台相关 ║
                        ║ 32位系统=int32 ║
                        ║ 64位系统=int64 ║
                        ╚════════════════╝
```

#### 有符号整数 vs 无符号整数

```
有符号整数（int）：可以表示负数
  用补码表示
  例 int8: 127 = 01111111
            -1 = 11111111
           -128 = 10000000

无符号整数（uint）：只能表示非负数
  范围更大
  例 uint8: 0~255
  例 uint16: 0~65535
```

#### 整数溢出流程图

```go
var x int8 = 127
x++  // -128（溢出！环绕了）
// 01111111 → 10000000（从127变成-128）

var y uint8 = 255
y++  // 0（无符号环绕）
// 11111111 → 00000000

// 溢出检测：
// Go编译器不会提醒你溢出
// 需要手动检查：
if x > math.MaxInt8-1 {
    fmt.Println("要溢出了！")
}
```

#### 浮点数在内存里的存储图解

```
float32（32位）：
  ┌─┬────────┬───────────────────────┐
  │S│ 指数(8)│   尾数(23)             │
  └─┴────────┴───────────────────────┘
  1位符号  8位指数      23位小数
  精度：约7位有效数字

float64（64位）：
  ┌─┬────────┬──────────────────────────────────┐
  │S│ 指数(11)│    尾数(52)                       │
  └─┴────────┴──────────────────────────────────┘
  1位符号  11位指数      52位小数
  精度：约15位有效数字
```

#### NaN和Inf的产生流程图

```
       ┌──────────────────┐
       │    浮点数计算      │
       └────────┬─────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
  ┌──────────┐    ┌──────────────┐
  │ 0.0 / 0.0 │    │ 1.0 / 0.0   │
  │   → NaN   │    │   → +Inf    │
  └──────────┘    └──────────────┘
       │                 │
       ▼                 ▼
  ┌──────────┐    ┌──────────────┐
  │NaN != NaN│    │正无穷大      │
  │经典陷阱！│    │超过最大范围  │
  └──────────┘    └──────────────┘
```

#### 字符串操作的完整流程

```
字符串 s = "Hello, 世界!"
          ↓
  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬──┬──┬──┬──┬──┐
  │H│e│l│l│o│,│ │ │世│世│世│界│界│界│!│
  └─┴─┴─┴─┴─┴─┴─┴─┴─┴──┴──┴──┴──┴──┘
  0 1 2 3 4 5 6 7   8  9 10 11 12 13 14
                    ↑↑↑          ↑↑↑
                  UTF-8编码     UTF-8编码
                  3字节"世"       3字节"界"

len(s) = 15（字节数）
for range: 9次（字符数/rune数）
```

#### 常量定义的完整流程图

```
const 声明
    │
    ├── 无类型常量
    │     │
    │     ├── 无类型整数 (const X = 42)
    │     ├── 无类型浮点 (const Pi = 3.14)
    │     ├── 无类型字符串 (const Name = "Alice")
    │     └── 无类型布尔 (const Debug = true)
    │
    ├── 有类型常量
    │     │
    │     └── const X int = 42  (只能给int用)
    │
    └── iota枚举
          │
          ├── 简单递增：A=0, B=1, C=2
          ├── 跳过值：_=0, A=1
          ├── 位运算：Read=1, Write=2, Exec=4
          └── 字节单位：KB=1024, MB=1048576
```

---

> **下一章**：[第4章 复合数据类型](./ch04-composite-types.md) —— 数组、Slice、Map、结构体、JSON和模板。
