# ADR-006: 使用阿里云百炼 Qwen API

## 状态

已采纳

## 上下文

系统需要接入大语言模型（LLM）能力，实现智能答疑、作业批改、试题生成等功能。需要选择一个稳定、经济、易接入的大模型 API 服务商。

## 决策

选择使用 **阿里云百炼（DashScope）的 Qwen（通义千问）API** 作为主要的大模型服务商。

## 理由

1. **OpenAI 兼容接口**：阿里云百炼提供与 OpenAI 兼容的 API 接口，可以直接使用 `langchain-openai` 的 `ChatOpenAI` 和 `OpenAIEmbeddings` 客户端，无需额外适配。

2. **性价比高**：相比 GPT-4 等国际模型，Qwen 系列模型价格更加经济，适合演示系统长期使用。

3. **中文支持优秀**：Qwen 模型在中文理解和生成方面表现优秀，适合国内课程场景。

4. **Embedding 支持**：提供 `text-embedding-v4` 模型，支持高质量的中文文本向量化，满足 RAG 检索需求。

5. **稳定性**：阿里云作为国内主流云服务商，API 稳定性和可用性有保障。

## 配置方式

```ini
# .env 配置
QWEN_API_KEY=sk-你的 Key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_CHAT_MODEL=qwen-plus
QWEN_EMBEDDING_MODEL=text-embedding-v4
```

## 模型选择

| 用途 | 模型 | 说明 |
|------|------|------|
| 聊天/答疑 | qwen-plus | 平衡性能和成本 |
| 复杂推理 | qwen-max | 更高精度 |
| Embedding | text-embedding-v4 | 中文优化 |

## 可替代方案

系统支持通过修改 `.env` 快速切换到大模型服务商：

```ini
# 切换到 DeepSeek
QWEN_API_KEY=sk-deepseek-xxx
QWEN_BASE_URL=https://api.deepseek.com/v1
QWEN_CHAT_MODEL=deepseek-chat
```

## 后果

### 正面影响

- 接入简单，兼容 LangChain 生态
- 成本可控
- 中文效果好

### 负面影响

- 依赖单一云服务商
- 需要自行注册账号和充值

## 相关文档

- `app/services/llm.py` - LLM 工厂实现
- `app/core/config.py` - 配置管理
- `README.md` - 运行前准备
