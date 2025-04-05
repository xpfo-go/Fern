import argparse
import asyncio
import os
import json
import queue
import threading

from contextlib import AsyncExitStack
from mcp import ClientSession
from openai import AsyncOpenAI
from typing import Optional, List
from openai.types.chat import (ChatCompletionToolParam, ChatCompletionUserMessageParam,
                               ChatCompletionAssistantMessageParam, ChatCompletionToolMessageParam,
                               ChatCompletionSystemMessageParam, ChatCompletionMessageParam,
                               ChatCompletionMessageToolCallParam)
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall


from mcp.client.sse import sse_client


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
        # only support single sse server, it may be expanded in the future
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None

        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            base_url=self.BASE_URL,
            api_key=self.API_KEY,
        )

        # only support single user now,
        # self.history_conversation: user history conversation
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

    async def connect_to_mcp_sse_server(self, server_url: str):
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

    async def clean_up(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    def process_stream_async2sync(self, query):
        llm_queue = queue.Queue()

        def run_llm_async(prompt: str):
            async def wrapper():
                async for text in self.process_stream(prompt):
                    llm_queue.put(text)
                # 用 None 表示结束
                llm_queue.put(None)

            # asyncio.run(wrapper())
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(wrapper())
            new_loop.close()

        def sync_llm_generator():
            while True:
                text = llm_queue.get()
                if text is None:
                    break
                yield text

        threading.Thread(target=run_llm_async, args=(query,), daemon=True).start()

        return sync_llm_generator

    async def process(self, query):
        # todo 流式调用还有问题
        """process response from openai api"""
        # add user query to history conversation
        if query != '':
            self.history_conversation.append(
                ChatCompletionUserMessageParam(
                    role='user',
                    content=query
                )
            )
        # get mcp server available tools
        tools = await self._get_available_tools()

        response = await self.client.chat.completions.create(
            model=self.MODEL_NAME,
            max_tokens=1000,
            messages=self.history_conversation,
            tools=tools
        )

        final_text = []
        message = response.choices[0].message
        final_text.append(message.content or "")

        # 处理响应并处理工具调用
        while message.tool_calls:
            # 处理每个工具调用
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # 执行工具调用
                result = await self.session.call_tool(tool_name, tool_args)

                # 将工具调用和结果添加到消息历史
                assistant_msg = ChatCompletionAssistantMessageParam(
                    role='assistant',
                    content='',
                    tool_calls=[ChatCompletionMessageToolCallParam(
                        id=tool_call.id,
                        function={
                            'arguments': json.dumps(tool_args),
                            'name': tool_name
                        },
                        type='function'
                    )]
                )
                self.history_conversation.append(assistant_msg)

                self.history_conversation.append(ChatCompletionToolMessageParam(
                    role='tool',
                    content=str(result),
                    tool_call_id=tool_call.id
                ))

            # 将工具调用的结果交给 LLM
            response = await self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=self.history_conversation,
                tools=tools
            )

            message = response.choices[0].message
            if message.content:
                final_text.append(message.content)

        return "".join(final_text)

    async def process_stream(self, query):
        """process stream response from openai api"""

        # add user query to history conversation
        if query != '':
            self.history_conversation.append(
                ChatCompletionUserMessageParam(
                    role='user',
                    content=query
                )
            )

        # get mcp server available tools
        tools = await self._get_available_tools()

        # create stream response from openai api
        stream = await self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=self.history_conversation,
            tools=tools,
            stream=True,
            temperature=self.Temperature
        )

        # init stream response state
        response_content = ""
        tool_calls: List[ChoiceDeltaToolCall] = []

        # process stream response
        async for chunk in stream:
            delta = chunk.choices[0].delta

            # if content is not None, it means the model is generating content
            if delta.content:
                response_content += delta.content
                yield delta.content  # return stream response

            # if tool_calls is not None, it means the model is generating want used tool calls
            for tool_delta in chunk.choices[0].delta.tool_calls or []:
                existing = next((tc for tc in tool_calls if tc.index == tool_delta.index), None)
                if existing:
                    existing.function.arguments += tool_delta.function.arguments
                else:
                    tool_calls.append(tool_delta)

        # add full assistant response to history conversation
        if response_content:
            # add content to history conversation
            assistant_msg = ChatCompletionAssistantMessageParam(
                role='assistant',
                content=response_content
            )
            self.history_conversation.append(assistant_msg)
        elif tool_calls:
            # add model want used tool calls to history conversation
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
                ) for tool_call_info in tool_calls]
            )
            self.history_conversation.append(assistant_msg)

        # Process tool calls
        # This ordering guarantees the tool invocation order
        tool_calls.sort(key=lambda tc: tc.index)
        for tool_call in tool_calls:
            if not tool_call.function.name:
                continue

            try:
                # MCP Server call tool.
                args = json.loads(tool_call.function.arguments)
                tool_response = await self.session.call_tool(
                    tool_call.function.name,
                    args
                )

                # add call tool response to history conversation
                self.history_conversation.append(ChatCompletionToolMessageParam(
                    role='tool',
                    content=str(tool_response),
                    tool_call_id=tool_call.id
                ))

                # recursive call process_stream to process tool response
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

    async def run_with_stream_console(self):
        """
        blocking run with console
        """
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

                print(f"\n历史记录: {self.history_conversation}")
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def run_with_console(self):
        while True:
            try:
                query = input(f"\n{self.Username}: ").strip()
                if query.lower() == 'quit':
                    break
                if query == '':
                    continue
                response = await self.process(query)
                print("\n菲伦：" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def run_with_sse_server(self):
        """
        TODO: blocking run with sse server
        """
        pass

    def __del__(self):
        self.clean_up()
