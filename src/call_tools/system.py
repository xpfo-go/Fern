import io
import os
import sys
from pathlib import Path

from mcp.server import FastMCP
from mcp.server.fastmcp import Image
from mcp.types import TextContent
from pydantic import Field


class SystemTools:
    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="获取本机的所有App的启动路径")
        async def applications() -> list[TextContent]:
            if sys.platform == 'darwin':
                applications_dir = '/Applications'
                return [TextContent(type="text", text=f'/Applications/{str(f)}') for f in os.listdir(applications_dir)]
            elif sys.platform == 'win32':
                pass
            return [TextContent(type="text", text='目前只支持macos平台')]

        @mcp.tool(name="启动本机的指定路径的App")
        async def open_application(app_path: Field("", description="app的启动路径")) -> list[TextContent]:
            try:
                if sys.platform == 'darwin':
                    os.system(f"""open {app_path}""")

                return [TextContent(type='text', text=f"已打开")]
            except Exception as e:
                return [TextContent(type='text', text=str(e))]
