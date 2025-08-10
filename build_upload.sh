docker buildx build \
  --platform linux/arm64 \
  -t digmatic/kubectl-mcp:$TAG \
  --push .