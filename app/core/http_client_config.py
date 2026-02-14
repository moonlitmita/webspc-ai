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

    # 统一禁用HTTP/2以避免协议兼容性问题和缺少依赖包的问题
    # 在K3s环境中，网络层与HTTP/2可能存在兼容性问题
    # 为保持环境一致性，开发环境也禁用HTTP/2
    http2_support = False

    import httpx
    return httpx.Client(
        base_url=base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        http2=http2_support,
        timeout=60.0
    )


def create_async_http_client(base_url: str, api_key: str) -> AsyncClient:
    """
    创建异步HTTP客户端，根据环境配置适当的HTTP设置
    """
    # 检查是否在K3s环境中运行（保留此变量用于将来可能的差异化配置）
    is_k3s_env = os.getenv("ENV", "").lower() == "prod" or os.getenv("KUBERNETES_SERVICE_HOST") is not None

    # 统一禁用HTTP/2以避免协议兼容性问题和缺少依赖包的问题
    # 在K3s环境中，网络层与HTTP/2可能存在兼容性问题
    # 为保持环境一致性，开发环境也禁用HTTP/2
    http2_support = False

    import httpx
    return httpx.AsyncClient(
        base_url=base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        http2=http2_support,
        timeout=60.0
    )


def get_httpx_client(http2_enabled: bool = True) -> AsyncClient:
    """
    获取httpx客户端，根据环境配置HTTP/2设置
    """
    # 检查是否在K3s环境中运行
    is_k3s_env = os.getenv("ENV", "").lower() == "prod" or os.getenv("KUBERNETES_SERVICE_HOST") is not None

    # 如果明确指定禁用HTTP/2或在K3s环境中运行，则禁用HTTP/2
    use_http2 = http2_enabled and not is_k3s_env

    import httpx
    return httpx.AsyncClient(
        http2=use_http2,
        timeout=60.0
    )