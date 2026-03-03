---
draft: true
---

# 2주차: 개발환경 구축

---

## 📌 강의 중점

- **VS Code** 설정과 필수 확장 프로그램
- **Python 가상환경** 관리 (venv, conda)
- **GitHub** 버전 관리와 협업 워크플로우
- **환경변수** 관리와 보안 (.env, secrets)

---

## 🎯 학습 목표

학습 완료 후 다음을 수행할 수 있습니다:

- VS Code에서 Python 개발환경을 구축할 수 있다
- 가상환경을 생성하고 패키지를 관리할 수 있다
- Git을 사용하여 코드를 버전 관리할 수 있다
- API 키를 안전하게 관리할 수 있다

---

## [Chapter 1] VS Code 설정

### 1.1 VS Code 설치 및 기본 설정

**설치**:
- [VS Code 공식 사이트](https://code.visualstudio.com/)에서 다운로드
- macOS: Homebrew로 설치 가능 (`brew install --cask visual-studio-code`)

**기본 설정** (`settings.json`):

```json
{
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.formatOnSave": true,
    "editor.wordWrap": "on",
    "files.autoSave": "afterDelay",
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "terminal.integrated.defaultProfile.osx": "zsh"
}
```

### 1.2 필수 확장 프로그램

```mermaid
graph TB
    subgraph Python["Python 개발"]
        P1["Python (ms-python)"]
        P2["Pylance"]
        P3["Python Debugger"]
        P4["Jupyter"]
    end

    subgraph Git["버전 관리"]
        G1["GitLens"]
        G2["GitHub Copilot"]
        G3["Git Graph"]
    end

    subgraph Util["유틸리티"]
        U1["Prettier"]
        U2["Thunder Client"]
        U3["YAML"]
        U4["Markdown Preview"]
    end

    subgraph AI["AI 도구"]
        A1["Claude Dev"]
        A2["Continue"]
        A3["Codeium"]
    end
```

**설치 명령어** (터미널):

```bash
# Python 개발 필수
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.debugpy

# Git 관련
code --install-extension eamodio.gitlens
code --install-extension GitHub.copilot

# 유틸리티
code --install-extension esbenp.prettier-vscode
code --install-extension rangav.vscode-thunder-client
code --install-extension redhat.vscode-yaml
```

### 1.3 키보드 단축키

| 기능 | Windows/Linux | macOS |
|------|---------------|-------|
| 명령 팔레트 | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| 파일 검색 | `Ctrl+P` | `Cmd+P` |
| 전체 검색 | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| 터미널 열기 | `` Ctrl+` `` | `` Cmd+` `` |
| 사이드바 토글 | `Ctrl+B` | `Cmd+B` |
| 멀티 커서 | `Ctrl+D` | `Cmd+D` |
| 코드 포맷 | `Shift+Alt+F` | `Shift+Option+F` |
| 정의로 이동 | `F12` | `F12` |

### 📚 참고 자료

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [VS Code Tips and Tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [VS Code Keyboard Shortcuts](https://code.visualstudio.com/shortcuts/keyboard-shortcuts-macos.pdf)

---

## [Chapter 2] Python 가상환경

### 2.1 가상환경의 필요성

```mermaid
graph LR
    subgraph Problem["문제 상황"]
        A["프로젝트 A<br/>requests==2.28"]
        B["프로젝트 B<br/>requests==2.31"]
        S["시스템 Python"]
        A --> S
        B --> S
    end

    subgraph Solution["해결책: 가상환경"]
        A2["프로젝트 A<br/>.venv_a"]
        B2["프로젝트 B<br/>.venv_b"]
        A2 -.- |독립| B2
    end

    Problem --> |가상환경 사용| Solution
```

### 2.2 venv 사용법

```bash
# 가상환경 생성
python -m venv .venv

# 활성화
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 비활성화
deactivate

# 패키지 설치
pip install anthropic openai fastapi

# 의존성 저장
pip freeze > requirements.txt

# 의존성 설치
pip install -r requirements.txt
```

### 2.3 Conda 환경 관리

```bash
# 환경 생성
conda create -n llm-course python=3.11

# 환경 활성화
conda activate llm-course

# 패키지 설치
conda install numpy pandas
pip install anthropic  # conda에 없는 패키지

# 환경 내보내기
conda env export > environment.yml

# 환경 복원
conda env create -f environment.yml

# 환경 목록 확인
conda env list

# 환경 삭제
conda env remove -n llm-course
```

### 2.4 프로젝트 구조

```
llm-architecture-ai/
├── .venv/                  # 가상환경 (git ignore)
├── .env                    # 환경변수 (git ignore)
├── .gitignore
├── requirements.txt        # 의존성 목록
├── pyproject.toml         # 프로젝트 설정
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── services/
│       ├── __init__.py
│       └── llm_service.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── notebooks/
    └── experiments.ipynb
```

### 2.5 requirements.txt 관리

```txt
# requirements.txt
# Core LLM APIs
anthropic>=0.18.0
openai>=1.12.0
google-generativeai>=0.4.0

# Web Framework
fastapi>=0.109.0
uvicorn>=0.27.0
httpx>=0.26.0

# Data Processing
pandas>=2.2.0
numpy>=1.26.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.6.0

# Development
pytest>=8.0.0
black>=24.1.0
pylint>=3.0.0
```

### 📚 참고 자료

- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [Conda User Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)

---

## [Chapter 3] GitHub 버전 관리

### 3.1 Git 기본 워크플로우

```mermaid
sequenceDiagram
    participant WD as Working Directory
    participant SA as Staging Area
    participant LR as Local Repository
    participant RR as Remote Repository

    WD->>SA: git add
    SA->>LR: git commit
    LR->>RR: git push
    RR->>LR: git fetch
    LR->>WD: git merge / git pull
```

### 3.2 필수 Git 명령어

```bash
# 저장소 초기화
git init

# 원격 저장소 복제
git clone https://github.com/username/repo.git

# 상태 확인
git status

# 변경사항 스테이징
git add .                    # 모든 파일
git add src/main.py          # 특정 파일

# 커밋
git commit -m "feat: LLM API 연동 기능 추가"

# 원격 저장소 연결
git remote add origin https://github.com/username/repo.git

# 푸시
git push origin main

# 풀
git pull origin main

# 브랜치 생성 및 전환
git checkout -b feature/rag-implementation

# 브랜치 병합
git checkout main
git merge feature/rag-implementation

# 로그 확인
git log --oneline --graph

# 변경사항 되돌리기
git checkout -- filename     # 작업 디렉토리 변경 취소
git reset HEAD filename      # 스테이징 취소
git revert <commit-hash>     # 커밋 되돌리기
```

### 3.3 .gitignore 설정

```gitignore
# .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/

# Environment variables
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
data/
output/
*.pkl
*.h5

# Jupyter
.ipynb_checkpoints/

# API Keys (절대 커밋하지 않음!)
*_credentials.json
*_secret.json
api_keys.txt
```

### 3.4 커밋 메시지 컨벤션

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 종류**:
| Type | 설명 |
|------|------|
| `feat` | 새로운 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `style` | 코드 포맷팅 |
| `refactor` | 코드 리팩토링 |
| `test` | 테스트 추가 |
| `chore` | 빌드, 설정 변경 |

**예시**:
```bash
git commit -m "feat(api): Claude API 연동 기능 구현"
git commit -m "fix(rag): 벡터 검색 결과 정렬 버그 수정"
git commit -m "docs: README 설치 가이드 추가"
```

### 3.5 GitHub Flow

```mermaid
gitGraph
    commit id: "Initial commit"
    branch feature/llm-api
    commit id: "Add Claude client"
    commit id: "Add error handling"
    checkout main
    merge feature/llm-api id: "Merge PR #1"
    branch feature/rag
    commit id: "Add vector store"
    commit id: "Add retriever"
    checkout main
    merge feature/rag id: "Merge PR #2"
    commit id: "Release v1.0"
```

### 📚 참고 자료

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)

---

## [Chapter 4] 환경변수 관리

### 4.1 환경변수의 중요성

```mermaid
graph TB
    subgraph Danger["위험한 방법"]
        D1["api_key = 'sk-abc123...'"]
        D2["GitHub에 푸시"]
        D3["API 키 노출!"]
        D1 --> D2 --> D3
    end

    subgraph Safe["안전한 방법"]
        S1[".env 파일에 저장"]
        S2[".gitignore에 등록"]
        S3["코드에서 환경변수로 로드"]
        S1 --> S2 --> S3
    end

    Danger --> |X| Safe
```

### 4.2 python-dotenv 사용

**.env 파일**:
```env
# .env
# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
MAX_TOKENS=4096
```

**Python에서 사용**:
```python
# config.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수 읽기
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# 필수 환경변수 검증
def validate_env():
    required = ["ANTHROPIC_API_KEY"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {missing}")
```

### 4.3 Pydantic Settings

```python
# settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # API Keys
    anthropic_api_key: str
    openai_api_key: str | None = None
    google_api_key: str | None = None

    # Application
    debug: bool = False
    log_level: str = "INFO"
    max_tokens: int = 4096

    # Database
    database_url: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤 반환"""
    return Settings()


# 사용 예시
settings = get_settings()
print(f"Debug mode: {settings.debug}")
```

### 4.4 보안 체크리스트

```yaml
# 환경변수 보안 체크리스트
pre_commit:
  - .env가 .gitignore에 있는지 확인
  - 하드코딩된 API 키가 없는지 검사
  - git-secrets 또는 pre-commit hooks 설정

development:
  - 개발/프로덕션 환경변수 분리
  - .env.example 템플릿 유지
  - 환경변수 문서화

production:
  - 환경변수를 안전한 저장소에 보관
  - 정기적으로 API 키 로테이션
  - 접근 권한 최소화
```

**.env.example** (git에 커밋):
```env
# .env.example
# 이 파일을 .env로 복사하고 실제 값을 입력하세요

# API Keys (필수)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional
GOOGLE_API_KEY=
DATABASE_URL=

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### 📚 참고 자료

- [python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12 Factor App - Config](https://12factor.net/config)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

## 💻 실습 코드

### 실습 1: 프로젝트 초기화

```bash
# 1. 프로젝트 디렉토리 생성
mkdir llm-architecture-ai
cd llm-architecture-ai

# 2. Git 초기화
git init

# 3. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 4. 기본 패키지 설치
pip install anthropic openai python-dotenv pydantic-settings

# 5. 의존성 저장
pip freeze > requirements.txt

# 6. .gitignore 생성
cat > .gitignore << 'EOF'
.venv/
.env
__pycache__/
*.pyc
.DS_Store
EOF

# 7. .env.example 생성
cat > .env.example << 'EOF'
ANTHROPIC_API_KEY=your_key_here
DEBUG=false
EOF

# 8. .env 생성 (실제 키 입력)
cp .env.example .env
# nano .env 또는 VS Code로 편집

# 9. 초기 커밋
git add .
git commit -m "chore: initial project setup"
```

### 실습 2: 설정 모듈 구현

```python
# src/config.py
"""애플리케이션 설정 관리 모듈"""

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 프로젝트 경로
    base_dir: Path = Path(__file__).parent.parent

    # API Keys
    anthropic_api_key: str
    openai_api_key: str | None = None

    # LLM Settings
    default_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7

    # Application
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤 반환 (캐싱)"""
    return Settings()


def validate_settings() -> None:
    """설정 유효성 검사"""
    settings = get_settings()

    if not settings.anthropic_api_key.startswith("sk-ant-"):
        raise ValueError("Invalid Anthropic API key format")

    print(f"✓ Settings loaded successfully")
    print(f"  - Debug mode: {settings.debug}")
    print(f"  - Default model: {settings.default_model}")
    print(f"  - Max tokens: {settings.max_tokens}")


if __name__ == "__main__":
    validate_settings()
```

### 실습 3: API 키 테스트

```python
# src/test_api.py
"""API 연결 테스트"""

from config import get_settings
import anthropic


def test_claude_connection():
    """Claude API 연결 테스트"""
    settings = get_settings()

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        response = client.messages.create(
            model=settings.default_model,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello! 간단히 응답해 주세요."}
            ]
        )
        print("✓ Claude API 연결 성공!")
        print(f"  응답: {response.content[0].text}")
        return True
    except anthropic.AuthenticationError:
        print("✗ API 키 인증 실패")
        return False
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return False


if __name__ == "__main__":
    test_claude_connection()
```

### 실습 4: VS Code 워크스페이스 설정

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        ".venv": true
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Python: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": ["src.main:app", "--reload"],
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

---

## 📝 과제

### 과제 1: 개발환경 구축 (제출)

1. GitHub 저장소 생성
2. 프로젝트 구조 설정 (src/, tests/, .env 등)
3. 가상환경 및 requirements.txt 구성
4. API 연결 테스트 스크린샷

**제출물**:
- GitHub 저장소 URL
- 프로젝트 구조 스크린샷
- API 테스트 결과 스크린샷

### 과제 2: Git 워크플로우 실습 (제출)

1. main 브랜치에서 feature 브랜치 생성
2. 기능 추가 후 커밋 (컨벤션 준수)
3. GitHub에 푸시 및 PR 생성
4. PR 머지

**제출물**:
- 커밋 히스토리 스크린샷 (`git log --oneline --graph`)
- PR 링크

---

## 🔗 추가 학습 자료

### 공식 문서
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Git Documentation](https://git-scm.com/doc)

### 튜토리얼
- [Real Python - Python Virtual Environments](https://realpython.com/python-virtual-environments-a-primer/)
- [GitHub Learning Lab](https://lab.github.com/)

### 영상
- [VS Code Tips & Tricks (YouTube)](https://www.youtube.com/watch?v=ifTF3ags0XI)
- [Git and GitHub for Beginners (freeCodeCamp)](https://www.youtube.com/watch?v=RGOj5yH7evk)

---

## 🚀 발전 전략 (Development Strategies)

### 전략 1: 건축공학 프로젝트 템플릿 구축

**목표**: 건축공학 데이터 분석 및 LLM 활용을 위한 표준 프로젝트 구조 개발

**실습 단계**:

```bash
# 건축공학 특화 프로젝트 구조 생성
mkdir structural-ai-project
cd structural-ai-project

# 도메인별 디렉토리 구성
mkdir -p {src/{analysis,design,optimization},data/{raw,processed,models},docs,notebooks,tests}

# 프로젝트 초기화
git init
python -m venv .venv
source .venv/bin/activate
```

**건축공학 특화 requirements.txt**:
```txt
# structural-requirements.txt
# LLM APIs
anthropic>=0.18.0
openai>=1.12.0

# 구조 해석 및 데이터 처리
numpy>=1.26.0
pandas>=2.2.0
scipy>=1.11.0
matplotlib>=3.8.0
seaborn>=0.13.0

# 구조공학 라이브러리
openseespy>=3.5.0         # 구조해석
pycalculix>=1.1.4        # FEM 분석
sectionproperties>=3.2.0 # 단면 특성 계산

# 웹 프레임워크
fastapi>=0.109.0
uvicorn>=0.27.0

# 유틸리티
python-dotenv>=1.0.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
```

**실제 적용 예시**:
```python
# src/config.py - 건축공학 프로젝트 설정
from pydantic_settings import BaseSettings
from pathlib import Path

class StructuralSettings(BaseSettings):
    """건축공학 AI 프로젝트 설정"""

    # API Keys
    anthropic_api_key: str

    # 프로젝트 경로
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"

    # 구조해석 설정
    default_steel_grade: str = "SM490"
    safety_factor: float = 1.5
    analysis_type: str = "static"  # static, dynamic, buckling

    # LLM 설정
    default_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.2  # 엔지니어링은 낮은 temperature 권장

    class Config:
        env_file = ".env"
```

**실무 연계 포인트**:
- 구조해석 결과 데이터를 LLM으로 해석하는 파이프라인 구축
- 설계 기준 자동 검토 시스템 개발
- 구조계산서 자동 생성 프로토타입

---

### 전략 2: VS Code 건축공학 워크플로우 최적화

**목표**: 구조공학 코딩 작업에 특화된 VS Code 설정 및 스니펫 구축

**스니펫 생성** (`.vscode/structural.code-snippets`):

```json
{
    "Structural Analysis Function": {
        "prefix": "struct-analysis",
        "body": [
            "def analyze_${1:member}(${2:parameters}):",
            "    \"\"\"${3:구조부재 해석 함수}",
            "    ",
            "    Args:",
            "        ${2:parameters}: ${4:매개변수 설명}",
            "    ",
            "    Returns:",
            "        dict: 해석 결과 (응력, 변형, 안전율 등)",
            "    \"\"\"",
            "    results = {",
            "        'stress': 0.0,  # MPa",
            "        'strain': 0.0,  # mm/mm",
            "        'safety_factor': 0.0,",
            "        'status': 'OK'  # OK, NG, WARNING",
            "    }",
            "    ",
            "    # 해석 로직",
            "    ${5:# TODO: 구현}",
            "    ",
            "    return results"
        ],
        "description": "구조해석 함수 템플릿"
    },

    "LLM Structural Query": {
        "prefix": "llm-struct",
        "body": [
            "def query_structural_llm(question: str, context: dict) -> str:",
            "    \"\"\"구조공학 질문을 LLM에 전달\"\"\"",
            "    from anthropic import Anthropic",
            "    from config import get_settings",
            "    ",
            "    settings = get_settings()",
            "    client = Anthropic(api_key=settings.anthropic_api_key)",
            "    ",
            "    prompt = f\"\"\"",
            "    당신은 구조공학 전문가입니다.",
            "    ",
            "    [구조 데이터]",
            "    {context}",
            "    ",
            "    [질문]",
            "    {question}",
            "    ",
            "    한국 건축구조기준(KBC)을 기반으로 명확하게 답변하세요.",
            "    \"\"\"",
            "    ",
            "    response = client.messages.create(",
            "        model=settings.default_model,",
            "        max_tokens=settings.max_tokens,",
            "        messages=[{\"role\": \"user\", \"content\": prompt}]",
            "    )",
            "    ",
            "    return response.content[0].text"
        ],
        "description": "구조공학 LLM 질의 함수"
    }
}
```

**건축공학 특화 확장 프로그램**:
```bash
# 데이터 시각화
code --install-extension ms-python.vscode-pylance
code --install-extension ms-toolsai.jupyter

# 마크다운 문서화 (계산서 작성)
code --install-extension yzhang.markdown-all-in-one
code --install-extension bierner.markdown-mermaid

# CSV/Excel 데이터 뷰어 (실험 데이터)
code --install-extension mechatroner.rainbow-csv
code --install-extension GrapeCity.gc-excelviewer
```

**실무 팁**:
- 구조계산 스크립트를 Jupyter Notebook으로 문서화
- Mermaid로 구조 시스템 다이어그램 작성
- CSV로 실험 데이터 직접 확인 및 편집

---

### 전략 3: 건축공학 데이터 버전 관리 전략

**목표**: 구조해석 결과, 설계 변경사항, 실험 데이터의 체계적 관리

**Git 브랜치 전략 (구조설계 프로젝트)**:

```bash
# 메인 브랜치 구조
main                # 최종 설계안
├── develop         # 개발 중인 설계안
├── feature/column-design    # 기둥 설계
├── feature/beam-design      # 보 설계
├── feature/foundation       # 기초 설계
└── hotfix/safety-factor     # 긴급 안전율 수정
```

**건축공학 특화 .gitignore**:
```gitignore
# .gitignore (건축공학 프로젝트)

# Python
__pycache__/
*.pyc
.venv/

# 환경변수
.env

# 대용량 데이터 파일 (Git LFS 사용 권장)
*.sap2000
*.etabs
*.midas
data/raw/*.xlsx
data/models/*.h5

# 중간 해석 결과 (재생성 가능)
data/processed/temp_*.csv
output/temp_*.png

# 개인 메모 및 임시 파일
**/notes_personal.md
**/_temp/

# IDE 설정 (개인별 다를 수 있음)
.vscode/settings.json.local
.idea/

# OS
.DS_Store
```

**커밋 컨벤션 (건축공학 프로젝트)**:
```bash
# 구조설계 관련 커밋 예시
git commit -m "feat(column): RC 기둥 설계 자동화 함수 추가"
git commit -m "fix(beam): 전단력 계산 오류 수정"
git commit -m "docs(analysis): OpenSees 모델링 가이드 추가"
git commit -m "refactor(load): 하중 조합 로직 간소화"
git commit -m "test(foundation): 지내력 계산 테스트 케이스 추가"

# LLM 통합 관련
git commit -m "feat(llm): 설계 검토 자동화 Claude API 연동"
git commit -m "feat(rag): 건축구조기준 벡터 DB 구축"
```

**실무 시나리오**:
```bash
# 시나리오: 설계 변경으로 인한 브랜치 작업
git checkout -b feature/seismic-retrofit

# 내진 보강 설계 작업
# 1. 기존 구조 해석
python src/analysis/existing_structure.py

# 2. 보강안 설계
python src/design/seismic_retrofit.py

# 3. 성능 평가
python src/optimization/performance_check.py

# 커밋
git add src/design/seismic_retrofit.py
git commit -m "feat(seismic): 내진 보강 설계 알고리즘 구현"

# 메인 브랜치에 병합 전 검토
git checkout develop
git merge feature/seismic-retrofit

# 테스트 통과 후 main에 병합
git checkout main
git merge develop
git tag -a v2.0-seismic-upgrade -m "내진 보강 설계안 v2.0"
```

---

### 전략 4: 환경변수 기반 다중 프로젝트 관리

**목표**: 여러 건축공학 프로젝트를 효율적으로 전환하며 작업

**프로젝트별 환경 파일 관리**:

```bash
# 프로젝트 구조
~/structural-projects/
├── building-a/
│   ├── .env.building-a
│   └── src/
├── building-b/
│   ├── .env.building-b
│   └── src/
└── shared-config/
    └── .env.template
```

**환경 전환 스크립트** (`switch_env.sh`):
```bash
#!/bin/bash
# switch_env.sh - 프로젝트 환경 전환 스크립트

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "사용법: ./switch_env.sh [building-a|building-b]"
    exit 1
fi

# 환경 파일 복사
if [ -f ".env.$PROJECT_NAME" ]; then
    cp .env.$PROJECT_NAME .env
    echo "✓ 환경 전환 완료: $PROJECT_NAME"

    # 가상환경 활성화
    source .venv/bin/activate

    # 프로젝트 정보 출력
    python -c "
from config import get_settings
settings = get_settings()
print(f'프로젝트: {settings.project_name}')
print(f'구조 타입: {settings.structure_type}')
print(f'설계 기준: {settings.design_code}')
    "
else
    echo "✗ 오류: .env.$PROJECT_NAME 파일이 없습니다"
    exit 1
fi
```

**다중 프로젝트 설정 클래스**:
```python
# src/multi_project_config.py
from enum import Enum
from pydantic_settings import BaseSettings

class ProjectType(str, Enum):
    """프로젝트 타입"""
    BUILDING_A = "building-a"
    BUILDING_B = "building-b"
    BRIDGE = "bridge-project"

class StructuralProjectSettings(BaseSettings):
    """프로젝트별 구조 설정"""

    # 프로젝트 식별
    project_name: str
    project_type: ProjectType

    # 구조 정보
    structure_type: str  # RC, Steel, Composite
    design_code: str = "KBC2016"

    # 건물 기본 정보
    building_height: float  # m
    num_stories: int
    seismic_zone: str = "I"  # I(최저) ~ II(최고)

    # API Keys
    anthropic_api_key: str

    # LLM 설정
    use_llm_review: bool = True
    llm_model: str = "claude-3-5-sonnet-20241022"

    class Config:
        env_file = ".env"

    def get_project_summary(self) -> str:
        """프로젝트 요약 정보"""
        return f"""
        프로젝트명: {self.project_name}
        구조 타입: {self.structure_type}
        층수: {self.num_stories}층 (높이 {self.building_height}m)
        내진 등급: {self.seismic_zone}
        설계 기준: {self.design_code}
        """
```

**실무 활용**:
```bash
# 프로젝트 A 작업
./switch_env.sh building-a
python src/analysis/main.py

# 프로젝트 B로 전환
./switch_env.sh building-b
python src/analysis/main.py
```

---

### 전략 5: LLM 기반 설계 검토 자동화 실습

**목표**: API 키 관리 학습을 넘어 실제 구조설계 검토 자동화 구현

**구조설계 검토 시스템 구현**:

```python
# src/design_review/llm_reviewer.py
"""LLM 기반 구조설계 자동 검토 시스템"""

from anthropic import Anthropic
from config import get_settings
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DesignResult:
    """설계 결과 데이터"""
    member_type: str  # "column", "beam", "foundation"
    member_id: str
    design_strength: float  # kN or kN·m
    required_strength: float  # kN or kN·m
    safety_factor: float
    utilization_ratio: float  # 사용률 (%)
    code_check: str  # "PASS", "FAIL", "WARNING"

class StructuralDesignReviewer:
    """구조설계 자동 검토 클래스"""

    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.default_model

    def review_design(self, design_results: List[DesignResult]) -> Dict:
        """설계 결과 종합 검토"""

        # 1. 데이터 요약
        summary = self._summarize_results(design_results)

        # 2. LLM 검토 프롬프트 생성
        prompt = self._create_review_prompt(summary, design_results)

        # 3. LLM 호출
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.2,  # 엔지니어링 검토는 낮은 온도
            messages=[{"role": "user", "content": prompt}]
        )

        review_text = response.content[0].text

        return {
            "summary": summary,
            "llm_review": review_text,
            "recommendations": self._extract_recommendations(review_text)
        }

    def _summarize_results(self, results: List[DesignResult]) -> Dict:
        """설계 결과 통계 요약"""
        total = len(results)
        passed = sum(1 for r in results if r.code_check == "PASS")
        failed = sum(1 for r in results if r.code_check == "FAIL")
        warnings = sum(1 for r in results if r.code_check == "WARNING")

        avg_utilization = sum(r.utilization_ratio for r in results) / total
        max_utilization = max(results, key=lambda r: r.utilization_ratio)

        return {
            "total_members": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "pass_rate": (passed / total) * 100,
            "avg_utilization": avg_utilization,
            "max_utilization_member": {
                "id": max_utilization.member_id,
                "ratio": max_utilization.utilization_ratio
            }
        }

    def _create_review_prompt(self, summary: Dict, results: List[DesignResult]) -> str:
        """LLM 검토 프롬프트 생성"""

        failed_members = [r for r in results if r.code_check == "FAIL"]
        warning_members = [r for r in results if r.code_check == "WARNING"]

        prompt = f"""
당신은 한국 건축구조기준(KBC 2016)을 준수하는 전문 구조엔지니어입니다.
다음 구조설계 결과를 검토하고 전문적인 의견을 제시하세요.

## 설계 결과 요약
- 전체 부재 수: {summary['total_members']}개
- 검토 통과: {summary['passed']}개 ({summary['pass_rate']:.1f}%)
- 검토 실패: {summary['failed']}개
- 경고: {summary['warnings']}개
- 평균 사용률: {summary['avg_utilization']:.1f}%
- 최대 사용률 부재: {summary['max_utilization_member']['id']} ({summary['max_utilization_member']['ratio']:.1f}%)

## 검토 실패 부재 상세
"""

        for member in failed_members:
            prompt += f"""
- {member.member_type} {member.member_id}:
  - 요구 강도: {member.required_strength:.2f} kN
  - 설계 강도: {member.design_strength:.2f} kN
  - 사용률: {member.utilization_ratio:.1f}%
  - 상태: {member.code_check}
"""

        prompt += """

## 요청사항
1. 설계 결과의 전반적인 안전성 평가
2. 검토 실패 부재에 대한 개선 방안 (구체적인 수치 제시)
3. 경고 부재에 대한 주의사항
4. 경제성 관점에서의 최적화 가능성
5. KBC 2016 기준 준수 여부 확인

명확하고 실무적인 답변을 부탁드립니다.
"""

        return prompt

    def _extract_recommendations(self, review_text: str) -> List[str]:
        """검토 결과에서 권장사항 추출"""
        # 간단한 파싱 로직 (실제로는 더 정교한 파싱 필요)
        recommendations = []
        lines = review_text.split('\n')

        for line in lines:
            if '권장' in line or '개선' in line or '변경' in line:
                recommendations.append(line.strip())

        return recommendations


# 사용 예시
if __name__ == "__main__":
    # 샘플 설계 결과 생성
    design_results = [
        DesignResult(
            member_type="column",
            member_id="C1-1F",
            design_strength=1200.0,
            required_strength=980.0,
            safety_factor=1.5,
            utilization_ratio=81.7,
            code_check="PASS"
        ),
        DesignResult(
            member_type="beam",
            member_id="B1-2F",
            design_strength=450.0,
            required_strength=520.0,
            safety_factor=1.5,
            utilization_ratio=115.6,
            code_check="FAIL"
        ),
        # ... 더 많은 부재 데이터
    ]

    reviewer = StructuralDesignReviewer()
    review_report = reviewer.review_design(design_results)

    print("=== 설계 검토 보고서 ===")
    print(review_report["llm_review"])
    print("\n=== 권장사항 ===")
    for rec in review_report["recommendations"]:
        print(f"- {rec}")
```

**실습 과제**:
1. 본인의 구조설계 프로젝트 데이터를 입력하여 검토 실행
2. LLM 응답 품질 평가 (정확성, 실무 적용 가능성)
3. 프롬프트 개선을 통한 답변 품질 향상

---

### 전략 6: 건축구조기준 RAG 시스템 준비

**목표**: Week 6-7의 RAG 학습을 위한 사전 환경 구축 및 데이터 수집

**데이터 수집 및 구조화**:

```bash
# 프로젝트 내 데이터 디렉토리 생성
mkdir -p data/kbc_standards/{pdf,text,vector_db}

# 한국 건축구조기준 문서 수집 (예시)
data/kbc_standards/
├── pdf/
│   ├── KBC2016_철근콘크리트구조.pdf
│   ├── KBC2016_강구조.pdf
│   └── KBC2016_내진설계.pdf
├── text/
│   └── extracted/  # PDF에서 추출한 텍스트
└── vector_db/
    └── (향후 chromadb 또는 faiss 데이터)
```

**PDF 텍스트 추출 스크립트**:
```python
# src/data_prep/extract_kbc.py
"""건축구조기준 PDF 텍스트 추출"""

import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path, output_path: Path):
    """PDF에서 텍스트 추출 및 저장"""

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        text_content = []
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            text_content.append(f"=== Page {page_num} ===\n{text}\n")

        # 추출된 텍스트 저장
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as out:
            out.writelines(text_content)

        print(f"✓ 추출 완료: {pdf_path.name} → {output_path.name}")
        print(f"  총 페이지 수: {len(reader.pages)}")

# 실행 예시
if __name__ == "__main__":
    pdf_dir = Path("data/kbc_standards/pdf")
    text_dir = Path("data/kbc_standards/text/extracted")

    for pdf_file in pdf_dir.glob("*.pdf"):
        output_file = text_dir / f"{pdf_file.stem}.txt"
        extract_text_from_pdf(pdf_file, output_file)
```

**메타데이터 관리**:
```python
# src/data_prep/kbc_metadata.py
"""건축구조기준 메타데이터 관리"""

from dataclasses import dataclass
from typing import List
import json

@dataclass
class KBCDocument:
    """KBC 문서 메타데이터"""
    doc_id: str
    title: str
    category: str  # "RC", "Steel", "Seismic", "Foundation"
    version: str
    file_path: str
    page_count: int
    tags: List[str]

# 메타데이터 관리
kbc_documents = [
    KBCDocument(
        doc_id="kbc2016_rc",
        title="철근콘크리트구조 설계기준",
        category="RC",
        version="KBC 2016",
        file_path="data/kbc_standards/pdf/KBC2016_철근콘크리트구조.pdf",
        page_count=250,
        tags=["reinforced concrete", "beam", "column", "flexure", "shear"]
    ),
    # 추가 문서들...
]

# JSON으로 저장
def save_metadata():
    metadata = [vars(doc) for doc in kbc_documents]
    with open("data/kbc_standards/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
```

**실습 과제**:
- 건축구조기준 PDF 수집 (학교 도서관, 건축구조기준센터)
- PDF 텍스트 추출 및 정제
- Week 6에서 활용할 데이터셋 준비

---

### 전략 7: 통합 개발환경 검증 체크리스트

**목표**: 2주차 학습 내용 종합 점검 및 실무 준비도 확인

**자가 점검 스크립트** (`check_environment.py`):

```python
# check_environment.py
"""개발환경 종합 검증 스크립트"""

import sys
import os
from pathlib import Path
import subprocess

class EnvironmentChecker:
    """개발환경 검증 클래스"""

    def __init__(self):
        self.passed = []
        self.failed = []

    def check_python_version(self):
        """Python 버전 확인"""
        version = sys.version_info
        if version >= (3, 10):
            self.passed.append(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.failed.append(f"✗ Python 버전 낮음: {version.major}.{version.minor}")

    def check_venv(self):
        """가상환경 활성화 확인"""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.passed.append("✓ 가상환경 활성화됨")
        else:
            self.failed.append("✗ 가상환경 비활성화 상태")

    def check_git(self):
        """Git 설치 및 저장소 확인"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.passed.append(f"✓ {result.stdout.strip()}")

                # Git 저장소 확인
                if Path(".git").exists():
                    self.passed.append("✓ Git 저장소 초기화됨")
                else:
                    self.failed.append("✗ Git 저장소 없음 (git init 필요)")
            else:
                self.failed.append("✗ Git 미설치")
        except FileNotFoundError:
            self.failed.append("✗ Git 미설치")

    def check_env_file(self):
        """.env 파일 확인"""
        if Path(".env").exists():
            self.passed.append("✓ .env 파일 존재")

            # 필수 환경변수 확인
            from dotenv import load_dotenv
            load_dotenv()

            required_vars = ["ANTHROPIC_API_KEY"]
            missing = [var for var in required_vars if not os.getenv(var)]

            if not missing:
                self.passed.append("✓ 필수 환경변수 설정됨")
            else:
                self.failed.append(f"✗ 누락된 환경변수: {missing}")
        else:
            self.failed.append("✗ .env 파일 없음")

    def check_gitignore(self):
        """.gitignore 확인"""
        if Path(".gitignore").exists():
            with open(".gitignore") as f:
                content = f.read()

            critical_entries = [".env", ".venv", "__pycache__"]
            missing = [entry for entry in critical_entries if entry not in content]

            if not missing:
                self.passed.append("✓ .gitignore 올바르게 설정됨")
            else:
                self.failed.append(f"✗ .gitignore에 추가 필요: {missing}")
        else:
            self.failed.append("✗ .gitignore 파일 없음")

    def check_packages(self):
        """필수 패키지 설치 확인"""
        required_packages = [
            "anthropic",
            "openai",
            "fastapi",
            "pydantic",
            "python-dotenv"
        ]

        installed = []
        missing = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                installed.append(package)
            except ImportError:
                missing.append(package)

        if not missing:
            self.passed.append(f"✓ 필수 패키지 설치됨 ({len(installed)}개)")
        else:
            self.failed.append(f"✗ 미설치 패키지: {missing}")

    def check_project_structure(self):
        """프로젝트 구조 확인"""
        required_dirs = ["src", "tests", "data"]
        existing = [d for d in required_dirs if Path(d).exists()]
        missing = [d for d in required_dirs if d not in existing]

        if len(existing) >= 2:
            self.passed.append(f"✓ 프로젝트 구조 존재 ({', '.join(existing)})")

        if missing:
            self.failed.append(f"✗ 권장 디렉토리 없음: {missing}")

    def check_vscode(self):
        """VS Code 설정 확인"""
        vscode_dir = Path(".vscode")
        if vscode_dir.exists():
            settings_file = vscode_dir / "settings.json"
            if settings_file.exists():
                self.passed.append("✓ VS Code 설정 파일 존재")
            else:
                self.failed.append("✗ .vscode/settings.json 없음")
        else:
            self.failed.append("✗ .vscode/ 디렉토리 없음")

    def run_all_checks(self):
        """모든 검증 실행"""
        print("=" * 50)
        print("개발환경 검증 시작...")
        print("=" * 50)

        self.check_python_version()
        self.check_venv()
        self.check_git()
        self.check_env_file()
        self.check_gitignore()
        self.check_packages()
        self.check_project_structure()
        self.check_vscode()

        # 결과 출력
        print("\n[통과한 항목]")
        for item in self.passed:
            print(f"  {item}")

        if self.failed:
            print("\n[실패한 항목]")
            for item in self.failed:
                print(f"  {item}")

        print("\n" + "=" * 50)
        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0
        print(f"검증 결과: {len(self.passed)}/{total} 통과 ({pass_rate:.1f}%)")
        print("=" * 50)

        return len(self.failed) == 0


if __name__ == "__main__":
    checker = EnvironmentChecker()
    success = checker.run_all_checks()

    if success:
        print("\n🎉 모든 검증 통과! 개발 준비 완료!")
        sys.exit(0)
    else:
        print("\n⚠️  일부 항목 수정 필요")
        sys.exit(1)
```

**실행 및 활용**:
```bash
# 개발환경 검증 실행
python check_environment.py

# CI/CD 파이프라인에 통합
# .github/workflows/check-env.yml
```

---

## 📌 발전 전략 요약

| 전략 | 핵심 목표 | 실무 연계 |
|------|----------|----------|
| 1. 프로젝트 템플릿 | 건축공학 특화 구조 | 실제 설계 프로젝트 구조화 |
| 2. VS Code 최적화 | 구조공학 워크플로우 | 코딩 효율성 향상 |
| 3. 버전 관리 전략 | 설계 변경사항 추적 | 설계 이력 관리 |
| 4. 다중 프로젝트 | 환경 전환 자동화 | 여러 건물 동시 작업 |
| 5. LLM 설계 검토 | 자동화된 검토 시스템 | 설계 품질 향상 |
| 6. RAG 시스템 준비 | 구조기준 데이터 수집 | Week 6-7 사전 준비 |
| 7. 환경 검증 | 종합 점검 자동화 | 개발 준비도 확인 |

**다음 주 연계**:
- Week 3: LLM API 실전 활용 (전략 5의 설계 검토 시스템 확장)
- Week 6-7: RAG 시스템 구축 (전략 6의 데이터 활용)
- Week 11-12: 최종 프로젝트 (모든 전략 통합)

---
