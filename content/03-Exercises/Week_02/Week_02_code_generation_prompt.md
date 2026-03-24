# Week 02 실습 코드 생성 — Claude Code 프롬프트

> 이 프롬프트를 Claude Code에서 실행하면 Week_02 강의노트(01-Notes/Week_02.md)에 사용된 모든 Python 코드와 한국어 주석이 포함된 실습 파일 6개가 생성됩니다.

---

## 프롬프트

```
"LLM활용건축공학AI구현" 강의 2주차 실습 코드를 생성해줘.
Anthropic Skilljar "Building with the Claude API — Section 1: Getting Started" 기반이고,
건축구조공학(RC 부재 설계, KDS 기준) 도메인에 맞춰 작성해야 해.

모든 코드는 Python이고, 주석은 한국어로 작성해줘.
모델은 "claude-sonnet-4-0"을 사용해.

아래 6개 파일을 각각 별도의 .py 파일로 생성해줘:

---

### 파일 1: 001_first_request.py
- dotenv로 .env에서 ANTHROPIC_API_KEY 로드
- Anthropic 클라이언트 생성 (환경변수 자동 인식 방식)
- client.messages.create()로 첫 API 호출 (model, max_tokens, messages 3개 필수 파라미터)
- 응답 텍스트 출력 (message.content[0].text)
- 응답 객체 분석: role, content, stop_reason, usage.input_tokens, usage.output_tokens 각각 출력
- 건축공학 응용 예제 추가: RC 기둥 설계 검토 요청
  - 기둥 단면 500x500mm, fck=24MPa, fy=400MPa, 주근 8-D25, 띠철근 D10@300
  - 설계 축력 Pu=2500kN, 설계 모멘트 Mu=150kN·m, 적용기준 KDS 14 20 20
  - 검토항목: 축력비(0.8 이하), 최소/최대 철근비(0.01~0.08), 띠철근 간격, 판정 결과 표
  - 토큰 사용량 출력

### 파일 2: 002_multi_turn.py
- 3개 헬퍼 함수 정의:
  - add_user_message(messages, text): 사용자 메시지를 리스트에 추가
  - add_assistant_message(messages, text): 어시스턴트 응답을 리스트에 추가
  - chat(messages, system=None): API 호출 후 응답 텍스트 반환, system 파라미터 옵션
- 3턴 대화 예시 (RC 보 최소 철근비 → KDS 공식 → fck=30MPa 실제 계산)
- 대화형 챗봇 루프 (while True, input(), quit/q/종료로 탈출)

### 파일 3: 003_system_prompt.py
- 수학 튜터 시스템 프롬프트 예시 (답을 직접 주지 말고 힌트로 유도)
- 건축공학 응용: KDS 기반 구조 검토 AI 어시스턴트
  - 시스템 프롬프트에 전문분야(KDS 14 20, KDS 41 17, KDS 41 10 15)와 행동규칙 5가지 포함
  - 3턴 멀티턴 대화:
    1턴: RC 기둥 초기 설계 조건 검토 (단면, 강도, 주근, 축력, 모멘트, 내진등급 C)
    2턴: 내진등급 변경(특등급 D)에 따른 재검토
    3턴: 부적합 항목 개선안 요청

### 파일 4: 004_temperature_streaming.py
- chat 함수에 temperature 파라미터 추가 (기본값 1.0)
- Temperature 비교 실험:
  - temperature=0.0: 구조 계산 (500x500 기둥 축하중강도 Pn 계산)
  - temperature=0.9: 설계 아이디어 브레인스토밍 (20층 횡력저항시스템)
- 기본 스트리밍 (stream=True, raw 이벤트 출력)
- 간편 스트리밍 (client.messages.stream, text_stream, print with flush=True)
- 스트리밍 후 get_final_message()로 메타데이터(모델, 종료사유, 토큰수) 출력

### 파일 5: 005_output_control.py
- 프리필링 예시: "차와 커피" 질문에 대해 프리필 없음 vs "커피가 더 나은데, 그 이유는" 프리필 비교
- chat 함수에 stop_sequences 파라미터 추가
- 정지 시퀀스 예시: 1~10 세기에서 "5"에서 중단
- 구조화된 JSON 추출: 프리필(```json\n) + 정지 시퀀스(```) 조합
  - 500x500 RC 기둥 설계 결과를 JSON으로 추출, json.loads()로 파싱
- 건축공학 적용: 비정형 현장 미팅 메모에서 구조 변경 정보를 JSON으로 추출
  - 키: member_id, floor, original_section, revised_section, original_rebar, revised_rebar, concrete_grade, deadline, requester

### 파일 6: 006_integrated_chatbot.py
- 모든 기법 통합 챗봇 (system prompt + temperature + stop_sequences)
- 시스템 프롬프트: 건축구조공학 전문 AI, KDS 14 20 기준, 단계별 풀이, 단위 명시, 가정사항 표기
- temperature=0.3 (공학적 정확성)
- 스트리밍 버전: text_stream으로 실시간 출력 + 턴마다 입력/출력 토큰수 표시
- "/json" 명령어 입력 시 프리필+정지시퀀스로 JSON 모드 전환

---

각 파일 상단에 "=== 파일 설명 ===" 형식의 한국어 주석 블록을 넣고,
코드 섹션마다 "# === 섹션명 ===" 구분 주석을 달아줘.
인라인 주석도 한국어로 작성해.
출력 경로: 03-Exercises/Week_02/
```

---

## 사용법

1. Claude Code 터미널에서 위 프롬프트를 복사하여 실행
2. 생성된 6개 `.py` 파일이 `03-Exercises/Week_02/`에 저장됨
3. `.ipynb`로 변환하려면 프롬프트에서 "`.py` 파일" → "`.ipynb` 파일"로 변경

## 매핑

| 생성 파일 | 강의노트 섹션 | Skilljar 레슨 |
|---|---|---|
| 001_first_request.py | Ch.1 (1.5, 1.6) | L03-L05 |
| 002_multi_turn.py | Ch.2 (2.1, 2.2) | L06-L07 |
| 003_system_prompt.py | Ch.2 (2.3, 2.4) | L08-L09 |
| 004_temperature_streaming.py | Ch.3 (3.1, 3.2) | L10-L11 |
| 005_output_control.py | Ch.4 (4.1-4.3) | L12-L14 |
| 006_integrated_chatbot.py | Ch.5 (5.1, 5.2) | 종합 |
