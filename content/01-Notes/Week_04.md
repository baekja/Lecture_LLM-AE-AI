---
draft: true
---

# 4주차: LLM API 심화 - Tool Use & 멀티모달

---

## 📌 강의 중점

- **Claude/OpenAI API** 공식 SDK 활용법
- **Tool Use (Function Calling)**: LLM이 외부 함수를 호출하는 메커니즘
- **멀티모달 입력**: 이미지, PDF 등 비텍스트 데이터 처리
- **스트리밍 응답**과 비용 최적화

---

## 🎯 학습 목표

학습 완료 후 다음을 수행할 수 있습니다:

- Claude/OpenAI SDK로 다양한 API 기능을 활용할 수 있다
- Tool Use를 구현하여 LLM이 외부 시스템과 상호작용하게 할 수 있다
- 이미지, PDF 등 멀티모달 입력을 처리할 수 있다
- 스트리밍을 활용한 실시간 응답을 구현할 수 있다

---

## [Chapter 1] LLM API SDK 심화

### 1.1 Anthropic Claude SDK

```python
import anthropic
from anthropic import Anthropic

# 클라이언트 초기화
client = Anthropic()  # ANTHROPIC_API_KEY 환경변수 자동 사용

# 기본 메시지 전송
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system="당신은 건축구조 전문가입니다.",
    messages=[
        {"role": "user", "content": "H형강 H-400x200x8x13의 단면 특성을 설명해주세요."}
    ]
)

print(response.content[0].text)
print(f"입력 토큰: {response.usage.input_tokens}")
print(f"출력 토큰: {response.usage.output_tokens}")
```

### 1.2 대화 히스토리 관리

```python
class ConversationManager:
    """대화 히스토리 관리 클래스"""

    def __init__(self, system_prompt: str = ""):
        self.client = Anthropic()
        self.system_prompt = system_prompt
        self.messages: list[dict] = []

    def chat(self, user_message: str) -> str:
        """대화 메시지 전송"""
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.messages
        )

        assistant_message = response.content[0].text
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def clear_history(self):
        """대화 히스토리 초기화"""
        self.messages = []


# 사용 예시
conv = ConversationManager(
    system_prompt="당신은 건축구조설계기준(KDS 41)을 기반으로 답변하는 전문가입니다."
)

print(conv.chat("내진설계의 기본 원칙은 무엇인가요?"))
print(conv.chat("방금 설명한 내용 중 응답수정계수에 대해 더 자세히 설명해주세요."))
```

### 1.3 모델 파라미터

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,           # 최대 출력 토큰 수
    temperature=0.7,           # 창의성 (0.0~1.0)
    top_p=0.9,                 # 누적 확률 샘플링
    stop_sequences=["END"],    # 중단 시퀀스
    system="시스템 프롬프트",
    messages=[...]
)
```

**Temperature 가이드**:
| 값 | 용도 |
|----|------|
| 0.0 | 사실 기반 답변, 계산, 코드 생성 |
| 0.3-0.5 | 일반적인 질의응답 |
| 0.7-0.9 | 창의적 글쓰기, 브레인스토밍 |

### 📚 참고 자료

- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Claude API Reference](https://docs.anthropic.com/claude/reference)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

---

## [Chapter 2] Tool Use (Function Calling)

### 2.1 Tool Use 개념

```mermaid
sequenceDiagram
    participant U as 사용자
    participant L as LLM
    participant T as Tool (함수)

    U->>L: "서울의 현재 날씨 알려줘"
    L->>L: Tool 호출 필요 판단
    L->>T: get_weather("서울")
    T->>L: {"temp": 15, "condition": "맑음"}
    L->>U: "서울의 현재 기온은 15°C이고 맑은 날씨입니다."
```

### 2.2 Tool 정의

```python
# 도구 정의
tools = [
    {
        "name": "get_building_code",
        "description": "건축법 또는 건축구조기준의 특정 조항을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code_type": {
                    "type": "string",
                    "enum": ["건축법", "KDS", "KBC"],
                    "description": "조회할 법규/기준 유형"
                },
                "article_number": {
                    "type": "string",
                    "description": "조항 번호 (예: '41 17 00')"
                },
                "keyword": {
                    "type": "string",
                    "description": "검색 키워드"
                }
            },
            "required": ["code_type"]
        }
    },
    {
        "name": "calculate_section_properties",
        "description": "구조 부재의 단면 특성(면적, 단면2차모멘트 등)을 계산합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "section_type": {
                    "type": "string",
                    "enum": ["H형강", "C형강", "각형강관", "원형강관"],
                    "description": "단면 유형"
                },
                "dimensions": {
                    "type": "object",
                    "description": "단면 치수 (mm)",
                    "properties": {
                        "height": {"type": "number"},
                        "width": {"type": "number"},
                        "web_thickness": {"type": "number"},
                        "flange_thickness": {"type": "number"}
                    }
                }
            },
            "required": ["section_type", "dimensions"]
        }
    }
]
```

### 2.3 Tool Use 구현

```python
import anthropic
import json


def get_building_code(code_type: str, article_number: str = None, keyword: str = None) -> dict:
    """건축 법규 조회 (실제 구현 시 DB 연동)"""
    # 시뮬레이션 데이터
    codes = {
        "KDS 41 17 00": {
            "title": "건축물 내진설계기준",
            "content": "내진등급에 따른 설계 요구사항..."
        }
    }

    if article_number and article_number in codes:
        return codes[article_number]
    return {"error": "해당 조항을 찾을 수 없습니다."}


def calculate_section_properties(section_type: str, dimensions: dict) -> dict:
    """단면 특성 계산"""
    if section_type == "H형강":
        h = dimensions.get("height", 0)
        b = dimensions.get("width", 0)
        tw = dimensions.get("web_thickness", 0)
        tf = dimensions.get("flange_thickness", 0)

        # 단면적 계산 (근사)
        area = 2 * b * tf + (h - 2 * tf) * tw

        # 단면2차모멘트 (근사)
        Ix = (b * h**3 - (b - tw) * (h - 2*tf)**3) / 12

        return {
            "section": f"H-{h}x{b}x{tw}x{tf}",
            "area_mm2": round(area, 2),
            "Ix_mm4": round(Ix, 2),
            "area_cm2": round(area / 100, 2),
            "Ix_cm4": round(Ix / 10000, 2)
        }

    return {"error": "지원하지 않는 단면 유형입니다."}


# Tool 실행 함수
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """도구 실행"""
    if tool_name == "get_building_code":
        result = get_building_code(**tool_input)
    elif tool_name == "calculate_section_properties":
        result = calculate_section_properties(**tool_input)
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result, ensure_ascii=False)


# Tool Use가 포함된 대화
def chat_with_tools(user_message: str):
    client = anthropic.Anthropic()

    messages = [{"role": "user", "content": user_message}]

    # 첫 번째 호출
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )

    # Tool 호출이 필요한 경우
    while response.stop_reason == "tool_use":
        # Tool 호출 결과 수집
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # 메시지에 어시스턴트 응답과 도구 결과 추가
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        # 다시 호출
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

    # 최종 텍스트 응답 반환
    return response.content[0].text


# 사용 예시
result = chat_with_tools(
    "H-400x200x8x13 형강의 단면적과 단면2차모멘트를 계산해주세요."
)
print(result)
```

### 2.4 Tool Use 워크플로우

```mermaid
flowchart TD
    A[사용자 질문] --> B{LLM 분석}
    B -->|Tool 필요| C[Tool 호출 요청]
    B -->|Tool 불필요| D[직접 응답]

    C --> E[Tool 실행]
    E --> F[결과 반환]
    F --> G{추가 Tool 필요?}
    G -->|예| C
    G -->|아니오| H[최종 응답 생성]

    D --> I[응답 출력]
    H --> I
```

### 📚 참고 자료

- [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)

---

## [Chapter 3] 멀티모달 입력

### 3.1 이미지 분석

```mermaid
graph LR
    subgraph Input["입력"]
        I1["건축 도면 이미지"]
        I2["구조물 사진"]
        I3["상세 도면"]
    end

    subgraph Process["Claude Vision"]
        P1["이미지 인코딩<br/>(Base64)"]
        P2["비전 모델 분석"]
        P3["텍스트 응답 생성"]
    end

    subgraph Output["출력"]
        O1["도면 해석"]
        O2["부재 식별"]
        O3["문제점 분석"]
    end

    Input --> Process --> Output
```

### 3.2 이미지 입력 구현

```python
import anthropic
import base64
import httpx
from pathlib import Path


def encode_image(image_path: str) -> tuple[str, str]:
    """이미지를 Base64로 인코딩"""
    path = Path(image_path)
    suffix = path.suffix.lower()

    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }

    media_type = media_types.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    return image_data, media_type


def analyze_image(image_path: str, prompt: str) -> str:
    """이미지 분석"""
    client = anthropic.Anthropic()
    image_data, media_type = encode_image(image_path)

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return response.content[0].text


# URL에서 이미지 분석
def analyze_image_url(image_url: str, prompt: str) -> str:
    """URL 이미지 분석"""
    client = anthropic.Anthropic()

    # 이미지 다운로드
    image_data = base64.standard_b64encode(
        httpx.get(image_url).content
    ).decode("utf-8")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return response.content[0].text


# 건축 도면 분석 예시
result = analyze_image(
    "structural_drawing.png",
    """
    이 구조 도면을 분석해 주세요:
    1. 구조 시스템 유형 (라멘, 가새 등)
    2. 주요 부재 식별 (기둥, 보, 슬래브)
    3. 예상 스팬 및 층고
    4. 특이사항이나 주의점
    """
)
print(result)
```

### 3.3 PDF 문서 분석

```python
import anthropic
import base64
from pathlib import Path


def analyze_pdf(pdf_path: str, prompt: str) -> str:
    """PDF 문서 분석 (Claude 3.5 지원)"""
    client = anthropic.Anthropic()

    with open(pdf_path, "rb") as f:
        pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return response.content[0].text


# 구조계산서 분석 예시
result = analyze_pdf(
    "structural_calculation.pdf",
    """
    이 구조계산서를 검토하고 다음을 분석해 주세요:
    1. 적용된 설계기준
    2. 하중 조합
    3. 주요 부재의 응력비
    4. 검토가 필요한 항목
    """
)
```

### 3.4 여러 이미지 비교

```python
def compare_images(image_paths: list[str], prompt: str) -> str:
    """여러 이미지 비교 분석"""
    client = anthropic.Anthropic()

    content = []
    for i, path in enumerate(image_paths, 1):
        image_data, media_type = encode_image(path)
        content.append({
            "type": "text",
            "text": f"이미지 {i}:"
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        })

    content.append({
        "type": "text",
        "text": prompt
    })

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}]
    )

    return response.content[0].text


# 시공 전후 비교 예시
result = compare_images(
    ["before.jpg", "after.jpg"],
    "두 이미지를 비교하여 시공 진행 상황과 변경 사항을 분석해 주세요."
)
```

### 📚 참고 자료

- [Claude Vision Guide](https://docs.anthropic.com/claude/docs/vision)
- [OpenAI Vision](https://platform.openai.com/docs/guides/vision)
- [PDF Processing Best Practices](https://docs.anthropic.com/claude/docs/pdf-support)

---

## [Chapter 4] 스트리밍과 최적화

### 4.1 스트리밍 응답

```python
import anthropic


def stream_response(message: str):
    """스트리밍 응답"""
    client = anthropic.Anthropic()

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": message}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()  # 줄바꿈

    # 최종 메시지 객체
    final_message = stream.get_final_message()
    print(f"\n토큰 사용: {final_message.usage}")


# 비동기 스트리밍
async def stream_response_async(message: str):
    """비동기 스트리밍"""
    client = anthropic.AsyncAnthropic()

    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": message}]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)


# 이벤트 기반 스트리밍
def stream_with_events(message: str):
    """이벤트 기반 스트리밍"""
    client = anthropic.Anthropic()

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": message}]
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                print(event.delta.text, end="")
            elif event.type == "message_stop":
                print("\n[완료]")
```

### 4.2 비용 최적화 전략

```mermaid
graph TB
    subgraph Strategies["비용 최적화 전략"]
        S1["모델 선택<br/>Haiku < Sonnet < Opus"]
        S2["캐싱 활용<br/>동일 요청 캐시"]
        S3["프롬프트 최적화<br/>불필요한 토큰 제거"]
        S4["배치 처리<br/>여러 요청 묶기"]
    end
```

```python
from functools import lru_cache
import hashlib
import json


class OptimizedLLMClient:
    """최적화된 LLM 클라이언트"""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.cache = {}

    def _cache_key(self, model: str, messages: list) -> str:
        """캐시 키 생성"""
        content = json.dumps({"model": model, "messages": messages}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def chat(
        self,
        message: str,
        model: str = "claude-3-5-sonnet-20241022",
        use_cache: bool = True
    ) -> str:
        """캐시 지원 채팅"""
        messages = [{"role": "user", "content": message}]
        cache_key = self._cache_key(model, messages)

        # 캐시 확인
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=messages
        )

        result = response.content[0].text

        # 캐시 저장
        if use_cache:
            self.cache[cache_key] = result

        return result

    def select_model(self, task_complexity: str) -> str:
        """작업 복잡도에 따른 모델 선택"""
        models = {
            "simple": "claude-3-haiku-20240307",      # 빠르고 저렴
            "moderate": "claude-3-5-sonnet-20241022", # 균형
            "complex": "claude-3-opus-20240229"       # 최고 품질
        }
        return models.get(task_complexity, models["moderate"])
```

### 4.3 Prompt Caching

```python
import anthropic


def chat_with_cache(system_prompt: str, user_message: str):
    """프롬프트 캐싱 활용 (긴 시스템 프롬프트에 효과적)"""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # 캐싱 활성화
            }
        ],
        messages=[{"role": "user", "content": user_message}]
    )

    # 캐시 사용 여부 확인
    print(f"캐시 생성 토큰: {response.usage.cache_creation_input_tokens}")
    print(f"캐시 읽기 토큰: {response.usage.cache_read_input_tokens}")

    return response.content[0].text


# 긴 시스템 프롬프트 (건축 법규 등)
long_system_prompt = """
[건축구조설계기준 KDS 41 전체 내용...]
...수천 줄의 텍스트...
"""

# 첫 번째 호출: 캐시 생성
result1 = chat_with_cache(long_system_prompt, "내진설계 등급 분류 기준은?")

# 두 번째 호출: 캐시 사용 (비용 절감)
result2 = chat_with_cache(long_system_prompt, "지진하중 산정 방법은?")
```

### 📚 참고 자료

- [Anthropic Streaming Guide](https://docs.anthropic.com/claude/docs/streaming)
- [Prompt Caching](https://docs.anthropic.com/claude/docs/prompt-caching)
- [API Rate Limits](https://docs.anthropic.com/claude/reference/rate-limits)

---

## 💻 실습 코드

### 실습 1: Tool Use - 건축 법규 조회

```python
# practice/tool_use_demo.py
"""Tool Use 실습 - 건축 법규 조회 봇"""

import anthropic
import json

# 법규 데이터베이스 (시뮬레이션)
BUILDING_CODES = {
    "KDS 41 17 00": {
        "title": "건축물 내진설계기준",
        "sections": {
            "4.2": "내진등급 및 내진범주",
            "5.3": "설계지반운동",
            "6.2": "지진하중 산정"
        }
    },
    "KDS 41 12 00": {
        "title": "건축물 하중기준",
        "sections": {
            "3.1": "고정하중",
            "3.2": "활하중",
            "3.3": "적설하중"
        }
    }
}


tools = [
    {
        "name": "search_building_code",
        "description": "건축구조기준(KDS)을 검색합니다",
        "input_schema": {
            "type": "object",
            "properties": {
                "code_id": {
                    "type": "string",
                    "description": "기준 번호 (예: KDS 41 17 00)"
                },
                "keyword": {
                    "type": "string",
                    "description": "검색 키워드"
                }
            },
            "required": ["keyword"]
        }
    }
]


def search_building_code(code_id: str = None, keyword: str = "") -> dict:
    """건축 법규 검색"""
    results = []

    for code_key, code_data in BUILDING_CODES.items():
        if code_id and code_id not in code_key:
            continue

        # 키워드 검색
        if keyword.lower() in code_data["title"].lower():
            results.append({
                "code": code_key,
                "title": code_data["title"],
                "sections": code_data["sections"]
            })
            continue

        for section_id, section_title in code_data["sections"].items():
            if keyword.lower() in section_title.lower():
                results.append({
                    "code": code_key,
                    "section": section_id,
                    "title": section_title
                })

    return {"results": results, "count": len(results)}


def run_tool(name: str, inputs: dict) -> str:
    if name == "search_building_code":
        return json.dumps(search_building_code(**inputs), ensure_ascii=False)
    return json.dumps({"error": "Unknown tool"})


def chat_with_codes(question: str) -> str:
    """법규 조회 기능이 있는 채팅"""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system="당신은 건축구조기준(KDS) 전문가입니다. 필요시 도구를 사용하여 정확한 정보를 제공하세요.",
        tools=tools,
        messages=messages
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system="당신은 건축구조기준(KDS) 전문가입니다.",
            tools=tools,
            messages=messages
        )

    return response.content[0].text


if __name__ == "__main__":
    questions = [
        "내진설계 관련 기준을 찾아주세요.",
        "활하중 기준은 어디에 있나요?",
        "KDS 41 17 00에서 지진하중 관련 내용을 알려주세요."
    ]

    for q in questions:
        print(f"\n질문: {q}")
        print(f"답변: {chat_with_codes(q)}")
        print("-" * 50)
```

### 실습 2: 건축 도면 분석

```python
# practice/vision_demo.py
"""이미지 분석 실습 - 건축 도면 분석"""

import anthropic
import base64
from pathlib import Path


def analyze_structural_drawing(image_path: str) -> dict:
    """구조 도면 분석"""
    client = anthropic.Anthropic()

    # 이미지 인코딩
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    suffix = Path(image_path).suffix.lower()
    media_type = "image/png" if suffix == ".png" else "image/jpeg"

    prompt = """
    이 구조 도면을 분석하여 다음 정보를 JSON 형식으로 추출해 주세요:

    {
        "structure_type": "구조 시스템 유형",
        "main_members": [
            {"type": "부재유형", "section": "예상 단면", "location": "위치"}
        ],
        "dimensions": {
            "span": "예상 스팬 (m)",
            "height": "예상 층고 (m)"
        },
        "notes": ["특이사항 목록"]
    }

    도면에서 확인할 수 없는 정보는 "불명"으로 표시하세요.
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )

    return response.content[0].text


def check_construction_progress(before_image: str, after_image: str) -> str:
    """시공 진행 상황 비교"""
    client = anthropic.Anthropic()

    images = []
    for path in [before_image, after_image]:
        with open(path, "rb") as f:
            images.append(base64.standard_b64encode(f.read()).decode("utf-8"))

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이전 사진:"},
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": images[0]}
                    },
                    {"type": "text", "text": "이후 사진:"},
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": images[1]}
                    },
                    {
                        "type": "text",
                        "text": """
                        두 사진을 비교하여 시공 진행 상황을 분석해 주세요:
                        1. 완료된 공정
                        2. 진행 중인 공정
                        3. 품질 이슈 (있는 경우)
                        4. 다음 예상 공정
                        """
                    }
                ]
            }
        ]
    )

    return response.content[0].text


if __name__ == "__main__":
    # 테스트 (실제 이미지 파일 필요)
    # result = analyze_structural_drawing("drawing.png")
    # print(result)
    pass
```

### 실습 3: 스트리밍 채팅 서버

```python
# practice/streaming_server.py
"""스트리밍 응답 FastAPI 서버"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import anthropic

app = FastAPI()


@app.get("/chat/stream")
async def stream_chat(message: str):
    """스트리밍 채팅 엔드포인트"""

    async def generate():
        client = anthropic.AsyncAnthropic()

        async with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system="당신은 건축구조 전문가입니다.",
            messages=[{"role": "user", "content": message}]
        ) as stream:
            async for text in stream.text_stream:
                yield f"data: {text}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


# 실행: uvicorn practice.streaming_server:app --reload
# 테스트: curl "http://localhost:8000/chat/stream?message=H형강에 대해 설명해주세요"
```

---

## 📝 과제

### 과제 1: Tool Use 구현 (제출)

건축공학 관련 Tool을 2개 이상 정의하고 구현하세요:

**예시 Tool**:
- 단면 특성 계산기
- 하중 조합 계산기
- 재료 물성치 조회
- 건축 법규 검색

**제출물**:
- Python 코드
- Tool 정의 JSON
- 실행 결과 스크린샷

### 과제 2: 이미지 분석 활용 (제출)

건축/구조 관련 이미지를 분석하는 프로그램 작성:

**가능한 주제**:
- 구조 도면 부재 식별
- 건축 사진 분석
- 시공 현장 안전 점검

**제출물**:
- Python 코드
- 테스트 이미지
- 분석 결과

---

## 🔗 추가 학습 자료

### 공식 문서
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use)
- [Claude Vision](https://docs.anthropic.com/claude/docs/vision)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

### 튜토리얼
- [Building AI Agents with Tool Use](https://www.anthropic.com/news/tool-use-ga)
- [Multimodal AI Applications](https://cookbook.openai.com/examples/gpt_with_vision_for_video_understanding)

### GitHub
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)

---

## 🚀 발전 전략 (Development Strategies)

### 전략 1: 실전 Tool Use 확장 - 건축구조 계산 라이브러리 구축

**목표**: 실무에서 자주 사용하는 구조계산 기능을 Tool로 패키징하여 재사용 가능한 라이브러리 제작

**구현 단계**:

```python
# tools/structural_tools.py
"""건축구조 계산 Tool 라이브러리"""

import numpy as np
from typing import Dict, List, Optional

class StructuralCalculationTools:
    """구조계산 Tool 정의 및 실행"""

    @staticmethod
    def get_tool_definitions() -> List[Dict]:
        """Tool 정의 반환"""
        return [
            {
                "name": "calculate_beam_deflection",
                "description": "단순보의 처짐을 계산합니다 (등분포하중 또는 집중하중)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "load_type": {
                            "type": "string",
                            "enum": ["uniform", "concentrated"],
                            "description": "하중 유형: uniform(등분포), concentrated(집중)"
                        },
                        "load_value": {
                            "type": "number",
                            "description": "하중 크기 (kN/m 또는 kN)"
                        },
                        "span": {
                            "type": "number",
                            "description": "경간 길이 (m)"
                        },
                        "elastic_modulus": {
                            "type": "number",
                            "description": "탄성계수 E (MPa), 기본값 205000 (강재)",
                            "default": 205000
                        },
                        "moment_of_inertia": {
                            "type": "number",
                            "description": "단면2차모멘트 I (cm^4)"
                        }
                    },
                    "required": ["load_type", "load_value", "span", "moment_of_inertia"]
                }
            },
            {
                "name": "check_beam_capacity",
                "description": "H형강 보의 휨내력과 전단내력을 검토합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section": {
                            "type": "string",
                            "description": "단면 규격 (예: H-400x200x8x13)"
                        },
                        "steel_grade": {
                            "type": "string",
                            "enum": ["SS275", "SS315", "SS355", "SS400", "SM355", "SM490"],
                            "description": "강재 등급"
                        },
                        "moment": {
                            "type": "number",
                            "description": "작용 휨모멘트 (kN·m)"
                        },
                        "shear": {
                            "type": "number",
                            "description": "작용 전단력 (kN)"
                        },
                        "unbraced_length": {
                            "type": "number",
                            "description": "비지지길이 (m), 기본값 3.0m",
                            "default": 3.0
                        }
                    },
                    "required": ["section", "steel_grade", "moment", "shear"]
                }
            },
            {
                "name": "calculate_seismic_load",
                "description": "KDS 41 17 00 기준 등가정적 지진하중을 계산합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "building_height": {
                            "type": "number",
                            "description": "건물 높이 (m)"
                        },
                        "seismic_zone": {
                            "type": "string",
                            "enum": ["I", "II"],
                            "description": "지진구역 (I: 0.22g, II: 0.14g)"
                        },
                        "soil_type": {
                            "type": "string",
                            "enum": ["S1", "S2", "S3", "S4", "S5"],
                            "description": "지반 종류"
                        },
                        "structural_system": {
                            "type": "string",
                            "enum": ["moment_frame", "braced_frame", "shear_wall"],
                            "description": "구조시스템"
                        },
                        "seismic_weight": {
                            "type": "number",
                            "description": "지진하중 산정용 건물 중량 (kN)"
                        }
                    },
                    "required": ["building_height", "seismic_zone", "soil_type",
                                "structural_system", "seismic_weight"]
                }
            }
        ]

    @staticmethod
    def calculate_beam_deflection(
        load_type: str,
        load_value: float,
        span: float,
        moment_of_inertia: float,
        elastic_modulus: float = 205000
    ) -> Dict:
        """보 처짐 계산"""
        L = span * 1000  # m → mm
        I = moment_of_inertia * 10000  # cm^4 → mm^4
        E = elastic_modulus  # MPa

        if load_type == "uniform":
            w = load_value  # kN/m
            delta = (5 * w * L**4) / (384 * E * I)  # mm
            max_moment = (w * span**2) / 8  # kN·m
        else:  # concentrated
            P = load_value  # kN
            delta = (P * 1000 * L**3) / (48 * E * I)  # mm
            max_moment = (P * span) / 4  # kN·m

        # 허용처짐 (L/360)
        allowable_delta = L / 360

        return {
            "max_deflection_mm": round(delta, 2),
            "allowable_deflection_mm": round(allowable_delta, 2),
            "deflection_ratio": f"L/{round(L/delta, 0)}",
            "is_safe": delta <= allowable_delta,
            "max_moment_kNm": round(max_moment, 2)
        }

    @staticmethod
    def check_beam_capacity(
        section: str,
        steel_grade: str,
        moment: float,
        shear: float,
        unbraced_length: float = 3.0
    ) -> Dict:
        """보 내력 검토"""
        # 단면 정보 데이터베이스 (실제로는 DB 또는 파일에서 로드)
        section_db = {
            "H-400x200x8x13": {
                "h": 400, "b": 200, "tw": 8, "tf": 13,
                "A": 84.12, "Ix": 23700, "Zx": 1340, "rx": 16.8
            },
            "H-350x175x7x11": {
                "h": 350, "b": 175, "tw": 7, "tf": 11,
                "A": 63.14, "Ix": 13600, "Zx": 875, "rx": 14.7
            }
        }

        # 강재 항복강도
        fy_db = {
            "SS275": 275, "SS315": 315, "SS355": 355,
            "SS400": 235, "SM355": 355, "SM490": 325
        }

        if section not in section_db:
            return {"error": "지원하지 않는 단면 규격입니다"}

        sec = section_db[section]
        fy = fy_db.get(steel_grade, 275)

        # 휨내력 계산 (간단한 소성모멘트, 실제는 횡좌굴 고려)
        Mp = sec["Zx"] * fy / 1000  # kN·m
        phi = 0.9  # 강도감소계수
        Mn = phi * Mp

        # 전단내력 계산
        Aw = sec["h"] * sec["tw"] / 100  # cm^2
        Vn = phi * 0.6 * fy * Aw  # kN

        # 응력비
        moment_ratio = moment / Mn
        shear_ratio = shear / Vn

        return {
            "section": section,
            "steel_grade": steel_grade,
            "nominal_moment_capacity_kNm": round(Mn, 2),
            "applied_moment_kNm": moment,
            "moment_demand_capacity_ratio": round(moment_ratio, 3),
            "nominal_shear_capacity_kN": round(Vn, 2),
            "applied_shear_kN": shear,
            "shear_demand_capacity_ratio": round(shear_ratio, 3),
            "moment_ok": moment_ratio <= 1.0,
            "shear_ok": shear_ratio <= 1.0,
            "overall_safe": moment_ratio <= 1.0 and shear_ratio <= 1.0
        }

# 사용 예시
if __name__ == "__main__":
    tools = StructuralCalculationTools()

    # 처짐 계산 테스트
    deflection_result = tools.calculate_beam_deflection(
        load_type="uniform",
        load_value=20,  # kN/m
        span=6,  # m
        moment_of_inertia=23700  # cm^4
    )
    print("처짐 계산 결과:", deflection_result)

    # 내력 검토 테스트
    capacity_result = tools.check_beam_capacity(
        section="H-400x200x8x13",
        steel_grade="SM355",
        moment=150,  # kN·m
        shear=80  # kN
    )
    print("내력 검토 결과:", capacity_result)
```

**실습 과제**:
1. 위 Tool을 Claude API와 통합하여 자연어로 구조계산 수행
2. 추가 Tool 구현: 기둥 좌굴 검토, 접합부 볼트 설계, 용접 설계
3. 계산 결과를 Markdown 표로 자동 생성하는 리포트 기능 추가

---

### 전략 2: 멀티모달 실전 활용 - 도면 자동 수량 산출

**목표**: 건축 도면 이미지에서 부재를 인식하고 수량을 자동 집계하는 시스템 구축

**구현 아키텍처**:

```python
# applications/drawing_quantity_takeoff.py
"""도면 기반 자동 수량 산출 시스템"""

import anthropic
import base64
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd

class DrawingAnalyzer:
    """도면 분석 및 수량 산출"""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analyze_structural_plan(self, image_path: str) -> Dict:
        """구조 평면도 분석"""
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        prompt = """
        이 구조 평면도를 분석하여 다음 정보를 JSON 형식으로 추출하세요:

        {
            "grid_system": {
                "x_axis": ["A", "B", "C", ...],
                "y_axis": ["1", "2", "3", ...],
                "typical_span_x": "m",
                "typical_span_y": "m"
            },
            "columns": [
                {
                    "location": "A1",
                    "type": "H형강 또는 각형강관",
                    "section": "예: H-400x400x13x21",
                    "quantity": 1
                }
            ],
            "beams": [
                {
                    "start": "A1",
                    "end": "A2",
                    "type": "H형강",
                    "section": "H-400x200x8x13",
                    "length_m": 8.0,
                    "quantity": 1
                }
            ],
            "slabs": [
                {
                    "area_name": "일반 바닥",
                    "thickness_mm": 150,
                    "area_m2": 100.0
                }
            ]
        }

        확인할 수 없는 정보는 "추정" 또는 "불명"으로 표시하세요.
        """

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        # JSON 파싱
        try:
            result_text = response.content[0].text
            # JSON 블록 추출
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0]
            else:
                json_str = result_text

            return json.loads(json_str)
        except:
            return {"error": "JSON 파싱 실패", "raw_text": result_text}

    def calculate_material_quantity(self, analysis_result: Dict) -> pd.DataFrame:
        """부재별 물량 집계"""
        materials = []

        # 기둥 집계
        if "columns" in analysis_result:
            column_summary = {}
            for col in analysis_result["columns"]:
                section = col.get("section", "불명")
                column_summary[section] = column_summary.get(section, 0) + col.get("quantity", 1)

            for section, qty in column_summary.items():
                materials.append({
                    "부재 유형": "기둥",
                    "규격": section,
                    "수량": qty,
                    "단위": "개소",
                    "비고": ""
                })

        # 보 집계
        if "beams" in analysis_result:
            beam_summary = {}
            for beam in analysis_result["beams"]:
                section = beam.get("section", "불명")
                length = beam.get("length_m", 0)
                key = section
                if key not in beam_summary:
                    beam_summary[key] = {"qty": 0, "total_length": 0}
                beam_summary[key]["qty"] += beam.get("quantity", 1)
                beam_summary[key]["total_length"] += length

            for section, data in beam_summary.items():
                materials.append({
                    "부재 유형": "보",
                    "규격": section,
                    "수량": data["qty"],
                    "단위": "개소",
                    "비고": f"총 길이: {data['total_length']}m"
                })

        # 슬래브 집계
        if "slabs" in analysis_result:
            for slab in analysis_result["slabs"]:
                materials.append({
                    "부재 유형": "슬래브",
                    "규격": f"두께 {slab.get('thickness_mm', 0)}mm",
                    "수량": slab.get("area_m2", 0),
                    "단위": "m²",
                    "비고": slab.get("area_name", "")
                })

        return pd.DataFrame(materials)

    def generate_quantity_report(
        self,
        image_paths: List[str],
        output_excel: str = "quantity_takeoff.xlsx"
    ):
        """복수 도면 분석 및 수량 산출 보고서 생성"""
        all_materials = []

        for i, path in enumerate(image_paths, 1):
            print(f"도면 {i} 분석 중: {path}")
            analysis = self.analyze_structural_plan(path)

            if "error" not in analysis:
                df = self.calculate_material_quantity(analysis)
                df["도면 번호"] = f"Sheet-{i}"
                all_materials.append(df)

        # 전체 집계
        if all_materials:
            combined = pd.concat(all_materials, ignore_index=True)

            # Excel 저장
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                # 도면별 시트
                for i, df in enumerate(all_materials, 1):
                    df.to_excel(writer, sheet_name=f"도면{i}", index=False)

                # 전체 집계 시트
                summary = combined.groupby(["부재 유형", "규격"]).agg({
                    "수량": "sum",
                    "단위": "first"
                }).reset_index()
                summary.to_excel(writer, sheet_name="전체 집계", index=False)

            print(f"수량 산출 완료: {output_excel}")
            return combined

        return None

# 사용 예시
if __name__ == "__main__":
    analyzer = DrawingAnalyzer()

    # 단일 도면 분석
    result = analyzer.analyze_structural_plan("floor_plan_1F.png")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 복수 도면 일괄 처리
    drawing_list = [
        "floor_plan_1F.png",
        "floor_plan_2F.png",
        "floor_plan_RF.png"
    ]
    analyzer.generate_quantity_report(drawing_list, "building_quantity.xlsx")
```

**확장 실습**:
1. 도면 스케일 자동 인식 및 실제 치수 계산
2. 부재 간섭 체크 (기둥-보 연결부)
3. 도면과 BIM 모델 비교 검증

---

### 전략 3: 고급 Tool Use - 에이전트 체인 구성

**목표**: 복잡한 구조설계 업무를 여러 Tool이 협업하여 수행하는 에이전트 시스템 구축

**아키텍처**:

```mermaid
graph TD
    A[사용자 요청: 보 설계] --> B{설계 에이전트}
    B --> C[Tool 1: 하중 조합]
    B --> D[Tool 2: 단면 가정]
    C --> E[Tool 3: 응력 계산]
    D --> E
    E --> F{내력 검토 OK?}
    F -->|No| D
    F -->|Yes| G[Tool 4: 처짐 검토]
    G --> H{처짐 OK?}
    H -->|No| D
    H -->|Yes| I[Tool 5: 설계서 생성]
    I --> J[최종 결과 출력]
```

**구현 코드**:

```python
# applications/design_agent.py
"""자동 구조설계 에이전트"""

import anthropic
import json
from typing import Dict, List, Optional

class StructuralDesignAgent:
    """구조설계 자동화 에이전트"""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.design_history = []

        # Tool 정의
        self.tools = [
            {
                "name": "calculate_load_combination",
                "description": "KDS 기준 하중 조합을 계산합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "dead_load": {"type": "number", "description": "고정하중 (kN/m)"},
                        "live_load": {"type": "number", "description": "활하중 (kN/m)"},
                        "snow_load": {"type": "number", "description": "적설하중 (kN/m)", "default": 0},
                        "load_case": {
                            "type": "string",
                            "enum": ["strength", "serviceability"],
                            "description": "검토 조건"
                        }
                    },
                    "required": ["dead_load", "live_load", "load_case"]
                }
            },
            {
                "name": "select_trial_section",
                "description": "예비 단면을 선택합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "required_moment_capacity": {
                            "type": "number",
                            "description": "필요 휨내력 (kN·m)"
                        },
                        "span": {"type": "number", "description": "경간 (m)"},
                        "steel_grade": {
                            "type": "string",
                            "enum": ["SM355", "SM490"],
                            "description": "강재 등급"
                        }
                    },
                    "required": ["required_moment_capacity", "span", "steel_grade"]
                }
            },
            {
                "name": "check_capacity",
                "description": "단면 내력을 검토합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section": {"type": "string"},
                        "applied_moment": {"type": "number"},
                        "applied_shear": {"type": "number"},
                        "steel_grade": {"type": "string"}
                    },
                    "required": ["section", "applied_moment", "applied_shear", "steel_grade"]
                }
            },
            {
                "name": "check_deflection",
                "description": "처짐을 검토합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section": {"type": "string"},
                        "span": {"type": "number"},
                        "service_load": {"type": "number"}
                    },
                    "required": ["section", "span", "service_load"]
                }
            },
            {
                "name": "generate_design_report",
                "description": "설계 보고서를 생성합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "design_results": {"type": "object"}
                    },
                    "required": ["design_results"]
                }
            }
        ]

    def calculate_load_combination(self, dead_load, live_load, snow_load=0, load_case="strength"):
        """하중 조합 계산"""
        if load_case == "strength":
            # 강도설계: 1.2D + 1.6L
            combined = 1.2 * dead_load + 1.6 * live_load + 0.5 * snow_load
        else:  # serviceability
            # 사용성 검토: D + L
            combined = dead_load + live_load + 0.7 * snow_load

        return {
            "load_case": load_case,
            "combined_load_kN_per_m": round(combined, 2),
            "dead_load": dead_load,
            "live_load": live_load,
            "snow_load": snow_load
        }

    def select_trial_section(self, required_moment_capacity, span, steel_grade="SM355"):
        """예비 단면 선택"""
        # 간단한 단면 데이터베이스
        sections = [
            {"name": "H-300x150x6.5x9", "Zx": 611, "Ix": 8390, "weight": 42.4},
            {"name": "H-350x175x7x11", "Zx": 875, "Ix": 13600, "weight": 49.6},
            {"name": "H-400x200x8x13", "Zx": 1340, "Ix": 23700, "weight": 66.0},
            {"name": "H-450x200x9x14", "Zx": 1640, "Ix": 33600, "weight": 76.0},
            {"name": "H-500x200x10x16", "Zx": 2110, "Ix": 47800, "weight": 89.6}
        ]

        fy = 355 if steel_grade == "SM355" else 325
        phi = 0.9

        # 필요 소성단면계수
        required_Zx = (required_moment_capacity * 1000) / (phi * fy)

        # 적합한 단면 선택 (1.1배 여유)
        for sec in sections:
            if sec["Zx"] >= required_Zx * 1.1:
                return {
                    "selected_section": sec["name"],
                    "plastic_modulus_cm3": sec["Zx"],
                    "moment_of_inertia_cm4": sec["Ix"],
                    "weight_kg_per_m": sec["weight"],
                    "required_Zx_cm3": round(required_Zx, 2)
                }

        return {"error": "적합한 단면을 찾을 수 없습니다. 더 큰 단면이 필요합니다."}

    def execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        """Tool 실행"""
        if tool_name == "calculate_load_combination":
            result = self.calculate_load_combination(**tool_input)
        elif tool_name == "select_trial_section":
            result = self.select_trial_section(**tool_input)
        elif tool_name == "check_capacity":
            # 앞서 정의한 StructuralCalculationTools 활용
            from tools.structural_tools import StructuralCalculationTools
            tools = StructuralCalculationTools()
            result = tools.check_beam_capacity(
                section=tool_input["section"],
                steel_grade=tool_input["steel_grade"],
                moment=tool_input["applied_moment"],
                shear=tool_input["applied_shear"]
            )
        elif tool_name == "check_deflection":
            from tools.structural_tools import StructuralCalculationTools
            tools = StructuralCalculationTools()
            # 단면 정보 가져오기 (간략화)
            result = tools.calculate_beam_deflection(
                load_type="uniform",
                load_value=tool_input["service_load"],
                span=tool_input["span"],
                moment_of_inertia=23700  # 실제로는 단면별 조회
            )
        elif tool_name == "generate_design_report":
            result = self._generate_report(tool_input["design_results"])
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, ensure_ascii=False)

    def _generate_report(self, design_results: Dict) -> Dict:
        """설계 보고서 생성"""
        return {
            "report_title": "구조 부재 설계 보고서",
            "design_summary": design_results,
            "status": "completed"
        }

    def design_beam(self, requirements: str) -> str:
        """자동 보 설계 수행"""
        system_prompt = """
        당신은 건축구조 전문가입니다.
        사용자의 요구사항에 따라 보 설계를 수행하세요.

        설계 절차:
        1. calculate_load_combination으로 하중 조합 계산
        2. select_trial_section으로 예비 단면 선택
        3. check_capacity로 내력 검토
        4. check_deflection으로 처짐 검토
        5. 검토 실패 시 단면 재선정
        6. generate_design_report로 최종 보고서 작성

        각 단계의 결과를 명확히 설명하고, 최종적으로 설계 결과를 요약하세요.
        """

        messages = [{"role": "user", "content": requirements}]

        # 최대 10회 반복 (무한 루프 방지)
        for iteration in range(10):
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system_prompt,
                tools=self.tools,
                messages=messages
            )

            # Tool 사용 여부 확인
            if response.stop_reason != "tool_use":
                # 최종 응답
                return response.content[0].text

            # Tool 실행
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Tool 호출] {block.name}: {block.input}")
                    result = self.execute_tool(block.name, block.input)
                    print(f"[Tool 결과] {result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

                    self.design_history.append({
                        "iteration": iteration,
                        "tool": block.name,
                        "input": block.input,
                        "result": json.loads(result)
                    })

            # 메시지 업데이트
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        return "설계 반복 횟수 초과. 설계 조건을 재검토하세요."

# 사용 예시
if __name__ == "__main__":
    agent = StructuralDesignAgent()

    requirements = """
    다음 조건으로 단순보를 설계하세요:
    - 경간: 8m
    - 고정하중: 15 kN/m
    - 활하중: 10 kN/m
    - 강재: SM355
    - 설계기준: KDS 41 31 00

    강도 및 사용성을 모두 만족하는 최소 단면을 선정하세요.
    """

    result = agent.design_beam(requirements)
    print("\n=== 최종 설계 결과 ===")
    print(result)

    print("\n=== 설계 이력 ===")
    for step in agent.design_history:
        print(f"Step {step['iteration']}: {step['tool']}")
```

**학습 포인트**:
- Tool 간 데이터 전달 및 의존성 관리
- 반복 설계 프로세스 자동화
- 설계 이력 추적 및 디버깅

---

### 전략 4: 비용 최적화 실전 - 지능형 캐싱 전략

**목표**: 대용량 설계기준 문서를 효율적으로 활용하는 캐싱 시스템 구축

**구현 방안**:

```python
# utils/smart_cache_manager.py
"""지능형 LLM 캐싱 시스템"""

import anthropic
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, List
import pickle

class SmartCacheManager:
    """프롬프트 캐싱 및 로컬 캐시 관리"""

    def __init__(self, cache_dir: str = ".cache"):
        self.client = anthropic.Anthropic()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 통계
        self.stats = {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "tokens_saved": 0
        }

    def _hash_request(self, model: str, messages: List[Dict]) -> str:
        """요청 해시 생성"""
        content = json.dumps({
            "model": model,
            "messages": messages
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _local_cache_path(self, request_hash: str) -> Path:
        """로컬 캐시 파일 경로"""
        return self.cache_dir / f"{request_hash}.pkl"

    def chat_with_cache(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        use_prompt_cache: bool = True,
        use_local_cache: bool = True,
        max_cache_age: int = 3600  # 1시간
    ) -> Dict:
        """캐시 지원 채팅"""
        messages = [{"role": "user", "content": message}]
        request_hash = self._hash_request("claude-3-5-sonnet-20241022", messages)
        cache_path = self._local_cache_path(request_hash)

        # 로컬 캐시 확인
        if use_local_cache and cache_path.exists():
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age < max_cache_age:
                with open(cache_path, "rb") as f:
                    cached_result = pickle.load(f)

                self.stats["cache_hits"] += 1
                self.stats["tokens_saved"] += cached_result.get("usage", {}).get("input_tokens", 0)

                print(f"[로컬 캐시 HIT] {cache_age:.0f}초 전 캐시 사용")
                return cached_result

        self.stats["cache_misses"] += 1
        self.stats["api_calls"] += 1

        # API 호출
        request_params = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "messages": messages
        }

        # 프롬프트 캐싱 활성화
        if system_prompt and use_prompt_cache:
            request_params["system"] = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        elif system_prompt:
            request_params["system"] = system_prompt

        response = self.client.messages.create(**request_params)

        # 응답 구조화
        result = {
            "text": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
                "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0)
            },
            "timestamp": time.time()
        }

        # 캐시 정보 출력
        if use_prompt_cache:
            print(f"[프롬프트 캐싱]")
            print(f"  캐시 생성: {result['usage']['cache_creation_input_tokens']} 토큰")
            print(f"  캐시 읽기: {result['usage']['cache_read_input_tokens']} 토큰")

        # 로컬 캐시 저장
        if use_local_cache:
            with open(cache_path, "wb") as f:
                pickle.dump(result, f)

        return result

    def print_stats(self):
        """캐싱 통계 출력"""
        print("\n=== 캐싱 통계 ===")
        print(f"API 호출 횟수: {self.stats['api_calls']}")
        print(f"캐시 HIT: {self.stats['cache_hits']}")
        print(f"캐시 MISS: {self.stats['cache_misses']}")
        if self.stats['cache_hits'] + self.stats['cache_misses'] > 0:
            hit_rate = self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) * 100
            print(f"캐시 적중률: {hit_rate:.1f}%")
        print(f"절약된 토큰: {self.stats['tokens_saved']:,}")

    def clear_cache(self, older_than: Optional[int] = None):
        """캐시 정리"""
        count = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            if older_than:
                age = time.time() - cache_file.stat().st_mtime
                if age < older_than:
                    continue
            cache_file.unlink()
            count += 1

        print(f"{count}개 캐시 파일 삭제 완료")

# 사용 예시: 건축기준 법규 조회 봇
if __name__ == "__main__":
    # KDS 전체 내용 (실제로는 파일에서 로드)
    kds_full_text = """
    [KDS 41 17 00 건축물 내진설계기준 전체 내용]
    ... 수천 줄의 텍스트 ...
    """ * 100  # 대용량 문서 시뮬레이션

    cache_manager = SmartCacheManager()

    # 첫 번째 질문 (캐시 생성)
    result1 = cache_manager.chat_with_cache(
        message="내진등급 분류 기준을 설명해주세요.",
        system_prompt=kds_full_text,
        use_prompt_cache=True
    )
    print(f"답변: {result1['text'][:200]}...")

    # 두 번째 질문 (프롬프트 캐시 활용)
    result2 = cache_manager.chat_with_cache(
        message="지진하중 산정 방법은?",
        system_prompt=kds_full_text,
        use_prompt_cache=True
    )
    print(f"답변: {result2['text'][:200]}...")

    # 세 번째 질문 (로컬 캐시 활용)
    time.sleep(2)
    result3 = cache_manager.chat_with_cache(
        message="내진등급 분류 기준을 설명해주세요.",  # 첫 번째와 동일
        system_prompt=kds_full_text,
        use_local_cache=True
    )

    cache_manager.print_stats()
```

**비용 절감 효과**:
- 프롬프트 캐싱: 긴 시스템 프롬프트 90% 비용 절감
- 로컬 캐싱: 동일 요청 100% 비용 절감
- 실제 프로젝트에서 월 API 비용 50-70% 감소 가능

---

### 전략 5: 스트리밍 + 멀티모달 통합 - 실시간 도면 해설 시스템

**목표**: 사용자가 도면을 업로드하면 실시간으로 스트리밍 방식으로 해설을 제공하는 웹 애플리케이션

**기술 스택**: FastAPI + WebSocket + Claude Streaming

```python
# applications/realtime_drawing_narrator.py
"""실시간 도면 해설 웹 애플리케이션"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse
import anthropic
import base64
import asyncio
import json

app = FastAPI()

# HTML 프론트엔드
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>실시간 도면 해설</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; }
        #preview { max-width: 600px; border: 1px solid #ccc; margin: 20px 0; }
        #output {
            border: 1px solid #ddd;
            padding: 15px;
            min-height: 300px;
            background: #f9f9f9;
            white-space: pre-wrap;
        }
        .streaming { color: #0066cc; }
    </style>
</head>
<body>
    <h1>🏗️ 실시간 건축 도면 해설 시스템</h1>

    <input type="file" id="imageInput" accept="image/*">
    <button onclick="analyzeImage()">도면 분석 시작</button>

    <h3>업로드된 도면:</h3>
    <img id="preview" />

    <h3>AI 해설 (실시간 스트리밍):</h3>
    <div id="output">여기에 실시간으로 해설이 표시됩니다...</div>

    <script>
        let ws = null;

        document.getElementById('imageInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = function(event) {
                document.getElementById('preview').src = event.target.result;
            };
            reader.readAsDataURL(file);
        });

        async function analyzeImage() {
            const fileInput = document.getElementById('imageInput');
            const file = fileInput.files[0];
            if (!file) {
                alert('도면을 먼저 업로드하세요.');
                return;
            }

            // Base64 인코딩
            const reader = new FileReader();
            reader.onload = async function(event) {
                const base64Data = event.target.result.split(',')[1];

                // WebSocket 연결
                ws = new WebSocket('ws://localhost:8000/ws/analyze');

                ws.onopen = function() {
                    // 이미지 데이터 전송
                    ws.send(JSON.stringify({
                        image_data: base64Data,
                        media_type: file.type
                    }));
                };

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);

                    if (data.type === 'stream') {
                        // 스트리밍 텍스트 추가
                        document.getElementById('output').textContent += data.text;
                    } else if (data.type === 'done') {
                        document.getElementById('output').textContent += '\\n\\n✅ 분석 완료';
                        ws.close();
                    } else if (data.type === 'error') {
                        document.getElementById('output').textContent += '\\n\\n❌ 오류: ' + data.message;
                        ws.close();
                    }
                };

                ws.onerror = function(error) {
                    console.error('WebSocket Error:', error);
                };

                // 출력 초기화
                document.getElementById('output').textContent = '';
            };

            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get_home():
    """메인 페이지"""
    return HTMLResponse(HTML_PAGE)

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket 기반 실시간 도면 분석"""
    await websocket.accept()

    try:
        # 클라이언트로부터 이미지 데이터 수신
        data = await websocket.receive_text()
        request_data = json.loads(data)

        image_data = request_data["image_data"]
        media_type = request_data.get("media_type", "image/jpeg")

        # Claude 스트리밍 분석
        client = anthropic.AsyncAnthropic()

        prompt = """
        이 건축 도면을 상세히 분석하여 다음을 설명해주세요:

        1. **도면 유형 및 기본 정보**
           - 평면도, 입면도, 단면도 등 도면 종류
           - 축선 체계 (Grid System)
           - 예상 스케일

        2. **구조 시스템 분석**
           - 구조 형식 (라멘구조, 가새구조 등)
           - 주요 구조 부재 (기둥, 보, 벽체)
           - 부재 배치 및 스팬

        3. **부재 규격 추정**
           - 주요 부재의 예상 단면 규격
           - 재료 추정 (철근콘크리트, 강구조 등)

        4. **설계 특이사항**
           - 불규칙성이나 특수 구조
           - 주의가 필요한 부분
           - 시공 시 고려사항

        5. **개선 제안**
           - 구조적 효율성 향상 방안
           - 설계 최적화 가능성

        전문가적 관점에서 상세하고 실용적으로 설명해주세요.
        """

        async with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        ) as stream:
            async for text in stream.text_stream:
                # 실시간으로 텍스트 전송
                await websocket.send_json({
                    "type": "stream",
                    "text": text
                })
                await asyncio.sleep(0.01)  # 부드러운 스트리밍

        # 완료 메시지
        await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        print("클라이언트 연결 종료")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

# 실행: uvicorn applications.realtime_drawing_narrator:app --reload
# 접속: http://localhost:8000
```

**확장 기능**:
1. 여러 도면 비교 분석 (평면도 + 단면도 동시 분석)
2. 도면 위에 주석 자동 추가 (OCR + 객체 감지)
3. 음성 해설 추가 (TTS 통합)

---

### 전략 6: 프로덕션 배포 - 구조설계 챗봇 API 서비스

**목표**: 실제 업무에 활용 가능한 수준의 구조설계 상담 API 서비스 구축

**아키텍처**:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  FastAPI     │────▶│  Claude API │
│   (React)   │◀────│  Backend     │◀────│             │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │  (대화기록)   │
                    └──────────────┘
```

**구현 예시**:

```python
# applications/production_api.py
"""프로덕션 구조설계 챗봇 API"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import anthropic
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

app = FastAPI(title="구조설계 상담 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/structural_design")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 대화 기록 모델
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    user_message = Column(Text)
    assistant_message = Column(Text)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Request/Response 모델
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    include_history: bool = True

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: dict

# 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Claude 클라이언트
client = anthropic.Anthropic()

# 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 건축구조 전문 상담 AI입니다.

전문 분야:
- 건축구조설계기준(KDS 41)
- 강구조 설계 (KDS 41 31 00)
- 철근콘크리트 설계 (KDS 14 20 00)
- 내진설계 (KDS 41 17 00)
- 구조해석 및 부재 설계

답변 원칙:
1. 기술적으로 정확하고 근거 있는 답변 제공
2. 설계기준 조항 명시 (예: KDS 41 17 00 제5.3절)
3. 계산 과정은 단계별로 명확하게 설명
4. 안전과 관련된 사항은 보수적으로 접근
5. 불확실한 경우 명확히 언급하고 전문가 검토 권장

답변 형식:
- 간결하고 구조화된 형태
- 필요 시 표나 리스트 활용
- 핵심 내용 강조
"""

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """구조설계 상담 챗봇"""
    try:
        # 세션 ID 생성
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 대화 히스토리 로드
        messages = []
        if request.include_history and request.session_id:
            history = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.created_at).limit(10).all()

            for conv in history:
                messages.append({"role": "user", "content": conv.user_message})
                messages.append({"role": "assistant", "content": conv.assistant_message})

        # 현재 메시지 추가
        messages.append({"role": "user", "content": request.message})

        # Claude API 호출
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        assistant_message = response.content[0].text

        # 데이터베이스 저장
        conv_record = Conversation(
            session_id=session_id,
            user_message=request.message,
            assistant_message=assistant_message,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens
        )
        db.add(conv_record)
        db.commit()

        return ChatResponse(
            response=assistant_message,
            session_id=session_id,
            tokens_used={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{session_id}")
async def get_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """대화 기록 조회"""
    history = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at).all()

    return [
        {
            "user": conv.user_message,
            "assistant": conv.assistant_message,
            "timestamp": conv.created_at.isoformat()
        }
        for conv in history
    ]

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "structural-design-api"}

# 실행: uvicorn applications.production_api:app --host 0.0.0.0 --port 8000
```

**배포 체크리스트**:
- [ ] 환경 변수 관리 (API 키, DB 접속 정보)
- [ ] Rate limiting 구현 (사용량 제한)
- [ ] 로깅 및 모니터링 (Sentry, CloudWatch)
- [ ] 에러 처리 및 예외 상황 대응
- [ ] API 문서화 (Swagger UI)
- [ ] 보안 (HTTPS, 인증/인가)
- [ ] 성능 최적화 (캐싱, DB 인덱싱)
- [ ] 백업 및 복구 전략

---

### 전략 7: 종합 프로젝트 - 건축구조 설계 통합 플랫폼

**최종 목표**: 4주차 학습 내용을 모두 활용한 실전 프로젝트

**플랫폼 기능**:
1. **도면 업로드 및 자동 분석** (멀티모달)
2. **자연어 기반 구조 계산** (Tool Use)
3. **설계 최적화 제안** (에이전트 체인)
4. **실시간 상담** (스트리밍)
5. **설계 보고서 자동 생성** (문서화)

**프로젝트 구조**:
```
structural_design_platform/
├── backend/
│   ├── api/
│   │   ├── chat.py          # 채팅 API
│   │   ├── tools.py         # Tool Use 엔드포인트
│   │   └── analysis.py      # 도면 분석 API
│   ├── agents/
│   │   ├── design_agent.py  # 설계 에이전트
│   │   └── optimization.py  # 최적화 에이전트
│   ├── tools/
│   │   ├── structural.py    # 구조계산 Tool
│   │   └── database.py      # 법규 DB Tool
│   └── utils/
│       ├── cache.py         # 캐싱 관리
│       └── report.py        # 보고서 생성
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── public/
├── tests/
│   ├── test_tools.py
│   └── test_agents.py
├── docs/
│   └── API.md
├── requirements.txt
└── README.md
```

**구현 로드맵**:
- Week 4: 핵심 Tool 구현 및 테스트
- Week 5: 에이전트 체인 및 최적화
- Week 6: 프론트엔드 통합
- Week 7: 성능 최적화 및 배포

**학습 성과 측정**:
- [ ] 3개 이상의 실용적인 Tool 구현
- [ ] 멀티모달 입력 처리 (이미지 + PDF)
- [ ] 에이전트 체인을 통한 복잡한 설계 자동화
- [ ] 프로덕션 수준의 API 서비스 구축
- [ ] 비용 최적화 전략 적용 (캐싱, 모델 선택)

---

## 📋 전략 실행 체크리스트

### 단기 (1-2주)
- [ ] Tool Use 라이브러리 구축 (전략 1)
- [ ] 도면 분석 자동화 구현 (전략 2)
- [ ] 기본 캐싱 시스템 적용 (전략 4)

### 중기 (3-4주)
- [ ] 에이전트 체인 구성 (전략 3)
- [ ] 실시간 스트리밍 시스템 (전략 5)
- [ ] API 서비스 프로토타입 (전략 6)

### 장기 (5-8주)
- [ ] 통합 플랫폼 개발 (전략 7)
- [ ] 실전 프로젝트 배포
- [ ] 포트폴리오 구축

---

**핵심 메시지**: 4주차는 단순히 API 사용법을 배우는 것을 넘어, 실무에 바로 적용 가능한 건축공학 AI 시스템을 구축하는 능력을 키우는 것이 목표입니다. 각 전략을 단계적으로 실습하며, 최종적으로 자신만의 구조설계 자동화 도구를 완성하세요.
