import argparse
import os

from mcp.server.fastmcp import FastMCP

from kubectl_process import run_kubectl


def add_tools(mcp: FastMCP):

    @mcp.tool()
    def kubectl(namespace: str, command_args: list[str]) -> str:
        """
        Use for running kubectl with any set of arguments

        Args:
            namespace: The namespace of the deployments
            command_args: kubectl command line arguments
        """
        try:
            return run_kubectl([*command_args, "-n", namespace])
        except Exception as ex:
            return str(ex)

    @mcp.tool()
    def kubectl_apply(namespace: str, yaml_content: str) -> str:
        """
        Used to apply a kubernetes yaml

        Args:
          yaml_content: The yaml file content to apply
          namespace: The namespace of the deployments

        """
        try:
            return run_kubectl(["apply", "-n", namespace, "-f", "-"], stdin=yaml_content)
        except Exception as ex:
            return str(ex)


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
