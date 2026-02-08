"""썸네일 프롬프트 생성 에이전트 (나노바나나용 마크다운)"""

from anthropic import Anthropic

from ..config import PodcastConfig
from ..prompts import thumbnail_prompts


class ThumbnailPromptAgent:
    """나노바나나용 썸네일 이미지 생성 프롬프트를 작성하는 에이전트"""

    def __init__(self, client: Anthropic, config: PodcastConfig):
        self.client = client
        self.config = config

    def run(
        self,
        column_text: str,
        title: str,
        category: str,
        core_topic: str,
    ) -> str:
        """
        에피소드 정보를 받아 나노바나나용 마크다운 프롬프트를 생성합니다.

        Returns:
            나노바나나용 마크다운 문자열
        """
        # 컬럼이 길면 앞부분만 참고용으로 전달
        column_short = column_text[:1000] if len(column_text) > 1000 else column_text

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=1024,
            system=thumbnail_prompts.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": thumbnail_prompts.USER_PROMPT_TEMPLATE.format(
                        title=title,
                        category=category,
                        core_topic=core_topic,
                        column_text_short=column_short,
                    ),
                }
            ],
        )

        return response.content[0].text
