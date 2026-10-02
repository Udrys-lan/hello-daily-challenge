"""端到端 HTTP 测试：登录 -> 上传附件 -> 下载 -> 验证下载计数。标准库 urllib 实现。"""
import http.cookiejar
import urllib.request
import urllib.parse
import re
import io
import uuid

BASE = "http://127.0.0.1:8000"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get(url):
    req = urllib.request.Request(url)
    with opener.open(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def post(url, data, headers=None):
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers or {})
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with opener.open(req, timeout=20) as r:
            return r.geturl(), r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.geturl(), e.read().decode("utf-8", errors="replace")


def csrf(html):
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return m.group(1) if m else ""


# 1) 登录页取 csrf
login_html = get(BASE + "/accounts/login/")
tok = csrf(login_html)
final_url, body = post(BASE + "/accounts/login/", {
    "username": "tester", "password": "testpass123", "csrfmiddlewaretoken": tok,
})
print("1) 登录后跳转到:", final_url)
assert "articles" in final_url, "登录失败"

# 2) 上传附件（multipart 用 urllib 手动构造）
boundary = uuid.uuid4().hex
content = b"hello attachment end2end"
part = (
    f"--{boundary}\r\n"
    "Content-Disposition: form-data; name=\"csrfmiddlewaretoken\"\r\n\r\n" + csrf(get(BASE + "/article/5/")) + "\r\n"
    f"--{boundary}\r\n"
    "Content-Disposition: form-data; name=\"file\"; filename=\"e2e.txt\"\r\n"
    "Content-Type: text/plain\r\n\r\n" + content.decode() + "\r\n"
    f"--{boundary}--\r\n"
).encode("utf-8")
req = urllib.request.Request(BASE + "/attachment/upload/5/", data=part)
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
with opener.open(req, timeout=20) as r:
    up_url = r.geturl()
print("2) 上传附件响应跳转:", up_url)
assert "article/5" in up_url, "上传失败"

# 3) 详情页应显示附件 e2e.txt
detail = get(BASE + "/article/5/")
print("3) 详情页含附件 e2e.txt:", "e2e.txt" in detail)

# 4) 查附件 id 与下载计数
import sqlite3
conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()
cur.execute("SELECT id, downloads FROM article_attachment WHERE file_name='e2e.txt'")
aid, dl_before = cur.fetchone()
print("4) 附件 id=%d 下载前计数=%d" % (aid, dl_before))

# 5) 下载 2 次
for _ in range(2):
    with opener.open(BASE + f"/attachment/download/{aid}/", timeout=20) as r:
        data = r.read()
assert data == content, "下载内容不一致"
cur.execute("SELECT downloads FROM article_attachment WHERE id=%d" % aid)
dl_after = cur.fetchone()[0]
conn.close()
print("5) 下载2次后计数:", dl_after, "(应为 %d)" % (dl_before + 2))
assert dl_after == dl_before + 2, "下载计数F自增失败"
print("=== 端到端HTTP自测通过 ===")
