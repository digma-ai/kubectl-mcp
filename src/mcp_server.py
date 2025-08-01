import argparse
import os

from fastmcp.exceptions import ToolError
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from kubectl_process import run_kubectl


def add_tools(mcp: FastMCP):

    @mcp.tool(name="kubectl", description="Use for running kubectl with any set of arguments")
    def kubectl(
        namespace: str = Field(description="The k8s namespace"),
        command_args: list[str] = Field(description="kubectl command line arguments"),
    ) -> str:
        try:
            return run_kubectl([*command_args, "-n", namespace])
        except Exception as ex:
            raise ToolError(ex)

    @mcp.tool(name="", description="Used to apply a kubernetes yaml")
    def kubectl_apply(
        namespace: str = Field(description="The k8s namespace"),
        yaml_content: str = Field(description="The yaml file content to apply"),
    ) -> str:
        try:
            return run_kubectl(["apply", "-n", namespace, "-f", "-"], stdin=yaml_content)
        except Exception as ex:
            raise ToolError(ex)


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
