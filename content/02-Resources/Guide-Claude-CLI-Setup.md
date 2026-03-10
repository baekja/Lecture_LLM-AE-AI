---
draft: true
tags:
  - lecture/LLM
  - 2026-1
created: 2026-03-03
---

# Claude Code (CLI) 설치 가이드

> [!ref] 공식 문서
> - [Claude Code 공식 설치 가이드](https://code.claude.com/docs/en/setup)
> - [Claude Code GitHub](https://github.com/anthropics/claude-code)

---

## 1단계: Anthropic 계정 가입 및 요금제 선택

### 계정 가입

1. [claude.ai](https://claude.ai) 접속
2. **Sign up** 클릭
3. 이메일 또는 Google 계정으로 가입
4. 이메일 인증 완료

### 요금제 선택

> [!tip] Pro 요금제 권장
> 이 수업에서는 Claude Code를 매주 사용하므로 **Pro 이상** 가입을 권장합니다.

| 요금제 | 월 비용 | Claude Code | 사용량 | 추천 대상 |
|--------|--------|:-----------:|--------|----------|
| Free | 무료 | ❌ | 기본 | 체험용 |
| **Pro** | **$20/월** | **✅** | **5배** | **수업 수강생 (권장)** |
| Max | $100/월~ | ✅ | 20배+ | 헤비 유저 |

**가입 방법:**
1. [claude.ai](https://claude.ai) 로그인
2. 좌측 하단 **Upgrade to Pro** 클릭
3. 결제 정보 입력 (해외 결제 가능 카드 필요)
4. 완료 후 **Claude Pro** 배지 확인

---

## 2단계: Claude Code 설치

> [!question] 내 운영체제는?
> 아래에서 자신의 OS에 맞는 방법을 따라주세요.

### macOS (권장 방법)

#### 방법 A: 공식 설치 스크립트 (가장 간단)

터미널을 열고 아래 명령어를 복사-붙여넣기합니다:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

> [!success] 이 방법이 가장 간단합니다
> Node.js 설치가 필요 없고, 자동 업데이트도 지원됩니다.

#### 방법 B: Homebrew 사용

Homebrew가 이미 설치되어 있다면:

```bash
brew install --cask claude-code
```

### Windows

> [!warning] Windows 사용자 필독
> Claude Code는 기본적으로 **Unix 계열** 터미널에서 동작합니다. Windows에서는 아래 두 가지 방법 중 하나를 사용하세요.

#### 방법 A: WSL (Windows Subsystem for Linux) — 권장

1. **PowerShell을 관리자 권한으로 실행** (시작 메뉴 → "PowerShell" 검색 → 우클릭 → 관리자로 실행)

2. WSL 설치:
```powershell
wsl --install
```

3. 컴퓨터 **재시작**

4. Ubuntu 터미널이 자동으로 열리면, 사용자 이름과 비밀번호 설정

5. Ubuntu 터미널에서 Claude Code 설치:
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

#### 방법 B: npm 사용 (Node.js 필요)

1. [Node.js 공식 사이트](https://nodejs.org/)에서 **LTS 버전** (v18 이상) 다운로드 및 설치

2. 설치 확인:
```bash
node --version
# v18.x.x 이상이어야 합니다
```

3. Claude Code 설치:
```bash
npm install -g @anthropic-ai/claude-code
```

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

---

## 3단계: 최초 실행 및 인증

1. 터미널에서 아무 폴더에서나 실행:
```bash
claude
```

2. **브라우저가 자동으로 열리며** Anthropic 로그인 페이지가 나타남

3. Pro 요금제로 가입한 계정으로 **로그인**

4. "Allow Claude Code" 버튼 클릭하여 **인증 승인**

5. 터미널로 돌아가면 Claude Code가 활성화됨:
```
╭──────────────────────────────────╮
│ Welcome to Claude Code!          │
│ Type your request...             │
╰──────────────────────────────────╯
```

> [!success] 설치 완료!
> 이제 자연어로 코딩 요청을 할 수 있습니다.

---

## 4단계: 동작 확인

아래 명령을 입력하여 정상 동작을 확인하세요:

```
> 현재 폴더에 hello.py를 만들어줘. "Hello, LLM-AE-AI!" 를 출력하는 코드로.
```

Claude Code가 파일을 생성하고 코드를 작성하면 성공입니다! 🎉

---

## 자주 묻는 질문 (FAQ)

### Q. 결제가 안 돼요
- 해외 결제가 가능한 **VISA/Mastercard** 카드가 필요합니다.
- 체크카드도 해외 결제 설정이 되어 있다면 사용 가능합니다.
- 카드사 앱에서 **해외 결제 차단 해제**를 확인하세요.

### Q. `claude` 명령어를 찾을 수 없다고 나와요
- 터미널을 **완전히 종료 후 재시작**해보세요.
- `source ~/.bashrc` 또는 `source ~/.zshrc` 를 실행해보세요.
- 그래도 안 되면 npm 방법으로 재설치: `npm install -g @anthropic-ai/claude-code`

### Q. WSL 설치 후 Ubuntu가 안 열려요
- Windows 업데이트를 최신으로 진행 후 재시작하세요.
- Microsoft Store에서 **Ubuntu** 앱을 검색하여 직접 설치하세요.

### Q. 무료 플랜으로도 수업을 따라갈 수 있나요?
- Claude Code는 **유료 플랜(Pro 이상)** 에서만 사용 가능합니다.
- API 크레딧 결제 방식도 가능하나, Pro 구독이 가장 경제적입니다.

---

## 유용한 Claude Code 기본 명령어

| 명령 | 설명 |
|------|------|
| `claude` | Claude Code 시작 |
| `claude --version` | 버전 확인 |
| `claude --help` | 도움말 |
| `/help` | 대화 중 도움말 |
| `/clear` | 대화 초기화 |
| `Ctrl + C` | 현재 작업 중단 |
| `Ctrl + D` | Claude Code 종료 |

---

> [!action] 체크리스트
> - [ ] Anthropic 계정 가입 완료
> - [ ] Pro 요금제 가입 완료
> - [ ] Claude Code 설치 완료
> - [ ] `claude` 명령어로 최초 실행 + 인증 완료
> - [ ] 테스트 코드 생성 확인
