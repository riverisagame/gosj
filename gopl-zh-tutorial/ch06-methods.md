# 第6章 方法

> Go的方法是为特定类型定义的函数。Go没有类（class），但对类型定义方法来实现面向对象的行为。理解方法、嵌入和封装是掌握Go OOP的关键。

---

## 目录

- [6.1 方法声明](#61-方法声明)
- [6.2 基于指针对象的方法](#62-基于指针对象的方法)
- [6.3 通过嵌入结构体来扩展类型](#63-通过嵌入结构体来扩展类型)
- [6.4 方法值和方法表达式](#64-方法值和方法表达式)
- [6.5 示例: Bit数组](#65-示例-bit数组)
- [6.6 封装](#66-封装)

---

## 6.1 方法声明

### 基本语法

```go
type Point struct {
    X, Y float64
}

// 普通函数
func Distance(p, q Point) float64 {
    return math.Hypot(q.X-p.X, q.Y-p.Y)
}

// 方法（接收器为Point）
func (p Point) Distance(q Point) float64 {
    return math.Hypot(q.X-p.X, q.Y-p.Y)
}

// 使用
p := Point{1, 2}
q := Point{4, 6}
fmt.Println(p.Distance(q))  // 方法调用
fmt.Println(Distance(p, q)) // 函数调用
```

- 方法 = 函数 + 接收器（receiver）
- 不能对内置类型添加方法（必须自定义类型）
- 同一类型的方法不能有相同名字

### 可以为哪些类型定义方法

```go
type MyInt int
func (m MyInt) IsPositive() bool {
    return m > 0
}

// ❌ 不能对int定义方法（int是内置类型）
// func (i int) IsPositive() bool // 编译错误
```

### 🔥 面试扩展

**高频题1：方法和函数的区别？为什么不用函数就够了？**
> 方法相比于函数的优势：
> 1. **调用语法更自然**：`p.Distance(q)`比`Distance(p, q)`更面向对象
> 2. **方法名可重载**（在不同类型上）：`Point.Distance`和`Line.Distance`是不同的
> 3. **接口实现**：只有方法才能实现接口，普通函数不行
> 4. **链式调用**：方法可以返回receiver实现链式调用（Builder模式）

**高频题2：可以给任何类型（包括内置类型）定义方法吗？**
> **不可以。** 必须给**自定义类型**定义方法。内置类型（int、string等）、其他包的类型的别名都不能直接添加方法。解决方案是创建新类型：`type MyInt int`。

---

## 6.2 基于指针对象的方法

### 值接收器 vs 指针接收器

```go
type Point struct { X, Y float64 }

// 值接收器：不修改原值
func (p Point) Add(q Point) Point {
    return Point{p.X + q.X, p.Y + q.Y}
}

// 指针接收器：可以修改原值
func (p *Point) ScaleBy(factor float64) {
    p.X *= factor
    p.Y *= factor
}
```

### 调用约定

```go
p := Point{1, 2}
pp := &p

// 值类型调用指针方法（自动取地址）
p.ScaleBy(2)   // (&p).ScaleBy(2) 的简写

// 指针类型调用值方法（自动解引用）
pp.Add(Point{3, 4})  // (*pp).Add(Point{3, 4}) 的简写
```

### 指针接收器 vs 值接收器的选择

| 场景 | 推荐 |
|------|------|
| 需要修改receiver | 指针 |
| 大结构体（> 64字节） | 指针（避免拷贝开销） |
| 小结构体、基本类型 | 值（清晰、不可变语义） |
| 切片、map等引用类型 | 取决于是否修改底层数据 |
| 不确定时 | **指针**👉 |

### 🔥 面试扩展

**高频题1：值接收器的方法和指针接收器的方法谁可以满足接口？**
```go
type Geometry interface {
    Area() float64
    Scale(float64)
}

type Rect struct { W, H float64 }

func (r Rect) Area() float64  { return r.W * r.H }
func (r *Rect) Scale(f float64) { r.W *= f; r.H *= f }

var r Rect
var g Geometry
g = r     // ❌ Rect没有实现Scale（指针接收器未实现）
g = &r    // ✅ *Rect实现了Area和Scale
```
> 规则：**值类型**只有值接收器的方法集；**指针类型**既有值接收器又有指针接收器的方法集。

**高频题2：方法调用的简化规则可能导致什么混淆？**
```go
type MyList []int

func (l MyList) Append(v int) {}
func (l *MyList) Prepend(v int) {}

var list MyList
list.Append(1)   // ✅ 值类型调值接收器
list.Prepend(1)  // ✅ 值类型可以调指针接收器（自动取地址）

var m MyList = nil
m.Prepend(1)     // ✅ nil切片可以调用！只要函数内部不访问nil的底层
```

**高频题3：什么时候必须用指针接收器？**
> 1. 需要修改receiver的状态
> 2. receiver是sync.Mutex等不可复制类型
> 3. 大结构体（避免拷贝开销）
> 4. 为了方法集一致性（所有方法要么全值要么全指针）

---

## 6.3 通过嵌入结构体来扩展类型

### 匿名嵌入

```go
type Point struct { X, Y float64 }
type Color struct { R, G, B uint8 }

type ColoredPoint struct {
    Point           // 匿名嵌入
    Color           // 匿名嵌入
}

cp := ColoredPoint{}
cp.X = 1            // cp.Point.X = 1 的简写
cp.Y = 2
cp.R = 255           // cp.Color.R = 255
```

### 方法的提升

嵌入结构体的方法被**提升**到外层结构体：

```go
func (p Point) Distance(q Point) float64 {
    return math.Hypot(q.X-p.X, q.Y-p.Y)
}

cp := ColoredPoint{Point: Point{1, 2}}
cp.Distance(Point{4, 6})  // 提升：Point的方法出现在ColoredPoint上
```

### 方法冲突

如果两个嵌入的结构体有同名方法怎么办？

```go
type A struct { ... }
func (A) F() {}

type B struct { ... }
func (B) F() {}

type C struct {
    A
    B
}
// c.F() // ❌ 编译错误：ambiguous selector c.F
// 必须显式指定：c.A.F() 或 c.B.F()
```

### 🔥 面试扩展

**高频题1：Go的"继承"和传统OO语言的继承有何本质区别？**
> Go的嵌入（embedding）本质是**组合**，不是继承：
> - Go没有虚方法（virtual method），没有多态override
> - 嵌入的方法只是提升（promotion），不是继承
> - 外层类型不能override内层类型的方法
> - 这是"has-a"关系，不是"is-a"关系

**高频题2：嵌入和组合的选择？**
> - 嵌入：需要方法提升，需要"像"父类型
> - 组合（命名嵌入）：不需要方法提升，命名更清晰
```go
type Employee struct {
    Person        // 嵌入：方法提升（Employee可以调用Person的方法）
    Address  Addr  // 组合：命名清晰，不提升方法
}
```

---

## 6.4 方法值和方法表达式

### 方法值

```go
p := Point{1, 2}
q := Point{4, 6}

distanceFromP := p.Distance  // 方法值，类型是func(Point) float64
fmt.Println(distanceFromP(q)) // 等价于p.Distance(q)
```

### 方法表达式

```go
f := Point.Distance  // 方法表达式，类型是func(Point, Point) float64
fmt.Println(f(p, q))  // 第一个参数是receiver
```

### 🔥 面试扩展

**高频题1：方法值和方法表达式在实际工程中有什么用？**
> 1. **回调**：方法值可作为回调函数传递（保留receiver上下文）
> 2. **时间计时**：`defer time.Now()`模式
> 3. **将方法传入map reduce**：`strings.Map(unicode.ToUpper, "hello")`

---

## 6.5 示例: Bit数组

```go
type IntSet struct {
    words []uint64
}

// 添加元素
func (s *IntSet) Add(x int) {
    word, bit := x/64, uint(x%64)
    for word >= len(s.words) {
        s.words = append(s.words, 0)
    }
    s.words[word] |= 1 << bit
}

// 检查是否存在
func (s *IntSet) Has(x int) bool {
    word, bit := x/64, uint(x%64)
    return word < len(s.words) && s.words[word]&(1<<bit) != 0
}
```

### 🔥 面试扩展

**高频题1：位运算实现的IntSet和map[int]bool实现的Set各有什么优势？**
> - Bit数组：**内存效率高**（每个元素1bit vs map中entry的几十字节），但只适合非负整数且元素分布密集
> - map[int]bool：通用性强，适用于任意元素类型，稀疏时内存也不会浪费

---

## 6.6 封装

### 通过大小写控制可见性

```go
// counter包
package counter

type Counter struct {
    n int  // 未导出：包外不可访问
}

func (c *Counter) Inc()  { c.n++ }
func (c *Counter) N() int { return c.n }  // Getter方法

// main包
c := counter.Counter{}
c.Inc()
fmt.Println(c.N())    // 1
// fmt.Println(c.n)    // ❌ 编译错误：未导出字段
```

### 封装的好处

1. 调用者不能直接修改内部状态，只能通过方法
2. 实现细节可以随时更改而不影响调用方
3. 防止外部设置无效状态

### 🔥 面试扩展

**高频题1：Go的封装和Java/C++的private有什么区别？**
> 核心区别：Go的封装是**包级别的**（包内所有文件可访问未导出标识符），不是类级别的。这简化了可见性模型（只有两种：包内可见/包外可见）。Go没有子类（subclass），所以不需要protected。

**高频题2：Getter和Setter的命名惯例？**
> - Getter方法省略Get前缀：`obj.Name()`而不是`obj.GetName()`
> - Setter方法用Set前缀：`obj.SetName("foo")`
> Go的惯例是：访问属性直接用`Attribute()`命名，而不是`GetAttribute()`。

## ⚡ 超级扩展

### ⚡ 6.1 方法接收器的完整选择指南

#### 值接收器 vs 指针接收器的全面对比

```go
type Person struct {
    Name string
    Age  int
}

// 值接收器：方法操作的是副本
func (p Person) Birthday() {
    p.Age++  // 只修改了副本
}

// 指针接收器：方法操作原对象
func (p *Person) BirthdayPtr() {
    p.Age++  // 修改原对象
}

p := Person{Name: "Alice", Age: 30}
p.Birthday()
fmt.Println(p.Age)  // 30 — 没变！

p.BirthdayPtr()
fmt.Println(p.Age)  // 31 — 变了！
```

**选择规则（Go官方指南）：**
| 条件 | 推荐 |
|------|------|
| 需要修改receiver | ✅ 指针 |
| receiver是大结构体 | ✅ 指针（避免拷贝） |
| receiver包含sync.Mutex/Map | ✅ 指针（不能复制） |
| 不确定时 | ✅ 指针（一致性优先） |
| receiver是map/func/slice | ⚠️ 看是否修改内容 |
| receiver是int/string等 | ✅ 值（不可变语义） |

#### 方法集的完整规则

```go
type T struct{}
func (t T) M1() {}
func (t *T) M2() {}

var t T
var pt *T = &t

// 规则1: T类型的方法集包含所有T接收器的方法
// t.M1()  ✅
// t.M2()  ✅ (自动取地址)

// 规则2: *T类型的方法集包含T和*T的所有方法
// pt.M1()  ✅ (自动解引用)
// pt.M2()  ✅

// 规则3: 接口实现的判断
// 如果接口要求M2(指针方法)，T类型不能满足
// var i Interface = t  // ❌ 如果Interface要求M2
// var i Interface = &t // ✅ 指针实现了所有方法
```

#### nil接收器的处理

```go
type IntSet struct {
    words []uint64
}

func (s *IntSet) Has(x int) bool {
    if s == nil {
        return false  // nil接收器安全处理
    }
    word, bit := x/64, uint(x%64)
    return word < len(s.words) && s.words[word]&(1<<bit) != 0
}

var s *IntSet  // nil
fmt.Println(s.Has(42))  // false (不会panic)
```

---

### ⚡ 6.2 嵌入结构体的完整机制

#### 结构体嵌入的底层内存布局

```go
type Point struct { X, Y int }
type ColoredPoint struct {
    Point            // 匿名嵌入
    Color uint32
}

// 内存布局等价于：
// type ColoredPoint struct {
//     X     int     // 从Point提升
//     Y     int     // 从Point提升
//     Color uint32
// }

cp := ColoredPoint{}
cp.X = 1     // cp.Point.X = 1 的简写
cp.Y = 2
cp.Color = 0xFF0000

// 注意：不是继承，是组合！
// ColoredPoint 不能赋值给 Point
// var p Point = cp  // ❌ 类型不匹配
```

#### 方法冲突的完整解析

```go
type A struct{}
func (A) F() int { return 1 }

type B struct{}
func (B) F() int { return 2 }

type C struct { A; B }

func main() {
    var c C
    // c.F()     // ❌ 编译错误: ambiguous selector
    fmt.Println(c.A.F())  // 1
    fmt.Println(c.B.F())  // 2
}
```

---

### ⚡ 6.3 封装和信息隐藏

#### Go封装机制的完整分析

```go
// counter包
package counter

type Counter struct {
    val int  // 未导出：包外不可直接访问
}

func NewCounter() *Counter {
    return &Counter{}
}

func (c *Counter) Inc() int {
    c.val++
    return c.val
}

func (c *Counter) Value() int {
    return c.val
}

// main包
c := counter.NewCounter()
// c.val    // ❌ 编译错误
fmt.Println(c.Inc())    // 1
fmt.Println(c.Inc())    // 2
fmt.Println(c.Value())  // 2
```

**为什么包内可见而包外不可见？**

```text
Go的可见性是基于包的，不是基于类型的：
- 同一包内的所有文件可访问未导出标识符
- 不需要"friend"或"internal"关键字
- 这就是Go的封装模型——简单而有效
```

#### 突破包限制的两种模式

```go
// 模式1: 内部测试包使用export_test.go
// export_test.go (在counter包中)
var Val = &val  // 导出私有变量供测试使用

// 模式2: 使用内部包（internal）
// go doc 强制 internal 包只能被同级或父级导入
```

---

### ⚡ 6.4 方法值和方法表达式的实战

```go
// 方法值：绑定receiver后的函数
// 类型：func(参数) 返回值

type Point struct{ X, Y float64 }

func (p Point) Distance(q Point) float64 {
    return math.Hypot(q.X-p.X, q.Y-p.Y)
}

p := Point{1, 2}
dist := p.Distance  // 方法值：绑定p的Distance方法
// 类型 dist: func(Point) float64

fmt.Println(dist(Point{4, 6}))  // 5.0

// 方法表达式：不绑定receiver
// 类型：func(Point, Point) float64
distExpr := Point.Distance
fmt.Println(distExpr(p, Point{4, 6}))  // 5.0

// 实际应用：map中存储方法
var ops = map[string]func(int, int) int{
    "add": func(a, b int) int { return a + b },
    "sub": func(a, b int) int { return a - b },
}
fmt.Println(ops["add"](3, 4))  // 7
```

---

---

### ⚡ 6.5 Bit数组示例的纳米级解析

#### 位运算——初二小白版

首先，什么是位（bit）？
```
计算机里最小的数据单位就是bit（比特）
一个bit只能是 0 或 1（就像开关，开=1，关=0）

8个bit = 1个byte（字节）
例如：
  00000000 → 0
  00000001 → 1
  00000010 → 2
  00000011 → 3
  ...
  11111111 → 255
```

**为什么用bit数组表示整数集合？**

想象你有一个超大文件柜（内存），每个抽屉（8个文件格）：
```
文件柜第一层:
  [格子0][格子1][格子2][格子3][格子4][格子5][格子6][格子7]
文件柜第二层:
  [格子8][格子9]...

数字5→在第0个抽屉的第5个格子上贴标签
数字100→在第12个抽屉的第4个格子上贴标签

查找：直接看那个格子有没有标签 → O(1)时间复杂度
```

**为什么叫"位图"（Bitmap）？**
```go
// 用一个bit标记一个数字是否存在
// uint64有64个bit，可以标记0~63这64个数字
// 如果用 []int 来存同样的信息：
//   需要64个int = 64*64 = 4096bit
// 如果用位图：
//   只需要1个uint64 = 64bit
// 节省了 64倍 内存！
```

#### IntSet的底层原理（给初中生看的）

```go
type IntSet struct {
    words []uint64   // 每个uint64是64个bit
}
// 所以: words[0] 存数字 0~63
//      words[1] 存数字 64~127
//      words[2] 存数字 128~191
//      以此类推...

func (s *IntSet) Add(x int) {
    // 数字x应该放在words[]的第几个uint64里？
    word := x / 64        // 例如 x=100, word=100/64=1, 放在words[1]
    // 在这个uint64的第几个bit？
    bit  := uint(x % 64)  // x=100, bit=100%64=36, 第36个bit
    
    // 如果words不够长，就加长
    for word >= len(s.words) {
        s.words = append(s.words, 0)  // 加一个全是0的uint64
    }
    
    // 设置那个bit为1
    // | 是按位或：只要bit1为1就是1
    // 1 << bit 是 "把1向左移动bit位"
    // 例如 bit=3, 1<<3 = 00001000
    s.words[word] |= 1 << bit
}

func (s *IntSet) Has(x int) bool {
    word := x / 64
    bit  := uint(x % 64)
    
    // 如果words不够长，数字不存在
    if word >= len(s.words) {
        return false
    }
    
    // & 是按位与：两个bit都是1才为1
    // 检查第bit位是不是1
    return s.words[word] & (1 << bit) != 0
}
```

**实战例子：**
```go
s := IntSet{}
s.Add(3)   // words[0] = ...00001000 (第3个bit设为1)
s.Add(10)  // words[0] = ...10000001000 (第3和10位是1)
s.Add(100) // words[1] = ...0010000... (第36位是1)

fmt.Println(s.Has(3))   // true
fmt.Println(s.Has(5))   // false
fmt.Println(s.Has(100)) // true
```

**面试题：Bit数组为什么比map[int]int快？**
```
map: 需要存储key和value的内存 + 哈希计算
bit数组: 只需要1个bit + 除法/取模运算

假设存100万个数字：
  map:    约50MB内存
  bit数组: 约125KB内存
  差了 400倍！
```

---

### ⚡ 6.6 封装（面向对象编程基础）

#### 面向对象的三大特性（给初中生）

```
1. 封装（Encapsulation） — 把数据和操作数据的方法打包在一起
   就像手机：你不用管内部怎么工作的，按按钮就能打电话

2. 继承（Inheritance） — Go没有继承，用"组合"代替
   就像乐高：你可以用已有的积木拼出新的造型

3. 多态（Polymorphism） — Go用接口实现
   同一个方法名，不同类型有不同的实现
   就像"叫"这个动作：
     狗叫：汪汪
     猫叫：喵喵
     都叫"叫"，但结果不同
```

#### Go的封装是怎么实现的？

```go
package bank

// 一个银行账户的例子
type Account struct {
    owner   string  // 小写开头 → 包外看不到
    balance float64 // 小写开头 → 包外看不到
    
    // 就像你的钱包：你能看到里面吗？不能→封装
}

// 但是你可以通过方法操作它
func (a *Account) Deposit(amount float64) {  // 存款
    if amount > 0 {
        a.balance += amount
    }
}

func (a *Account) Withdraw(amount float64) bool {  // 取款
    if amount > 0 && a.balance >= amount {
        a.balance -= amount
        return true
    }
    return false
}

func (a *Account) Balance() float64 {  // 查询余额
    return a.balance
}
```

**为什么封装好？**
```go
// 如果没有封装：
acc := Account{}
acc.balance = -1000  // ❌ 余额可以是负数！不合理！

// 有了封装：
acc := Account{}
// acc.balance = -1000  // ❌ 编译错误！看不到balance
acc.Deposit(100)
acc.Withdraw(50)        // ✅ 余额不能为负，安全！
```

**面试题：封装和性能的关系？**
```
封装看起来多了个方法调用，但Go编译器会内联小方法
实际运行中：
  acc.Balance() 和直接的 acc.balance 读取
  性能几乎一样（因为内联后没区别）
  
结论：不要为了"性能"破坏封装
```

---

### ⚡ 6.7 大厂面试题全集（方法篇）

**面试题1：下面代码输出什么？**
```go
type Num int

func (n Num) Add(m Num) Num {
    return n + m
}

func main() {
    var a Num = 10
    var b Num = 20
    fmt.Println(a.Add(b))  // ?
}
// 输出: 30
// 自定义类型Num底层是int，+操作对自定义类型有效
```

**面试题2：指针和值接收器的{}写法**
```go
type T struct {
    val int
}

func (t T) M1()  { fmt.Println(t.val) }
func (t *T) M2() { fmt.Println(t.val) }

func main() {
    var t T
    var p *T = &t
    
    p.M1()  // ✅ (*p).M1() 自动解引用
    t.M2()  // ✅ (&t).M2() 自动取地址
    
    // 接口就不行了
    var i interface{ M2() }
    // i = t  // ❌ T没有实现M2（指针接收器）
    i = &t   // ✅
}
```

**面试题3：值接收器什么时候导致bug？**
```go
type Slice []int

func (s Slice) Add(v int) {
    s = append(s, v)  // 修改的是副本！
}

func main() {
    s := Slice{1, 2}
    s.Add(3)
    fmt.Println(s)  // [1 2] 而不是 [1 2 3]！
}
// 修复：用指针接收器
func (s *Slice) Add(v int) {
    *s = append(*s, v)
}
```

**面试题4：方法值和方法表达式面试题**
```go
type Point struct{ X, Y float64 }

func (p Point) Add(q Point) Point {
    return Point{p.X + q.X, p.Y + q.Y}
}

func main() {
    p := Point{1, 2}
    
    // 方法值：receiver被绑定到p
    f := p.Add     // func(Point) Point
    fmt.Println(f(Point{3, 4}))  // {4, 6}
    
    // 方法表达式：receiver作为第一个参数
    g := Point.Add  // func(Point, Point) Point
    fmt.Println(g(p, Point{3, 4}))  // {4, 6}
    
    // 有什么用？
    // 可以把方法作为参数传递
    func mapPoint(arr []Point, fn func(Point) Point) []Point {
        res := make([]Point, len(arr))
        for i, p := range arr {
            res[i] = fn(p)
        }
        return res
    }
    // mapPoint(arr, p.Add) 把p.Add方法当成函数传进去
}
```

**面试题5：下面代码为什么编译出错？**
```go
type MyInt int

func (m MyInt) Double() MyInt {
    return m * 2
}

// 下面的会编译错误：
func (m *MyInt) Triple() MyInt {  // 可以
    return (*m) * 3
}

// 但不能给内置类型加方法
// func (m int) Quadruple() int {  // ❌ 编译错误！
//     return m * 4
// }
```

---

### ⚡ 6.8 嵌入结构体的超级扩展——组合模式

#### Go的结构体嵌入 vs Java继承

```
Java的继承（is-a）：
  class Cat extends Animal { ... }
  // Cat是一种Animal
  // 问题：如果Cat想同时有Flying能力？Java只能单继承

Go的组合（has-a）：
  type Cat struct {
      Legs           // Cat有腿（嵌入）
      *Fur           // Cat有毛（指针嵌入）
  }
  // Cat不是Legs，但Cat有Legs的功能
  // 可以任意组合，更灵活
```

#### 嵌入的三大用途

```go
// 用途1: 方法提升（让代码更简洁）
type Base struct{}
func (b Base) SayHi() { fmt.Println("Hi!") }

type Child struct{ Base }
var c Child
c.SayHi()  // 方法提升，就像Child也有SayHi一样

// 用途2: 实现接口组合
type Reader interface{ Read([]byte) (int, error) }
type Writer interface{ Write([]byte) (int, error) }
type ReadWriter interface {
    Reader
    Writer
}

// 用途3: override（模拟）
type Animal struct{}
func (a Animal) Speak() { fmt.Println("...") }

type Dog struct{ Animal }
func (d Dog) Speak() { fmt.Println("Woof!") }

func main() {
    d := Dog{}
    d.Speak()         // Woof! (Dog的Speak覆盖了Animal的)
    d.Animal.Speak()  // ... (还可以调被覆盖的)
}
```

---

---

### ⚡ 6.9 再补4道大厂面试题

**面试题6：Go中如何实现"多态"？**
```go
// Go没有继承，但可以用接口实现多态

// 定义接口
type Speaker interface {
    Speak() string
}

// 不同的实现
type Dog struct{}
func (d Dog) Speak() string { return "汪汪！" }

type Cat struct{}
func (c Cat) Speak() string { return "喵喵～" }

type Duck struct{}
func (d Duck) Speak() string { return "嘎嘎！" }

func main() {
    animals := []Speaker{Dog{}, Cat{}, Duck{}}
    
    for _, a := range animals {
        fmt.Println(a.Speak())  // 同一个方法名，不同行为
    }
    // 汪汪！
    // 喵喵～
    // 嘎嘎！
}

// 这就是多态：同一个接口，不同的实现
```

**面试题7：结构体嵌入时，方法冲突怎么办？**
```go
type A struct{}
func (a A) F() { fmt.Println("A的F") }

type B struct{}
func (b B) F() { fmt.Println("B的F") }

type C struct {
    A
    B
}

func main() {
    c := C{}
    // c.F()  // ❌ 编译错误：ambiguous selector!
    c.A.F()  // ✅ 明确调用A的F
    c.B.F()  // ✅ 明确调用B的F
}
```

**面试题8：String()方法是什么？**
```go
// 如果一个类型有 String() 方法
// fmt.Println 会自动调用它

type Person struct {
    Name string
    Age  int
}

func (p Person) String() string {
    return fmt.Sprintf("%s (%d岁)", p.Name, p.Age)
}

func main() {
    p := Person{"小明", 18}
    fmt.Println(p)     // 小明 (18岁) ← 自动调用了String()
    fmt.Printf("%v\n", p) // 也是小明 (18岁)
    fmt.Printf("%+v\n", p) // {Name:小明 Age:18}
    // 只有%v和默认打印会调用String()
}
```

**面试题9：值接收器和指针接收器，什么时候用哪个？**
```
用指针接收器的情况：
  - 需要修改接收器的值
  - 接收器是大结构体（避免拷贝）
  - 接收器里有sync.Mutex等不可复制类型
  - 你需要和指针方法保持方法集一致

用值接收器的情况：
  - 接收器是小类型（int, string等）
  - 接收器不应该被修改（不可变语义）
  - 你希望类型也能满足接口（值类型的方法集包含值方法）

记不住怎么办？
  → 先用指针接收器（最安全）
  → 等你有充分理由才用值接收器
```

---

---

### ⚡ 6.10 泛型方法（Go 1.27+即将到来）——给初中生

#### 什么是泛型方法？

```go
// 以前：方法不能有自己的类型参数
// 只能把类型参数放在结构体上

type Stack[T any] struct {
    items []T
}

// 结构体的方法可以引用结构体的类型参数T
func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

// 但如果方法想有自己的类型参数——不行！
// func (s *Stack[T]) Map[U any](f func(T) U) []U {  // ❌ Go 1.26前不行

// Go 1.27（即将）：方法可以有自己独立的类型参数！
type MySlice []int

func (ms MySlice) Transform[U any](f func(int) U) []U {
    result := make([]U, len(ms))
    for i, v := range ms {
        result[i] = f(v)
    }
    return result
}

// 使用：
ms := MySlice{1, 2, 3}
strs := ms.Transform(func(n int) string {
    return fmt.Sprintf("数%d", n)
})
// strs = ["数1", "数2", "数3"]
```

**限制：** 泛型方法不能用于接口实现。如果接口定义了方法，实现时不能是泛型方法。

---

> **下一章**：[第7章 接口](./ch07-interfaces.md) —— 接口是合约、接口类型、接口值、类型断言、类型分支等。
