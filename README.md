# 데이터베이스 2026

# DuckDB

https://nano5.notion.site/DuckDB-350daf211d4280189a1ecaa5ca2da47b?source=copy_link

<img width="536" height="640" alt="image" src="https://github.com/user-attachments/assets/65f1cb1b-2492-4cce-b546-79a33a8e2ba4" />

---

# 🚀 db_02_duckdb (Flet + DuckDB + uv)

DuckDB를 사용하여 데이터를 처리하는 Flet 프로젝트

## 🛠️ uv 설치 (최초 1회)
이미 설치되어 있다면 안해도 됨

Windows에 설치
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS/Linux에 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🏗️ 의존성 설치
프로젝트 폴더에서 아래 명령어를 실행하면 `.venv` 생성되고 패키지 설치됨

```bash
uv sync
```

## ▶️ 실행 및 핫 리로드 (Run & Hot Reload)

```bash
uv run flet run -r
```

문제가 있을 경우에는 web browser 모드로 실행

```bash
uv run flet run --web -r
```

---

# 🃏 Term Project: YGO Deck Lab

YGOProDeck 공개 API 데이터를 DuckDB에 저장하고, Flet GUI에서 카드 검색/상세 조회/덱 빌더를 제공하는 데이터베이스 텀 프로젝트입니다.

## 실행

```bash
uv sync
uv run flet run -w -p 8550 main.py
```

실행 후 브라우저에서 `http://127.0.0.1:8550`으로 접속합니다.

## 주요 파일

- `main.py`: Flet entry point 및 화면 조립
- `app/bootstrap.py`: provider, repository, service 의존성 조립
- `domain/`: 카드/덱/시드 DTO, 상수, 규칙
- `provider/ygoprodeck/`: API 클라이언트, 캐시, fallback, 매핑
- `repository/duckdb/`: DuckDB 조회/저장/시딩 구현
- `service/`: 검색, 상세, 덱 검증/저장, 초기화 비즈니스 로직
- `views/`: 검색/덱 빌더/저장된 덱 화면 구성
- `sql/schema.sql`: 테이블 생성 스키마
- `sql/sample_queries.sql`: 설계서에 넣을 주요 JOIN 쿼리
- `docs/ygo_erd_crowsfeet.html`: Crow's Foot ERD
- `docs/design_notes.md`: 설계서 작성용 메모

## 데이터

- 최초 실행 시 `data/ygo_cards.duckdb` 생성
- API 응답은 `data/ygo_cards_cache.json`에 캐시
- 네트워크가 막힌 경우에도 최소 예비 데이터로 앱 실행 가능
