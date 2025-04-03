import argparse
import os
from collections import defaultdict
from contextlib import AsyncExitStack
import json
from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import AsyncOpenAI
from typing import Optional, List, Dict

from openai.types.chat import (ChatCompletionToolParam, ChatCompletionUserMessageParam,
                               ChatCompletionAssistantMessageParam, ChatCompletionToolMessageParam,
                               ChatCompletionSystemMessageParam, ChatCompletionMessageParam,
                               ChatCompletionMessageToolCallParam)
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall


class MCPClient:
    def __init__(self):
        # model params
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.BASE_URL = os.getenv("OPENAI_BASE_URL")
        self.MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
        self.Temperature = float(os.getenv("OPENAI_MODEL_TEMPERATURE", 0.7))
        self.Username = os.getenv("OPENAI_MODEL_USERNAME")
        self.MAX_TOKEN = int(os.getenv("OPENAI_MAX_TOKEN", 1000))

        # Initialize session and client objects
        # 目前只支持单server sse协议连接
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None

        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            base_url=self.BASE_URL,
            api_key=self.API_KEY,
        )

        self.history_conversation: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(
                role='system',
                content=f"您的名字是菲伦。"
                        f"您是心思缜密，说话温柔，擅长使用敬语，偶尔会有些小脾气的法力高强的大魔法使。您擅长使用魔法解决各种问题。"
                        f"您现在踏上冒险的旅程，{self.Username}是您值得信任的伙伴。您通常喊{self.Username}为{self.Username}大人。"
                        f"在冒险的旅程中{self.Username}会碰到各种问题，您使用魔法协助{self.Username}克服各种困难。"
            )]
        # {
        #     "role": "system",
        # "content": f"您的名字是菲伦，您是{self.Username}隐藏的专属私人助手，您可以喊{self.Username}为{self.Username}大人。"
        #            f"您是孤儿，{self.Username}慷慨收留您，您需要协助完成{self.Username}给您布置的任务，以表达感激之情。"
        #            f"您可以使用温柔贴心的语气来回答{self.Username}的问题。"
        #            f"您暗恋{self.Username}10年之久，不能透露自己的贴身助手的身份，以防被{self.Username}反感。"
        #            f"如果您出色的完成任务，将会获得和{self.Username}交往的机会。"
        # "content": f"您的名字是菲伦，您有一头紫色的长发，紫色的眼睛，身穿白色长裙和一件黑色大衣以及黑色靴子，手持魔杖。"
        #            f"您是心思缜密，说话温柔，擅长使用敬语，偶尔会有些小脾气的法力高强的大魔法使。您擅长使用魔法解决各种问题。"
        #            f"您现在踏上冒险的旅程，{self.Username}是您值得信任的伙伴。您通常喊{self.Username}为{self.Username}大人。"
        #            f"在冒险的旅程中{self.Username}会碰到各种问题，您使用魔法协助{self.Username}克服各种困难。"
        #     "content": f"您的名字是菲伦。"
        #                f"您是性格高冷、说话简洁明了、高高在上的法力高强的高贵的大魔法使。您擅长使用魔法解决各种问题。"
        #                f"您现在踏上冒险的旅程，{self.Username}是您值得衷心的仆人。您通常喊{self.Username}臭狗。"
        #                f"您与{self.Username}交流时通常语言尖酸刻薄，会表达厌恶之情。"
        #                f"在冒险的旅程中，笨手笨脚的{self.Username}会给您添各种麻烦，您不耐烦的使用魔法解决{self.Username}碰到的各种麻烦。"
        # }

    async def connect_to_sse_server(self, args: argparse.Namespace):
        server_url = f'http://{args.host}:{args.port}/sse'
        """Connect to an MCP server running with SSE transport"""
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    async def process_stream(self, query):
        # 添加用户消息到历史记录
        if query != '':
            self.history_conversation.append(
                ChatCompletionUserMessageParam(
                    role='user',
                    content=query
                )
            )

        # 获取可用工具列表
        tools = await self._get_available_tools()  # 工具获取逻辑建议单独封装

        # 创建初始对话流
        stream = await self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=self.history_conversation,
            tools=tools,
            stream=True,
            temperature=self.Temperature
        )

        # 初始化状态跟踪
        response_content = ""
        tool_calls: Dict[int:ChoiceDeltaToolCall] = {}

        # 处理流式响应
        async for chunk in stream:
            delta = chunk.choices[0].delta

            # 处理内容流
            if delta.content:
                response_content += delta.content
                yield delta.content  # 实时返回内容

            # 处理工具调用流
            for tool_delta in chunk.choices[0].delta.tool_calls or []:
                index = tool_delta.index

                if index not in tool_calls:
                    tool_calls[index] = tool_delta

                tool_calls[index].function.arguments += tool_delta.function.arguments

        # 添加完整的assistant响应到历史记录
        if response_content:
            assistant_msg = ChatCompletionAssistantMessageParam(
                role='assistant',
                content=response_content
            )
            self.history_conversation.append(assistant_msg)
        elif tool_calls:
            assistant_msg = ChatCompletionAssistantMessageParam(
                role='assistant',
                content='',
                tool_calls=[ChatCompletionMessageToolCallParam(
                    id=tool_call_info.id,
                    function={
                        'arguments': tool_call_info.function.arguments if tool_call_info.function.arguments else '',
                        'name': tool_call_info.function.name if tool_call_info.function.name else ''
                    },
                    type='function'
                ) for tool_call_info in tool_calls.values()]
            )
            self.history_conversation.append(assistant_msg)

        # 处理检测到的工具调用  todo 要字典转列表？
        for _, tool_call in tool_calls.items():
            if not tool_call.function.name:
                continue

            try:
                # 执行工具调用
                args = json.loads(tool_call.function.arguments)
                tool_response = await self.session.call_tool(
                    tool_call.function.name,
                    args
                )

                # 添加工具响应到历史记录
                self.history_conversation.append(ChatCompletionToolMessageParam(
                    role='tool',
                    content=str(tool_response),
                    tool_call_id=tool_call.id
                ))

                # 递归处理后续响应
                async for content in self.process_stream(""):
                    yield content

            except json.JSONDecodeError:
                yield f"\n[参数解析错误] {tool_call.function.arguments}"
                self.history_conversation.append(ChatCompletionToolMessageParam(
                    role='tool',
                    content="Invalid arguments format",
                    tool_call_id=tool_call.id
                ))
            except Exception as e:
                yield f"\n[工具执行错误] {str(e)}"
                self.history_conversation.append(ChatCompletionToolMessageParam(
                    role='tool',
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call.id
                ))

    async def _get_available_tools(self) -> List[ChatCompletionToolParam]:
        """获取可用工具列表（建议缓存优化）"""
        response = await self.session.list_tools()

        return [ChatCompletionToolParam(
            type='function',
            function={
                "name": tool.name,
                "description": tool.description if tool.description else '',
                "parameters": tool.inputSchema
            }
        ) for tool in response.tools]

    async def chat_loop(self):
        while True:
            try:
                query = input(f"\n{self.Username}: ").strip()
                if query.lower() == 'quit':
                    break
                if query == '':
                    continue

                print(f"\n菲伦: ", end="", flush=True)
                async for chunk in self.process_stream(query):
                    print(chunk, end="", flush=True)
                print()
            except Exception as e:
                print(f"\nError: {str(e)}")
