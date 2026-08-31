#!/bin/bash
# 클로드 코드 실행 스크립트
# 사용법:
#   ./run_claude.sh                  대화형 실행
#   ./run_claude.sh "질문 내용"       한 번만 물어보고 종료
#   ./run_claude.sh -c               직전 대화 이어서 실행

set -e

# 프로젝트 디렉토리(이 스크립트가 있는 위치)로 이동
cd "$(dirname "$0")"

CLAUDE_BIN="$HOME/.local/bin/claude"
if [ ! -x "$CLAUDE_BIN" ]; then
    CLAUDE_BIN="$(command -v claude || true)"
fi

if [ -z "$CLAUDE_BIN" ]; then
    echo "claude 명령을 찾을 수 없습니다. 설치 후 다시 실행하세요." >&2
    exit 1
fi

exec "$CLAUDE_BIN" "$@"
