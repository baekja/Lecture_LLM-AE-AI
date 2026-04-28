# Week 07 — Model Context Protocol (MCP) 실습 가이드

본 주차의 실습 노트북은 학습 목적에 따라 **3개 트랙**으로 구성되어 있다. 각 트랙은 독립적으로 학습 가능하나, **권장 학습 순서는 skilljar → structural → tutorial(보조)** 또는 **tutorial → skilljar → structural** 이다.

## 폴더 구조

```
Week_07/
├── skilljar/              # Track A — Skilljar 원본 (DocumentMCP) [권장: 강의 정규]
├── structural/            # Track B — 한국 건축공학 도메인 응용 [권장: 도메인 심화]
├── tutorial/              # Track C — 학생 친화 한국어 튜토리얼 [보조: 자율 학습]
└── README.md              # 본 문서
```

## Track A: `skilljar/` — Skilljar 원본 (DocumentMCP)

강의노트 `Week_07.md` §1.1~§2.6과 식별자 100% 일치. Skilljar S6 코스의 DocumentMCP 예제(`docs` dict, `read_doc_contents`, `edit_document`, `MCPClient` 클래스)를 셀별로 분해.

| 노트북 | 학습 목표 | Skilljar L# |
|---|---|:---:|
| `S6_01_mcp_server.ipynb` | FastMCP 서버 + `@mcp.tool` 도구 정의 | L01–L04 |
| `S6_02_mcp_inspector.ipynb` | `mcp dev` Inspector로 LLM 없이 검증 | L05 |
| `S6_03_mcp_client.ipynb` | `MCPClient` 클래스 + async context manager | L02·L06 |
| `S6_04_resources.ipynb` | `docs://documents` direct + templated, MIME types | L07·L08 |
| `S6_05_prompts.ipynb` | `format` 프롬프트 + `/` 슬래시 명령 | L09·L10 |
| `S6_06_practice.ipynb` | 학생 자율 도메인 (Tools 3 + Resources 2 + Prompts 1) | L11 |

**권장 사용**: 강의노트 §1.1~§2.6을 읽으며 동기 학습.

**의존**: 같은 폴더의 `cli_project/` 폴더 (Skilljar 원본 zip 압축 해제본). 노트북이 셀별로 `mcp_server.py` / `mcp_client.py`를 누적 저장하므로 노트북을 순서대로 실행해야 후속 노트북이 정상 작동.

## Track B: `structural/` — 한국 건축공학 도메인 응용

강의노트 `Week_07.md` §2.7의 6단계 빌드업을 단계 노트북 6개 + 통합본 1개로 분해.

| 노트북 | 학습 목표 | §2.7 단계 |
|---|---|:---:|
| `S6_st01_intro_structural_mcp.ipynb` | 도메인 첫 도구 (KDS 콘크리트 검토) | ① |
| `S6_st02_kds_resources.ipynb` | KDS 조문·재료 리소스 (`kds://`, `data://materials/`) | ② |
| `S6_st03_kds_rag_resource.ipynb` | W05 RAG 체인 → MCP 리소스 (`kds://search/{query}`) | ② 심화 |
| `S6_st04_midas_parser_tool.ipynb` | Midas `.mgt` 파서 도구 | ③ |
| `S6_st05_structural_review_prompt.ipynb` | `structural_review` 프롬프트 + 3자 협업 | ④ |
| `S6_st06_claude_code_register.ipynb` | `claude mcp add`로 Claude Code 등록 | ⑥ (보너스) |
| `S6_07_structural_mcp.ipynb` | 통합본 (단계 ①~⑥ 압축) — 제출용 | 통합 |

**권장 사용**: skilljar/ 트랙 완료 후, 또는 W05 RAG 노트북 (`S4_07_structural_rag.ipynb`) 완료 후 학습.

**의존**: 누적 빌드업으로 `structural_mcp.py`가 단계별 갱신. 단독 실행 시 `S6_07_structural_mcp.ipynb` (통합본) 권장.

## Track C: `tutorial/` — 학생 친화 한국어 튜토리얼

기존 노트북(`_backup_20260428_pre-skilljar-rewrite/`)의 친숙한 한국어 도메인(시간/덧셈/면적, 재료 물성치, KDS 검토)을 보강한 학생용 튜토리얼. 각 노트북에 **체크포인트 3개**, **강의노트 매핑 박스**, **트러블슈팅 섹션**을 포함.

| 노트북 | 학습 목표 | 강의노트 대응 |
|---|---|:---:|
| `T01_first_mcp_server.ipynb` | 첫 MCP 서버 (시간/덧셈/면적) | §1.1·§1.4 |
| `T02_inspector_walkthrough.ipynb` | Inspector 단계별 가이드 + 트러블슈팅 | §1.5 |
| `T03_mcp_client_basics.ipynb` | low-level → 함수 → 클래스 단계적 추상화 | §1.2·§2.1 |
| `T04_resources_materials.ipynb` | 재료 물성치 리소스 (한국 도메인) | §2.2·§2.3 |
| `T05_prompts_kds_review.ipynb` | KDS 검토 프롬프트 (5개 카탈로그) | §2.4·§2.5 |
| `T06_capstone_practice.ipynb` | 자율 실습 (도메인 5개 추천 + 부분 작성된 가이드) | §2.6 |

**권장 사용**: 강의 시작 전 자기학습용 또는 skilljar/ 트랙이 어렵게 느껴질 때 보조 학습.

**의존**: 누적 빌드업으로 `tutorial_server.py`가 단계별 갱신. T03의 `SimpleMCPClient`를 T04에서 확장.

## 권장 학습 경로

### 경로 1: 강의 정규 학습 (가장 권장)
```
[강의노트 §1.1] → skilljar/S6_01 → [§1.4] → skilljar/S6_02 (Inspector)
   → [§1.2·§2.1] → skilljar/S6_03 → [§2.2·§2.3] → skilljar/S6_04
   → [§2.4·§2.5] → skilljar/S6_05 → [§2.6] → skilljar/S6_06
   → [§2.7] → structural/S6_st01~S6_st06 → structural/S6_07 (통합)
```

### 경로 2: 한국어 친화 자율 학습
```
tutorial/T01 → tutorial/T02 → tutorial/T03 → tutorial/T04 → tutorial/T05 → tutorial/T06
   → (도메인 응용) → structural/S6_st01~S6_07
```

### 경로 3: 도메인 직행 (구조공학 전공자)
```
W05 S4_07 (RAG) → structural/S6_st01 → S6_st02 → S6_st03 (RAG 재활용)
   → S6_st04 (Midas) → S6_st05 (프롬프트) → S6_st06 (Claude Code 등록) → S6_07 (통합)
```

## 백업 폴더

| 폴더 | 내용 | 권한 |
|---|---|---|
| `skilljar/_originals_skilljar/` | Skilljar S6 cli_project 원본 (불변, 참조용) | 읽기 전용 |
| `skilljar/_backup_20260428_pre-skilljar-rewrite/` | 재작성 전 노트북 7개 + server.py | 읽기 전용 |
| `skilljar/_backup_20260413/` | 이전 백업 (Apr 13) | 읽기 전용 |
| `skilljar/_student_practice_20260428/` | 학생 풀이용 (TODO 셀 비운 사본) — 향후 작성 | — |

## 강의노트 백업

본 캠페인 시점의 강의노트는 다음에 보관:

```
01-Notes/_backup_20260428/
├── Week_07.md
└── Week_07_EN.md
```

## 제출 가이드 (강의노트 §2.7과 일관)

**필수**: `skilljar/S6_01` ~ `skilljar/S6_05` 완료본
**선택 (택일)**: `skilljar/S6_06` (자율 도메인) 또는 `structural/S6_07` (통합본)

**평가 관점**:
1. 서버·클라이언트·Inspector 루프의 재현성
2. Resources·Prompts 설계의 직관성 (MIME/URI 규약)
3. 도메인 응용에서 Tools·Resources·Prompts 3자 협업

---

본 README는 `2026-04-28`에 노트북 재작성 캠페인 결과로 작성됨. 추후 강의노트 갱신 시 이 문서도 동기화.
