"""제목 + 소개글 생성 에이전트"""

from anthropic import Anthropic

from ..config import PodcastConfig
from ..prompts import title_intro_prompts


class TitleIntroAgent:
    """팟캐스트 에피소드의 제목과 소개글을 생성하는 에이전트"""

    def __init__(self, client: Anthropic, config: PodcastConfig):
        self.client = client
        self.config = config

    def run(
        self,
        column_text: str,
        script: str,
        category: str,
        core_topic: str,
    ) -> dict:
        """
        컬럼, 대본, 분류 정보를 받아 제목과 소개글을 생성합니다.

        Returns:
            {
                "title": "에피소드 제목",
                "intro": "소개글 본문",
                "hashtags": "해시태그 문자열"
            }
        """
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=1024,
            system=title_intro_prompts.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": title_intro_prompts.USER_PROMPT_TEMPLATE.format(
                        category=category,
                        core_topic=core_topic,
                        column_text=column_text,
                        script=script,
                    ),
                }
            ],
        )

        return self._parse_response(response.content[0].text)

    def _parse_response(self, text: str) -> dict:
        """응답을 파싱하여 제목, 소개글, 해시태그로 분리합니다."""
        result = {"title": "", "intro": "", "hashtags": "", "raw": text}

        sections = {"제목": "title", "소개글": "intro", "해시태그": "hashtags"}
        current_key = None
        current_lines = []

        for line in text.strip().split("\n"):
            stripped = line.strip()

            # 섹션 헤더 감지
            found_section = False
            for header, key in sections.items():
                if stripped.startswith(f"[{header}]"):
                    if current_key:
                        result[current_key] = "\n".join(current_lines).strip()
                    current_key = key
                    current_lines = []
                    found_section = True
                    break

            if not found_section and current_key:
                current_lines.append(line)

        # 마지막 섹션 저장
        if current_key:
            result[current_key] = "\n".join(current_lines).strip()

        return result
