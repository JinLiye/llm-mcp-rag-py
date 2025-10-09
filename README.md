# LLM-MCP-RAG-py

## Dependency
```
pip install -r requirement.txt
```
Also need to install [nodejs](https://nodejs.org/zh-cn)

## How To Run
- get chat api from [openrouter](https://openrouter.ai/)
- get embedding api from [siliconflow](https://cloud.siliconflow.cn/models)
- create and put api key in .env file

    **example of .env**
    ```
    OPENAI_API_KEY=xxx
    OPENAI_BASE_URL=https://openrouter.ai/api/v1

    EMBEDDING_KEY=xxx
    EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
    ```
- To start the main program, use the following command:
    ```
    python ./scr/main.py
    ```
    To test the chat functionality module, run:
    ```
    python ./src/test_chat.py
    ```
    To test the MCP client functionality, execute:
    ```
    python ./src/testMCPClient.py
    ```
    To test the Agent module functionality, run:
    ```
    python ./src/Agent.py
    ```
    **Note:** When testing the Agent, make sure to set up the MCP client correctly. Modify the directory path r'C:\Users\32114\Desktop\code\llm-mcp-rag-py\output' to suit your needs, allowing access to the appropriate directory.
## LLM
- [OpenAI API](https://platform.openai.com/docs/api-reference/chat)

## MCP

- [MCP 架构](https://modelcontextprotocol.io/docs/concepts/architecture)
- [MCP Client](https://modelcontextprotocol.io/quickstart/client)
- [Fetch MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
- [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)

## RAG

- [Retrieval Augmented Generation](https://scriv.ai/guides/retrieval-augmented-generation-overview/)
    - 译文: https://www.yuque.com/serviceup/misc/cn-retrieval-augmented-generation-overview
- [硅基流动](https://cloud.siliconflow.cn/models)

- [json数据](https://jsonplaceholder.typicode.com/)

## Acknowledgments
This project is based on the work of [llm-mcp-rag](https://github.com/KelvinQiu802/llm-mcp-rag), which was originally implemented in TypeScript. This implementation has been rewritten using Python