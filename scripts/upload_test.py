"""用 urllib 正确构造 multipart/form-data 上传中文文件名文件，验证知识库入库。
用法：python scripts/upload_test.py  （需服务已在 8000 端口运行）
"""
import http.cookiejar
import os
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"
# 兼容 Git Bash / Windows 代理环境
os.environ.setdefault("NO_PROXY", "127.0.0.1")
os.environ.setdefault("no_proxy", "127.0.0.1")


def login(username: str, password: str, cj) -> None:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    data = urllib.parse.urlencode({"username": username, "password": password}).encode()
    opener.open(BASE + "/login", data)


def upload(cj, course_id: int, file_path: str):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    with open(file_path, "rb") as f:
        content = f.read()
    fn = os.path.basename(file_path).encode("utf-8")
    boundary = "----CourseTABoundary7MA4YWxkTrZu0gW"
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="course_id"\r\n\r\n{course_id}\r\n'.encode()
        + f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{fn.decode("utf-8")}"\r\n'.encode()
        + b"Content-Type: text/plain\r\n\r\n"
        + content
        + f"\r\n--{boundary}--\r\n".encode()
    )
    req = urllib.request.Request(
        BASE + "/kb/upload",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
    )
    page = opener.open(req).read().decode("utf-8")
    m = re.search(r"上传成功[^<]*", page)
    print("页面显示：", m.group(0) if m else "未找到结果提示")

    # 校验数据库是否正确存储了中文标题（直接查库需 pymysql）
    import pymysql

    from app.core.config import settings  # noqa

    conn = pymysql.connect(
        host=settings.MYSQL_HOST, port=settings.MYSQL_PORT, user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD, database=settings.MYSQL_DB, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    with conn.cursor() as cur:
        cur.execute("SELECT id,title,chunk_num FROM knowledge_docs ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
    conn.close()
    print("数据库最新记录：", row)


if __name__ == "__main__":
    cj = http.cookiejar.CookieJar()
    login("teacher", "123456", cj)
    upload(cj, 1, "data/seed_kb/数据结构讲义.txt")
