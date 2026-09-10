"""请求/响应工具函数。"""
import hashlib
import uuid

import aiohttp


def hash_password(password: str) -> str:
    """以 SHA-256 对明文密码做哈希（演示采用，生产请使用加盐 bcrypt）。"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def gen_token() -> str:
    """生成简单会话 token（本地会话方案）。"""
    return uuid.uuid4().hex


def to_dict(obj) -> dict:
    """将 SQLAlchemy 模型实例转为普通 dict。"""
    d = {}
    for col in obj.__table__.columns:
        d[col.name] = getattr(obj, col.name)
    return d


async def fetch_url(url: str, method: str = "GET", **kwargs) -> dict | None:
    """安全的 HTTP 请求工具。
    
    安全约束：
    - 仅允许 http/https 协议
    - 拒绝 localhost、环回地址、私有地址
    """
    import ipaddress
    from urllib.parse import urlparse
    import socket
    
    # 解析 URL
    parsed = urlparse(url)
    
    # 协议检查
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"不支持的协议：{parsed.scheme}，仅允许 http/https")
    
    # 获取主机
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("无效的主机名")
    
    # 解析 IP 地址
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise ValueError(f"无法解析主机：{hostname}")
    
    # 检查 IP 地址
    for addr_info in ip_addresses:
        ip = addr_info[4][0]
        try:
            ip_obj = ipaddress.ip_address(ip)
            # 拒绝私有地址和环回地址
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
                raise ValueError(f"拒绝访问私有/环回地址：{ip}")
        except ValueError as e:
            if "拒绝访问" in str(e):
                raise
    
    # 执行请求
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, **kwargs) as response:
            return await response.json()
