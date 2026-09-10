/**
 * 安全工具函数：XSS 防护、输入清理等
 */
import DOMPurify from 'dompurify'

/**
 * 清理 HTML 内容，防止 XSS 攻击
 */
export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  })
}

/**
 * 清理用户输入，移除潜在的危险字符
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/**
 * 验证 URL 是否安全（仅允许 http/https，拒绝私有地址）
 */
export function isValidURL(url: string): boolean {
  try {
    const parsed = new URL(url)
    
    // 仅允许 http/https
    if (!/^https?:$/.test(parsed.protocol)) {
      return false
    }
    
    // 拒绝私有 IP 地址
    const hostname = parsed.hostname
    if (
      hostname === 'localhost' ||
      hostname === '127.0.0.1' ||
      /^10\./.test(hostname) ||
      /^172\.(1[6-9]|2[0-9]|3[0-1])\./.test(hostname) ||
      /^192\.168\./.test(hostname)
    ) {
      return false
    }
    
    return true
  } catch {
    return false
  }
}
