#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

"""
工具包装器模块，用于处理工具调用参数验证和格式化
"""

import json
from typing import Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class ValidatingToolWrapper(BaseTool):
    """
    包装MCP工具，确保参数在调用前经过验证和格式化
    """

    def __init__(self, tool: BaseTool):
        self._tool = tool
        name = getattr(tool, 'name', 'unnamed_tool')
        description = getattr(tool, 'description', '')
        args_schema = self._create_validated_args_schema(tool)

        # 从原工具复制其他属性
        super().__init__(
            name=name,
            description=description,
            args_schema=args_schema,
            return_direct=getattr(tool, 'return_direct', False),
            verbose=getattr(tool, 'verbose', False),
            callbacks=getattr(tool, 'callbacks', None),
            tags=getattr(tool, 'tags', []),
            metadata=getattr(tool, 'metadata', {}),
            handle_tool_error=getattr(tool, 'handle_tool_error', None),
            handle_validation_error=getattr(tool, 'handle_validation_error', None)
        )

    def _create_validated_args_schema(self, original_tool: BaseTool):
        """
        创建一个新的参数模式，确保所有参数都是字符串类型
        """
        if not hasattr(original_tool, 'args_schema') or not original_tool.args_schema:
            # 如果原工具没有参数模式，创建一个空的
            return type("ValidatedEmptySchema", (BaseModel,), {})

        # 获取原始参数模式的字段定义
        original_fields = {}
        if hasattr(original_tool.args_schema, '__fields__'):
            # Pydantic v1
            original_fields = original_tool.args_schema.__fields__
        elif hasattr(original_tool.args_schema, 'model_fields'):
            # Pydantic v2
            original_fields = original_tool.args_schema.model_fields

        # 创建新的字段定义，确保所有字段都是字符串类型
        validated_fields = {}
        for field_name, field_info in original_fields.items():
            description = getattr(field_info, 'description', '') or getattr(getattr(field_info, 'field_info', None), 'description', '') or ''
            validated_fields[field_name] = (str, Field(description=description))

        if validated_fields:
            # 动态创建新的Pydantic模型
            schema_name = getattr(original_tool.args_schema, '__name__', 'ToolSchema')
            class_name = f"Validated{schema_name}"

            return type(
                class_name,
                (BaseModel,),
                {'__annotations__': {k: v[0] for k, v in validated_fields.items()}, **validated_fields}
            )
        else:
            return type("ValidatedEmptySchema", (BaseModel,), {})

    def _run(self, **kwargs):
        """
        同步运行工具
        """
        validated_kwargs = self._validate_and_format_args(kwargs)
        result = self._tool.invoke(validated_kwargs)
        return self._ensure_string_result(result)

    async def _arun(self, **kwargs):
        """
        异步运行工具
        """
        validated_kwargs = self._validate_and_format_args(kwargs)
        result = await self._tool.ainvoke(validated_kwargs)
        return self._ensure_string_result(result)

    def _validate_and_format_args(self, kwargs):
        """
        验证并格式化参数，确保所有参数都是字符串类型
        """
        validated_kwargs = {}
        for key, value in kwargs.items():
            if value is None:
                validated_kwargs[key] = ""
            elif isinstance(value, (dict, list)):
                validated_kwargs[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                validated_kwargs[key] = str(value).lower()
            elif isinstance(value, (int, float)):
                validated_kwargs[key] = str(value)
            else:
                validated_kwargs[key] = str(value)
        return validated_kwargs

    def _ensure_string_result(self, result: Any) -> str:
        """
        确保返回结果是字符串类型
        """
        if result is None:
            return "操作完成，无返回结果"
        elif isinstance(result, str):
            return result
        elif isinstance(result, (dict, list)):
            try:
                return json.dumps(result, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(result)
        else:
            return str(result)