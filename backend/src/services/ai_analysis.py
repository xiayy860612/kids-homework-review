"""AI analysis service for wrong question images."""

import asyncio
from datetime import UTC, datetime

from openai import AsyncOpenAI
from openai import OpenAIError as OpenAIError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings


class AIAnalysisService:
    """Service for AI-powered wrong question analysis."""

    def __init__(self) -> None:
        """Initialize AI analysis service."""
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_API_BASE,
            # timeout=settings.AI_TIMEOUT,
        )

    async def call_ai_model(
        self, image_base64: str, title: str
    ) -> str:
        """Call AI model to analyze the image.

        Args:
            image_base64: Base64 encoded image
            title: Question title

        Returns:
            Markdown formatted analysis result

        Raises:
            OpenAIError: If AI API call fails
        """
        # Build prompt
        prompt = f"""你是一位经验丰富的老师，请分析这道题目（标题：{title}）的截图。

请按照以下结构提供详细解析：

## 1. 题目分析
- 简要说明题目考查的知识点
- 难度评估（简单/中等/困难）

## 2. 解题思路
- 逐步推导的解题思路
- 关键步骤说明

## 3. 详细解答
- 完整的解题步骤
- 每一步的详细说明
- 必要的公式和定理

## 4. 知识点总结
- 相关的知识点梳理
- 易错点提醒
- 类似题型的解题技巧

请使用清晰的 Markdown 格式输出，确保排版清晰、步骤详细、便于学生理解。

重要格式要求：
- 数学公式必须使用 LaTeX 格式
- 行内公式：必须用单个美元符号包裹，如 $x^2 + 2x$（禁止使用 \\( 和 \\)）
- 块级公式（单独一行）：用双美元符号包裹，如 $$\\int_0^1 x dx$$（禁止使用 \\[ 和 \\]）
- 公式中的中文单位（如"千克"、"米"等）直接写在公式内，使用 \\text{{}} 命令包裹
- 正确示例：
  - 行内：质量 $m = 5\\text{{kg}}$
  - 块级：$$9000 \\div 1000 = 9\\text{{千克}}$$
- 标题使用 ## 或 ### 开头
- 列表使用 - 或 1. 开头"""

        response = await self.client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_base64},
                        },
                    ],
                }
            ],
            # max_tokens=20000,
            temperature=0.3,
        )

        # Extract analysis result
        return response.choices[0].message.content or "无法获取解析结果"
