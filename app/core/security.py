"""安全中间件：添加安全响应头。"""
import re
from fastapi import Request
from fastapi.responses import Response


# 私有 IP 地址正则
PRIVATE_IP_PATTERNS = [
    re.compile(r"^127\."),  # 127.0.0.0/8
    re.compile(r"^10\."),  # 10.0.0.0/8
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\."),  # 172.16.0.0/12
    re.compile(r"^192\.168\."),  # 192.168.0.0/16
    re.compile(r"^0\.0\.0\.0"),  # 0.0.0.0
    re.compile(r"^::1$"),  # IPv6 localhost
    re.compile(r"^fe80:"),  # IPv6 link-local
    re.compile(r"^fc00:"),  # IPv6 unique-local
]


def is_private_ip(ip: str) -> bool:
    """检查 IP 是否为私有地址。"""
    for pattern in PRIVATE_IP_PATTERNS:
        if pattern.match(ip):
            return True
    return False


async def security_headers_middleware(request: Request, call_next):
    """添加安全响应头的中间件 - 在 CORS 之后执行，保留 CORS 头。"""
    response = await call_next(request)
    
    # 注意：不再在这里设置 CORS 头，由 FastAPI 的 CORSMiddleware 统一处理
    # 只添加其他安全头
    
    # Content-Security-Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' http://localhost:* https://*; "
        "frame-ancestors 'none';"
    )
    
    # X-Content-Type-Options
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # X-Frame-Options
    response.headers["X-Frame-Options"] = "DENY"
    
    # X-XSS-Protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer-Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions-Policy
    response.headers["Permissions-Policy"] = (
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "magnetometer=(), microphone=(), payment=(), usb=()"
    )
    
    return response
