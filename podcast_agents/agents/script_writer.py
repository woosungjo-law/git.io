"""팟캐스트 대본 생성 에이전트 - 7분 분량 대본 작성"""

from anthropic import Anthropic

from ..config import PodcastConfig
from ..prompts import script_prompts


class ScriptWriterAgent:
    """컬럼을 7분짜리 팟캐스트 대본으로 변환하는 에이전트"""

    def __init__(self, client: Anthropic, config: PodcastConfig):
        self.client = client
        self.config = config

    def run(
        self, column_text: str, category: str, core_topic: str
    ) -> str:
        """
        컬럼과 분류 정보를 받아 팟캐스트 대본을 생성합니다.

        Returns:
            7분 분량의 팟캐스트 대본 (문자열)
        """
        style = self.config.category_styles.get(
            category, self.config.category_styles["자기계발"]
        )

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=script_prompts.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": script_prompts.USER_PROMPT_TEMPLATE.format(
                        category=category,
                        tone=style["tone"],
                        approach=style["approach"],
                        target_audience=style["target_audience"],
                        opening_style=style["opening_style"],
                        core_topic=core_topic,
                        column_text=column_text,
                    ),
                }
            ],
        )

        return response.content[0].text
