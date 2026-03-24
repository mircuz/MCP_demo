"""Model Serving tools — LLM and ML inference on Databricks."""

from __future__ import annotations

from config import MODEL_SERVING_ENDPOINT


def register(mcp, w):
    """Register model-serving tools with the MCP server."""

    @mcp.tool()
    def invoke_model(prompt: str, max_tokens: int = 512) -> str:
        """Send a prompt to a model hosted on Databricks Model Serving.

        Args:
            prompt: The user message to send to the model.
            max_tokens: Maximum tokens in the response (default 512).
        """
        response = w.serving_endpoints.query(
            name=MODEL_SERVING_ENDPOINT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
