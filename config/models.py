# API 提供商及其模型配置
PROVIDERS = {
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1/",
        "models": {
            "DeepSeek Chat": "deepseek/deepseek-chat:free",
            "DeepSeek R1": "deepseek/deepseek-r1:free",
            "Claude 2": "anthropic/claude-2:free",
            "GPT-3.5": "openai/gpt-3.5-turbo:free",
            "Gemini Flash Lite": "google/gemini-2.0-flash-lite-preview-02-05:free",
            "Gemini Pro Exp": "google/gemini-2.0-pro-exp-02-05:free",
            "Gemini Flash Thinking": "google/gemini-2.0-flash-thinking-exp:free",
            "Gemini Flash Thinking 1219": "google/gemini-2.0-flash-thinking-exp-1219:free",
            "Gemini Flash": "google/gemini-2.0-flash-exp:free",
            "Gemma 3 27B": "google/gemma-3-27b-it:free",
            "Claude 3 Opus": "anthropic/claude-3-opus:free",
            "Claude 3 Sonnet": "anthropic/claude-3-sonnet:free",
            "Mistral Medium": "mistral/mistral-medium:free",
            "Mixtral": "mistralai/mixtral-8x7b:free"
        }
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": {
            "GPT-3.5": "gpt-3.5-turbo",
            "GPT-4": "gpt-4"
        }
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "models": {
            "DeepSeek Chat": "deepseek-chat",
            "DeepSeek Code": "deepseek-coder"
        }
    },
    "Google": {
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "models": {
            "Gemini Flash Lite 2.0": "gemini-flash-lite-2.0",
            "Gemini Pro 2.0": "gemini-pro-2.0",
            "Gemini 2.0 Flash Thinking 01-21": "gemini-2.0-flash-thinking-01-21",
            "Gemini 2.0 Flash Thinking": "gemini-2.0-flash-thinking",
            "Gemini Flash 2.0": "gemini-flash-2.0",
            "Gemma 3 27B": "gemma-3-27b"
        }
    }
}

# 默认配置
DEFAULT_PROVIDER = "OpenRouter"
DEFAULT_MODEL = "deepseek/deepseek-r1:free"
DEFAULT_BASE_URL = PROVIDERS[DEFAULT_PROVIDER]["base_url"] 