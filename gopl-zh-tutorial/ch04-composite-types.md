# 第4章 复合数据类型

> Go的复合数据类型（数组、Slice、Map、结构体）是构建复杂数据结构的基石。理解它们的底层内存布局和行为差异，是写出高效Go代码的关键。

---

## 目录

- [4.1 数组](#41-数组)
- [4.2 Slice](#42-slice)
- [4.3 Map](#43-map)
- [4.4 结构体](#44-结构体)
- [4.5 JSON](#45-json)
- [4.6 文本和HTML模板](#46-文本和html模板)

---

## 4.1 数组

### 声明和初始化

```go
var a [3]int             // [0 0 0]（零值初始化）
a[0] = 1                 // 赋值

b := [3]int{1, 2, 3}     // [1 2 3]
c := [...]int{1, 2, 3}   // 编译器自动计数，等价于[3]int

// 指定索引初始化
d := [10]int{5: 2, 8: 3} // [0 0 0 0 0 2 0 0 3 0]
```

### 数组是值类型

**Go中数组是值类型**，赋值和传参都会复制整个数组：

```go
a := [3]int{1, 2, 3}
b := a                    // 复制整个数组
b[0] = 100
fmt.Println(a[0])         // 1（不受影响）

// 传参也复制
func zero(arr [3]int) {
    arr[0] = 0            // 只修改了副本
}
```

### 🔥 面试扩展

**高频题1：为什么Go数组是值类型而不是引用类型？**
> 这是Go的设计取舍。值类型语义清晰且安全（没有别名问题，不用担心被意外修改）。但大型数组的复制开销大。实际中建议：
> 1. **用Slice代替数组**（几乎99%的场景）
> 2. 必须用数组时可传指针：`func zero(arr *[1000]int)`

**高频题2：数组的底层内存布局？**
> 数组元素在内存中**连续线性排列**，元素之间没有填充（对齐除外）。所以`a[i]`通过`base + i*sizeof(elem)`直接计算地址，O(1)随机访问，CPU缓存友好。

**高频题3：比较数组可以用`==`吗？**
> 可以，但前提是**元素类型可比**（comparable）。`[3]int`可用`==`比较，但`[3]func(){}`不行（函数不可比较）。

---

## 4.2 Slice

### 底层结构

```go
// runtime/slice.go
type slice struct {
    array unsafe.Pointer  // 底层数组指针
    len   int             // 当前长度
    cap   int             // 最大容量
}
```

### 创建Slice

```go
// 1. make创建
s := make([]int, 5)       // len=5, cap=5, [0 0 0 0 0]
s := make([]int, 5, 10)   // len=5, cap=10

// 2. 字面量
s := []int{1, 2, 3}       // len=3, cap=3

// 3. 从数组切片
arr := [5]int{1, 2, 3, 4, 5}
s := arr[1:4]             // [2 3 4], len=3, cap=4
```

### append操作

```go
var s []int               // nil，len=0, cap=0
s = append(s, 1)          // 扩容：cap=1
s = append(s, 2)          // 扩容：cap=2
s = append(s, 3)          // 扩容：cap=4
s = append(s, 4, 5, 6)    // 可能扩容
```

### Slice扩容策略

```go
// Go 1.18+的扩容策略（简化）：
// cap < 256:  double
// cap >= 256:  cap += (cap + 3*256) / 4 (≈1.25倍)
```

### Slice使用陷阱

```go
// 陷阱1：共享底层数组
arr := [5]int{1, 2, 3, 4, 5}
a := arr[:2]  // [1 2], len=2, cap=5
b := arr[3:]  // [4 5], len=2, cap=2
a = append(a, 100)  // 修改了arr[2]=100！因为a的cap=5

// 陷阱2：append超过cap要扩容
a := make([]int, 2, 3)  // [0 0], len=2, cap=3
b := a[:2]              // 共享
a = append(a, 1)        // len=3, cap=3, 仍在原数组
a = append(a, 2)        // 扩容！a指向新数组，b仍指向旧数组

// 陷阱3：nil slice和empty slice
var s []int             // nil slice, s==nil为true
s = []int{}             // empty slice, s==nil为false, len=0
s = make([]int, 0)      // empty slice, s==nil为false
```

### 🔥 面试扩展

**高频题1：Slice的扩容为什么不是精确的2倍/1.25倍？**
> 实际扩容逻辑更复杂：
> - 容量小于256时，翻倍
> - 大于等于256时，增长因子≈(cap+3*256)/4，逐渐接近1.25
> - 还要考虑**内存对齐**，最终容量会round up到最接近的分配粒度
> 这种策略在"小容量快速翻倍"和"大容量节约内存"间取得平衡。

**高频题2：`append`函数是协程安全的吗？**
> **不。** 多个goroutine同时`append`到同一个slice会导致数据竞争（可能丢失数据，甚至panic）。多goroutine并发操作必须加锁或使用channel。

**高频题3：如何安全地复制slice？**
```go
src := []int{1, 2, 3}
dst := make([]int, len(src))
copy(dst, src)          // 完全独立副本

// 或使用append技巧
dst := append([]int(nil), src...)  // 一行复制
```

**高频题4：如何高效地从slice中间删除元素？**
```go
// 保持顺序
s = append(s[:i], s[i+1:]...)  // O(n)

// 不保持顺序（快速，O(1)）
s[i] = s[len(s)-1]
s = s[:len(s)-1]
```

**高频题5：`var s []int`和`s := []int{}`的区别？**
> - `var s []int`：nil slice，json.Marshal输出`null`
> - `s := []int{}`：empty slice，json.Marshal输出`[]`
> 很多场景需要区分。数据库查询返回空结果集时，用empty slice表示"查到0条"，用nil slice表示"未查询"。

**高频题6：`copy`函数的行为细节？**
> - `copy(dst, src)`复制`min(len(dst), len(src))`个元素
> - 如果dst和src有重叠，行为正确（如同`memmove`）
> - 可以从字符串复制到[]byte：`copy([]byte, "hello")`

---

## 4.3 Map

### 声明和操作

```go
// 创建
m := make(map[string]int)
m2 := map[string]int{
    "alice": 31,
    "bob":   25,
}
var m3 map[string]int  // nil map

// 增删改查
m["key"] = 42          // 插入/更新
v := m["key"]           // 取值（key不存在时返回零值）
v, ok := m["key"]       // 检查是否存在
delete(m, "key")        // 删除

// 遍历（顺序随机！）
for k, v := range m {
    fmt.Println(k, v)
}
```

### nil map

```go
var m map[string]int  // nil map
// m["key"] = 42      // ❌ panic: assignment to entry in nil map
delete(m, "key")      // ✅ 删除nil map安全（no-op）
v := m["key"]          // ✅ 读取nil map返回零值
fmt.Println(len(m))    // ✅ 0
```

### 🔥 面试扩展

**高频题1：Go map的底层数据结构？**
> Map是**哈希表**，结构如下：
```
hmap结构体:
  - count: 元素数量
  - B: 2^B个bucket
  - buckets: bucket数组指针
  - oldbuckets: 扩容时保留旧bucket
  - nevacuate: 扩容迁移进度

每个bucket (bmap)：
  - 最多8个key-value对
  - overflow指针（链接溢出bucket）
  - key/value分别存储（避免padding浪费）
```

**高频题2：map的扩容机制？**
> **触发条件**：装载因子（元素数/bucket数）> 6.5 或 溢出bucket过多
> **扩容方式**：
> - **等量扩容**（sameSizeGrow）：溢出bucket太多时重新整理（B不变）
> - **翻倍扩容**（biggerGrow）：元素过多时B+1
> **渐进式迁移**：不是一次性完成，而是在每次插入/删除/查找时逐步迁移，避免性能抖动

**高频题3：map遍历顺序为什么随机化？**
> Go 1.0的时候是有序的，开发者容易依赖这个未定义行为。Go 1.0之后**故意随机化**遍历起始位置和顺序，强迫开发者不依赖顺序。这是Go设计哲学的典型体现——避免未定义行为被依赖。

**高频题4：map是协程安全的吗？**
> **不。** 并发读写map会`fatal error: concurrent map read and map write`。解决方案：
> 1. 外部加`sync.RWMutex`
> 2. 使用`sync.Map`（适合读多写少或key稳定场景）
> 3. 使用`golang.org/x/sync/syncmap`

**高频题5：`sync.Map`和普通map+mutex各有什么优缺点？**

| 特性 | map + RWMutex | sync.Map |
|------|---------------|----------|
| 写多读少 | ❌ 锁竞争 | ❌ 性能差 |
| 读多写少 | ✅ 可接受 | ✅ 优秀（Read Mostly） |
| key反复写 | ✅ | ❌ key值会不断累积 |
| 场景 | 通用 | 读多写少、多goroutine写入不同key |

**高频题6：map可以作为函数参数吗？传值还是引用？**
> map本身是引用类型（底层是hmap指针），传递map副本时底层数据是共享的，函数内修改会影响外部。但slice和interface的传递同理——共享底层数据结构。

---

## 4.4 结构体

### 定义和初始化

```go
type Employee struct {
    ID        int
    Name      string
    Address   string
    Dob       time.Time
    Position  string
    Salary    int
    ManagerID int
}

// 顺序初始化（不推荐，字段顺序变了就错）
var dilbert Employee = Employee{1, "Dilbert", "...", ...}

// 推荐：指定字段名
dilbert := Employee{
    Name:   "Dilbert",
    Salary: 5000,
}
```

### 结构体指针

```go
// 访问字段时自动解引用
func EmployeeByID(id int) *Employee { ... }
employee := EmployeeByID(1)
employee.Salary = 6000  // (*employee).Salary的语法糖
```

### 结构体嵌入

```go
type Point struct {
    X, Y int
}

type Circle struct {
    Center Point  // 命名嵌入
    Radius int
}

type Wheel struct {
    Circle          // 匿名嵌入
    Spokes int
}

var w Wheel
w.X = 8            // w.Circle.Center.X的简写
w.Y = 8
w.Radius = 5
w.Spokes = 20
```

### 🔥 面试扩展

**高频题1：结构体的内存对齐规则？**
> Go结构体字段按声明顺序排列，每个字段的起始地址必须对齐到其对齐边界：
```go
type T1 struct {
    a bool   // 1字节，偏移0
    b int32  // 4字节，偏移4（不是1，插入了3字节padding）
    c int64  // 8字节，偏移8
}  // 大小：24字节（含尾部padding）

type T2 struct {
    a bool   // 1字节，偏移0
    c int64  // 8字节，偏移8
    b int32  // 4字节，偏移16
}  // 大小：24字节（尾部到24）

// 优化：大字段放前面
type T3 struct {
    c int64  // 8字节，偏移0
    b int32  // 4字节，偏移8
    a bool   // 1字节，偏移12
}  // 大小：16字节（无尾部padding时）
```

**高频题2：零值结构体`struct{}`的内存占用和使用场景？**
> `struct{}`**零字节**，用于：
> 1. **set集合**：`map[string]struct{}`
> 2. **信号channel**：`chan struct{}`（比`chan bool`更语义化）
> 3. **方法绑定**：作为receiver

**高频题3：Go有构造方法吗？惯用的初始化模式？**
> Go没有构造方法，习惯使用**工厂函数**（New函数）：
```go
func NewEmployee(id int, name string) *Employee {
    return &Employee{
        ID:   id,
        Name: name,
    }
}
```

**高频题4：匿名字段的方法提升机制？**
> 嵌入的匿名结构体的所有方法都被**提升**到外层结构体，好像外层结构体自己定义的一样。这实现了Go的"继承"（实际上是组合 + 语法糖）。

**高频题5：结构体可以包含自身类型的字段吗？**
> 直接包含不行（会导致无限递归），但可包含自身指针：
```go
type Node struct {
    Value int
    Next  *Node   // ✅
    // Next Node  // ❌ 编译错误
}
```

---

## 4.5 JSON

### 编码（Marshal）

```go
type Movie struct {
    Title  string   `json:"title"`
    Year   int      `json:"released"`
    Color  bool     `json:"color,omitempty"`
    Actors []string `json:"actors"`
}

movies := []Movie{
    {Title: "Casablanca", Year: 1942, Color: false, Actors: []string{"Humphrey", "Ingrid"}},
}

// 编码
data, _ := json.Marshal(movies)
fmt.Println(string(data))
// [{"title":"Casablanca","released":1942,"actors":["Humphrey","Ingrid"]}]

// 格式化编码
data, _ := json.MarshalIndent(movies, "", "    ")
```

### 解码（Unmarshal）

```go
var movies []Movie
err := json.Unmarshal(data, &movies)
```

### 流式编码/解码

```go
// 编码到Writer
json.NewEncoder(w).Encode(movies)

// 从Reader解码
json.NewDecoder(r).Decode(&movies)
```

### 🔥 面试扩展

**高频题1：`json.Marshal`的字段标签规则？**
> - `json:"name"`：字段名为name
> - `json:"-"`：忽略该字段
> - `json:"name,omitempty"`：零值时不输出
> - `json:"name,string"`：将值编码为JSON字符串
> - 只有**导出字段**（大写开头）才能被编解码

**高频题2：Go JSON序列化的性能问题和对策？**
> 标准库`encoding/json`使用反射，在大规模序列化时性能不佳。优化方案：
> 1. **预计算序列化器**：`jsonEncoderCache`
> 2. 使用第三方库：`jsoniter`（性能提高3-5倍），`ffjson`（代码生成）
> 3. 手动实现`MarshalJSON`/`UnmarshalJSON`
> 4. 使用`easyjson`（代码生成，性能最优）

**高频题3：如何自定义JSON序列化行为？**
```go
type Point struct{ X, Y int }

func (p Point) MarshalJSON() ([]byte, error) {
    return json.Marshal(map[string]int{
        "latitude":  p.X,
        "longitude": p.Y,
    })
}
```

**高频题4：`omitempty`标签的注意事项？**
> 零值字段（0, false, ""）会被省略。但**结构体类型的零值**不会被省略，即使所有字段都是零值。用指针可以让结构体字段被omitempty正确处理。

**高频题5：JSON编码中时间类型如何处理？**
> Go的`time.Time`默认编码为RFC3339格式（"2006-01-02T15:04:05Z07:00"），与前端交互友好。

---

## 4.6 文本和HTML模板

### text/template

```go
import "text/template"

const temp = `{{.TotalCount}} issues:
{{range .Items}}----------------------------------------
Number: {{.Number}}
User:   {{.User.Login}}
Title:  {{.Title | printf "%.64s"}}
Age:    {{.CreatedAt | daysAgo}} days
{{end}}`

report, _ := template.New("report").
    Funcs(template.FuncMap{"daysAgo": daysAgo}).
    Parse(temp)

report.Execute(os.Stdout, result)
```

### html/template

```go
import "html/template"

// 自动转义HTML，防止XSS攻击
const issueList = `<h1>{{.TotalCount}} issues</h1>`
```

### 🔥 面试扩展

**高频题1：`text/template`和`html/template`的核心区别？**
> `html/template`在输出时自动进行**上下文相关转义**（contextual auto-escaping），知道当前在HTML标签内、属性内、CSS内还是JavaScript内，实施对应的转义策略，防止XSS注入。

**高频题2：模板函数的流水线操作？**
> `{{.Title | printf "%.64s" ｜ len}}`：先格式化为64字符，再计算长度。Go模板的管道就是Unix管道的翻版。

## ⚡ 超级扩展

### ⚡ 4.1 数组的底层内存布局和性能

#### 数组的连续内存布局证明

```go
type arr [4]int32  // 每个元素4字节，共16字节连续

func main() {
    var a arr
    base := uintptr(unsafe.Pointer(&a))
    for i := 0; i < len(a); i++ {
        elemAddr := uintptr(unsafe.Pointer(&a[i]))
        fmt.Printf("a[%d] addr=%p offset=%d\n", i, elemAddr, elemAddr-base)
    }
}
// 输出:
// a[0] addr=0xc000... offset=0
// a[1] addr=0xc000... offset=4  ← 连续+4
// a[2] addr=0xc000... offset=8  ← 连续+4
// a[3] addr=0xc000... offset=12 ← 连续+4
```

#### 数组传参的性能对比

```go
const size = 10000000  // 1000万int元素 ≈ 80MB

type BigArray [size]int

// 值传递：复制80MB！
func processCopy(arr BigArray) int {
    return arr[0]  // 传参耗时 ~200ms
}

// 指针传递：复制8字节指针
func processPtr(arr *BigArray) int {
    return arr[0]  // 几乎零开销
}

func main() {
    var arr BigArray
    arr[size-1] = 42
    
    start := time.Now()
    processCopy(arr)
    fmt.Println("copy:", time.Since(start))  // ~200ms
    
    start = time.Now()
    processPtr(&arr)
    fmt.Println("ptr:", time.Since(start))   // ~ns
}
```

**规则：** 数组长度 > 100时，永远用指针传递。但在实践中，**99%的场景应该用切片而不是数组**。

---

### ⚡ 4.2 Slice底层完整结构和扩容机制

#### Slice的完整内存布局

```go
// runtime/slice.go
type slice struct {
    array unsafe.Pointer  // 底层数组指针
    len   int             // 当前元素个数
    cap   int             // 最大可容纳元素数
}

// 示例
s := make([]int, 3, 5)
// s.array → [0, 0, 0, ?, ?]  其中5个位置的空间
// s.len   = 3
// s.cap   = 5
//  ? 表示未分配元素（访问会导致panic）
```

#### Slice扩容的完整内存分配

```go
var s []int
for i := 0; i < 1025; i++ {
    s = append(s, i)
    // 每次扩容时cap的变化：
    // 0 → 1 (翻倍)
    // 1 → 2 (翻倍)
    // 2 → 4 (翻倍)
    // 4 → 8 (翻倍)
    // 8 → 16 (翻倍)
    // ...
    // 256 → 512 (翻倍, Go 1.18+策略: <256翻倍)
    // 512 → 640 (约1.25倍, >=256线性增长)
    // 640 → 800
    // 800 → 1008
    // 1008 → 1264
}
```

**Go 1.18+ 扩容源码：**

```go
// runtime/slice.go
func growslice(et *_type, old slice, cap int) slice {
    newcap := old.cap
    doublecap := newcap + newcap
    if cap > doublecap {
        newcap = cap
    } else {
        if old.cap < 256 {
            newcap = doublecap
        } else {
            for newcap < cap {
                newcap += (newcap + 3*256) / 4  // 约1.25倍
            }
        }
    }
    // 内存对齐（round up到最接近的分配粒度）
    // ...
    return slice{array, old.len, newcap}
}
```

#### append的常见陷阱大全

```go
// 陷阱1：append超过cap后，原切片不变
s := make([]int, 2, 3)
oldPointer := &s[0]
s = append(s, 1)  // 还在旧数组，cap=3
s = append(s, 2)  // 扩容！s指向新数组，oldPointer指向旧数组

// 陷阱2：切片共享底层数组的相互影响
arr := [5]int{1, 2, 3, 4, 5}
s1 := arr[0:3]  // [1,2,3], len=3, cap=5
s2 := arr[2:4]  // [3,4], len=2, cap=3
s1[2] = 999      // arr[2]=999, s2[0]也变成999

// 陷阱3：append不影响原切片
s := arr[0:2]    // [1,2], cap=5
s = append(s, 10)  // arr[2]=10, 还在共享
// 但如果s的cap=2（arr[3:5]），append会创建新数组

// 陷阱4：nil切片和空切片
var nilSlice []int           // json → null
emptySlice := []int{}        // json → []
nilSlice = append(nilSlice, 1) // ✅ 安全
```

#### 使用copy的安全深拷贝

```go
// copy(dst, src) 复制 min(len(dst), len(src)) 个元素

src := []int{1, 2, 3}
dst := make([]int, 2)
n := copy(dst, src)  // n=2, dst=[1,2]

// 完全拷贝（一行）
clone := make([]int, len(src))
copy(clone, src)

// 或者更加简短
clone := append([]int(nil), src...)  // 一行深拷贝
```

#### 删除元素的性能分析

```go
// 保持顺序的删除（慢但稳）
func removeOrdered[T any](s []T, i int) []T {
    return append(s[:i], s[i+1:]...)
    // 时间复杂度 O(n)
    // 需要复制 s[i+1:] 的所有元素
}

// 不保持顺序的删除（快但有副作用）
func removeUnordered[T any](s []T, i int) []T {
    s[i] = s[len(s)-1]
    return s[:len(s)-1]
    // 时间复杂度 O(1)
    // 把最后一个元素移到被删除位置，然后缩容
}

// 高效的过滤（使用单一赋值）
func filter[T any](s []T, keep func(T) bool) []T {
    n := 0
    for _, v := range s {
        if keep(v) {
            s[n] = v
            n++
        }
    }
    return s[:n]
}
```

---

### ⚡ 4.3 Map完整内部实现

#### hmap 结构体完整图解

```go
// runtime/map.go

type hmap struct {
    count     int              // 元素数量
    flags     uint8            // 状态标志
    B         uint8            // buckets数量 = 2^B
    noverflow uint16           // 溢出桶数量
    hash0     uint32           // 随机哈希种子

    buckets    unsafe.Pointer  // 2^B个桶的数组指针
    oldbuckets unsafe.Pointer  // 扩容时指向旧桶
    nevacuate  uintptr         // 渐进式扩容迁移进度

    extra *mapextra            // 额外信息
}

// 每个bucket的结构
type bmap struct {
    topbits  [8]uint8    // 每个key的哈希高8位
    keys     [8]keyType  // 8个key（实际编译时确定类型）
    values   [8]valType  // 8个value
    overflow *bmap       // 溢出桶指针
}

// map的内存分布图示:
//
// hmap {
//   count: 20
//   B:     2    (4个桶)
//   buckets: → [bucket0] [bucket1] [bucket2] [bucket3]
//                ↓溢出       ↓溢出
//             [overflow]  [overflow] ... 每个桶最多8个key-value
// }
//
// 当装载因子 > 6.5 或溢出桶过多时触发扩容
```

#### 装载因子的计算

```go
// 装载因子 = count / (2^B)
// 当 > 6.5 时触发翻倍扩容
// 这也是为什么map的B增长策略是：超过6.5时B+1

// 如果溢出桶过多（超过普通桶数量），触发等量扩容
// 等量扩容：B不变，整理数据（减少溢出桶）
// 翻倍扩容：B+1，数据均匀分散到新桶
```

#### 完整的哈希冲突解决流程

```go
// 插入 key="alice" 的完整流程：
// 1. 计算哈希：hash("alice") = 0x7f3a9b2c...
// 2. 取低B位确定桶：hash & (2^B - 1) → bucket index
// 3. 取高8位：hash >> (64-8) → top hash
// 4. 遍历桶的topbits数组：
//    4a. 找到空位（topbits[i] == 0）→ 插入
//    4b. topbits[i] == top hash → 比较key → 找到就更新/没找到继续
//    4c. 遍历到溢出桶
// 5. 如果所有溢出桶都满了 → 新建溢出桶
```

#### 扩容的完整流程

```go
// 翻倍扩容（B+1）的渐进式迁移：
// 1. 创建新的bucket数组（2^(B+1)个）
// 2. oldbuckets 指向旧数组
// 3. 触发迁移（每次写操作迁移2个桶）
// 4. 已迁移数据从oldbuckets中删除
// 5. 全部迁移完后，oldbuckets置空

// 迁移过程：
// key原本在bucket[i]中，新位置分到两个桶：
// 根据 hash & (2^B) 决定：
//   - 0 → 新位置还是 i
//   - 1 → 新位置是 i + 2^B
```

#### 遍历随机的完整实现

```go
// for k, v := range m {
//   fmt.Println(k, v)
// }

// 编译后调用 runtime.mapiterinit()
// 内部使用 fastrand() 生成随机起始位置

// runtime.mapiterinit 的核心逻辑：
// 1. 生成随机数 r = fastrand()
// 2. 用 r 选择起始bucket: startBucket = r & (2^B - 1)
// 3. 随机决定起始cell: startCell = uint8(r >> 8) & 7
// 4. 从 startBucket 的 startCell 开始遍历
// 5. 遍历完全部和溢出桶后，从下一个bucket继续
// 6. 当回到 startBucket 时结束
```

#### map并发安全的五种方案

```go
// 方案1: sync.RWMutex（最常用）
type SafeMap struct {
    mu sync.RWMutex
    m  map[string]int
}
func (s *SafeMap) Get(k string) int {
    s.mu.RLock()
    defer s.mu.RUnlock()
    return s.m[k]
}

// 方案2: sync.Map（适合读多写少）
var m sync.Map
m.Store("key", 1)          // 写入
v, ok := m.Load("key")      // 读取
m.LoadOrStore("key", 2)     // 原子性加载或存储
m.Range(func(k, v any) bool { return true })  // 安全遍历

// 方案3: 分片锁（高并发时减少锁竞争）
type ShardedMap struct {
    shards [32]struct {
        sync.RWMutex
        m map[string]int
    }
}
func (s *ShardedMap) getShard(key string) int {
    h := fnv.New32a()
    h.Write([]byte(key))
    return int(h.Sum32()) % 32
}

// 方案4: Channel序列化访问
// 方案5: 无锁数据结构（仅极高端场景）
```

---

### ⚡ 4.4 结构体内存对齐完整指南

#### 各类型对齐边界

| 类型 | 对齐边界 | 大小 |
|------|---------|------|
| bool, byte, int8, uint8 | 1字节 | 1 |
| int16, uint16 | 2字节 | 2 |
| int32, float32, rune | 4字节 | 4 |
| int64, float64, uint64 | 8字节 | 8 |
| string | 8字节 | 16 |
| 指针 | 8字节(64位) | 8 |
| slice | 8字节 | 24 |
| map | 8字节 | 8 |
| channel | 8字节 | 8 |
| interface{} | 8字节 | 16 |

#### 结构体的填充（padding）计算

```go
// 每个字段的起始地址必须对齐到其对齐边界
// 结构体总大小必须是对齐边界最大值的整数倍

// 未优化
// T1 的大小 = ?
type T1 struct {
    a bool    // offset=0, size=1
    // padding: 3字节 (因为下一个字段b需要4字节对齐)
    b int32   // offset=4, size=4
    c bool    // offset=8, size=1
    // padding: 7字节 (因为结构体最大对齐是8, 总大小必须是8的倍数)
}
// sizeof(T1) = 16

// 优化后：把大字段放前面
type T2 struct {
    b int32   // offset=0, size=4
    a bool    // offset=4, size=1
    c bool    // offset=5, size=1
    // padding: 2字节 (结构体最大对齐4, 当前5+1=6, 需要到8)
}
// sizeof(T2) = 8
```

**在实际工程中的优化技巧：**
```go
// 大数据结构通过字段重排可节省大量内存

type Bad struct {    // 大小: 48字节
    a string         // 16
    b int32          // 4 + 4 padding
    c string         // 16
    d bool           // 1 + 7 padding
}

type Good struct {  // 大小: 40字节（节省8字节）
    a string         // 16
    c string         // 16
    b int32          // 4
    d bool           // 1 + 3 padding
}
```

#### 带标签的结构体比较

```go
type A struct { X int; Y string }
type B struct { X int; Y string }

// 即使结构体字段完全一样，它们也是不同类型
// 但如果底层类型相同，且都是命名类型，需要显式转换

var a A
var b B
// b = a     // ❌ 类型不同
// a == b    // ❌ 类型不同

// 匿名结构体可以比较
var p struct{ X int; Y string }
var q struct{ X int; Y string }
p = q    // ✅ 相同底层类型
p == q   // ✅ 所有字段可比较
```

---

### ⚡ 4.5 JSON序列化深度分析

#### 标准库JSON编码器的完整调用链

```go
// json.Marshal(v)
// 1. 使用反射确定v的类型
// 2. 查找编码器缓存（encodersByType）
// 3. 如果v实现了json.Marshaler接口，调用v.MarshalJSON()
// 4. 否则根据类型使用对应的编码函数
// 5. 递归编码每个字段/元素
// 6. 写入bytes.Buffer
// 7. 返回[]byte
```

#### 结构体标签的完整语法

```go
type Config struct {
    // 基本标签
    Name  string `json:"name"`
    
    // omitempty: 零值时不输出
    Desc  string `json:"desc,omitempty"`
    
    // string: 将值编码为JSON字符串
    ID    int64  `json:"id,string"`
    
    // 忽略字段
    Pass  string `json:"-"`
    
    // 复合标签（多个包共享同一个struct）
    Field string `json:"field" yaml:"field" xml:"field"`
}
```

#### 自定义序列化的完整模式

```go
type Duration time.Duration

func (d Duration) MarshalJSON() ([]byte, error) {
    s := fmt.Sprintf(`"%s"`, time.Duration(d).String())
    return []byte(s), nil
}

func (d *Duration) UnmarshalJSON(data []byte) error {
    s := strings.Trim(string(data), `"`)
    dur, err := time.ParseDuration(s)
    if err != nil {
        return err
    }
    *d = Duration(dur)
    return nil
}

// 使用
var dur Duration
json.Unmarshal([]byte(`"3s"`), &dur)  // 3秒
```

#### 处理未知字段

```go
raw := `{"name":"alice","age":30,"unknown":"value"}`

// 方法1: 使用json.RawMessage保留未知数据
var partial struct {
    Name    string          `json:"name"`
    Unknown json.RawMessage `json:"-"`
}

// 方法2: 解码到map
var m map[string]interface{}
json.Unmarshal([]byte(raw), &m)
```

---

---

### ⚡ 4.6 大厂面试题全集（复合数据类型篇）

**面试题1：nil slice 和 empty slice 有什么区别？**
```go
var s1 []int        // nil slice（json → null）
s2 := []int{}       // empty slice（json → []）
s3 := make([]int, 0) // empty slice

fmt.Println(s1 == nil)  // true
fmt.Println(s2 == nil)  // false
fmt.Println(s3 == nil)  // false

// 序列化时的区别：
json.Marshal(s1)  // "null"
json.Marshal(s2)  // "[]"

// 什么时候用哪个？
// 数据库查询：没查过数据用nil，查到0条用empty
```

**面试题2：slice的扩容策略（Go 1.18+）**
```go
// 当 cap < 256：翻倍增长
// 当 cap >= 256：增长约 1.25 倍
//
// 例子：
// cap 1 → 2（翻倍）
// cap 2 → 4（翻倍）
// cap 100 → 200（翻倍）
// cap 256 → 512（翻倍）
// cap 512 → 640（约1.25倍）
// cap 1000 → 1280（约1.28倍）
//
// 为什么这么设计？
// 小切片：翻倍增长，快速到达合适大小
// 大切片：缓慢增长，避免浪费太多内存
```

**面试题3：为什么 for range map 的顺序是随机的？**
```go
m := map[string]int{"a": 1, "b": 2, "c": 3}

for k, v := range m {
    fmt.Println(k, v)
}
// 可能输出：a=1, b=2, c=3
// 也可能：b=2, a=1, c=3
// 也可能：c=3, a=1, b=2
// 每次运行可能都不同！

// Go故意这样做（Go 1.0之后），
// 防止程序员依赖map顺序——本来就不该依赖
```

**面试题4：map的并发读写为什么会panic？**
```go
m := make(map[int]int)

go func() {
    for {
        _ = m[1]    // 同时读
    }
}()

go func() {
    for {
        m[2] = 2   // 同时写
    }
}()
// fatal error: concurrent map read and map write

// 原因：map的内部结构（哈希表、扩容）不是并发安全的
// 方案1：加 sync.RWMutex
// 方案2：用 sync.Map
```

**面试题5：结构体内存对齐怎么优化？**
```go
// ❌ 不好（24字节）
type Bad struct {
    a bool    // 1字节 + 3填充
    b int32   // 4字节
    c bool    // 1字节 + 7填充
}

// ✅ 好（12字节）
type Good struct {
    b int32   // 4字节
    a bool    // 1字节
    c bool    // 1字节 + 2填充
}

// 规则：把大的字段放前面
// 按大小排序：int64 > int32/int64指针 > int16 > bool/byte
// 可以省下很多内存！
```

**面试题6：JSON序列化时怎么忽略某个字段？**
```go
type User struct {
    Name     string `json:"name"`
    Password string `json:"-"`         // "-" 表示永远不输出
    Email    string `json:"email,omitempty"`  // 空时不输出
}

func main() {
    u := User{
        Name:     "Alice",
        Password: "123456",
        Email:    "",
    }
    b, _ := json.Marshal(u)
    fmt.Println(string(b))  // {"name":"Alice"}
    // Password不见了！Email空也没有
}
```

**面试题7：copy函数怎么用的？**
```go
src := []int{1, 2, 3}
dst := make([]int, len(src))

n := copy(dst, src)  // 复制min(len(dst), len(src))个
// n = 3, dst = [1, 2, 3]

// 一行复制（经典写法）：
clone := append([]int(nil), src...)
```

**面试题8：切片删除元素的方法**
```go
// 从中间删除，保持顺序
s := []int{1, 2, 3, 4, 5}
i := 2
s = append(s[:i], s[i+1:]...)
// s = [1, 2, 4, 5]

// 不保持顺序（更快）
s[i] = s[len(s)-1]  // 把最后一个移到被删位置
s = s[:len(s)-1]    // 缩容
```

**面试题9：map的key可以是哪些类型？**
```
可以（comparable）：
  bool, 数值类型, string, pointer, channel,
  只包含可比较类型的 interface, struct, array

不可以：
  slice, map, function
  （因为不能比较 ==）
```

---

### ⚡ 4.7 map底层完整图解——给初中生的超级讲解

#### 哈希表是什么？（给初二小白）

```
哈希表 = 高效查找的"魔法抽屉"

想象你去图书馆还书：
  没有魔法抽屉：你要一本一本找，慢！
  有魔法抽屉：你把书名告诉管理员，管理员3秒找到
    → 这就是哈希表

魔法怎么实现的？
  书名 → 哈希函数（一个公式）→ 抽屉号
  "Go语言圣经" → 公式计算 → 3号抽屉
  打开3号抽屉 → 找到了！
```

#### Go map的内部结构（用图片描述）

```
一个map = 很多个"桶"（bucket）

假设 m := make(map[string]int, 8)

每个桶最多装8个key-value对
装满了就加一个"溢出桶"（overflow bucket）

m["alice"] = 25 的过程：
  1. 计算 "alice" 的哈希值
  2. 哈希值对8取模 → 决定放哪个桶
  3. 检查桶里是否有空位
  4. 有 → 放进去
  5. 没 → 放溢出桶
```

#### 什么是哈希冲突？

```
"alice" → 哈希 → 3号桶
"bob"   → 哈希 → 3号桶（和alice冲突了！）

解决方式：每个桶能装8个人
  先放alice（占一个位置）
  再放bob（挨着alice占另一个位置）
  同一个桶里的8个位置都满了 → 建"溢出"房间
```

#### 什么时候扩容？

```
触发条件1（装载因子 > 6.5）：
  平均每个桶装了6.5个以上的key → 翻倍扩容

触发条件2（溢出桶太多）：
  每个桶只有8个位置
  如果很多key冲突，溢出桶太多 → 等量扩容

扩容是"渐进式"的（不是一次性）：
  每次你操作map时，搬一点
  逐步把旧桶的数据搬到新桶
  避免同一时间太卡
```

**为什么 for range map 顺序随机？**
```
Go从1.0就故意做成随机的！
用 fastrand() 生成随机数
每次都从不同桶开始遍历
让程序员不依赖map顺序
```

---

### ⚡ 4.8 零拷贝字符串转换

正常的转换为什么慢：`[]byte(s)` 复制了全部字节
零拷贝（Go 1.20+）：
```go
import "unsafe"

func StringToBytes(s string) []byte {
    return unsafe.Slice(unsafe.StringData(s), len(s))
}

func BytesToString(b []byte) string {
    return unsafe.String(unsafe.SliceData(b), len(b))
}

// ⚠️ 返回的[]byte绝对不能修改！
// 因为string是只读的
```

---

### ⚡ 4.9 再补5道大厂面试题

**面试题10：为什么map的key不能是slice？**
```
Go规定map的key必须可用 == 比较
slice不能==比较（除了nil），所以不能当key
可以当key的：bool, int, string, pointer, struct（字段都可比）
```

**面试题11：如何合并两个map？**
```go
func mergeMaps(m1, m2 map[string]int) map[string]int {
    result := make(map[string]int, len(m1)+len(m2))
    for k, v := range m1 { result[k] = v }
    for k, v := range m2 { result[k] = v }
    return result
}
```

**面试题12：数组和slice传参的区别？**
```go
func changeArray(arr [3]int) { arr[0] = 100 }  // 改的是副本
func changeSlice(s []int)   { s[0] = 100 }     // 改的是原数据

arr := [3]int{1,2,3}; changeArray(arr); fmt.Println(arr[0])  // 1
sli := []int{1,2,3}; changeSlice(sli); fmt.Println(sli[0])   // 100
```

**面试题13：JSON中处理未知字段？**
```go
data := `{"name":"alice","extra":"unknown"}`
var m map[string]interface{}
json.Unmarshal([]byte(data), &m)
fmt.Println(m["extra"])  // unknown
```

**面试题14：数组和切片哪个更快？**
```
数组访问 = 切片访问（一样快，O(1)）
数组传参 = O(n)（复制整体）
切片传参 = O(1)（只复制24字节header）
结论：99%用切片
```

---

---

### ⚡ 4.10 Go 1.21+ 切片和map的新函数大全

#### 终于有了标准库！slices包和maps包

Go 1.21之前，切片的排序、查找都要自己写。
Go 1.21之后，slices包和maps包提供了所有常用操作！

#### slices包完整参考

```go
import "slices"

s := []int{3, 1, 4, 1, 5, 9, 2}

//--- 查找 ---
slices.Contains(s, 4)           // true
slices.Index(s, 4)              // 2（第一次出现的位置）
slices.IndexFunc(s, func(v int) bool { return v > 5 })  // 4（第一个>5的）

//--- 排序 ---
slices.Sort(s)                  // [1, 1, 2, 3, 4, 5, 9]
slices.IsSorted(s)              // true（检查是否已排序）
slices.SortFunc(s, func(a, b int) int { return b - a })  // 自定义排序

//--- 去重（必须已排序） ---
slices.Compact([]int{1, 1, 2, 2, 3})  // [1, 2, 3]（去除相邻重复）
slices.CompactFunc([]string{"a","A","b"}, func(a,b string) bool {
    return strings.ToLower(a) == strings.ToLower(b)
})  // ["a", "b"]

//--- 删除和插入 ---
s := []int{1, 2, 3, 4, 5}
s = slices.Delete(s, 1, 3)       // [1, 4, 5]（删除索引1到3）
s = slices.DeleteFunc(s, func(v int) bool { return v%2 == 0 })  // [1, 5]（删偶数）
s = slices.Insert(s, 1, 2, 3)    // [1, 2, 3, 5]（插入）

//--- 其他 ---
slices.Replace(s, 0, 2, 10, 20)  // [10, 20, 3, 5]
slices.Clip(s)                   // 减少容量 len(s) == cap(s)
slices.Equal(s1, s2)             // 比较两个切片是否相等
slices.Reverse(s)                // 反转

//--- 二分查找 ---
s := []int{1, 3, 5, 7, 9}
idx, found := slices.BinarySearch(s, 5)  // 2, true
```

#### maps包完整参考

```go
import "maps"

m := map[string]int{"a": 1, "b": 2, "c": 3}

// 复制map
m2 := maps.Clone(m)     // 浅复制（值如果是引用类型，共享底层）
m2["a"] = 100          // 不影响m

// 复制到指定的map
m3 := make(map[string]int)
maps.Copy(m3, m)        // 把m所有key-value复制到m3

// 删除匹配条件的key
maps.DeleteFunc(m, func(k string, v int) bool { return v < 2 })
// m = {"b": 2, "c": 3}

// 比较两个map
maps.Equal(m1, m2)                           // 值相等？
maps.EqualFunc(m1, m2, func(v1, v2 int) bool { return v1 < v2*2 })  // 自定义比较
```

#### clear(map) 和 clear(slice)（Go 1.21+）

```go
// clear(map)：清空所有键值对
m := map[string]int{"a": 1, "b": 2}
clear(m)
fmt.Println(len(m))  // 0

// clear(slice)：所有元素归零
s := []int{1, 2, 3}
clear(s)
fmt.Println(s)  // [0, 0, 0]（长度不变，元素变零值）

// 对于切片，clear 把每个元素设为零值
// 不是删除元素！
// 想删除全部元素：s = s[:0]
```

---

---

### ⚡ 4.11 数组、Slice、Map和结构体的完整流程图

#### 数组的内存布局图

```
var arr [5]int = [5]int{10, 20, 30, 40, 50}

在内存里连续排列：
┌──────┬──────┬──────┬──────┬──────┐
│  10  │  20  │  30  │  40  │  50  │
│int(8)│int(8)│int(8)│int(8)│int(8)│
└──────┴──────┴──────┴──────┴──────┘
 偏移0   偏移8   偏移16  偏移24  偏移32

每个元素=8字节（64位系统上的int）
总共=40字节连续
```

#### Slice的完整结构图

```
s := make([]int, 3, 5)
s[0] = 1; s[1] = 2; s[2] = 3

在内存里的slice结构体（24字节）：
┌──────────────────┐
│ slice {          │
│   array ----→ ┌──┬──┬──┬──┬──┐
│   len = 3    │ 1│ 2│ 3│  │  │  ← 底层数组(cap=5)
│   cap = 5    └──┴──┴──┴──┴──┘
│ }               ↑已用  ↑空闲
└──────────────────┘

s = append(s, 4)
  ┌──┬──┬──┬──┬──┐
  │ 1│ 2│ 3│ 4│  │  ← len=4, cap=5, 仍在原数组
  └──┴──┴──┴──┴──┘

s = append(s, 5, 6)
  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
  │ 1│ 2│ 3│ 4│ 5│ 6│  │  │  │  │ ← 扩容！新数组
  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
  len=6, cap=10（翻倍了）
```

#### Slice扩容策略流程图

```
          append(s, v)
              │
              ▼
    ┌─────────────────────┐
    │ len(s) < cap(s) ?    │
    └─────────┬───────────┘
              │
        ╭─────┴──────╮
      是↓            ↓否
        │             │
  ┌─────┴────┐  ┌────┴──────────┐
  │放原数组  │  │ 需要扩容！    │
  └──────────┘  └────┬──────────┘
                      │
              ┌───────┴────────┐
              │ cap < 256?     │
              └───────┬────────┘
                  ╭───┴───╮
                  │      │
                是↓      ↓否
                  │      │
            ┌────┴──┐ ┌─┴──────────┐
            │翻倍   │ │ ≈1.25倍    │
            └────┬──┘ └─────┬──────┘
                  │          │
                  ▼          ▼
            ┌────────────────────┐
            │ 分配新数组+复制数据  │
            └────────────────────┘
```

#### Map的完整工作流程图

```
            m["alice"] = 25
                  │
                  ▼
        ┌──────────────────┐
        │ 计算"alice"的哈希 │
        └────────┬─────────┘
                  │
                  ▼
        ┌──────────────────┐
        │ bucket = hash % 8│  → 假设得到3号桶
        └────────┬─────────┘
                  │
                  ▼
        ┌──────────────────────┐
        │ 检查3号桶的8个位置    │
        └────────┬─────────────┘
                  │
           ╭──────┴──────╮
         有空格↓          ↓无空格
           │              │
     ┌─────┴────┐  ┌─────┴──────────┐
     │ 插入到这个 │  │ 溢出桶       │
     │ 位置      │  │ 有空格？     │
     └──────────┘  └──────┬────────┘
                           │
                      ╭────┴───╮
                    有↓        ↓无
                      │        │
                ┌─────┴──┐ ┌───┴────────┐
                │ 插入   │ │ 新建溢出桶 │
                └────────┘ └────────────┘
```

#### Map扩容触发条件图

```
每次插入数据时检查：

              ┌──────────────┐
              │ 元素数量/桶数 │
              │ > 6.5 ?      │
              └──────┬───────┘
                是↓  │  ↓否
                  │  │
            ┌─────┴──┴────┐
            │ 翻倍扩容！  │
            │ B = B+1    │
            │ 桶数翻倍   │
            └─────┬──────┘
                  │
            ┌─────┴──────┐     ┌──────────────┐
            │ 渐进式迁移  │◄────│ 每次操作搬一点│
            └────────────┘     └──────────────┘

另外的触发条件：
  溢出桶太多（超过普通桶数）
  → 等量扩容（不增加桶数，但整理数据）
  → 减少溢出桶
```

#### 结构体内存对齐流程图

```
type Example struct {
    a bool    // 1字节
    b int32   // 4字节
    c int64   // 8字节
}

内存布局（未优化）：
┌─────┬──────┬──────┬──────────────┐
│ a(1)│填充3 │b(4)  │c(8)          │
│     │      │      │              │
└─────┴──────┴──────┴──────────────┘
偏移0   1~3    4~7     8~15
总大小 = 16字节（不是1+4+8=13！有padding）

优化后：把大的字段放前面
type Example2 struct {
    c int64   // 8字节  偏移0
    b int32   // 4字节  偏移8
    a bool    // 1字节  偏移12
    // 填充3字节到偏移16
}
┌──────────────────┬──────┬─────┬──────┐
│c(8)             │b(4)  │a(1) │填充3 │
└──────────────────┴──────┴─────┴──────┘
偏移0~7            8~11   12    13~15
总大小 = 16字节（但字段排列更合理）
```

---

> **下一章**：[第5章 函数](./ch05-functions.md) —— 函数声明、递归、多返回值、错误处理、defer、panic/recover。
