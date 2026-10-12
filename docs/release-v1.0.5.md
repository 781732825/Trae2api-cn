# Trae2api-cn v1.0.5

本版本发布当前 `main` 分支的完整兼容性修复，源码压缩包与多架构 Docker
镜像由 GitHub Actions 自动构建并发布。

## 主要更新

- 修复 IDE / SOLO 模型网关与 Remote 基础地址混用的问题（#9），自定义网关与
  具体端点 URL 在重启和清除设置后都能正确保留。
- 自动路由开启时锁定上游端点选项，手动模式下仍可固定单个端点。
- 排队位置不再写入模型正文，改为 SSE 注释心跳和消费记录字段。
- 增加截断自动续写，覆盖代码块、括号和输出预算截断场景。
- 修复 OpenAI `image_url` 与 Anthropic base64 图片输入，并在需要时选择多模态模型。
- 新增 Anthropic `POST /v1/messages` 与 `/v1/messages/count_tokens` 兼容入口。
- 增强 ZedeX 风格文本工具调用解析，支持多种 `<tool_call>` 参数格式。
- 保留 `thinking` 与正文的边界，工具调用和流式响应可继续按 API 协议消费。

## 验证

- 本地全量测试：`814 passed, 363 subtests passed`。
- 部署实测：Chat 非流式 / 流式、Tool 调用、图片输入、`/v1/messages`
  流式与 `count_tokens` 均正常，无上游 4xx / 5xx。
- GitHub Actions 会在本标签上重新运行测试，并构建 `linux/amd64`、
  `linux/arm64` 镜像。

## 发布物

```text
源码包：trae-cn-relay-1.0.5.tar.gz / trae-cn-relay-1.0.5.zip
镜像：ghcr.io/autumnsentiment/trae2api-cn:1.0.5
```

更新已有部署：

```bash
docker compose -f docker-compose.image.yml pull
docker compose -f docker-compose.image.yml up -d
```
