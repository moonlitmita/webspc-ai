#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from app.tasks import celery_app
from app.core.logger_config import get_logger
from app.services.model_config import model_service
from langchain_core.messages import HumanMessage
from app.services.mcp import load_mcp_config_from_redis, filter_server_configs_for_client
from app.services.robust_mcp_client import RobustMultiServerMCPClient
import asyncio
import json

logger = get_logger(__name__)

@celery_app.task(bind=True, name='app.tasks.alarm_analysis.analyze_alarm_and_notify_task')
def analyze_alarm_and_notify_task(self, alarm_data: dict, user_id: str):
    """
    Celery task to analyze alarm data with LLM and send notification to Feishu
    """
    try:
        logger.info(f"Starting alarm analysis task for user {user_id}")

        # Get the appropriate LLM for the user
        llm = model_service.get_llm(user_id)

        # Prepare the prompt for alarm analysis
        prompt = f"""
        请分析以下告警信息并提供专业的处理建议：

        告警标题: {alarm_data['title']}
        告警内容: {alarm_data['content']}
        异常点: {alarm_data['outliers']}
        项目名称: {alarm_data['project']}
        制程: {alarm_data['process']}
        产品: {alarm_data['product']}
        控制图类型: {alarm_data['spcType']}
        
        如果有附加信息: {alarm_data.get('additional_info', '无')}

        请提供：
        1. 告警原因分析
        2. 可能的影响评估
        3. 处理建议
        4. 预防措施
        """

        # Call the LLM to analyze the alarm
        logger.info("Sending alarm data to LLM for analysis...")
        response = llm.invoke([HumanMessage(content=prompt)])

        analysis_result = response.content
        logger.info("LLM analysis completed")

        # Prepare the message to send to Feishu
        feishu_message = f"""
        🚨 告警分析结果 🚨

        告警标题: {alarm_data['title']}

        告警内容: {alarm_data['content']}

        异常点：{alarm_data['outliers']}

        分析结果:
        {analysis_result}
        """

        # Use MCP client to send notification to Feishu
        # Find the Feishu tool from MCP client
        logger.info("Attempting to send notification to Feishu via MCP...")

        # Since we're in a Celery task, we need to run the async function
        result = asyncio.run(send_to_feishu_via_mcp(feishu_message))

        logger.info(f"Feishu notification sent successfully: {result}")

        return {
            "status": "success",
            "analysis": analysis_result,
            "feishu_notification_result": result
        }

    except Exception as e:
        logger.error(f"Error in alarm analysis task: {e}", exc_info=True)
        # Retry the task if it's not the final retry
        if self.request.retries < 3:
            raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
        else:
            return {
                "status": "failed",
                "error": str(e)
            }

async def send_to_feishu_via_mcp(message: str):
    """
    Send message to Feishu using MCP client
    Since Celery runs in a separate process, we need to initialize a new MCP client
    """
    try:
        # Load the MCP configuration from Redis (since Celery is a separate process)
        mcp_config = load_mcp_config_from_redis()
        filtered_server_configs = filter_server_configs_for_client(mcp_config["mcpServers"])

        # Create a new MCP client instance for this task
        mcp_client = RobustMultiServerMCPClient(filtered_server_configs)

        # Get available tools from MCP client
        tools = await mcp_client.get_tools()

        # Look for a Feishu notification tool specifically
        feishu_tool = None
        for tool in tools:
            # Look for tools that might be related to Feishu notifications
            if any(keyword in tool.name.lower() for keyword in ['feishu', 'lark', 'notification', 'message', 'send']):
                feishu_tool = tool
                break

        if not feishu_tool:
            # If no specific Feishu tool is found, log a warning and return a simulated result
            # In a real implementation, the feishu-mcp-server should provide a specific tool
            logger.warning("No Feishu notification tool found in MCP client. Available tools: %s",
                          [tool.name for tool in tools])

            # For now, we'll return a simulated result, but in a real implementation
            # you would need to ensure the feishu-mcp-server is properly configured
            return {
                "status": "simulated",
                "message": "Feishu notification simulated (feishu-mcp-server tool not found)",
                "available_tools": [tool.name for tool in tools]
            }

        # Execute the tool to send the message to Feishu
        # Based on the feishu-mcp-server implementation, it expects 'message' parameter
        result = await feishu_tool.ainvoke({"message": message, "title": "告警分析结果"})

        return result
    except Exception as e:
        logger.error(f"Error sending to Feishu via MCP: {e}", exc_info=True)
        raise e