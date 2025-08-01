import argparse
import os

from mcp.server.fastmcp import FastMCP


def add_tools(mcp: FastMCP):

    @mcp.tool()
    def echo_tool(text: str) -> str:
        """Echo the input text"""
        return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--transport", type=str, choices=["sse", "stdio", "streamable-http"], default="sse")
    parser.add_argument("-p", "--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")

    args = parser.parse_args()

    port = os.getenv("PORT", args.port)
    host = os.getenv("HOST", args.host)

    mcp = FastMCP("Kubectl Mcp Server", port=port, host=host)
    add_tools(mcp=mcp)
    mcp.run(transport=args.transport)
