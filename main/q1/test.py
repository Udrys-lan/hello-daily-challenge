from main import analyze_log

def run_tests():
    # 测试1：正常app.jsonl，你可以自己建立这个测试文件
    res1 = analyze_log("q1.jsonl")
    print("测试1正常文件 total:", res1["total"])
    print("by_level:", res1["by_level"])
    print("by_user:", res1["by_user"])
    print("last_error:", res1["last_error"])

    # 测试2：不存在的文件
    res2 = analyze_log("not_exist.jsonl")
    print("\n测试2 文件不存在：", res2)

    # 测试3：空文件 empty.jsonl
    res3 = analyze_log("empty.jsonl")
    print("\n测试3 空文件：", res3)

    # 测试4：包含坏行 bad.jsonl
    res4 = analyze_log("bad.jsonl")
    print("\n测试4含错误行 total:", res4["total"])
    print("last_error:", res4["last_error"])

if __name__ == "__main__":
    run_tests()
