import flet as ft
import duckdb
# import random


def main(page: ft.Page):
    page.title = "Asset List"
    page.padding = 16
    page.window.width = 450
    page.window.height = 530

    # 데이터베이스 접속
    con = duckdb.connect("data/finance.db")
    
    # 테이블 생성
    con.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            ticker VARCHAR PRIMARY KEY,
            name VARCHAR,
            type VARCHAR
        )
    """)

    # assets.csv 파일을 읽어서 테이블에 추가
    con.execute("""
        INSERT OR IGNORE INTO assets 
        SELECT * FROM read_csv_auto('data/assets.csv')
    """)

    print("데이터베이스 저장 완료")

    snack_bar = ft.SnackBar(content=ft.Text("데이터베이스 저장 완료"))
    page.overlay.append(snack_bar)
    snack_bar.open = True

    # DB로부터 Pandas DataFrame으로 읽어오기
    df = con.execute("SELECT * FROM assets").df()

    def get_data(filter_query=""):
        if filter_query:
            query = """
                SELECT * FROM assets 
                WHERE name ILIKE ?
                OR ticker ILIKE ?
            """
            search_str = f'%{filter_query}%'
            return con.execute(query, [search_str, search_str,]).df()
        else:
            return con.execute("SELECT * FROM assets").df()

    df = get_data()

    # 너비 비율 계산
    # lengths = {col: int(max(df[col].astype(str).map(len).max(), len(col))) for col in df.columns}
    lengths = {}
    for col in df.columns:
        # 컬럼명 자체의 길이와 데이터들 중 최대 길이
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        lengths[col] = int(max_len)

    # 헤더
    sticky_header = ft.Row(
        controls=[
            ft.Container(width=40),
            *[ft.Container(
                ft.Text(col.upper(), weight="bold", size=16), 
                expand=lengths[col], 
            ) 
            for col in df.columns]
        ],
    )

    # 필터링을 반영한 row 생성 함수
    def create_rows(current_df):
        rows = []
        for _, row in current_df.iterrows():
            # 배경색 랜덤 생성

            # # hex_color = "".join(f"{random.randint(60, 255):02x}" for _ in range(3))
            # r = random.randint(60, 255)
            # g = random.randint(60, 255)
            # b = random.randint(60, 255)
            # hex_color = f"{r:02x}{g:02x}{b:02x}"

            # 이름의 각 글자 유니코드 값을 더해서 고유 숫자 생성
            name_sum = sum(ord(char) for char in str(row['name']))
            
            # Red, Green, Blue 값 (0~255) 결정
            # 각 값에 다른 소수를 곱해서 색상이 겹치지 않도록 해줌
            # 196으로 나눈 나머지(0~195)에 60을 더하면 최대 255 (0xff)
            r = (name_sum * 13) % 196 + 60
            g = (name_sum * 17) % 196 + 60
            b = (name_sum * 19) % 196 + 60
            
            hex_color = f"{r:02x}{g:02x}{b:02x}"
            
            img_column = ft.Container(
                content=ft.Image(
                    # 종목명 앞에서부터 5글자를 사용해서 place holder 이미지 요청
                    src=f"https://placehold.jp/30/{hex_color}/000/150x150.png?text={row['name'][:5]}",
                    width=30,
                    height=30,
                ),
                width=30,
                height=30,
                border_radius=15, # 반지름을 줘서 원형 마스크 생성
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )

            rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(img_column, width=40, alignment=ft.Alignment.CENTER),
                        *[ft.Text(str(row[col]), expand=lengths[col]) for col in current_df.columns]
                    ]),
                    height=40,
                )
            )
        return rows

    # 스크롤 되는 영역에 create_rows() 함수 결과 지정
    scrollable_data = ft.Column(
        controls=create_rows(df),
        scroll=ft.ScrollMode.ALWAYS,
        expand=True
    )

    # 필터링 이벤트 핸들러
    def on_filter_change(e):
        # 입력된 텍스트로 DB 검색
        filtered_df = get_data(e.control.value)
        scrollable_data.controls = create_rows(filtered_df)
        page.update()

    # 필터 입력
    filter_input = ft.Container(
        ft.TextField(
            label="종목 또는 티커 검색",
            prefix_icon=ft.Icons.SEARCH,
            hint_text="종목명이나 티커를 입력하세요",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_700),
            expand=True,
            on_change=on_filter_change,
        )
    )

    page.add(
        filter_input,
        sticky_header,
        ft.Divider(),
        scrollable_data
    )


if __name__ == "__main__":
    ft.run(main)