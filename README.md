# YGO Deck Lab

YGO Deck Lab은 유희왕 카드 데이터를 DuckDB에 저장하고 Flet GUI에서 카드 검색, 상세 조회, 덱 구성, 금지 제한 검증, 저장된 덱 조회/삭제를 수행하는 데이터베이스 텀 프로젝트입니다.

## 주요 기능

- YGOPRODeck 공개 API 또는 캐시 데이터를 이용한 카드 데이터 초기화
- 카드명, 효과 텍스트, 카드 종류, 속성, 종족, 아키타입, 공격력/수비력 조건 검색
- 카드 이미지, 가격, 수록 세트, 금지 제한 정보를 포함한 상세 조회
- MAIN / EXTRA / SIDE 덱 구성 및 카드 수량 검증
- TCG / OCG / GOAT 포맷 기준 금지 제한 검증
- 덱 저장, 저장된 덱 상세 조회, 덱 삭제

## 사용 기술

- Python
- Flet
- DuckDB
- pandas
- uv

## 실행 방법

```bash
uv sync
uv run flet run main.py
```

웹 브라우저로 확인해야 할 때만 다음 명령을 사용합니다.

```bash
uv run flet run -w -p 8550 main.py
```

## 프로젝트 구조

```text
app/                  의존성 조립 및 설정
domain/               DTO, 상수, 규칙
provider/             YGOPRODeck API, 캐시, fallback 데이터 처리
repository/duckdb/    DuckDB 연결, SQL 실행, Repository 구현
service/              카드 검색, 상세 조회, 덱 검증, 저장 비즈니스 로직
views/                Flet 화면 구성
sql/                  DuckDB DDL 및 주요 Join 쿼리
docs/mermaid/         ERD, Architecture, Sequence Diagram 원본
tests/                Repository 및 Service 테스트
```

## 데이터베이스 설계

주요 엔터티는 `card`, `deck`이며, 주요 관계 테이블은 `deck_card`, `card_archetype`, `card_set_entry`, `ban_status`, `card_price`, `card_image`입니다.

카드 종류, 속성, 종족, 아키타입, 수록 세트, 레어도, 금지 제한 포맷, 가격 출처처럼 반복되는 값은 별도 테이블로 분리하여 중복을 줄였습니다.

DDL은 `sql/schema.sql`에 정리되어 있고, 세 개 이상의 테이블을 사용하는 Join 예시는 `sql/sample_queries.sql`에서 확인할 수 있습니다.

## 설계 자료

- `docs/mermaid/01_erd_crowsfeet.mmd`: Crow's Foot ERD
- `docs/mermaid/02_architecture.mmd`: 전체 아키텍처
- `docs/mermaid/03_repository_class.mmd`: Repository Interface 구조
- `docs/mermaid/04_seq_uc01_initialize.mmd` ~ `09_seq_uc06_saved_deck_query_delete.mmd`: 구현 Use Case별 Sequence Diagram
- `docs/ygo_deck_lab_erd_import.sql`: VSCode ERD Editor import용 SQL

## 테스트

```bash
uv run python -m unittest discover
```
