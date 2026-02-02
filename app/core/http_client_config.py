#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

"""
HTTP客户端配置模块，用于处理不同环境下的HTTP请求配置
特别是解决K3s环境中的HTTP/2兼容性问题
"""

import os
from httpx import Client, AsyncClient
from openai import AsyncOpenAI


def create_sync_http_client(base_url: str, api_key: str) -> Client:
    """
    创建同步HTTP客户端，根据环境配置适当的HTTP设置
    """
    # 检查是否在K3s环境中运行（保留此变量用于将来可能的差异化配置）
    is_k3s_env = os.getenv("ENV", "").lower() == "prod" or os.getenv("KUBERNETES_SERVICE_HOST") is not None

    # 根据环境决定是否禁用HTTP/2
    import httpx

    # 统一禁用HTTP/2以避免协议兼容性问题和缺少依赖包的问题
    # 在K3s环境中，网络层与HTTP/2可能存在兼容性问题
    # 为保持环境一致性，开发环境也禁用HTTP/2
    http2_support = False

    return httpx.Client(
        base_url=base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        http2=http2_support,
        timeout=60.0
    )


def create_async_http_client(base_url: str, api_key: str) -> AsyncOpenAI:
    """
    创建异步OpenAI客户端，根据环境配置适当的HTTP设置
    """
    # 检查是否在K3s环境中运行
    is_k3s_env = os.getenv("ENV", "").lower() == "prod" or os.getenv("KUBERNETES_SERVICE_HOST") is not None

    # 根据环境决定是否禁用HTTP/2
    http_client = None
    if is_k3s_env:
        # 在K3s环境中，使用自定义HTTP客户端禁用HTTP/2
        import httpx
        http_client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            http2=False,  # 禁用HTTP/2以避免协议错误
            timeout=60.0
        )

    # 创建OpenAI客户端
    if http_client:
        return AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=http_client
        )
    else:
        return AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )


def get_httpx_client(http2_enabled: bool = True) -> AsyncClient:
    """
    获取httpx客户端，根据环境配置HTTP/2设置
    """
    import httpx

    # 检查是否在K3s环境中运行
    is_k3s_env = os.getenv("ENV", "").lower() == "prod" or os.getenv("KUBERNETES_SERVICE_HOST") is not None

    # 如果明确指定禁用HTTP/2或在K3s环境中运行，则禁用HTTP/2
    use_http2 = http2_enabled and not is_k3s_env

    return AsyncClient(
        http2=use_http2,
        timeout=60.0
    )