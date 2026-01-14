import gradio as gr
import tiktoken
from tokenizers import Tokenizer
import html
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
import uvicorn


# Define colors for token visualization (pastel colors similar to OpenAI)
TOKEN_COLORS = [
    "rgba(107,64,216,.3)",
    "rgba(104,222,122,.4)",
    "rgba(244,172,54,.4)",
    "rgba(239,65,70,.4)",
    "rgba(39,181,234,.4)"
]

def generate_token_html(token_texts):
    """
    Generate HTML for token visualization
    """
    if not token_texts:
        return ""
        
    html_content = '<div style="font-family: monospace; line-height: 1.5; font-size: 16px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; white-space: pre-wrap; background-color: #fff; color: #000;">'
    
    for i, token in enumerate(token_texts):
        color = TOKEN_COLORS[i % len(TOKEN_COLORS)]
        # Escape HTML characters in token to prevent rendering issues
        safe_token = html.escape(token)
        # Verify if token is a newline to handle it visually if needed, 
        # but pre-wrap handles it.
        html_content += f'<span style="background-color: {color};">{safe_token}</span>'
    
    html_content += '</div>'
    return html_content

# Load the DeepSeek tokenizer with error handling
try:
    deepseek_tokenizer = Tokenizer.from_file("deepseek/tokenizer.json")
except Exception as e:
    print(f"Error loading DeepSeek tokenizer: {e}")
    print("Please ensure tokenizer.json exists in the application directory")
    raise

try:
    gpt_tokenizer = Tokenizer.from_file("gpt-oss-120b/tokenizer.json")
except Exception as e:
    print(f"Error loading GPT tokenizer: {e}")
    print("Please ensure tokenizer.json exists in the application directory")
    raise



def count_tokens_tiktoken(text):
    """
    Count the number of tokens in the provided text using tiktoken
    """
    if not text:
        return 0, []
        
    # Use the cl100k_base encoding which is suitable for most models including GPT-4
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    token_texts = [encoding.decode_single_token_bytes(t).decode('utf-8', errors='replace') for t in tokens]
    return len(tokens), token_texts

def count_tokens_deepseek(text):
    """
    Count the number of tokens in the provided text using DeepSeek tokenizer
    """
    if not text:
        return 0, []

    encoding = deepseek_tokenizer.encode(text)
    # Use offsets to extract the actual text corresponding to each token
    token_texts = [text[start:end] for start, end in encoding.offsets]
    return len(encoding.ids), token_texts


def count_tokens_gpt(text):
    """
    Count the number of tokens in the provided text using GPT tokenizer
    """
    if not text:
        return 0, []

    encoding = gpt_tokenizer.encode(text)
    # Use offsets to extract the actual text corresponding to each token
    token_texts = [text[start:end] for start, end in encoding.offsets]
    return len(encoding.ids), token_texts



# Define Pydantic model
class TokenRequest(BaseModel):
    text: str = Field(..., description="需要计算 Token 的文本内容", example="你好，世界！")
    tokenizer_type: str = Field(
        default="tiktoken", 
        description="使用的分词器类型。可选值: tiktoken (OpenAI), deepseek3.1, gpt-oss-120b",
        example="deepseek3.1"
    )

app = FastAPI(
    title="Token 计算服务",
    description="提供基于多种分词器（DeepSeek, OpenAI, GPT-OSS）的 Token 计算 API。",
    version="1.0.0"
)

@app.post("/api/token", summary="计算文本 Token", description="根据指定的文本和分词器类型，计算 Token 数量并返回 Token 列表。")
def api_count_tokens(request: TokenRequest):
    count = 0
    token_texts = []
    
    if request.tokenizer_type == "tiktoken":
        count, token_texts = count_tokens_tiktoken(request.text)
    elif request.tokenizer_type == "deepseek3.1":
        count, token_texts = count_tokens_deepseek(request.text)
    elif request.tokenizer_type == "gpt-oss-120b":
        count, token_texts = count_tokens_gpt(request.text)
    else:
        # Default to tiktoken
        count, token_texts = count_tokens_tiktoken(request.text)
    
    return {"count": count, "tokens": token_texts}


def count_tokens(text, tokenizer_type):
    """
    Count the number of tokens in the provided text based on the selected tokenizer
    """
    count = 0
    token_texts = []
    
    if tokenizer_type == "tiktoken":
        count, token_texts = count_tokens_tiktoken(text)
    elif tokenizer_type == "deepseek3.1":
        count, token_texts = count_tokens_deepseek(text)
    elif tokenizer_type == "gpt-oss-120b":
        count, token_texts = count_tokens_gpt(text)
    else:
        # Default to tiktoken
        count, token_texts = count_tokens_tiktoken(text)
    
    html_output = generate_token_html(token_texts)
    return count, html_output

def create_interface():
    """
    Create the Gradio interface for token counting
    """
    with gr.Blocks(title="Token 计算器", css=".token-span { display: inline-block; }") as interface:
        gr.Markdown("# 🧮 Token 计算器")
        gr.Markdown("在下方文本框中输入文本，并选择一个分词器来计算 Token 数量。")

        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="输入文本",
                    placeholder="在此输入您的文本...",
                    lines=10
                )
                tokenizer_selector = gr.Radio(
                    choices=["deepseek3.1", "tiktoken", "gpt-oss-120b"],
                    value="deepseek3.1",
                    label="分词器选择"
                )
                count_button = gr.Button("计算 Token", variant="primary")

            with gr.Column():
                token_count = gr.Number(
                    label="Token 数量",
                    interactive=False
                )
                gr.Markdown("### Token 可视化")
                visualization_output = gr.HTML()
                
                gr.Markdown("### 说明")
                gr.Markdown("Token 是语言模型处理的文本块。不同的分词器对相同文本可能会产生不同的 Token 数量。")

        count_button.click(
            fn=count_tokens,
            inputs=[text_input, tokenizer_selector],
            outputs=[token_count, visualization_output]
        )

        gr.Examples(
            examples=[
                "你好，今天过得怎么样？",
                "The quick brown fox jumps over the lazy dog.",
                "这是一个较长的示例文本，用于演示此工具的 Token 计算功能。如您所见，文本越长，Token 数量越多。"
            ],
            inputs=text_input
        )

    return interface

interface = create_interface()
app = gr.mount_gradio_app(app, interface, path="/token")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)