"""에이전트 시스템 설정"""

from dataclasses import dataclass, field


@dataclass
class PodcastConfig:
    """팟캐스트 생성 설정"""

    # 팟캐스트 기본 정보
    podcast_name: str = "조우성 변호사의 인생내공"
    host_name: str = "조우성"
    host_title: str = "변호사"
    duration_minutes: int = 7

    # 대본 분량 가이드 (7분 기준 약 1,400~1,600자 말하기 분량)
    target_char_count: int = 1500
    char_count_tolerance: int = 200

    # 카테고리별 톤 & 스타일
    category_styles: dict = field(default_factory=lambda: {
        "법률": {
            "tone": "전문적이면서도 친근한",
            "approach": "복잡한 법률 개념을 일상 언어로 풀어서 설명",
            "target_audience": "법률 지식이 필요한 일반인, 기업인",
            "opening_style": "실제 사례나 최근 이슈로 시작",
        },
        "인문학": {
            "tone": "사색적이고 따뜻한",
            "approach": "고전과 현대를 연결하며 삶의 통찰을 전달",
            "target_audience": "삶의 지혜를 찾는 직장인, 리더",
            "opening_style": "인문학적 질문이나 고전 인용으로 시작",
        },
        "자기계발": {
            "tone": "에너지 넘치고 실용적인",
            "approach": "구체적 행동 지침과 마인드셋 변화를 제시",
            "target_audience": "성장을 추구하는 직장인, 리더",
            "opening_style": "공감가는 고민이나 상황 묘사로 시작",
        },
    })

    # Anthropic API 설정
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
