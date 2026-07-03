# 第11章 测试

> **大白话版：** 你写完作业要检查有没有做错。写程序也一样——写完了要"测试"一下对不对。
> Go语言自带检查工具，不用装额外软件，一条命令就能测！

---

## 零基础小课堂：测试是什么？

你写了一个"加法函数"：
```go
func 加法(a, b int) int {
    return a + b
}
```

你相信它算对了吗？测试一下：
- 1 + 1 = 2 ✅ 测过了
- 100 + 200 = 300 ✅ 测过了
- 0 + 0 = 0 ✅ 测过了
- (-1) + 1 = 0 ✅ 测过了

**测试 = 用各种输入试你的代码，看它对不对**

就像考试前做题复习：
- 你复习了各种题型
- 每种题型都做对了几道
- 考试时才不会翻车

**Go的测试超级简单：**
- 文件名：`xxx_test.go`
- 函数名：`TestXxx(t *testing.T)`
- 运行：`go test`

---

---

## 目录

- [11.1 go test](#111-go-test)
- [11.2 测试函数](#112-测试函数)
- [11.3 测试覆盖率](#113-测试覆盖率)
- [11.4 基准测试](#114-基准测试)
- [11.5 剖析](#115-剖析)
- [11.6 示例函数](#116-示例函数)

---

### 大白话go test

go test=Go自带的考试系统。

你写完代码→go test→系统自动检查对不对。

就像老师发了试卷，你做完后自动批改：
- 做对了 ✓
- 做错了 ✗
- 哪里错了 提示

## 11.1 go test

### 测试文件规范

- 文件名：`*_test.go`
- 函数名：`TestXxx(t *testing.T)`
- 位置：与被测试文件同目录

```bash
# 运行所有测试
go test ./...

# 详细输出
go test -v ./...

# 运行特定测试
go test -run TestFoo

# 运行测试并显示覆盖率
go test -coverprofile=coverage.out
go tool cover -html=coverage.out
```

---

### 大白话测试函数

func Test加法(t *testing.T) {
    结果 := 加法(1, 2)
    if 结果 != 3 {
        t.Errorf("1+2应该是3，得到%v", 结果)
    }
}

测试函数=检查你的代码对不对。
就像考试对答案：
1+2=3？✓ 过了
1+2=4？✗ 错了，报告错误

## 11.2 测试函数

### 表格驱动测试

```go
func TestIsPalindrome(t *testing.T) {
    tests := []struct {
        input string
        want  bool
    }{
        {"", true},
        {"a", true},
        {"aba", true},
        {"abc", false},
        {"kayak", true},
        {"A man, a plan, a canal: Panama", true},
    }
    for _, tt := range tests {
        t.Run(tt.input, func(t *testing.T) {
            if got := IsPalindrome(tt.input); got != tt.want {
                t.Errorf("IsPalindrome(%q) = %v, want %v", tt.input, got, tt.want)
            }
        })
    }
}
```

### t.Error vs t.Fatal

```go
t.Error("failed")   // 记录失败，继续执行
t.Fatal("abort")    // 记录失败，终止当前测试

// 建议：后续检查需要当前断言成功才用Fatal
```

### 子测试

```go
func TestFoo(t *testing.T) {
    t.Run("Case1", func(t *testing.T) {
        // ...
    })
    t.Run("Case2", func(t *testing.T) {
        // ...
    })
}
```

### 随机测试

```go
func TestRandom(t *testing.T) {
    for i := 0; i < 1000; i++ {
        a := rand.Int()
        b := rand.Int()
        got := Add(a, b)
        want := a + b
        if got != want {
            t.Fatalf("Add(%d, %d) = %d, want %d", a, b, got, want)
        }
    }
}
```

### 🔥 面试扩展

**高频题1：表格驱动测试（Table-Driven Test）为什么是Go的推荐模式？**
> 1. **数据驱动**：测试逻辑和测试数据分离
> 2. **易扩展**：添加新case只需添加一行数据
> 3. **可读性好**：一眼看出所有边界情况
> 4. **减少重复**：不需要为每个case写一个测试函数
> 这是Go官方和社区的推荐测试风格。

**高频题2：`go test -run`支持正则吗？**
> 支持。`-run`参数是一个正则表达式，匹配测试函数名。同时也支持子测试名：
> `go test -run 'TestFoo/Case1'`

**高频题3：`go test -v`展示的子测试缩进如何实现？**
> 当子测试失败时，父测试也被标记为失败。`-v`模式下，输出会体现测试的嵌套层级。子测试可以用`t.Run`创建任意多层嵌套。

**高频题4：测试依赖、测试顺序、并行测试？**
> Go的测试函数是顺序执行的（默认）。可以在测试中用`t.Parallel()`标记为可并行执行，go test会并行执行标记为并行的测试函数。但是，同一个测试文件内的并行测试**相互之间无视顺序**。

**高频题5：如何测试HTTP服务？**
```go
func TestHandler(t *testing.T) {
    // 使用测试服务器
    ts := httptest.NewServer(http.HandlerFunc(handler))
    defer ts.Close()

    resp, _ := http.Get(ts.URL + "/test")
    body, _ := io.ReadAll(resp.Body)
    resp.Body.Close()

    if string(body) != expected {
        t.Errorf("got %q, want %q", body, expected)
    }
}
```

**高频题6：测试文件的分类和命名？**
> - `*_test.go`：**内部测试**（package foo）
> - `*_external_test.go`：**外部测试**（package foo_test），模拟包外部调用
> Go同时支持这两种测试，后者可以避免循环导入。

---

### 大白话覆盖率

覆盖率=你的测试"覆盖"了代码的百分之多少。

就像你打扫房间：
- 只扫了客厅 → 覆盖率30%
- 全扫了 → 覆盖率100%

但覆盖率100%≠没bug！就像你全扫了也不代表每个角落都干净。

## 11.3 测试覆盖率

```go
$ go test -cover
coverage: 68.4% of statements

$ go test -coverprofile=coverage.out
$ go tool cover -html=coverage.out  // 浏览器可视化
$ go tool cover -func=coverage.out  // 每个函数覆盖率
```

### 🔥 面试扩展

**高频题1：Go的覆盖率分析和传统的行覆盖率有何不同？**
> Go使用**语句覆盖率（statement coverage）**而非行覆盖率。每个Go语句插桩，分析哪些语句被执行过。`go tool cover`以可视化方式展示每个语句块的覆盖情况（绿色=覆盖，红色=未覆盖）。

**高频题2：覆盖率接近100%就是好测试吗？**
> 不是。覆盖率不度量**正确性**：
> - 高覆盖率不能保证逻辑正确（可能所有断言都是错的）
> - 需要结合**变异测试（mutation testing）**来验证测试的质量
> - 100%覆盖率的测试但缺乏断言相当于什么都没测

---

### 大白话基准测试

基准测试=看你的代码跑得多快。

就像体测：
- 50米跑了几秒？
- 跳远跳了多少米？

代码也一样：
- 这个函数运行要多久？
- 优化之后快了多少？

## 11.4 基准测试

```go
func BenchmarkStringJoin(b *testing.B) {
    strings := []string{"hello", "world", "foo", "bar", "baz"}
    for i := 0; i < b.N; i++ {
        JoinStrings(strings)
    }
}

// 重置计时器
func BenchmarkComplex(b *testing.B) {
    setup()  // 不计入基准时间
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        doSomething()
    }
}

// 跳过基准测试中的一些迭代
func BenchmarkParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            doSomething()
        }
    })
}
```

### 运行基准测试

```bash
go test -bench=.                    # 运行所有benchmark
go test -bench=BenchmarkJoin       # 运行特定
go test -bench=. -benchmem         # 内存分配信息
go test -bench=. -count=10         # 运行10次
go test -bench=. -benchtime=10s    # 每个至少10秒
```

### 🔥 面试扩展

**高频题1：Benchmark结果的稳定性和可靠性？**
> `b.N`由go test自动调整（先小，逐步增加直到稳定）。影响基准精度因素：
> 1. CPU频率缩放（Turbo Boost）
> 2. GC干扰
> 3. 后台进程
> 4. 缓存热度
> 建议：`-count=5`运行多次，取平均值。

**高频题2：`b.ResetTimer()`和`b.StartTimer()`/`b.StopTimer()`的用途？**
> - `ResetTimer()`：丢弃配置/初始化时间
> - `StopTimer()`：暂停计时（如排序后验证结果）
> - `StartTimer()`：恢复计时
> 这些方法帮助精确测量被测试代码的耗时。

---

## 11.5 剖析

```go
$ go test -cpuprofile=cpu.out      # CPU剖析
$ go test -memprofile=mem.out      # 内存剖析
$ go test -blockprofile=block.out  # 阻塞剖析

$ go tool pprof cpu.out            # 分析
(pprof) top10                      # 前10耗时函数
(pprof) web                        # 浏览器火焰图
```

### 🔥 面试扩展

**高频题1：Go支持的剖析类型？**
> 1. **CPU剖析**：采样（默认每秒100次），确定CPU密集型函数
> 2. **内存剖析**：跟踪活跃分配和总分配
> 3. **阻塞剖析**：跟踪goroutine阻塞（channel、锁、系统调用）
> 4. **互斥剖析**：跟踪锁竞争
> 5. **Goroutine剖析**：查看当前所有goroutine堆栈
> 6. **线程剖析**：查看OS线程创建

**高频题2：pprof火焰图如何读懂？**
> - 每个矩形块是一个函数调用
> - 宽度代表CPU耗时（CPUprofile）或内存分配（memprofile）
> - 从上到下的调用链
> - 查找最宽的底部方块就是热点

---

## 11.6 示例函数

### Example测试

```go
func ExampleIsPalindrome() {
    fmt.Println(IsPalindrome("A man, a plan, a canal: Panama"))
    fmt.Println(IsPalindrome("hello"))
    // Output:
    // true
    // false
}

// 无序输出
func ExampleFoo() {
    // Unordered output:
    // hello
    // world
}
```

### 🔥 面试扩展

**高频题1：示例函数（Example Function）的三大作用？**
> 1. **作为测试**：`// Output:`注释是期望输出，go test自动比对
> 2. **作为文档**：`go doc`会自动显示示例函数。Godoc中会和类型/函数关联——通过函数名后缀关联（如`ExampleFoo_Bar`关联`Foo.Bar`方法）
> 3. **作为可执行参考代码**：用户可以直接复制示例运行

**高频题2：示例函数的命名规则？**
> - `Example()`：包的示例（在godoc中放在包文档顶部）
> - `ExampleFuncName()`：函数的示例
> - `ExampleTypeName_MethodName()`：方法的示例
> - `ExampleFuncName_suffix()`：多个变体

## ⚡ 超级扩展

### ⚡ 11.1 go test 完整生命周期

#### go test 的执行流程

```bash
# 1. 扫描 *_test.go 文件
# 2. 编译测试二进制
# 3. 运行测试
# 4. 输出结果

go test -v ./...
```

#### 测试缓存的正确理解

```go
// go test 缓存编译结果
// 只有当源码或测试文件改变时才重新编译
// 使用 -count=1 跳过缓存
go test -count=1 ./...
```

#### 测试标志大全

```bash
-v              # 详细输出
-run TestXxx    # 运行匹配的测试
-count N        # 每个测试运行N次（默认1）
-parallel N     # 最大并行数
-timeout D      # 超时（默认10分钟）
-short          # 短测试模式
-race           # 启用竞争检测
-coverprofile   # 覆盖率输出
-bench          # 运行基准测试
-benchmem       # 内存分配统计
-benchtime      # 基准测试时间
-cpuprofile     # CPU剖析
-memprofile     # 内存剖析
-blockprofile   # 阻塞剖析
```

---

### ⚡ 11.2 测试的高级模式

#### HTTP Test 完整示例

```go
func TestHandleGet(t *testing.T) {
    // 创建测试服务
    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte(`{"status":"ok"}`))
    }))
    defer ts.Close()
    
    // 发送请求
    resp, err := http.Get(ts.URL + "/api/status")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()
    
    // 验证响应
    body, _ := io.ReadAll(resp.Body)
    if resp.StatusCode != http.StatusOK {
        t.Errorf("status = %d, want %d", resp.StatusCode, http.StatusOK)
    }
    if !bytes.Contains(body, []byte(`"status":"ok"`)) {
        t.Errorf("body = %s, want contain status ok", body)
    }
}
```

#### 测试数据库操作的模式

```go
func TestDB(t *testing.T) {
    // 使用SQLite内存数据库（不需要外部依赖）
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatal(err)
    }
    defer db.Close()
    
    // 运行迁移
    db.Exec(`CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)`)
    
    // 测试插入和查询
    _, err = db.Exec(`INSERT INTO users (name) VALUES (?)`, "alice")
    if err != nil {
        t.Fatal(err)
    }
}
```

#### 测试的Setup和Teardown

```go
func TestMain(m *testing.M) {
    log.Println("=== SETUP ===")
    // 初始化测试数据库、创建临时文件等
    
    code := m.Run()  // 运行所有测试
    
    log.Println("=== TEARDOWN ===")
    // 清理资源
    
    os.Exit(code)
}
```

#### Golden File 测试模式

```go
func TestGolden(t *testing.T) {
    input := `{"name":"test"}`
    got := processJSON(input)
    
    golden := filepath.Join("testdata", t.Name()+".golden")
    if *update {
        os.WriteFile(golden, []byte(got), 0644)
    }
    
    want, _ := os.ReadFile(golden)
    if got != string(want) {
        t.Errorf("got != want\ngot:\n%s\nwant:\n%s", got, want)
    }
}
```

---

### ⚡ 11.3 Fuzzing测试（Go 1.18+）

```go
func FuzzReverse(f *testing.F) {
    // 种子数据
    f.Add("hello")
    f.Add("世界")
    f.Add("12345")
    
    f.Fuzz(func(t *testing.T, s string) {
        reversed := Reverse(s)
        doubleReversed := Reverse(reversed)
        if s != doubleReversed {
            t.Errorf("Before: %q, after: %q", s, doubleReversed)
        }
        if utf8.ValidString(s) && !utf8.ValidString(reversed) {
            t.Errorf("Reverse produced invalid UTF-8: %q", reversed)
        }
    })
}

// 运行：
// go test -fuzz FuzzReverse -fuzztime 30s
```

---

---

### ⚡ 11.4 测试的方方面面——给初中生

#### 什么是单元测试？（给初二小白）

```
单元测试 = 单独测试每个函数

就像你组装一台电脑：
  先单独测电源是否能通电 ✅
  再单独测CPU是否能工作 ✅
  ...
  然后组装到一起测试

如果你不单独测试，直接组装：
  电脑不亮了 → 你找去吧，可能是电源、主板、显卡... 哪个的问题？
```

#### 测试文件命名规则

```go
// 文件名必须是 *_test.go
// calc.go       → 源码文件
// calc_test.go  → 测试文件

// 测试函数必须是 TestXxx(t *testing.T)
func TestAdd(t *testing.T) { ... }
func TestSubtract(t *testing.T) { ... }
```

#### 一个完整的测试例子

```go
// calc.go
func Add(a, b int) int {
    return a + b
}

// calc_test.go
package calc

import "testing"

func TestAdd(t *testing.T) {
    // 给的各种输入
    cases := []struct {
        a, b, want int
    }{
        {1, 2, 3},
        {0, 0, 0},
        {-1, 1, 0},
        {100, 200, 300},
        {-5, -3, -8},
        {999999, 1, 1000000},
    }
    
    for _, c := range cases {
        got := Add(c.a, c.b)
        if got != c.want {
            t.Errorf("Add(%d, %d) = %d, want %d", c.a, c.b, got, c.want)
        }
    }
}
```

---

### ⚡ 11.5 测试覆盖率的完整解释

#### 什么是覆盖率？（给初中生）

```
代码覆盖率 = 你的代码有多少行被测试执行到了

就像你做作业：
  老师出了10道题
  你做了8道
  → 覆盖率 80%
```

#### 如何查看覆盖率

```bash
# 1. 生成覆盖率数据
go test -coverprofile=coverage.out ./...

# 2. 在终端看每个函数的覆盖率
go tool cover -func=coverage.out

# 3. 在浏览器看（绿色=覆盖，红色=没覆盖）
go tool cover -html=coverage.out
```

---

### ⚡ 11.6 基准测试（Benchmark）的超级详解

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {    // b.N 由Go自动调整
        Add(1, 2)
    }
}

// 运行：go test -bench=.
// 输出：BenchmarkAdd-8  1000000000  0.25 ns/op
//                           ↑运行次数  ↑每次耗时
```

---

### ⚡ 11.7 大厂面试题全集（测试篇）

**面试题1：Table-driven test是什么？**
```go
// 表格驱动测试 = 把测试数据放在一个表格里循环执行
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    int
        want    int
        wantErr bool
    }{
        {"正常除法", 10, 2, 5, false},
        {"被除数为0", 0, 5, 0, false},
        {"除数为0", 10, 0, 0, true},
        {"负数除法", -10, 2, -5, false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)
            if tt.wantErr && err == nil {
                t.Error("期望错误但没有")
            }
            if !tt.wantErr && err != nil {
                t.Errorf("不期望的错误: %v", err)
            }
            if got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

**面试题2：子测试（Subtests）有什么用？**
```
子测试的优势：
1. 一个测试用例失败，不影响其他用例继续执行
2. 可以单独运行某个用例：go test -run TestDivide/被除数为0
3. 并行执行：t.Parallel() 让子测试并行
4. 清晰的层次结构，一目了然
```

**面试题3：如何测试HTTP服务器？**
```go
func TestPing(t *testing.T) {
    // 创建测试 HTTP 服务器
    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintln(w, "pong")
    }))
    defer ts.Close()
    
    resp, err := http.Get(ts.URL + "/ping")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()
    
    body, _ := io.ReadAll(resp.Body)
    if string(body) != "pong\n" {
        t.Errorf("got %q, want %q", body, "pong\n")
    }
}
```

**面试题4：Go的Fuzzing测试（模糊测试，Go 1.18+）**
```go
// Fuzzing = 让计算机自动生成各种奇怪的输入来测你的代码
// 就像你测试一个"接受用户输入"的程序：
//   让计算机自动生成各种随机输入
//   空字符串、超长字符串、特殊字符...
//   看会不会崩溃

func FuzzHello(f *testing.F) {
    // 种子语料库（一些初始输入）
    f.Add("hello")
    f.Add("world")
    
    f.Fuzz(func(t *testing.T, s string) {
        Hello(s)  // 用随机字符串调用
    })
}

// 运行：go test -fuzz FuzzHello
```

**面试题5：Mock（模拟对象）在Go中怎么实现？**
```go
// Mock = 造一个假的实现，用来替代真实的依赖
// 比如测试支付功能，不能真的去扣钱
// 就造一个"假的支付接口"

// 1. 先用接口定义行为
type Payment interface {
    Charge(amount int) error
}

// 2. 真实现（操作真实银行）
type RealPayment struct{}
func (r *RealPayment) Charge(amount int) error {
    // 真实的扣款逻辑
    return nil
}

// 3. Mock实现（假的，用于测试）
type MockPayment struct{}
func (m *MockPayment) Charge(amount int) error {
    if amount <= 0 {
        return errors.New("金额必须大于0")
    }
    return nil  // 不真的扣钱
}
```

---

---

### ⚡ 11.8 测试的更多细节——给初中生的超级讲解

#### 什么是单元测试的完整例子？

```go
// main.go
package main

func Add(a, b int) int {
    return a + b
}

func IsEven(n int) bool {
    return n%2 == 0
}

// main_test.go
package main

import "testing"

func TestAdd(t *testing.T) {
    // 测试用例：正常情况
    result := Add(1, 2)
    if result != 3 {
        t.Errorf("Add(1, 2) = %d, want 3", result)
    }
    
    // 测试负数
    result = Add(-1, 1)
    if result != 0 {
        t.Errorf("Add(-1, 1) = %d, want 0", result)
    }
    
    // 测试大数
    result = Add(1000000, 2000000)
    if result != 3000000 {
        t.Errorf("Add(1000000, 2000000) = %d, want 3000000", result)
    }
}

func TestIsEven(t *testing.T) {
    if !IsEven(2) {
        t.Error("IsEven(2) = false, want true")
    }
    if IsEven(3) {
        t.Error("IsEven(3) = true, want false")
    }
    if !IsEven(0) {
        t.Error("IsEven(0) = false, want true")
    }
}
```

#### go test的输出怎么看？

```bash
# 全部通过：
$ go test -v
=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
=== RUN   TestIsEven
--- PASS: TestIsEver (0.00s)
PASS
ok      myproject 0.352s

# 有测试失败：
$ go test -v
=== RUN   TestAdd
--- FAIL: TestAdd (0.00s)
    main_test.go:10: Add(1, 2) = 4, want 3  ← 错误信息
FAIL
FAIL    myproject 0.351s
```

#### 测试文件可以放在不同的包里

```go
// 方式1：内部测试（和源码同包）
package main

// 方式2：外部测试（模拟其他人用你的包）
package main_test

// 外部测试的好处：
// 像真正的用户一样测试你的包
// 只能访问导出的函数/类型
```

#### t.Helper() 的使用

```go
// 当你有辅助函数时，用 t.Helper()
// 这样出错时显示的是调用者位置，不是辅助函数位置

func assertEqual(t *testing.T, got, want int) {
    t.Helper()  // 标记为辅助函数
    if got != want {
        t.Errorf("got %d, want %d", got, want)
    }
}

func TestAdd(t *testing.T) {
    assertEqual(t, Add(1, 2), 3)  // 如果出错，报错指向这一行
    // 而不是 assertEqual 函数内部的那一行
}
```

#### t.Cleanup() 的使用

```go
func TestWithFile(t *testing.T) {
    f, err := os.CreateTemp("", "test")
    if err != nil {
        t.Fatal(err)
    }
    
    // 注册清理函数
    t.Cleanup(func() {
        os.Remove(f.Name())  // 测试结束后删除临时文件
    })
    
    // 测试用文件...
}
```

---

### ⚡ 11.9 示例函数的超级详解

#### 示例函数到底是什么？

```go
// 示例函数（Example Function）
// 既是文档，又是测试！

func ExampleAdd() {
    result := Add(1, 2)
    fmt.Println(result)
    // Output: 3  ← 这个注释就是"期望输出"
}

// 运行：go test 会自动检查 Output 是否匹配
// 如果Add(1,2)返回的不是3，测试失败！
```

**示例函数的命名规则：**
```go
// 给整个包的示例
func Example() { ... }

// 给函数的示例
func ExampleAdd() { ... }

// 给方法的示例
func ExampleFile_Read() { ... }  // File.Read方法的示例

// 多个示例
func ExampleAdd_second() { ... }  // 后缀区分
```

**示例函数在godoc中的显示：**
```
当用户输入 go doc Add 时
会自动显示 ExampleAdd 的代码
用户可以直接复制运行！
```

---

### ⚡ 11.10 再补5道大厂面试题

**面试题7：写一个测试，测试除数为0的情况？**
```go
func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("除法：除数不能为0")
    }
    return a / b, nil
}

func TestDivide(t *testing.T) {
    // 测试正常情况
    result, err := Divide(10, 2)
    if err != nil {
        t.Fatalf("不期望的错误: %v", err)
    }
    if result != 5 {
        t.Errorf("Divide(10, 2) = %d, want 5", result)
    }
    
    // 测试除数为0
    _, err = Divide(10, 0)
    if err == nil {
        t.Error("期望错误但没有")
    }
}
```

**面试题8：Benchmark和Test能放在同一个文件吗？**
```go
// 可以！同一个_test.go文件里可以同时有
// TestXxx 和 BenchmarkXxx 函数
// 不用分开
```

**面试题9：怎么测试一个会panic的函数？**
```go
// 被测试函数
func SafeIndex(arr []int, i int) int {
    if i < 0 || i >= len(arr) {
        panic("索引越界")
    }
    return arr[i]
}

// 测试
func TestSafeIndex(t *testing.T) {
    // 测试正常情况
    result := SafeIndex([]int{1, 2, 3}, 1)
    if result != 2 {
        t.Errorf("got %d, want 2", result)
    }
    
    // 测试异常情况（应该panic）
    defer func() {
        if r := recover(); r == nil {
            t.Error("期望panic但没有")
        }
    }()
    SafeIndex([]int{1, 2, 3}, 10)  // 应该panic
}
```

**面试题10：TestMain是干什么的？**
```go
// TestMain 是测试的"入口函数"
// 在所有TestXxx之前和之后执行

func TestMain(m *testing.M) {
    fmt.Println("===== 所有测试开始前执行一次 =====")
    
    // 初始化：建数据库、开文件、连服务器...
    
    code := m.Run()  // 运行所有Test函数
    
    // 清理：删数据库、关文件、断服务器...
    
    fmt.Println("===== 所有测试结束后执行一次 =====")
    
    os.Exit(code)  // 返回测试结果
}
```

**面试题11：并行测试（t.Parallel）怎么用？**
```go
func TestParallel1(t *testing.T) {
    t.Parallel()  // 标记为可并行运行
    time.Sleep(1 * time.Second)
    fmt.Println("测试1完成")
}

func TestParallel2(t *testing.T) {
    t.Parallel()
    time.Sleep(1 * time.Second)
    fmt.Println("测试2完成")
}

// 默认情况下：TestParallel1和TestParallel2同时运行
// 总时间：1秒（而不是2秒）
```

---

---

### ⚡ 11.11 synctest——并发测试的救星（Go 1.25稳定）

#### 测试并发代码为什么难？

```
普通代码的测试：
  输入已知 → 输出可预测 → 好测

并发代码的测试：
  time.Sleep(1秒) → 真的等1秒 → 测试慢！
  goroutine顺序不确定 → 结果不确定 → 难验证！

synctest = 让时间"加速"
```

#### testing/synctest包的基本用法

```go
import "testing/synctest"

func TestConcurrentCode(t *testing.T) {
    synctest.Run(func() {
        done := make(chan bool)
        
        go func() {
            time.Sleep(1 * time.Hour)  // synctest下：几乎立刻完成！
            done <- true
        }()
        
        select {
        case <-done:
            // 通过
        case <-time.After(1 * time.Second):
            t.Error("1小时后的操作在1秒内没完成")
        }
    })
}
```

**synctest能做什么？**
```
1. 假的time.Now()：时间可以由你控制
2. 假的time.Sleep()：不用真的等待
3. time.After()立刻触发
4. 所有goroutine调度可以预测

就像玩游戏的"加速模式"：
  游戏里的1小时 ＝ 现实中的1秒
  测试快了3600倍！
```

---

---

### ⚡ 11.12 t.Parallel、测试缓存、httptest详解

#### t.Parallel()——并行测试

```go
// Go默认按顺序执行测试
// 但如果你的测试不互相影响，可以并行

func TestSlow1(t *testing.T) {
    t.Parallel()  // 标记为可并行
    time.Sleep(2 * time.Second)
}

func TestSlow2(t *testing.T) {
    t.Parallel()
    time.Sleep(2 * time.Second)
}

// 顺序执行：4秒
// 并行执行：2秒（两个同时跑！）

// 注意：并行测试不能共享变量！
```

#### 测试缓存——为什么第二次那么快？

```bash
# 第一次运行：
go test ./...  # 编译+测试，3秒

# 第二次运行（源码没变）：
go test ./...  # 直接输出 cached，0.1秒！

# Go的测试缓存机制：
# 1. 编译结果缓存
# 2. 测试结果缓存（ok 或 FAIL）
# 3. 只有源码或依赖变了才重新测试

# 跳过缓存：
go test -count=1 ./...

# 清理测试缓存：
go clean -testcache
```

#### httptest——测试HTTP服务器

```go
import "net/http/httptest"

func TestHelloHandler(t *testing.T) {
    // 创建测试服务器
    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintln(w, "Hello, World!")
    }))
    defer ts.Close()  // 测试完后关闭
    
    // 发送请求
    resp, err := http.Get(ts.URL + "/hello")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()
    
    // 验证响应
    body, _ := io.ReadAll(resp.Body)
    if string(body) != "Hello, World!\n" {
        t.Errorf("got %q, want %q", body, "Hello, World!\n")
    }
}
```

#### golden file测试模式

```go
// golden file = 把预期输出存到文件里
// 避免在测试代码里写超长字符串

var update = flag.Bool("update", false, "更新golden文件")

func TestGolden(t *testing.T) {
    got := myFunction()
    
    golden := filepath.Join("testdata", t.Name()+".golden")
    
    if *update {
        os.WriteFile(golden, []byte(got), 0644)
        return
    }
    
    want, _ := os.ReadFile(golden)
    if got != string(want) {
        t.Errorf("输出不匹配\ngot:\n%s\nwant:\n%s", got, want)
    }
}

// 运行：go test -update   → 更新所有golden文件
// 正常：go test           → 和golden文件比较
```

---

---

### ⚡ 11.13 测试的完整流程图集合

#### go test的执行流程图

```
          go test -v ./...
               │
               ▼
     ┌─────────────────────┐
     │ 扫描 *_test.go 文件   │
     └──────────┬──────────┘
                │
                ▼
     ┌─────────────────────┐
     │ 编译测试二进制        │
     └──────────┬──────────┘
                │
                ▼
     ┌─────────────────────┐
     │ 检查是否有TestMain   │
     └──────────┬──────────┘
                │
          ╭─────┴─────╮
          │           │
        有↓           ↓无
          │           │
    ┌─────┴──────┐ ┌──┴──────────────┐
    │执行TestMain│ │按顺序执行所有    │
    │(一次Setup  │ │TestXxx函数      │
    │ 一次Cleanup│ │                 │
    └─────┬──────┘ └──┬──────────────┘
          │           │
          ▼           ▼
    ┌────────────────────────┐
    │ 输出测试结果             │
    │ PASS 或 FAIL (含行号)    │
    └────────────────────────┘
```

#### 测试函数的执行流程（单个）

```
          go test -run TestAdd
               │
               ▼
     ┌─────────────────────┐
     │ 调用 TestAdd(t)      │
     └──────────┬──────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ 执行测试代码              │
     │ t.Error() → 记录失败+继续  │
     │ t.Fatal() → 记录失败+停止  │
     │ t.Skip()  → 跳过此测试    │
     │ t.Parallel() → 标记并行  │
     └──────────┬───────────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ 测试结束                 │
     │ 没调用t.Error → PASS     │
     │ 调用了t.Error → FAIL     │
     └──────────────────────────┘
```

#### 表格驱动测试的结构图

```go
func TestDivide(t *testing.T) {
    tests := []struct{   ← 测试数据表
        name    string
        a, b    int
        want    int
        wantErr bool
    }{
        {"正数÷正数", 10, 2, 5, false},
        {"负数÷正数", -10, 2, -5, false},
        {"除数为零", 10, 0, 0, true},
        {"零÷正数", 0, 5, 0, false},
        {"大数测试", 1000000, 2, 500000, false},
    }

                    ↓
    ┌──────────────────────────────────┐
    │ for _, tt := range tests {       │
    │     t.Run(tt.name, func(t *T) {  │
    │         got, err := Divide(tt)   │
    │         // 断言...               │
    │     })                           │
    │ }                                │
    └──────────────────────────────────┘
}                    ↓
              5个测试用例都运行
             每个可以单独执行
             go test -run TestDivide/正数÷正数
```

#### 测试覆盖率的工作图

```
         go test -coverprofile=coverage.out
                      │
                      ▼
         ┌─────────────────────────┐
         │ 编译器在每行代码插入标记 │
         └──────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │ 运行测试                 │
         │ 执行到某行 → 标记为"已覆盖"│
         │ 没执行到 → 标记为"未覆盖"│
         └──────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │ 输出覆盖率报告            │
         │ 浏览器查看(绿色/红色)      │
         │ go tool cover -html=o.out │
         └─────────────────────────┘
```

#### 基准测试的工作原理

```
         go test -bench=. -benchmem
                      │
                      ▼
         ┌─────────────────────────┐
         │ 先让b.N=1，运行一次       │
         │ 如果运行时间<基准时间      │
         │ (默认1秒)→ 加倍b.N       │
         │ 继续测试直到时间足够       │
         └──────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │ b.N=1 → 2 → 4 → 8 → 16  │
         │ ... → 直到结果稳定       │
         └──────────┬──────────────┘
                    │
                    ▼
BenchmarkXxx-8  100000000  0.25 ns/op  0 B/op  0 allocs/op
    │           │          │           │       │
   CPU核数   运行次数   每次耗时    每次内存  每次分配次数
```

#### pprof性能剖析的工作流

```
         ┌───────────────┐
         │ 你的程序       │
         └───┬───────────┘
             │
             ├── go test -bench=. -cpuprofile=cpu.out
             │     ↓
             │   go tool pprof cpu.out
             │     ↓
             │   (pprof) top10
             │   (pprof) web     → 火焰图
             │
             ├── go test -memprofile=mem.out
             │
             └── import _ "net/http/pprof"
                   http://localhost:6060/debug/pprof/
```

---

---

### ⚡ 11.14 测试的纳米级图解大全

#### go test完整执行流程

```
           go test ./...
               │
               ▼
     ┌──────────────────────┐
     │ 1. 查找 *_test.go     │
     │    扫描所有Go源文件   │
     └──────────┬───────────┘
               │
               ▼
     ┌──────────────────────┐
     │ 2. 编译测试二进制      │
     │    main包 + 测试文件  │
     └──────────┬───────────┘
               │
               ▼
     ┌──────────────────────┐
     │ 3. 检查TestMain       │  ← 如果有TestMain，用它做入口
     │    有？→ 执行它       │
     │    没有？→ 直接运行   │
     └──────────┬───────────┘
               │
               ▼
     ┌──────────────────────┐
     │ 4. 按顺序执行每个     │
     │    TestXxx函数         │
     │                        │
     │ 对每个Test函数：       │
     │ ├─ 创建t *testing.T   │
     │ ├─ 执行测试代码       │
     │ ├─ t.Parallel()?      │
     │ │ 是→等所有非并行完成 │
     │ │ 否→立即执行        │
     │ └─ 记录PASS/FAIL     │
     └──────────┬───────────┘
               │
               ▼
     ┌──────────────────────┐
     │ 5. 输出结果           │
     │    ok  包名  时间     │
     │    FAIL 包名  时间    │
     └──────────────────────┘
```

#### 表格驱动测试结构图

```go
func TestAdd(t *testing.T) {
    // 测试数据表
    tests := []struct {
        name string        // 测试用例名称
        a, b int           // 输入
        want int           // 期望输出
    }{
        {name: "正数相加", a: 1, b: 2, want: 3},
        {name: "负数相加", a: -1, b: -2, want: -3},
        {name: "零值",    a: 0, b: 0, want: 0},
        {name: "大数",    a: 1000000, b: 2000000, want: 3000000},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // 执行
            got := Add(tt.a, tt.b)
            // 断言
            if got != tt.want {
                t.Errorf("Add(%d,%d) = %d, want %d",
                    tt.a, tt.b, got, tt.want)
            }
        })
    }
}


测试用例1       测试用例2       测试用例3       测试用例4
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│正数相加 │   │负数相加 │   │ 零值   │   │ 大数   │
│ 1+2=3  │   │-1+-2=-3│   │ 0+0=0  │   │1M+2M=3M│
└────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                          │
                          ▼
                   全部通过？→ PASS
                   有失败？→ FAIL（只看失败的那个）
```

#### t.Error vs t.Fatal 对比图

```
        测试执行中
            │
            ▼
      发现错误
            │
      ╔═════╧══════╗
   用↓t.Error  用↓t.Fatal
      │            │
      ▼            ▼
┌────────────┐ ┌────────────┐
│ 记录错误    │ │ 记录错误    │
│ 继续执行！  │ │ 立刻停止！  │
└────────────┘ └────────────┘
      │            │
      ▼            ▼
┌────────────┐ ┌────────────┐
│测试函数继续│ │测试函数返回│
│执行剩余代码│ │不继续执行  │
└────────────┘ └────────────┘

什么时候用t.Error：
  - 检查多个字段的验证
  - 一个失败不影响其他检查
  
什么时候用t.Fatal：
  - 初始化失败（后续都无法执行）
  - 打开文件/数据库失败
  - 测试的前置条件不满足
```

#### 基准测试的b.N自适应图

```
        go test -bench=.
               │
               ▼
     ┌───────────────────┐
     │ 先设b.N=1         │
     │ 跑一次看看多久    │
     └────────┬──────────┘
              │
              ▼
     ┌───────────────────┐
     │ 如果运行时间 < 1秒 │
     │ 则 b.N *= 2       │
     └────────┬──────────┘
              │
              ▼
     ┌───────────────────┐
     │ b.N=1  → 跑完 <1s │
     │ b.N=2  → 跑完 <1s │
     │ b.N=4  → 跑完 <1s │
     │ b.N=8  → 跑完 <1s │
     │ ...               │
     │ b.N=1000000 → 跑完 │
     │ 大约1秒，稳定！   │
     └────────┬──────────┘
              │
              ▼
     ┌───────────────────┐
     │ 输出结果：         │
     │ 1000000000 0.25ns │
     │          ↑       ↑│
     │     运行次数  每次耗时│
     └───────────────────┘
```

#### 测试覆盖率的可视化图

```
代码覆盖率 = 测试执行了多少行代码

函数 Add(a, b int) int {       ← 已覆盖（绿色）
    return a + b               ← 已覆盖（绿色）
}

函数 Divide(a, b int) (int, error) {
    if b == 0 {                 ← 未覆盖（红色）← 没测除数为0
        return 0, errors.New("÷0") ← 未覆盖（红色）
    }
    return a / b, nil           ← 已覆盖（绿色）
}

覆盖率 = 绿色行数 / （绿色+红色）行数

查看方式：
  go test -coverprofile=cover.out
  go tool cover -html=cover.out  → 浏览器打开（绿/红可视化）
  go tool cover -func=cover.out  → 终端看每个函数的覆盖率
```

#### 子测试的层次结构图

```
TestAdd
 ├── 正数相加   ← 可以单独跑：go test -run TestAdd/正数相加
 ├── 负数相加
 ├── 零值
 └── 大数

TestDivide
 ├── 正常除法
 ├── 除数为0
 └── 负数除法

子测试的好处：
  1. 一个失败不影响其他
  2. 可以单独运行某个用例
  3. 清晰的层次结构
  4. 支持t.Parallel()并行
```

---

---

### ⚡ 11.15 大厂面试题扩展（测试篇·10道）

**面试题1：单元测试和基准测试的文件名有什么要求？**
```go
// 文件名必须以 _test.go 结尾
// calc.go → calc_test.go ✅
// calc_test.go → 被go test识别
// calc_check.go → ❌ 不是测试文件

// 测试函数：TestXxx(t *testing.T)
// 基准测试：BenchmarkXxx(b *testing.B)
// 示例函数：ExampleXxx()
```

**面试题2：t.Error 和 t.Fatal 的区别？**
```go
func TestExample(t *testing.T) {
    // t.Error：记录错误但继续执行
    t.Error("出错了")  // 继续执行后面的代码
    fmt.Println("我还会执行")  // ✅
    
    // t.Fatal：记录错误并立即停止
    t.Fatal("严重错误")  // 立即退出这个测试函数
    fmt.Println("我不会执行")  // ❌ 不执行
}
```

**面试题3：go test -v 和 go test -run 有什么用？**
```bash
# -v：详细输出（显示每个测试的PASS/FAIL）
go test -v ./...

# -run：只运行匹配的测试（支持正则）
go test -run TestAdd        # 只运行TestAdd
go test -run TestAdd/正数   # 只运行子测试
```

**面试题4：测试覆盖率怎么生成和查看？**
```bash
# 生成覆盖率数据
go test -coverprofile=cover.out ./...

# 终端查看每个函数的覆盖率
go tool cover -func=cover.out

# 浏览器查看（绿色=覆盖，红色=未覆盖）
go tool cover -html=cover.out
```

**面试题5：怎么跳过测试缓存？什么时候需要？**
```bash
# 默认：源码没变就用缓存结果
# 第二次运行：cached（0.1秒）

# 跳过缓存：
go test -count=1 ./...

# 什么时候跳过？
# 1. 改了外部依赖但Go不知道
# 2. 测试依赖系统时间/网络
# 3. CI/CD中确保每次都重新测
```

**面试题6：怎么测试一个会panic的函数？**
```go
func Divide(a, b int) int {
    if b == 0 {
        panic("除数不能为0")
    }
    return a / b
}

func TestDividePanic(t *testing.T) {
    defer func() {
        if r := recover(); r == nil {
            t.Error("应该panic但没有")
        }
    }()
    Divide(10, 0)  // 应该panic
}
```

**面试题7：子测试（t.Run）有什么好处？**
```go
func TestMath(t *testing.T) {
    tests := []struct{
        name string
        a, b, want int
    }{
        {"加+加", 1, 2, 3},
        {"负数", -1, -2, -3},
        {"零值", 0, 0, 0},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}

// 好处：
// 1. 每个子测试独立运行
// 2. 一个失败不影响其他
// 3. 可以单独运行某个：go test -run TestMath/负数
// 4. 输出更清晰：有层级关系
```

**面试题8：TestMain是做什么的？**
```go
func TestMain(m *testing.M) {
    fmt.Println("=== SETUP ===")
    // 初始化：建数据库、开文件、连服务器
    
    code := m.Run()  // 运行所有测试
    
    fmt.Println("=== TEARDOWN ===")
    // 清理：删数据库、关文件
    
    os.Exit(code)
}
// TestMain在整个包测试前执行一次
// m.Run()运行所有Test函数
```

**面试题9：httptest怎么测试HTTP服务？**
```go
func TestHandler(t *testing.T) {
    ts := httptest.NewServer(http.HandlerFunc(
        func(w http.ResponseWriter, r *http.Request) {
            fmt.Fprintln(w, "ok")
        },
    ))
    defer ts.Close()
    
    resp, err := http.Get(ts.URL + "/test")
    if err != nil { t.Fatal(err) }
    defer resp.Body.Close()
    
    body, _ := io.ReadAll(resp.Body)
    if string(body) != "ok\n" {
        t.Errorf("got %q, want %q", body, "ok\n")
    }
}
```

**面试题10：Fuzzing测试（Go 1.18+）是什么？**
```go
func FuzzReverse(f *testing.F) {
    // 种子语料（初始输入）
    f.Add("hello")
    f.Add("世界")
    
    f.Fuzz(func(t *testing.T, s string) {
        reversed := Reverse(s)
        double := Reverse(reversed)
        if s != double {
            t.Errorf("反转两次不等于原串: %q", s)
        }
        if utf8.ValidString(s) && !utf8.ValidString(reversed) {
            t.Errorf("产生了无效UTF-8: %q", reversed)
        }
    })
}
// 运行：go test -fuzz FuzzReverse
// Fuzzing自动生成随机输入测试边界情况
```

---

### 🧠 11.17 纳米级知识点：测试框架、stub、覆盖率统计、benchmark统计、pprof

```
go test过程：扫描*_test.go→找TestXxx→编译→执行
t.Fatal→runtime.Goexit()退出当前goroutine

stub（桩）：用接口模拟外部依赖（不真的发邮件）

覆盖率：编译器插计数器，走过的行++

benchmark：b.N从1翻倍直到够1秒

pprof采样：每0.01秒记录CPU在哪→火焰图
```

---

<!-- @Ref: docs/sps/plans/20260703_plan_wave2_extension.md | @Date: 2026-07-03 -->
### 🚀 底层原理纳米级精讲

#### 11.1 synctest 并发测试的逻辑时钟虚拟引擎
在进行微服务或高并发系统的单元测试时，如果代码中包含了超时控制（如 `time.Sleep` 或 `time.After`），传统的测试不得不老老实实挂起硬件 CPU 线程去等待。这会导致单元测试变得极慢。
- **`testing/synctest` (Go 1.21+) 物理引擎**：
  `synctest` 在运行时内部构建了一个 **“虚拟时钟沙箱 (Virtual Time Sandbox)”**：
  1. **隔离泡泡（Bubble）**：在沙箱内运行的协程发起 `time.Sleep` 时，运行时**绝对不会去挂起底层 OS 线程**，而是将当前协程放入虚拟睡眠队列，并使该协程在逻辑上挂起；
  2. **时钟瞬时跃迁**：当沙箱内没有任何非空闲协程可执行时，虚拟时钟引擎会直接修改内部的计数器值（使虚拟时钟瞬间跳转），并瞬时将等待超时的协程拉回运行队列。这把原本需要数秒的测试压缩到了微秒内执行完毕，实现了微观时间控制。

#### 11.2 -race 数据竞争检测底层的 ThreadSanitizer 影子内存模型
高并发下，如果有两个 Goroutine 同时读写同一个全局变量，且其中至少有一个是写操作，就会发生 **数据竞争 (Data Race)**，导致内存数据损坏。
- **`-race` 编译插桩**：
  当运行 `go test -race` 时，编译器会在所有内存读写操作之前，强制插入一段分析代码。
- **影子内存模型（ThreadSanitizer 状态机）**：
  Go 的 race 检测器基于谷歌的 ThreadSanitizer（TSan）算法：
  1. **物理影子内存 (Shadow Memory)**：
     它把系统的虚拟内存划分为两部分。对于应用程序的每 8 字节（64位）真实物理内存，TSan 都会在旁边的保留区物理分配 **4 个影子字（每个 8 字节，共 32 字节）**；
  2. **影子字状态记录**：
     每个影子字里存放了最后 4 次读写该 8 字节内存的 Goroutine ID、时钟纪元（Epoch）、读写类型及偏移。
  3. **并发碰撞检测**：
     当有新的协程来读写该内存时，TSan 会在硬件寄存器内，将新协程的状态与这 4 个影子字的状态进行按位比对。一旦发现存在两个不同的 Goroutine ID 同时在没有持有相同锁（即通过 channel 或 mutex 建立 happens-before 顺序）的情况下执行了写冲突，就会当场抛出异常警告（WARNING: DATA RACE），使隐藏的并发 Bug 无处逃形。

---

<!-- @Ref: docs/sps/plans/20260703_plan_wave3_extension.md | @Date: 2026-07-03 -->
#### 11.3 testing/synctest 隔离沙箱虚拟时间流转
`synctest` 在隔离泡泡（Bubble）内部，通过重写 runtime 的定时器调度逻辑，将物理硬件时钟转换为逻辑时钟：

```text
隔离沙箱 (Bubble)
 ┌──────────────────────┐
 │ G1 发起 time.Sleep   │ ──► 挂起，放入虚拟睡眠队列 (不占 OS 线程)
 ├──────────────────────┤
 │ 所有协程均进入等待？   │ ──► 虚拟时间引擎瞬间跳转 ──► 虚拟时钟 +10 秒
 ├──────────────────────┤
 │ 唤醒 G1 协程并执行   │ ◄── 瞬间到达，耗时 1 微秒！
 └──────────────────────┘
```

### 🏆 大厂CTO级面试金典

#### 11.3 大厂面试金典真题

##### 1. Go 1.21 新引入的 `testing/synctest` 是如何消除并发测试中的 time.Sleep 真实等待时间的？
- **小白通俗说辞**：
  > 以前测超时就像打单机游戏，到了夜间（sleep）你就只能傻傻等天亮。现在 Go 给你提供了一个“修改器”。只要你在泡泡里，你按个快捷键，游戏里的时间瞬间就过去了一万秒，游戏天亮了，但真实的世界才过去了一瞬间，这样你测试超时的 Bug 就不需要空等了。
- **CTO 专业黑话**：
  > Go 1.21 引入的 `testing/synctest` 包在底层建立了一个隔离的“逻辑时钟泡泡”（Bubble）。
  > 在该泡泡内部，所有的常规 `time.Sleep` 和定时器通道都不会真正去调用操作系统的硬件定时中断（这会导致测试协程空等），而是将 G 放入等待挂起队列。当运行至没有活跃的非空闲协程时，`synctest` 的虚拟时间引擎会通过直接改写内部 timer 树的纪元值，让虚拟时钟瞬间跳转到下一个定时器到期点，并在微秒级内拉起被挂起的 G。这消除了测试代码在 I/O 模拟时的无效物理耗时。

##### 2. 大厂在高并发微服务压测时，是如何利用 Race Detector 的影子内存数据发现隐藏的数据竞争的？
- **小白通俗说辞**：
  > 影子内存就像是公司安检口的高清摄像头，不仅记录你干了什么，还把最后4个碰过这个商品的人的工号、时间全记录在旁边的小本子上。如果摄像头发现两个不同工号的人在同一秒内没有签字画押就跑来同时抢这个商品，摄像头就会立刻在屏幕上红灯大作，把这两个人的工号和现场照片直接打印出来，让并发 Bug 当场现形。
- **CTO 专业黑话**：
  > Race Detector 的核心在于 ThreadSanitizer (TSan) 的“影子内存（Shadow Memory）”与“向量时钟（Vector Clock）”比对逻辑。
  > 编译器在编译期进行静态插桩，在所有内存 Load/Store 前插入 `__tsan_read` / `__tsan_write` 钩子。运行时将物理地址空间按 1:4 比例映射为影子内存。
  > 当 Goroutine $G_a$ 写入地址 $A$ 时，TSan 将 $G_a$ 的唯一 ID、向量时钟、访问尺寸及写类型压缩为一个 64 位影子字，写入 $A$ 对应的影子插槽。当 Goroutine $G_b$ 随后读写 $A$ 时，TSan 通过位操作比对新时钟与已存在的 4 个影子字状态，若未能通过 Happens-before 关系阻断（即没有临界区 Lock/Unlock 或 Channel 发收导致的偏序关系），则判定发生数据竞争，输出符号化栈回溯，这在分布式微服务压测中是发现隐式空指针与野指针的重要手段。

> **下一章**：[第12章 反射](./ch12-reflection.md) —— reflect.Type、reflect.Value、动态调用、结构体标签。

---

### 🔬 11.16 底层原理：go test是怎么工作的？测试覆盖率是怎么统计的？

#### go test 执行过程——从源码到测试结果

```
           go test ./...
               │
               ▼
     ┌──────────────────────────┐
     │ 1. 扫描 *_test.go 文件   │
     │    calc.go → calc_test.go│
     │    这俩一起编译          │
     └──────────┬───────────────┘
               │
               ▼
     ┌──────────────────────────┐
     │ 2. 创建一个临时的main包   │
     │    把所有的TestXxx函数    │
     │    注册到这个main里      │
     └──────────┬───────────────┘
               │
               ▼
     ┌──────────────────────────┐
     │ 3. 编译为测试二进制       │
     │    /tmp/go-test-xxx.test │
     │    里面有TestMain或自动   │
     │    生成的测试main        │
     └──────────┬───────────────┘
               │
               ▼
     ┌──────────────────────────┐
     │ 4. 运行测试二进制         │
     │    一个个执行TestXxx     │
     │    记录结果              │
     └──────────┬───────────────┘
               │
               ▼
     ┌──────────────────────────┐
     │ 5. 输出结果              │
     │    PASS / FAIL           │
     │    把临时文件删掉        │
     └──────────────────────────┘

核心：go test 内部调用 go test -c 编译成二进制
  然后执行这个二进制
  所以测试本质上是一个独立程序！
```

#### 测试覆盖率插桩——怎么知道哪些代码被执行了

```
普通编译：
  func Add(a, b int) int {
      return a + b
  }
  // → 编译成 ADD RAX, RBX

覆盖率编译（插桩后）：
  func Add(a, b int) int {
      coverCounters[0]++  ← 插入计数器
      return a + b
  }
  // → MOV [计数器], 1; ADD RAX, RBX

覆盖率工具在编译时：
  1. 在每个代码块（基本块）前插入计数器
  2. 计数器存在一个全局数组里
  3. 测试执行时，走过的代码块计数器+1
  4. 测试结束后，统计哪些计数器>0

go test -coverprofile=cover.out 的背后：
  1. 编译器插桩（插入计数器）
  2. 运行测试
  3. 每个代码块执行时计数器+1
  4. 生成cover.out（每行代码的执行次数）

=> 覆盖率 = 计数器>0的代码块 / 总代码块
```

#### t.Error 和 t.Fatal 的底层实现

```go
// testing.T 内部有个字段 failed bool

type T struct {
    mu     sync.Mutex  // 并发安全
    failed bool       // 是否失败
    skipped bool      // 是否跳过
    ...
}

func (t *T) Error(args ...interface{}) {
    t.mu.Lock()
    t.failed = true     // 标记失败
    t.mu.Unlock()
    log.Println(args)   // 打印日志
    // ⚠️ 不停止！继续执行
}

func (t *T) Fatal(args ...interface{}) {
    t.mu.Lock()
    t.failed = true
    t.mu.Unlock()
    log.Println(args)
    runtime.Goexit()    // ← 退出当前goroutine！
    // 这会导致当前测试函数停止
    // 但不影响其他测试函数
}

区别就一句话：
  Error 只是记个红牌（继续跑）
  Fatal 记红牌+直接下场（停止当前测试）
```

#### Benchmark 的 b.N 自适应算法

```go
func BenchmarkXxx(b *testing.B) {
    for i := 0; i < b.N; i++ {
        DoSomething()
    }
}

b.N 不是固定的！Go自动调整：

开始时：b.N = 1
1. 用b.N=1跑一次
2. 看跑了多久
3. 如果 < 1秒 → b.N *= 2 → 再跑
4. 重复直到总时间 ≥ 1秒
5. 用最终的b.N跑出稳定结果

举例：DoSomething()一次需要0.5μs
  第1次: b.N=1   → 0.5μs < 1s → b.N=2
  第2次: b.N=2   → 1μs < 1s → b.N=4
  第3次: b.N=4   → 2μs < 1s → b.N=8
  ...
  第21次: b.N=2^20=1,048,576 → 0.52s < 1s → b.N=2,097,152
  第22次: b.N=2,097,152 → 1.05s ≥ 1s ✅
  
  输出：
  BenchmarkXxx-8  2097152  512 ns/op
      运行次数 ↑    每次耗时 ↑
```

#### testing/synctest 为什么能加速时间

```go
import "testing/synctest"

synctest.Run(func() {
    time.Sleep(1 * time.Hour)  // 不会真的等1小时！
})

原理：
  synctest 替换了 time 包的底层实现
  
  正常：time.Sleep → 系统调用 → 内核挂起goroutine → 真的等
  synctest：time.Sleep → 假的计时器 → 立刻返回
  
  time.Now() 也变成假的：
    可以手动控制当前时间
    
  就像游戏的"加速模式"：
    游戏里的1小时 = 现实中的1毫秒
```

#### 测试缓存——为什么第二次go test这么快

```
第一次：
  go test ./...  → 编译+测试 → 3秒

第二次（源码没变）：
  go test ./...  → (cached) → 0.1秒

缓存原理：
  1. 计算源码和测试文件的哈希值
  2. 把哈希值和测试结果一起存到 $GOCACHE
  3. 下次运行：计算哈希 → 命中缓存 → 直接输出上次结果

什么情况下会刷新缓存？
  1. 改动了任何 .go 文件
  2. 改动了 go.mod（依赖变了）
  3. 加了 -count=1 强制跳过

什么情况下缓存"骗"了你？
  测试依赖了外部系统（时间、网络、文件）
  → 外部变了但Go不知道
  → 一直用缓存结果
  → 解决：go test -count=1
```

---

##### 3. 数据竞争检测器（Race Detector）在判定数据碰撞时，是如何计算“向量时钟（Vector Clock）”的？
- **小白通俗说辞**：
  > 向量时钟就像是每个人手腕上的“本地时间表”，上面不仅记着自己的时间，还记着他所知道的其它伙伴的时间。
  > 如果两个人要交换信息（通过 Channel 或者是锁），就互相抄一下对方的时间表。如果摄像头（Race 检查器）发现 A 手里的时间表记着“B 已经写了这块地”，但 B 却完全不知道 A 也在写（两个人的时间表没有交叉同步过，即 Happens-before 失效），摄像头就会立刻判定这是非法抢占，触发报警。
- **CTO 专业黑话**：
  > 在 ThreadSanitizer（TSan）算法中，每个线程和协程都维护一个一维整型数组，称为**向量时钟（Vector Clock, $V$）**。
  > 对于协程 $G_i$，其时钟为 $V_i$。当发生事件或内存访问时，其自身的逻辑时钟自增：$V_i[i] = V_i[i] + 1$。
  > 当发生 Happens-before 偏序事件（如通道发送 `ch <-` 与接收 `<- ch`）时，接收端会通过原子操作合并发送端的向量时钟：
  > $$V_{\text{receiver}}[k] = \max(V_{\text{receiver}}[k], V_{\text{sender}}[k])$$
  > 在 Load/Store 内存操作发生时，Race 检查器会将当前时钟与对应影子内存中的时钟进行偏序比对。一旦满足 $\neg(V_a < V_b) \wedge \neg(V_b < V_a)$（即两个向量时钟无法在时间轴上建立先后偏序关系），则代表存在并发碰撞，抛出 Data Race 警报。

> **下一章**：[第12章 反射](./ch12-reflection.md) —— reflect.Type、reflect.Value、动态调用、结构体标签。

### 🎤 Q&A 测试篇

**Q: t.Error vs t.Fatal？** A: Error只记录不停止；Fatal记录+runtime.Goexit()停止当前测试。

**Q: 测试缓存怎么跳过？** A: go test -count=1。缓存基于源码哈希，外部变时Go不知。

**Q: 覆盖率100%就没bug？** A: 不是！覆盖率只测哪些代码跑了，不测逻辑对不对。断言才是关键。

**Q: 子测试好处？** A: 独立运行/单独跑(go test -run)/清晰层级/支持t.Parallel()。
