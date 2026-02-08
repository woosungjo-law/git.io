"""컬럼 분류 에이전트 - 법률/인문학/자기계발 카테고리 판별"""

import re

from anthropic import Anthropic

from ..config import PodcastConfig
from ..prompts import classifier_prompts


class ClassifierAgent:
    """컬럼을 3가지 카테고리로 분류하는 에이전트"""

    VALID_CATEGORIES = {"법률", "인문학", "자기계발"}

    def __init__(self, client: Anthropic, config: PodcastConfig):
        self.client = client
        self.config = config

    def run(self, column_text: str) -> dict:
        """
        컬럼을 분류하고 결과를 반환합니다.

        Returns:
            {
                "category": "법률" | "인문학" | "자기계발",
                "core_topic": "핵심 주제 한 줄 요약",
                "reasoning": "분류 근거"
            }
        """
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=512,
            system=classifier_prompts.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": classifier_prompts.USER_PROMPT_TEMPLATE.format(
                        column_text=column_text
                    ),
                }
            ],
        )

        return self._parse_response(response.content[0].text)

    def _parse_response(self, text: str) -> dict:
        """응답을 파싱하여 구조화된 데이터를 반환합니다."""
        result = {
            "category": "자기계발",  # 기본값
            "core_topic": "",
            "reasoning": "",
        }

        for line in text.strip().split("\n"):
            line = line.strip()
            if line.startswith("카테고리:"):
                category = line.replace("카테고리:", "").strip()
                if category in self.VALID_CATEGORIES:
                    result["category"] = category
            elif line.startswith("핵심주제:"):
                result["core_topic"] = line.replace("핵심주제:", "").strip()
            elif line.startswith("분류근거:"):
                result["reasoning"] = line.replace("분류근거:", "").strip()

        return result
