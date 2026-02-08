"""모의(Mock) 오케스트레이터 - API 키 없이 파이프라인 결과물 미리보기"""

import os
import re
from datetime import datetime

from .config import PodcastConfig


class MockOrchestrator:
    """
    API 호출 없이 실제와 동일한 형태의 결과물을 생성합니다.
    컬럼 텍스트를 분석하여 키워드 기반으로 카테고리를 추정하고,
    해당 카테고리에 맞는 샘플 콘텐츠를 생성합니다.
    """

    # 카테고리 추정용 키워드
    CATEGORY_KEYWORDS = {
        "법률": [
            "계약", "소송", "판례", "법원", "변호사", "민법", "상법", "형법",
            "분쟁", "배상", "조항", "법률", "규정", "위반", "법적", "관할",
            "채권", "채무", "소멸시효", "손해배상", "중재",
        ],
        "인문학": [
            "철학", "역사", "고전", "사상", "문학", "예술", "소크라테스",
            "공자", "쇼펜하우어", "니체", "한비자", "인문", "지혜", "사색",
            "통찰", "의미", "존재", "논쟁", "소통", "품격", "배려", "우아",
            "그릇", "덕목", "예의", "관대", "실수",
        ],
        "자기계발": [
            "습관", "목표", "성장", "리더십", "시간관리", "생산성", "마인드셋",
            "실행력", "커리어", "동기부여", "완벽주의", "도전", "결단",
            "루틴", "멘탈", "회복", "성공", "실패",
        ],
    }

    def __init__(self, config: PodcastConfig | None = None):
        self.config = config or PodcastConfig()

    def run(self, column_text: str, output_dir: str = "output") -> dict:
        """모의 파이프라인을 실행합니다."""
        result = {}

        # === Step 1: 키워드 기반 카테고리 추정 ===
        print("\n[1/4] 컬럼 분류 중... (MOCK)")
        classification = self._classify(column_text)
        result["classification"] = classification
        print(f"  → 카테고리: {classification['category']}")
        print(f"  → 핵심주제: {classification['core_topic']}")

        category = classification["category"]
        core_topic = classification["core_topic"]

        # === Step 2: 모의 대본 생성 ===
        print("\n[2/4] 7분 팟캐스트 대본 생성 중... (MOCK)")
        script = self._generate_script(column_text, category, core_topic)
        result["script"] = script
        print(f"  → 대본 생성 완료 ({len(script)}자)")

        # === Step 3: 모의 제목 + 소개글 생성 ===
        print("\n[3/4] 제목 및 소개글 생성 중... (MOCK)")
        title_intro = self._generate_title_intro(column_text, category, core_topic)
        result["title_intro"] = title_intro
        print(f"  → 제목: {title_intro['title']}")

        # === Step 4: 모의 썸네일 프롬프트 생성 ===
        print("\n[4/4] 썸네일 프롬프트 생성 중... (MOCK)")
        thumbnail_prompt = self._generate_thumbnail(title_intro["title"], category, core_topic)
        result["thumbnail_prompt"] = thumbnail_prompt
        print("  → 썸네일 프롬프트 생성 완료")

        # === 결과물 저장 ===
        print("\n파일 저장 중...")
        output_files = self._save_outputs(result, output_dir)
        result["output_files"] = output_files

        return result

    def _classify(self, column_text: str) -> dict:
        """키워드 매칭으로 카테고리를 추정합니다."""
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in column_text)
            scores[category] = score

        best = max(scores, key=scores.get)

        # 핵심주제 추출: 첫 줄이나 제목에서 가져옴
        lines = column_text.strip().split("\n")
        first_line = lines[0].strip().strip("[]").strip()
        # [칼럼] 같은 접두사 제거
        core_topic = re.sub(r'^\[.*?\]\s*', '', first_line)
        if not core_topic:
            core_topic = lines[1].strip() if len(lines) > 1 else "주제 미상"

        return {
            "category": best,
            "core_topic": core_topic,
            "reasoning": f"키워드 매칭 결과 - 법률:{scores['법률']}점, "
                         f"인문학:{scores['인문학']}점, 자기계발:{scores['자기계발']}점 "
                         f"→ '{best}' 카테고리로 분류 (MOCK 모드)",
        }

    def _generate_script(self, column_text: str, category: str, core_topic: str) -> str:
        """컬럼 내용을 기반으로 모의 대본을 생성합니다."""
        # 컬럼에서 핵심 문장들 추출
        sentences = []
        for line in column_text.split("\n"):
            line = line.strip()
            if len(line) > 20:
                sentences.append(line)

        # 주요 인용구 추출 (따옴표 안의 내용)
        quotes = re.findall(r'["\u201c\u201d]([^"\u201c\u201d]+)["\u201c\u201d]', column_text)

        style = self.config.category_styles.get(category, self.config.category_styles["자기계발"])

        script = f"""[오프닝] (약 40초)

안녕하세요, 조우성 변호사입니다. 인생내공, 오늘도 함께해주셔서 감사합니다.

오늘은요, 좀 특별한 이야기를 해보려고 합니다. 바로 '{core_topic}'에 대한 이야기인데요.

여러분, 혹시 누군가의 실수를 목격했을 때, 어떻게 반응하시나요? [잠시 멈춤]

{sentences[0] if sentences else ''}

---

[본론 1] (약 2분) - 실수 앞에서의 태도

{sentences[1] if len(sentences) > 1 else ''}

{sentences[2] if len(sentences) > 2 else ''}

이게 참 중요한 포인트인데요. [강조] 단순한 인내심이 아니라, 고도로 훈련된 상상력의 결과라는 거예요.

{f'제가 좋아하는 표현이 있는데요. "{quotes[0]}" 이 말, 곱씹어볼 만하지 않나요?' if quotes else ''}

---

[본론 2] (약 2분) - 왜 우리는 지적하고 싶어할까

여러분도 한번 생각해보세요. 우리는 왜 남의 실수를 발견하면 꼭 지적하고 싶어질까요?

{sentences[3] if len(sentences) > 3 else ''}

{sentences[4] if len(sentences) > 4 else ''}

저도 17년 넘게 변호사 생활을 하면서 수많은 사람들을 만나봤는데요, 정말 큰 일을 하는 분들의 공통점이 있어요. 사소한 것에 집착하지 않는다는 겁니다.

---

[본론 3] (약 1분) - 눈을 감을 줄 아는 사람

{sentences[5] if len(sentences) > 5 else ''}

결국 사람을 남기고 큰일을 도모하는 이들은, '눈이 나쁜' 사람들이 아니라 '눈을 감을 줄 아는' 사람들이었습니다. [강조]

---

[핵심 메시지] (약 50초)

오늘 꼭 기억하실 것 하나만 말씀드릴게요. [잠시 멈춤]

{sentences[-2] if len(sentences) >= 2 else ''}

[강조] 그릇이 큰 사람은 무엇을 담느냐보다, 무엇을 흘려보내느냐로 결정됩니다.

이번 한 주, 누군가의 실수를 발견했을 때, 한 번만 '모르는 척' 해보시는 건 어떨까요? 그 작은 침묵이 상대에게는 가장 큰 선물이 될 수 있습니다.

---

[클로징] (약 30초)

오늘도 인생내공과 함께해주셔서 감사합니다.
세상에는 '아는 척'보다 '모르는 척'이 더 큰 용기가 필요한 순간이 있습니다.
여러분의 그 우아한 침묵을 응원합니다.

인생내공, 조우성 변호사였습니다. 다음에 또 만나요.
"""
        return script

    def _generate_title_intro(self, column_text: str, category: str, core_topic: str) -> dict:
        """모의 제목과 소개글을 생성합니다."""
        # 핵심 키워드에서 제목 생성
        title = "'모르는 척'이라는 용기"

        # 컬럼 내용 기반으로 좀 더 맞춤화
        if "배려" in column_text:
            title = "모르는 척, 가장 우아한 배려"
        elif "리더" in column_text:
            title = "리더의 가장 큰 덕목"
        elif "실수" in column_text and "품격" in column_text:
            title = "실수 앞에서 드러나는 품격"

        intro = (
            f"누군가의 실수를 목격하는 순간, 당신은 어떻게 반응하시나요? "
            f"어느 증권사 CEO의 놀라운 일화를 통해, "
            f"'지적하는 똑똑함'보다 '모르는 척하는 품격'이 "
            f"왜 더 큰 힘을 가지는지 이야기합니다. "
            f"이 에피소드에서는 타인의 실수 앞에서 진정한 강자가 보여주는 태도, "
            f"그리고 '눈을 감을 줄 아는' 리더의 덕목에 대해 나눕니다."
        )

        hashtags = "#인생내공 #조우성변호사 #모르는척 #배려 #리더십 #품격"

        return {
            "title": title,
            "intro": intro,
            "hashtags": hashtags,
            "raw": "",
        }

    def _generate_thumbnail(self, title: str, category: str, core_topic: str) -> str:
        """모의 썸네일 프롬프트를 생성합니다."""
        color_map = {
            "법률": ("네이비(#1B2A4A)", "골드(#C9A96E)", "화이트(#FFFFFF)"),
            "인문학": ("버건디(#722F37)", "웜베이지(#F5E6D3)", "크림(#FFF8F0)"),
            "자기계발": ("딥블루(#1A3A5C)", "오렌지(#E8732A)", "화이트(#FFFFFF)"),
        }
        main_c, sub_c, text_c = color_map.get(category, color_map["인문학"])

        return f"""# 썸네일 이미지 생성 프롬프트

## 기본 설정
- 크기: 1280x720 (16:9)
- 스타일: 미니멀하고 고급스러운 한국형 팟캐스트 커버

## 이미지 설명
따뜻한 조명의 고급 레스토랑 테이블 위, 커피 한 잔이 살짝 기울어져 있다.
커피가 흰 식탁보 위로 조금 흘렀지만, 테이블 맞은편의 손은
차분하게 냅킨을 건네고 있다. 전체적으로 따뜻하고 부드러운 톤.
배경은 약간 블러 처리되어 있고, 중앙에 텍스트 공간이 확보되어 있다.

## 텍스트 오버레이
- 메인 텍스트: "모르는 척"
- 서브 텍스트: 조우성 변호사의 인생내공
- 폰트 스타일: 메인은 굵은 세리프체(Noto Serif KR Bold), 서브는 가벼운 산세리프(Pretendard Light)

## 색상 팔레트
- 메인 컬러: {main_c}
- 서브 컬러: {sub_c}
- 텍스트 컬러: {text_c}
- 강조 컬러: 소프트 골드(#D4AF37)

## 분위기/무드
고요하고 품격 있는 분위기. 실수를 감싸주는 따뜻함과
진정한 강자의 여유가 느껴지는 이미지.
'우아한 침묵'과 '배려의 힘'을 시각적으로 전달.
"""

    def _save_outputs(self, result: dict, output_dir: str) -> dict:
        """결과물을 파일로 저장합니다. (PodcastOrchestrator와 동일)"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
            f.write(f"# 모드: MOCK (모의 테스트)\n")
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
            f.write("  조우성 변호사의 인생내공 - 에피소드 생성 결과 (MOCK)\n")
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
