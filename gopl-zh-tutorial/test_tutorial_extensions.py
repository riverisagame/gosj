# -*- coding: utf-8 -*-
import os
import sys

# 确保在 Windows 环境下 stdout 支持 utf-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# 待检查的教程文件列表（13个章节文件）
chapters = [
    "ch01-introduction.md",
    "ch02-program-structure.md",
    "ch03-basic-types.md",
    "ch04-composite-types.md",
    "ch05-functions.md",
    "ch06-methods.md",
    "ch07-interfaces.md",
    "ch08-goroutines-channels.md",
    "ch09-shared-vars-concurrency.md",
    "ch10-packages-tools.md",
    "ch11-testing.md",
    "ch12-reflection.md",
    "ch13-unsafe-cgo.md",
]

# 附录文件
appendix = "appendix-go-versions.md"

# Wave 2 必须包含的硬核底层原理关键字检测字典
wave2_keywords = {
    "ch01-introduction.md": ["entersyscall", "exitsyscall"],
    "ch02-program-structure.md": ["未命名常量", "对齐边界"],
    "ch03-basic-types.md": ["DecodeRune", "查表优化"],
    "ch04-composite-types.md": ["hashWriting", "写冲突"],
    "ch05-functions.md": ["逃逸分析", "状态复用"],
    "ch06-methods.md": ["方法表达式", "虚函数表"],
    "ch07-interfaces.md": ["assertE2I", "类型断言"],
    "ch08-goroutines-channels.md": ["copystack", "栈分裂"],
    "ch09-shared-vars-concurrency.md": ["sync.Pool", "poolLocal"],
    "ch10-packages-tools.md": ["Sumdb", "默克尔树"],
    "ch11-testing.md": ["ThreadSanitizer", "影子内存"],
    "ch12-reflection.md": ["Value.Set", "flag 安全校验"],
    "ch13-unsafe-cgo.md": ["汇编函数", "堆逃逸"],
}

# Wave 3 必须包含的纳米级图解与最硬核大厂面试关键字
wave3_keywords = {
    "ch01-introduction.md": ["rt0_go", "ELF/PE"],
    "ch02-program-structure.md": ["有向无环图", "SP 寄存器"],
    "ch03-basic-types.md": ["IEEE 754", "指数与尾数"],
    "ch04-composite-types.md": ["roundupsize", "溢出桶"],
    "ch05-functions.md": ["bitmask", "recover()"],
    "ch06-methods.md": ["method value", "值接收者"],
    "ch07-interfaces.md": ["itabTable", "无锁哈希"],
    "ch08-goroutines-channels.md": ["G0 调度栈", "sudog 双向"],
    "ch09-shared-vars-concurrency.md": ["CanSpin", "victim"],
    "ch10-packages-tools.md": ["MVS 算法", "依赖树"],
    "ch11-testing.md": ["隔离泡泡", "TSan"],
    "ch12-reflection.md": ["flagRO", "私有成员"],
    "ch13-unsafe-cgo.md": ["混合写屏", "XMM 寄存器"],
}

# Wave 4 必须包含的真实应用场景与顶级大厂面试真题关键字
wave4_keywords = {
    "ch01-introduction.md": ["automaxprocs", "CPU 限流"],
    "ch02-program-structure.md": ["支付网关", "GC 暂停"],
    "ch03-basic-types.md": ["Redis 键", "Memory Swapping"],
    "ch04-composite-types.md": ["百亿级", "Pointer-free"],
    "ch05-functions.md": ["OOM", "参数求值"],
    "ch06-methods.md": ["回调函数", "捕获了大变量"],
    "ch07-interfaces.md": ["RPC", "动态路由"],
    "ch08-goroutines-channels.md": ["netpoller", "百万"],
    "ch09-shared-vars-concurrency.md": ["秒杀", "分段锁"],
    "ch10-packages-tools.md": ["静默投毒", "中间人"],
    "ch11-testing.md": ["CI 流水线", "3 小时"],
    "ch12-reflection.md": ["ORM 框架", "相对字节偏移"],
    "ch13-unsafe-cgo.md": ["FFmpeg", "Go 的堆指针"],
}

# Wave 5 必须包含的硬件微架构级对冲与大厂面试关键字检测字典
wave5_keywords = {
    "ch01-introduction.md": ["NUMA", "远程内存"],
    "ch02-program-structure.md": ["存取周期", "字段物理排序"],
    "ch03-basic-types.md": ["MESI", "伪共享"],
    "ch04-composite-types.md": ["TLB", "分页"],
    "ch05-functions.md": ["分支预测", "无分支"],
    "ch06-methods.md": ["动态分发", "I-Cache"],
    "ch07-interfaces.md": ["页表", "缺页中断"],
    "ch08-goroutines-channels.md": ["缓存线无效", "RingBuffer"],
    "ch09-shared-vars-concurrency.md": ["指令重排", "内存屏障"],
    "ch10-packages-tools.md": ["死代码", "符号图"],
    "ch11-testing.md": ["频率抖动", "调频"],
    "ch12-reflection.md": ["直达寻址", "越过反射"],
    "ch13-unsafe-cgo.md": ["AVX-512", "向量指令"],
}

# Wave 6 必须包含的可观测性、运行时剖析与 eBPF 内核探测级关键字检测字典
wave6_keywords = {
    "ch01-introduction.md": ["时钟中断", "pprof"],
    "ch02-program-structure.md": ["uprobe", "eBPF"],
    "ch03-basic-types.md": ["PMC", "perf"],
    "ch04-composite-types.md": ["alloc_space", "inuse_space"],
    "ch05-functions.md": ["Frame Pointer", "栈回溯"],
    "ch06-methods.md": ["0xCC", "插桩"],
    "ch07-interfaces.md": ["assertion", "时延震荡"],
    "ch08-goroutines-channels.md": ["调度器延迟", "Scheduler"],
    "ch09-shared-vars-concurrency.md": ["block", "lock"],
    "ch10-packages-tools.md": ["AST", "SSA"],
    "ch11-testing.md": ["抢占", "cgroups"],
    "ch12-reflection.md": ["DWARF", "debug_info"],
    "ch13-unsafe-cgo.md": ["G0 系统调度", "perf"],
}

# Wave 7 必须包含的分布式微服务高可用架构级关键字检测字典
wave7_keywords = {
    "ch01-introduction.md": ["优雅退出", "SIGTERM"],
    "ch02-program-structure.md": ["动态热加载", "原子指针"],
    "ch03-basic-types.md": ["精度对冲", "BigDecimal"],
    "ch04-composite-types.md": ["一致性哈希", "虚拟节点"],
    "ch05-functions.md": ["重试风暴", "自适应重试"],
    "ch06-methods.md": ["动态代理", "本地存根"],
    "ch07-interfaces.md": ["Any", "解包"],
    "ch08-goroutines-channels.md": ["令牌桶", "漏桶"],
    "ch09-shared-vars-concurrency.md": ["看门狗", "脑裂"],
    "ch10-packages-tools.md": ["Wasm", "热插拔"],
    "ch11-testing.md": ["网络分区", "混沌工程"],
    "ch12-reflection.md": ["mapstructure", "反序列化"],
    "ch13-unsafe-cgo.md": ["AES-GCM", "网卡吞吐"],
}

def test_extensions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    failed = False
    
    print("=== 开始执行教程文档无损扩展 Wave 7 TDD 测试 ===")
    
    # 1. 验证 13 个章节文件
    for chap in chapters:
        file_path = os.path.join(base_dir, chap)
        if not os.path.exists(file_path):
            print(f"[FAIL] 找不到教程文件: {chap}")
            failed = True
            continue
            
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # 必须包含大标题
        has_principles = "### 🚀 底层原理纳米级精讲" in content
        has_questions = "### 🏆 大厂CTO级面试金典" in content
        
        if not has_principles or not has_questions:
            print(f"[FAIL] 文件 {chap} 缺失必须的追加模块:")
            failed = True
            continue
            
        # 验证 Wave 2 关键字
        missing_kw2 = [kw for kw in wave2_keywords[chap] if kw not in content]
        if missing_kw2:
            print(f"[FAIL] 文件 {chap} 缺失 Wave 2 关键字: {missing_kw2}")
            failed = True
            
        # 验证 Wave 3 关键字
        missing_kw3 = [kw for kw in wave3_keywords[chap] if kw not in content]
        if missing_kw3:
            print(f"[FAIL] 文件 {chap} 缺失 Wave 3 关键字: {missing_kw3}")
            failed = True
            
        # 验证 Wave 4 关键字
        missing_kw4 = [kw for kw in wave4_keywords[chap] if kw not in content]
        if missing_kw4:
            print(f"[FAIL] 文件 {chap} 缺失 Wave 4 关键字: {missing_kw4}")
            failed = True
            
        # 验证 Wave 5 关键字
        missing_kw5 = [kw for kw in wave5_keywords[chap] if kw not in content]
        if missing_kw5:
            print(f"[FAIL] 文件 {chap} 缺失 Wave 5 关键字: {missing_kw5}")
            failed = True
            
        # 验证 Wave 6 关键字
        missing_kw6 = [kw for kw in wave6_keywords[chap] if kw not in content]
        if missing_kw6:
            print(f"[FAIL] 文件 {chap} 缺失 Wave 6 关键字: {missing_kw6}")
            failed = True
            
        # 验证 Wave 7 关键字
        missing_kw7 = [kw for kw in wave7_keywords[chap] if kw not in content]
        if missing_kw7:
            print(f"[FAIL] 文件 {chap} 缺失 Wave 7 关键字: {missing_kw7}")
            failed = True
            
        # 验证是否包含 ASCII 流程图特征框线字符
        box_chars = ["┌", "┐", "└", "┘", "│", "─", "▼", "▲", "├", "┤", "┴", "┬"]
        has_ascii_diagram = any(char in content for char in box_chars)
        if not has_ascii_diagram:
            print(f"[FAIL] 文件 {chap} 缺失 ASCII 架构图/流程图解")
            failed = True
            
        if not missing_kw2 and not missing_kw3 and not missing_kw4 and not missing_kw5 and not missing_kw6 and not missing_kw7 and has_ascii_diagram:
            print(f"[PASS] 文件 {chap} 已成功通过 Wave 7 校验。")
            
    # 2. 验证附录文件
    app_path = os.path.join(base_dir, appendix)
    if not os.path.exists(app_path):
        print(f"[FAIL] 找不到附录文件: {appendix}")
        failed = True
    else:
        with open(app_path, "r", encoding="utf-8", errors="replace") as f:
            app_content = f.read()
            
        has_new_versions = "Go 1.24" in app_content and "Go 1.26" in app_content
        has_wave2_appendix = "SwissTable" in app_content and "Green Tea" in app_content
        has_wave3_appendix = "SIMD" in app_content
        has_wave4_appendix = "SIMD" in app_content and "SwissTable" in app_content
        has_wave5_appendix = "预取" in app_content and "Prefetching" in app_content
        has_wave6_appendix = "Rehash" in app_content and "观测" in app_content
        has_wave7_appendix = "服务发现" in app_content and "比对" in app_content
        
        if not has_new_versions or not has_wave2_appendix or not has_wave3_appendix or not has_wave4_appendix or not has_wave5_appendix or not has_wave6_appendix or not has_wave7_appendix:
            print(f"[FAIL] 附录 {appendix} 缺失版本演进或 Wave 7 分布式架构精讲")
            failed = True
        else:
            print(f"[PASS] 附录 {appendix} 已成功更新至 Wave 7。")
            
    if failed:
        print("\n=== 测试未通过：存在缺失的 Wave 7 分布式架构扩展章节/关键字 ===")
        sys.exit(1)
    else:
        print("\n=== 测试全部通过！13个章节及附录均符合 Wave 7 扩展规范 ===")
        sys.exit(0)

if __name__ == "__main__":
    test_extensions()
