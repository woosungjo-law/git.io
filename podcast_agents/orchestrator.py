"""오케스트레이터 - 에이전트 파이프라인 전체 통합 관리"""

import os
import re
from datetime import datetime

from anthropic import Anthropic

from .config import PodcastConfig
from .agents.classifier import ClassifierAgent
from .agents.script_writer import ScriptWriterAgent
from .agents.title_intro_generator import TitleIntroAgent
from .agents.thumbnail_generator import ThumbnailPromptAgent


class PodcastOrchestrator:
    """
    팟캐스트 콘텐츠 생성 파이프라인을 통합 관리합니다.

    흐름:
    1. 컬럼 → 분류 에이전트 → 카테고리 판별
    2. 컬럼 + 카테고리 → 대본 에이전트 → 7분 대본
    3. 컬럼 + 대본 + 카테고리 → 제목/소개 에이전트 → 제목 + 소개글
    4. 에피소드 정보 → 썸네일 에이전트 → 나노바나나 마크다운 프롬프트
    """

    def __init__(self, api_key: str | None = None, config: PodcastConfig | None = None):
        self.config = config or PodcastConfig()
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()

        # 에이전트 초기화
        self.classifier = ClassifierAgent(self.client, self.config)
        self.script_writer = ScriptWriterAgent(self.client, self.config)
        self.title_intro = TitleIntroAgent(self.client, self.config)
        self.thumbnail = ThumbnailPromptAgent(self.client, self.config)

    def run(self, column_text: str, output_dir: str = "output") -> dict:
        """
        전체 파이프라인을 실행합니다.

        Args:
            column_text: 원본 컬럼 텍스트
            output_dir: 결과물 저장 디렉토리

        Returns:
            {
                "classification": {...},
                "script": "대본 텍스트",
                "title_intro": {...},
                "thumbnail_prompt": "마크다운 문자열",
                "output_files": {...}
            }
        """
        result = {}

        # === Step 1: 컬럼 분류 ===
        print("\n[1/4] 컬럼 분류 중...")
        classification = self.classifier.run(column_text)
        result["classification"] = classification
        print(f"  → 카테고리: {classification['category']}")
        print(f"  → 핵심주제: {classification['core_topic']}")

        category = classification["category"]
        core_topic = classification["core_topic"]

        # === Step 2: 팟캐스트 대본 생성 ===
        print("\n[2/4] 7분 팟캐스트 대본 생성 중...")
        script = self.script_writer.run(column_text, category, core_topic)
        result["script"] = script
        char_count = len(script)
        print(f"  → 대본 생성 완료 ({char_count}자)")

        # === Step 3: 제목 + 소개글 생성 ===
        print("\n[3/4] 제목 및 소개글 생성 중...")
        title_intro = self.title_intro.run(
            column_text, script, category, core_topic
        )
        result["title_intro"] = title_intro
        print(f"  → 제목: {title_intro['title']}")

        # === Step 4: 썸네일 프롬프트 생성 ===
        print("\n[4/4] 썸네일 프롬프트 생성 중...")
        thumbnail_prompt = self.thumbnail.run(
            column_text,
            title_intro["title"],
            category,
            core_topic,
        )
        result["thumbnail_prompt"] = thumbnail_prompt
        print("  → 썸네일 프롬프트 생성 완료")

        # === 결과물 저장 ===
        print("\n파일 저장 중...")
        output_files = self._save_outputs(result, output_dir)
        result["output_files"] = output_files

        return result

    def _save_outputs(self, result: dict, output_dir: str) -> dict:
        """결과물을 파일로 저장합니다."""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 제목에서 파일명으로 사용 가능한 문자만 추출
        title_slug = re.sub(r'[^\w가-힣]', '_', result["title_intro"]["title"])[:30]
        prefix = f"{timestamp}_{title_slug}"

        files = {}

        # 1. 대본 저장
        script_path = os.path.join(output_dir, f"{prefix}_대본.txt")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(f"# 조우성 변호사의 인생내공\n")
            f.write(f"# 에피소드: {result['title_intro']['title']}\n")
            f.write(f"# 카테고리: {result['classification']['category']}\n")
            f.write(f"# 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(result["script"])
        files["script"] = script_path
        print(f"  → 대본: {script_path}")

        # 2. 제목 + 소개글 저장
        intro_path = os.path.join(output_dir, f"{prefix}_소개글.txt")
        with open(intro_path, "w", encoding="utf-8") as f:
            f.write(f"[제목]\n{result['title_intro']['title']}\n\n")
            f.write(f"[소개글]\n{result['title_intro']['intro']}\n\n")
            f.write(f"[해시태그]\n{result['title_intro']['hashtags']}\n")
        files["intro"] = intro_path
        print(f"  → 소개글: {intro_path}")

        # 3. 썸네일 프롬프트 저장 (마크다운)
        thumb_path = os.path.join(output_dir, f"{prefix}_썸네일.md")
        with open(thumb_path, "w", encoding="utf-8") as f:
            f.write(result["thumbnail_prompt"])
        files["thumbnail"] = thumb_path
        print(f"  → 썸네일: {thumb_path}")

        # 4. 전체 결과 요약 저장
        summary_path = os.path.join(output_dir, f"{prefix}_요약.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("  조우성 변호사의 인생내공 - 에피소드 생성 결과\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"[분류]\n")
            f.write(f"  카테고리: {result['classification']['category']}\n")
            f.write(f"  핵심주제: {result['classification']['core_topic']}\n")
            f.write(f"  분류근거: {result['classification']['reasoning']}\n\n")
            f.write(f"[제목] {result['title_intro']['title']}\n\n")
            f.write(f"[소개글]\n{result['title_intro']['intro']}\n\n")
            f.write(f"[해시태그]\n{result['title_intro']['hashtags']}\n\n")
            f.write(f"[대본 분량] {len(result['script'])}자\n\n")
            f.write(f"[생성 파일]\n")
            for key, path in files.items():
                f.write(f"  - {key}: {path}\n")
        files["summary"] = summary_path
        print(f"  → 요약: {summary_path}")

        return files
