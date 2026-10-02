import json

def analyze_log(filepath: str) -> dict:
    # 初始化返回结果
    result = {
        "total": 0,
        "by_level": {},
        "by_user": {},
        "last_error": None
    }
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    log = json.loads(line)
                except json.JSONDecodeError:
                    # json解析失败，跳过本行
                    continue

                # 解析成功，计数+1
                result["total"] += 1
                level = log["level"]
                user = log["user"]
                message = log["message"]

                # by_level统计
                if level in result["by_level"]:
                    result["by_level"][level] += 1
                else:
                    result["by_level"][level] = 1

                # by_user统计
                if user in result["by_user"]:
                    result["by_user"][user] += 1
                else:
                    result["by_user"][user] = 1

                # 如果是ERROR，更新last_error
                if level == "ERROR":
                    result["last_error"] = message

    except FileNotFoundError:
        # 文件直接不存在，直接返回初始化好的空结果，不抛异常
        pass
    return result
