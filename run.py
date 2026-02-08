#!/usr/bin/env python3
"""
조우성 변호사의 인생내공 - 팟캐스트 콘텐츠 생성기

사용법:
    # 파일에서 컬럼 읽기
    python run.py --file column.txt

    # 직접 텍스트 입력 (대화형)
    python run.py

    # 출력 디렉토리 지정
    python run.py --file column.txt --output ./my_output

    # API 키 직접 지정 (기본: ANTHROPIC_API_KEY 환경변수)
    python run.py --file column.txt --api-key sk-ant-...

    # 모의 테스트 모드 (API 키 없이 결과물 형태 미리보기)
    python run.py --file column.txt --mock
"""

import argparse
import sys
import os

from podcast_agents.config import PodcastConfig
from podcast_agents.orchestrator import PodcastOrchestrator


def read_column_from_file(filepath: str) -> str:
    """파일에서 컬럼 텍스트를 읽어옵니다."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def read_column_interactive() -> str:
    """대화형으로 컬럼 텍스트를 입력받습니다."""
    print("=" * 60)
    print("  조우성 변호사의 인생내공 - 팟캐스트 콘텐츠 생성기")
    print("=" * 60)
    print()
    print("컬럼 텍스트를 입력하세요.")
    print("(입력 완료 후 빈 줄에서 Ctrl+D 또는 'END'를 입력하세요)")
    print("-" * 60)

    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
    except EOFError:
        pass

    text = "\n".join(lines).strip()
    if not text:
        print("오류: 컬럼 텍스트가 비어있습니다.")
        sys.exit(1)

    return text


def main():
    parser = argparse.ArgumentParser(
        description="조우성 변호사의 인생내공 - 팟캐스트 콘텐츠 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
예시:
  python run.py --file my_column.txt
  python run.py --file my_column.txt --output ./results
  python run.py  (대화형 입력 모드)

출력물:
  - 7분 팟캐스트 대본 (.txt)
  - 에피소드 제목 + 소개글 (.txt)
  - 나노바나나용 썸네일 프롬프트 (.md)
  - 전체 요약 (.txt)
""",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="컬럼 텍스트 파일 경로",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="결과물 저장 디렉토리 (기본: ./output)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Anthropic API 키 (기본: ANTHROPIC_API_KEY 환경변수)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="사용할 모델 (기본: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="모의 테스트 모드 (API 키 없이 결과물 형태 미리보기)",
    )

    args = parser.parse_args()

    # 컬럼 텍스트 읽기
    if args.file:
        if not os.path.exists(args.file):
            print(f"오류: 파일을 찾을 수 없습니다: {args.file}")
            sys.exit(1)
        column_text = read_column_from_file(args.file)
        print(f"파일 로드 완료: {args.file} ({len(column_text)}자)")
    else:
        column_text = read_column_interactive()

    # 설정
    config = PodcastConfig()
    if args.model:
        config.model = args.model

    # 오케스트레이터 선택 (mock vs real)
    if args.mock:
        from podcast_agents.mock_orchestrator import MockOrchestrator
        orchestrator = MockOrchestrator(config=config)
    else:
        orchestrator = PodcastOrchestrator(api_key=args.api_key, config=config)

    print("\n" + "=" * 60)
    print("  팟캐스트 콘텐츠 생성을 시작합니다")
    print("=" * 60)

    result = orchestrator.run(column_text, output_dir=args.output)

    # 완료 메시지
    print("\n" + "=" * 60)
    print("  생성 완료!")
    print("=" * 60)
    print(f"\n카테고리: {result['classification']['category']}")
    print(f"제목: {result['title_intro']['title']}")
    print(f"대본 분량: {len(result['script'])}자")
    print(f"\n저장 위치: {args.output}/")
    for key, path in result["output_files"].items():
        print(f"  - {path}")
    print()


if __name__ == "__main__":
    main()
