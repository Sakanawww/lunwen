"""测试聊天 API 完整流程"""
import requests
import json
import os

# 从环境变量读取凭据（避免硬编码）
TEST_USERNAME = os.getenv('TEST_USERNAME', 'admin')
TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'admin123')

# 模拟登录获取 token
login_resp = requests.post('http://127.0.0.1:8000/api/auth/login', json={
    'username': TEST_USERNAME,
    'password': TEST_PASSWORD
})
print('登录状态:', login_resp.status_code)
if login_resp.status_code == 200:
    data = login_resp.json()
    token = data.get('token')
    print('Token:', token[:20] + '...' if token else 'None')
    
    # 测试聊天 API
    if token:
        cookies = {'token': token}
        chat_resp = requests.post('http://127.0.0.1:8000/api/chat/stream', 
            json={'question': '什么是二叉树', 'course_id': 1},
            cookies=cookies,
            stream=True)
        print('聊天 API 状态:', chat_resp.status_code)
        
        # 读取 SSE 流
        full_text = ''
        sources = []
        for line in chat_resp.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        parsed = json.loads(data)
                        if 'token' in parsed:
                            full_text += parsed['token']
                            print('流式 token:', parsed['token'][:30])
                        if 'text' in parsed:
                            full_text = parsed['text']
                            sources = parsed.get('sources', [])
                        if 'sources' in parsed and isinstance(parsed['sources'], list):
                            sources = parsed['sources']
                    except Exception as e:
                        print('解析错误:', e)
        
        print('\n=== 最终回复 ===')
        print(full_text[:500] if full_text else '无内容')
        print('\n=== 参考来源 ===')
        print(sources)
