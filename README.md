# Token Counter Service

这是一个基于 FastAPI 和 Gradio 的 Token 计算服务，支持多种分词器（Tokenizers），提供 REST API 和 Web 可视化界面。

## 功能

- **多模型支持**：支持 DeepSeek, Tiktoken (OpenAI), GPT-OSS-120B 等多种分词器。
- **Web 界面**：集成 Gradio 界面，提供直观的 Token 计数和可视化功能。
- **REST API**：提供标准的 API 接口，方便集成到其他应用中。
- **Token 可视化**：在 Web 界面中通过颜色区分不同的 Token。

## 安装

1.  克隆仓库或下载代码。
2.  安装依赖：

```bash
pip install -r requirements.txt
```

确保项目目录下存在以下分词器配置文件（如果使用本地模型）：
- `deepseek/tokenizer.json`
- `gpt-oss-120b/tokenizer.json`

## 运行

使用以下命令启动服务：

```bash
python token_counter.py
```

服务默认运行在 `http://0.0.0.0:7860`。

## 使用说明

### Web 界面

启动服务后，访问 `http://localhost:7860/token` 即可使用图形化界面进行 Token 计算。

### API 接口

#### 计算 Token

- **URL**: `/api/token`
- **Method**: `POST`
- **Content-Type**: `application/json`

**请求参数**:

| 参数名 | 类型 | 必选 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| `text` | string | 是 | 需要计算 Token 的文本 | - |
| `tokenizer_type` | string | 否 | 分词器类型 | `tiktoken` |

**支持的分词器类型 (`tokenizer_type`)**:
- `tiktoken` (默认)
- `deepseek3.1`
- `gpt-oss-120b`

**请求示例**:

```json
{
    "text": "你好，世界！",
    "tokenizer_type": "deepseek3.1"
}
```

**响应示例**:

```json
{
    "count": 4,
    "tokens": ["你好", "，", "世界", "！"]
}
```
