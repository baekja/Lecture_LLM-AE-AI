"""
강의 노트 생성 프롬프트 채점 시스템

학생이 작성한 프롬프트를 기반으로 Claude가 생성한 강의 노트를 평가한다.
채점 방식: 코드 기반 정량 평가(40%) + LLM 심사위원 정성 평가(60%)

사용법:
    python grading_system.py --prompt "프롬프트 텍스트"
    python grading_system.py --prompt-file student_prompt.txt
    python grading_system.py --note-file generated_note.md
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# 상수 정의
# ---------------------------------------------------------------------------

MODEL: str = "claude-sonnet-4-0"

# 코드 채점 가중치 (총 40%)
CODE_WEIGHTS: dict[str, float] = {
    "structure": 10.0,    # 구조 완성도
    "format": 8.0,        # 포맷 준수
    "examples": 8.0,      # 예제 포함
    "code_quality": 7.0,  # 코드 품질
    "volume": 7.0,        # 분량 적정성
}

# LLM 심사 가중치 (총 60%)
LLM_WEIGHT: float = 60.0

# 학점 기준표
LETTER_GRADE_THRESHOLDS: list[tuple[float, str]] = [
    (90.0, "A"),
    (80.0, "B"),
    (70.0, "C"),
    (60.0, "D"),
    (0.0, "F"),
]

# 노트 생성 시스템 프롬프트
NOTE_GENERATION_SYSTEM_PROMPT: str = """당신은 경희대학교 건축공학과 'LLM활용 건축공학 AI구현' 과목의
강의 노트 작성 전문가입니다. 학생이 제공하는 프롬프트에 따라 고품질 강의 노트를 생성하세요.

강의 노트는 Obsidian 마크다운 형식으로 작성하며, 다음 요소를 적절히 활용하세요:
- H1/H2/H3 계층 구조
- 코드 블록 (Python 예제)
- 테이블, Mermaid 다이어그램
- Obsidian 콜아웃 ([!finding], [!tip], [!question] 등)
- 3단계 예제 (Skilljar/범용/구조공학)
- 한국어 본문 + 영어 기술 용어 병기
"""

# LLM 심사위원 시스템 프롬프트
LLM_JUDGE_SYSTEM_PROMPT: str = """당신은 대학 강의 노트 품질 심사위원입니다.
'LLM활용 건축공학 AI구현' 과목의 강의 노트를 평가합니다.

다음 5점 척도로 평가하세요:

| 점수 | 기준 |
|------|------|
| 1 | 주제와 무관한 내용이거나 심각한 오류 포함 |
| 2 | 일부 관련 내용 있으나 핵심 기법/예제 누락 |
| 3 | 대체로 정확하나 예제가 빈약하거나 흐름이 부자연스러움 |
| 4 | 정확하고 체계적, 3단계 예제 포함, 사소한 개선 여지 있음 |
| 5 | 완벽한 구조, 풍부한 예제, Mermaid+콜아웃 적절 활용, 교육적 흐름 탁월 |

다음 네 가지 측면을 반드시 평가하세요:
1. 프롬프트 엔지니어링/평가 내용의 기술적 정확성
2. 교육적 흐름 (평가 → 기법 → 심화 → 종합)
3. 3단계 예제의 품질과 관련성
4. 한국어 + 영어 기술 용어 사용의 적절성

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{
    "score": <1-5 정수>,
    "technical_accuracy": "<기술적 정확성 평가>",
    "pedagogical_flow": "<교육적 흐름 평가>",
    "example_quality": "<예제 품질 평가>",
    "terminology": "<용어 사용 평가>",
    "overall_feedback": "<종합 피드백>"
}
"""


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class CodeGradingResult:
    """코드 기반 채점 결과를 담는 데이터 클래스."""

    structure: float = 0.0       # 구조 완성도 (0-100)
    format: float = 0.0          # 포맷 준수 (0-100)
    examples: float = 0.0        # 예제 포함 (0-100)
    code_quality: float = 0.0    # 코드 품질 (0-100)
    volume: float = 0.0          # 분량 적정성 (0-100)
    details: dict[str, str] = field(default_factory=dict)

    def weighted_score(self) -> float:
        """가중 점수 합산 (40점 만점 기준)."""
        total = 0.0
        for dim, weight in CODE_WEIGHTS.items():
            raw = getattr(self, dim)
            total += (raw / 100.0) * weight
        return total


@dataclass
class LLMJudgeResult:
    """LLM 심사위원 평가 결과를 담는 데이터 클래스."""

    score: int = 1                           # 1-5 척도
    technical_accuracy: str = ""             # 기술적 정확성 피드백
    pedagogical_flow: str = ""               # 교육적 흐름 피드백
    example_quality: str = ""                # 예제 품질 피드백
    terminology: str = ""                    # 용어 사용 피드백
    overall_feedback: str = ""               # 종합 피드백

    def weighted_score(self) -> float:
        """5점 척도를 60점 만점 기준으로 환산."""
        return (self.score / 5.0) * LLM_WEIGHT


@dataclass
class GradingReport:
    """최종 채점 보고서."""

    note_preview: str = ""
    code_result: CodeGradingResult = field(default_factory=CodeGradingResult)
    llm_result: LLMJudgeResult = field(default_factory=LLMJudgeResult)

    @property
    def combined_score(self) -> float:
        """코드 채점 + LLM 심사 합산 점수 (100점 만점)."""
        return self.code_result.weighted_score() + self.llm_result.weighted_score()

    @property
    def letter_grade(self) -> str:
        """점수에 따른 학점 반환."""
        score = self.combined_score
        for threshold, grade in LETTER_GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"


# ---------------------------------------------------------------------------
# 메인 채점 클래스
# ---------------------------------------------------------------------------

class LectureNoteGrader:
    """강의 노트 프롬프트 채점 시스템.

    학생이 작성한 프롬프트로 강의 노트를 생성하고,
    코드 기반(40%) + LLM 심사(60%) 하이브리드 방식으로 채점한다.
    """

    def __init__(self) -> None:
        """Anthropic 클라이언트를 초기화한다."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("[오류] ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
            print("       .env 파일에 ANTHROPIC_API_KEY=sk-... 형태로 추가하세요.")
            sys.exit(1)
        self.client = anthropic.Anthropic(api_key=api_key)

    # ----- 노트 생성 -----

    def generate_note(self, prompt: str) -> str:
        """학생 프롬프트를 기반으로 Claude에게 강의 노트를 생성시킨다.

        Args:
            prompt: 학생이 작성한 프롬프트 텍스트.

        Returns:
            생성된 강의 노트 마크다운 텍스트.
        """
        print("[1/3] 강의 노트 생성 중...")
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=NOTE_GENERATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        note = response.content[0].text
        print(f"      생성 완료 ({len(note.splitlines())}줄, {len(note)}자)")
        return note

    # ----- 코드 기반 채점 (40%) -----

    def _check_structure(self, note: str) -> tuple[float, str]:
        """구조 완성도를 검사한다 (H1/H2/H3 헤더, 코드 블록, 테이블).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            (0-100 점수, 세부 설명) 튜플.
        """
        checks: dict[str, bool] = {
            "H1 헤더 존재": bool(re.search(r"^# .+", note, re.MULTILINE)),
            "H2 헤더 존재": bool(re.search(r"^## .+", note, re.MULTILINE)),
            "H3 헤더 존재": bool(re.search(r"^### .+", note, re.MULTILINE)),
            "코드 블록 존재": bool(re.search(r"```[\s\S]+?```", note)),
            "테이블 존재": bool(re.search(r"\|.+\|.+\|", note)),
        }
        passed = sum(checks.values())
        score = (passed / len(checks)) * 100.0
        detail_parts = [f"  {'[O]' if v else '[X]'} {k}" for k, v in checks.items()]
        detail = "\n".join(detail_parts)
        return score, detail

    def _check_format(self, note: str) -> tuple[float, str]:
        """포맷 준수 여부를 검사한다 (콜아웃, Mermaid, 이미지 참조).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            (0-100 점수, 세부 설명) 튜플.
        """
        checks: dict[str, bool] = {
            "콜아웃 사용": bool(re.search(r">\s*\[!(finding|tip|question|warning|note|info|example|ref|method|result|hypothesis|action|deadline|gdrive)\]", note, re.IGNORECASE)),
            "Mermaid 다이어그램": bool(re.search(r"```mermaid", note, re.IGNORECASE)),
            "이미지 참조": bool(re.search(r"!\[.*?\]\(.*?\)", note)),
        }
        passed = sum(checks.values())
        score = (passed / len(checks)) * 100.0
        detail_parts = [f"  {'[O]' if v else '[X]'} {k}" for k, v in checks.items()]
        detail = "\n".join(detail_parts)
        return score, detail

    def _check_examples(self, note: str) -> tuple[float, str]:
        """3단계 예제 포함 여부를 검사한다 (Skilljar/범용/구조공학).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            (0-100 점수, 세부 설명) 튜플.
        """
        note_lower = note.lower()
        checks: dict[str, bool] = {
            "Skilljar 예제": any(
                kw in note_lower
                for kw in ["skilljar", "스킬자", "플랫폼 예제", "lms"]
            ),
            "범용 예제": any(
                kw in note_lower
                for kw in ["범용", "일반", "universal", "general", "공통 예제"]
            ),
            "구조공학 예제": any(
                kw in note_lower
                for kw in [
                    "구조공학", "structural", "건축구조",
                    "콘크리트", "철근", "벽체", "coupling beam",
                    "내진", "전단벽", "보-기둥",
                ]
            ),
        }
        passed = sum(checks.values())
        score = (passed / len(checks)) * 100.0
        detail_parts = [f"  {'[O]' if v else '[X]'} {k}" for k, v in checks.items()]
        detail = "\n".join(detail_parts)
        return score, detail

    def _check_code_quality(self, note: str) -> tuple[float, str]:
        """코드 블록의 품질을 검사한다 (Python 블록, 한국어 주석, 타입 힌트).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            (0-100 점수, 세부 설명) 튜플.
        """
        # Python 코드 블록 추출
        python_blocks = re.findall(
            r"```python\s*([\s\S]*?)```", note, re.IGNORECASE
        )
        all_code = "\n".join(python_blocks)

        checks: dict[str, bool] = {
            "Python 코드 블록 존재": len(python_blocks) > 0,
            "한국어 주석 포함": bool(re.search(r"#\s*[가-힣]", all_code)),
            "타입 힌트 사용": bool(
                re.search(r"(:\s*(str|int|float|bool|list|dict|Optional|Any|tuple))|(\s*->\s*)", all_code)
            ),
        }
        passed = sum(checks.values())
        score = (passed / len(checks)) * 100.0
        detail_parts = [
            f"  {'[O]' if v else '[X]'} {k}" for k, v in checks.items()
        ]
        detail_parts.append(f"  Python 코드 블록 수: {len(python_blocks)}개")
        detail = "\n".join(detail_parts)
        return score, detail

    def _check_volume(self, note: str) -> tuple[float, str]:
        """분량 적정성을 검사한다 (최소 500줄 기준).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            (0-100 점수, 세부 설명) 튜플.
        """
        line_count = len(note.splitlines())
        min_lines = 500

        if line_count >= min_lines:
            score = 100.0
        else:
            # 비례 점수 (최소 0점)
            score = (line_count / min_lines) * 100.0

        detail = f"  총 {line_count}줄 (기준: {min_lines}줄 이상)"
        return score, detail

    def grade_code(self, note: str) -> CodeGradingResult:
        """코드 기반 정량 채점을 수행한다 (40% 배점).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            CodeGradingResult 객체.
        """
        print("[2/3] 코드 기반 채점 중...")
        result = CodeGradingResult()

        result.structure, result.details["structure"] = self._check_structure(note)
        result.format, result.details["format"] = self._check_format(note)
        result.examples, result.details["examples"] = self._check_examples(note)
        result.code_quality, result.details["code_quality"] = self._check_code_quality(note)
        result.volume, result.details["volume"] = self._check_volume(note)

        print(f"      코드 채점 완료 (가중합: {result.weighted_score():.1f}/40)")
        return result

    # ----- LLM 심사위원 평가 (60%) -----

    def grade_llm(self, note: str) -> LLMJudgeResult:
        """LLM 심사위원이 강의 노트를 정성 평가한다 (60% 배점).

        Args:
            note: 강의 노트 텍스트.

        Returns:
            LLMJudgeResult 객체.
        """
        print("[3/3] LLM 심사위원 평가 중...")
        user_message = f"""아래 강의 노트를 평가해주세요.

---
{note}
---

위 강의 노트를 5점 척도로 평가하고, 지정된 JSON 형식으로 응답하세요."""

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=LLM_JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text = response.content[0].text.strip()

        # JSON 파싱 (코드 블록 감싸기 대응)
        json_text = raw_text
        if "```" in json_text:
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", json_text)
            if json_match:
                json_text = json_match.group(1).strip()

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            print("      [경고] LLM 응답 JSON 파싱 실패. 기본값(3점) 적용.")
            data = {
                "score": 3,
                "technical_accuracy": "파싱 실패로 평가 불가",
                "pedagogical_flow": "파싱 실패로 평가 불가",
                "example_quality": "파싱 실패로 평가 불가",
                "terminology": "파싱 실패로 평가 불가",
                "overall_feedback": f"원본 응답: {raw_text[:300]}",
            }

        result = LLMJudgeResult(
            score=max(1, min(5, int(data.get("score", 3)))),
            technical_accuracy=str(data.get("technical_accuracy", "")),
            pedagogical_flow=str(data.get("pedagogical_flow", "")),
            example_quality=str(data.get("example_quality", "")),
            terminology=str(data.get("terminology", "")),
            overall_feedback=str(data.get("overall_feedback", "")),
        )

        print(f"      LLM 평가 완료 (점수: {result.score}/5, 환산: {result.weighted_score():.1f}/60)")
        return result

    # ----- 통합 채점 -----

    def grade(self, prompt: Optional[str] = None, note: Optional[str] = None) -> GradingReport:
        """프롬프트 또는 노트를 받아 전체 채점을 수행한다.

        Args:
            prompt: 학생 프롬프트 (노트 생성 필요 시).
            note: 이미 생성된 강의 노트 (직접 채점 시).

        Returns:
            GradingReport 객체.
        """
        if note is None:
            if prompt is None:
                print("[오류] 프롬프트 또는 노트 중 하나는 반드시 제공해야 합니다.")
                sys.exit(1)
            note = self.generate_note(prompt)
        else:
            print("[1/3] 기존 노트 파일 사용 (생성 단계 건너뜀)")

        report = GradingReport()
        report.note_preview = note[:500]
        report.code_result = self.grade_code(note)
        report.llm_result = self.grade_llm(note)

        return report


# ---------------------------------------------------------------------------
# 결과 출력
# ---------------------------------------------------------------------------

def print_report(report: GradingReport) -> None:
    """채점 보고서를 구조화된 형식으로 출력한다.

    Args:
        report: 채점 결과를 담은 GradingReport 객체.
    """
    separator = "=" * 70

    print(f"\n{separator}")
    print("  강의 노트 프롬프트 채점 결과")
    print(separator)

    # 노트 미리보기
    print("\n[생성된 노트 미리보기]")
    print("-" * 50)
    print(report.note_preview)
    if len(report.note_preview) >= 500:
        print("... (이하 생략)")
    print("-" * 50)

    # 코드 기반 채점 결과
    print(f"\n[코드 기반 채점] (40% 배점)")
    print("-" * 50)

    dimension_names: dict[str, str] = {
        "structure": "구조 완성도",
        "format": "포맷 준수",
        "examples": "예제 포함",
        "code_quality": "코드 품질",
        "volume": "분량 적정성",
    }

    code_result = report.code_result
    for dim_key, dim_name in dimension_names.items():
        raw_score = getattr(code_result, dim_key)
        weight = CODE_WEIGHTS[dim_key]
        weighted = (raw_score / 100.0) * weight
        print(f"\n  {dim_name} (배점 {weight:.0f}%)")
        print(f"    원점수: {raw_score:.0f}/100  |  가중점수: {weighted:.1f}/{weight:.0f}")
        if dim_key in code_result.details:
            for line in code_result.details[dim_key].split("\n"):
                print(f"    {line.strip()}")

    print(f"\n  코드 채점 소계: {code_result.weighted_score():.1f} / 40.0")

    # LLM 심사위원 결과
    llm_result = report.llm_result
    print(f"\n[LLM 심사위원 평가] (60% 배점)")
    print("-" * 50)
    print(f"  5점 척도 점수: {llm_result.score}/5")
    print(f"  환산 점수:     {llm_result.weighted_score():.1f}/60.0")
    print(f"\n  기술적 정확성: {llm_result.technical_accuracy}")
    print(f"  교육적 흐름:   {llm_result.pedagogical_flow}")
    print(f"  예제 품질:     {llm_result.example_quality}")
    print(f"  용어 사용:     {llm_result.terminology}")
    print(f"  종합 피드백:   {llm_result.overall_feedback}")

    # 최종 점수
    print(f"\n{separator}")
    print(f"  최종 점수:  {report.combined_score:.1f} / 100")
    print(f"  학점:       {report.letter_grade}")
    print(separator)


# ---------------------------------------------------------------------------
# CLI 엔트리포인트
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """커맨드라인 인자를 파싱한다.

    Returns:
        파싱된 인자 Namespace 객체.
    """
    parser = argparse.ArgumentParser(
        description="강의 노트 생성 프롬프트 채점 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
사용 예시:
  python grading_system.py --prompt "3주차 프롬프트 평가 강의 노트를 작성해주세요."
  python grading_system.py --prompt-file student_prompt.txt
  python grading_system.py --note-file generated_note.md
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--prompt",
        type=str,
        help="학생의 프롬프트 텍스트 (직접 입력)",
    )
    group.add_argument(
        "--prompt-file",
        type=str,
        help="학생의 프롬프트가 담긴 텍스트 파일 경로",
    )
    group.add_argument(
        "--note-file",
        type=str,
        help="이미 생성된 강의 노트 파일 경로 (생성 단계 건너뛰고 바로 채점)",
    )

    return parser.parse_args()


def main() -> None:
    """메인 실행 함수."""
    args = parse_args()

    grader = LectureNoteGrader()

    if args.prompt:
        # 프롬프트 텍스트 직접 전달
        report = grader.grade(prompt=args.prompt)

    elif args.prompt_file:
        # 프롬프트 파일에서 읽기
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            print(f"[오류] 프롬프트 파일을 찾을 수 없습니다: {prompt_path}")
            sys.exit(1)
        prompt_text = prompt_path.read_text(encoding="utf-8")
        print(f"프롬프트 파일 로드 완료: {prompt_path} ({len(prompt_text)}자)")
        report = grader.grade(prompt=prompt_text)

    elif args.note_file:
        # 기존 노트 파일 직접 채점
        note_path = Path(args.note_file)
        if not note_path.exists():
            print(f"[오류] 노트 파일을 찾을 수 없습니다: {note_path}")
            sys.exit(1)
        note_text = note_path.read_text(encoding="utf-8")
        print(f"노트 파일 로드 완료: {note_path} ({len(note_text)}자, {len(note_text.splitlines())}줄)")
        report = grader.grade(note=note_text)

    print_report(report)


if __name__ == "__main__":
    main()
