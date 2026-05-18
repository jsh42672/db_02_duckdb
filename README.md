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
