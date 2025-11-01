model_configs = {
    "localmodel": {
        "label": "LocalModel",
        "models": {
            "localmodel-1": {
                "id": "localmodel-1",
                "name": "localmodel-1",
                "base_url": "http://localhost:666",
                "api_key_env": "LOCALMODEL_API_KEY"
            }
        }
    },
    "siliconflow": {
        "label": "SiliconFlow",
        "models": {
            "deepseek-r1": {
                "id": "deepseek-r1",
                "name": "DeepSeek-R1",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key_env": "SILICONFLOW_API_KEY"
            },
            "qwen2.5-7b-instruct": {
                "id": "qwen2.5-7b-instruct",
                "name": "Qwen/Qwen2.5-7B-Instruct",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key_env": "SILICONFLOW_API_KEY"
            },
            "qwen2.5-14b-instruct": {
                "id": "qwen2.5-14b-instruct",
                "name": "Qwen/Qwen2.5-14B-Instruct",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key_env": "SILICONFLOW_API_KEY"
            },
            "qwen2.5-32b-instruct": {
                "id": "qwen2.5-32b-instruct",
                "name": "Qwen/Qwen2.5-32B-Instruct",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key_env": "SILICONFLOW_API_KEY"
            },
            "glm-4-9b-chat": {
                "id": "glm-4-9b-chat",
                "name": "THUDM/glm-4-9b-chat",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key_env": "SILICONFLOW_API_KEY"
            },
            "yi-1.5-9b-chat-16k": {
                "id": "yi-1.5-9b-chat-16k",
                "name": "01-ai/Yi-1.5-9B-Chat-16K",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key_env": "SILICONFLOW_API_KEY"
            }
        }
    },
    "modelscope": {
        "label": "ModelScope",
        "models": {
            "qwen3-8b-instruct": {
                "id": "qwen3-8b-instruct",
                "name": "Qwen/Qwen3-8B-Instruct",
                "base_url": "https://api-inference.modelscope.cn/v1",
                "api_key_env": "MODELSCOPE_API_KEY"
            },
            "qwen3-14b-instruct": {
                "id": "qwen3-14b-instruct",
                "name": "Qwen/Qwen3-14B-Instruct",
                "base_url": "https://api-inference.modelscope.cn/v1",
                "api_key_env": "MODELSCOPE_API_KEY"
            },
            "qwen3-coder-480b-a35b-instruct": {
                "id": "qwen3-coder-480b-a35b-instruct",
                "name": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
                "base_url": "https://api-inference.modelscope.cn/v1",
                "api_key_env": "MODELSCOPE_API_KEY"
            },
            "qwen3-235b-a22b-instruct": {
                "id": "qwen3-235b-a22b-instruct",
                "name": "Qwen/Qwen3-235B-A22B-Instruct",
                "base_url": "https://api-inference.modelscope.cn/v1",
                "api_key_env": "MODELSCOPE_API_KEY"
            }
        }
    },
    "dashscope": {
        "label": "DashScope",
        "models": {
            "qwen-max": {
                "id": "qwen-max",
                "name": "qwen-max",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen-max-latest": {
                "id": "qwen-max-latest",
                "name": "qwen-max-latest",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen-plus": {
                "id": "qwen-plus",
                "name": "qwen-plus",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen-plus-latest": {
                "id": "qwen-plus-latest",
                "name": "qwen-plus-latest",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen-turbo": {
                "id": "qwen-turbo",
                "name": "qwen-turbo",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen-turbo-latest": {
                "id": "qwen-turbo-latest",
                "name": "qwen-turbo-latest",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen3-max": {
                "id": "qwen3-max",
                "name": "qwen3-max",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen3-8b": {
                "id": "qwen3-8b",
                "name": "qwen3-8b",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen3-14b": {
                "id": "qwen3-14b",
                "name": "qwen3-14b",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen3-32b": {
                "id": "qwen3-32b",
                "name": "qwen3-32b",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen3-coder-plus": {
                "id": "qwen3-coder-plus",
                "name": "qwen3-coder-plus",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "qwen3-coder-flash": {
                "id": "qwen3-coder-flash",
                "name": "qwen3-coder-flash",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_env": "DASHSCOPE_API_KEY"
            }
        }
    },
    "zhipuai": {
        "label": "ChatGLM",
        "models": {
            "glm-4-flash": {
                "id": "glm-4-flash",
                "name": "glm-4-flash",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            },
            "glm-4-plus": {
                "id": "glm-4-plus",
                "name": "glm-4-plus",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            },
            "glm-4-pro": {
                "id": "glm-4-pro",
                "name": "glm-4-pro",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            },
            "glm-4-air": {
                "id": "glm-4-air",
                "name": "glm-4-air",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            },
            "glm-4-airx": {
                "id": "glm-4-airx",
                "name": "glm-4-airx",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            },
            "glm-4-long": {
                "id": "glm-4-long",
                "name": "glm-4-long",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            },
            "glm-4v-plus": {
                "id": "glm-4v-plus",
                "name": "glm-4v-plus",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key_env": "ZHIPUAI_API_KEY"
            }
        }
    },
    "moonshot": {
        "label": "Moonshot",
        "models": {
            "kimi-8k": {
                "id": "kimi-8k",
                "name": "kimi-8k",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key_env": "MOONSHOT_API_KEY"
            },
            "kimi-32k": {
                "id": "kimi-32k",
                "name": "kimi-32k",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key_env": "MOONSHOT_API_KEY"
            },
            "kimi-128k": {
                "id": "kimi-128k",
                "name": "kimi-128k",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key_env": "MOONSHOT_API_KEY"
            },
            "kimi-200w-long-text": {
                "id": "kimi-200w-long-text",
                "name": "kimi-200w-long-text",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key_env": "MOONSHOT_API_KEY"
            }
        }
    },
    "doubao": {
        "label": "Doubao",
        "models": {
            "doubao-lite-4k": {
                "id": "doubao-lite-4k",
                "name": "doubao-lite-4k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            },
            "doubao-lite-32k": {
                "id": "doubao-lite-32k",
                "name": "doubao-lite-32k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            },
            "doubao-lite-128k": {
                "id": "doubao-lite-128k",
                "name": "doubao-lite-128k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            },
            "doubao-pro-4k": {
                "id": "doubao-pro-4k",
                "name": "doubao-pro-4k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            },
            "doubao-pro-32k": {
                "id": "doubao-pro-32k",
                "name": "doubao-pro-32k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            },
            "doubao-pro-128k": {
                "id": "doubao-pro-128k",
                "name": "doubao-pro-128k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            },
            "doubao-pro-256k": {
                "id": "doubao-pro-256k",
                "name": "doubao-pro-256k",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key_env": "DOUBAO_API_KEY"
            }
        }
    },
    "deepseek": {
        "label": "DeepSeek",
        "models": {
            "deepseek-chat": {
                "id": "deepseek-chat",
                "name": "deepseek-chat",
                "base_url": "https://api.deepseek.com/v1",
                "api_key_env": "DEEPSEEK_API_KEY"
            },
            "deepseek-coder": {
                "id": "deepseek-coder",
                "name": "deepseek-coder",
                "base_url": "https://api.deepseek.com/v1",
                "api_key_env": "DEEPSEEK_API_KEY"
            },
            "deepseek-reasoner": {
                "id": "deepseek-reasoner",
                "name": "deepseek-reasoner",
                "base_url": "https://api.deepseek.com/v1",
                "api_key_env": "DEEPSEEK_API_KEY"
            }
        }
    }
}