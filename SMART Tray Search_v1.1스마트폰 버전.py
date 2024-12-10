import asyncio
from aiohttp import ClientSession
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.checkbox import CheckBox
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import mainthread
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import os
import csv

# 한글 폰트 등록
LabelBase.register(name='NotoSans', fn_regular='C:\\Users\\User\\Downloads\\Noto_Sans_KR\\NotoSansKR-VariableFont_wght.ttf')

# 화면 크기 설정
Window.size = (360, 640)

class KoreanSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'NotoSans'

class SearchEngineSelectorApp(App):
    def build(self):
        self.title = "SMART Tray Search_v_1.1"
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 로고 이미지 삽입
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
        self.logo_image = Image(source=logo_path, size_hint=(1, 0.2))
        self.main_layout.add_widget(self.logo_image)

        # 검색 엔진 선택 레이블 및 스피너
        self.label = Label(text="검색 엔진을 선택하세요:", font_size=18, font_name='NotoSans', size_hint=(1, 0.05))
        self.main_layout.add_widget(self.label)
        
        self.engine_spinner = Spinner(
            text='네이버',
            values=('네이버', '다음'),
            option_cls=KoreanSpinnerOption,
            size_hint=(1, 0.1),
            height=44,
            font_name='NotoSans'
        )
        self.main_layout.add_widget(self.engine_spinner)

        # 검색어 입력 레이블 및 텍스트 입력
        self.search_label = Label(text="검색할 내용을 입력하세요:", font_size=18, font_name='NotoSans', size_hint=(1, 0.05))
        self.main_layout.add_widget(self.search_label)

        self.search_input = TextInput(size_hint=(1, 0.1), height=44, font_name='NotoSans')
        self.main_layout.add_widget(self.search_input)

        # 추가 검색어 수식어 입력 레이블 및 텍스트 입력
        self.suffix_label = Label(text="추가 검색어 입력:", font_size=18, font_name='NotoSans', size_hint=(1, 0.05))
        self.main_layout.add_widget(self.suffix_label)

        self.suffix_input = TextInput(size_hint=(1, 0.1), height=44, font_name='NotoSans')
        self.main_layout.add_widget(self.suffix_input)

        # 검색 옵션 및 필터링 옵션 레이아웃
        self.option_layout = BoxLayout(size_hint=(1, 0.1), height=44, spacing=10)
        
        self.image_checkbox = CheckBox(size_hint=(0.1, 1))
        self.image_label = Label(text="이미지", font_size=18, font_name='NotoSans', size_hint=(0.4, 1))
        self.option_layout.add_widget(self.image_checkbox)
        self.option_layout.add_widget(self.image_label)
        
        self.content_checkbox = CheckBox(size_hint=(0.1, 1))
        self.content_label = Label(text="내용", font_size=18, font_name='NotoSans', size_hint=(0.4, 1))
        self.option_layout.add_widget(self.content_checkbox)
        self.option_layout.add_widget(self.content_label)

        self.filter_spinner = Spinner(
            text='전체',
            values=('전체', '뉴스', '블로그', '카페'),
            option_cls=KoreanSpinnerOption,
            size_hint=(1, 1),
            height=44,
            font_name='NotoSans'
        )
        self.option_layout.add_widget(self.filter_spinner)

        self.main_layout.add_widget(self.option_layout)

        # 날짜 필터링 레이블 및 TextInput
        self.date_filter_label = Label(text="날짜 필터링:", font_size=18, font_name='NotoSans', size_hint=(1, 0.05))
        self.main_layout.add_widget(self.date_filter_label)
        
        self.start_date = TextInput(size_hint=(1, 0.1), height=44, hint_text="시작 날짜 (예: 2022-01-01)", font_name='NotoSans')
        self.main_layout.add_widget(self.start_date)
        
        self.end_date = TextInput(size_hint=(1, 0.1), height=44, hint_text="종료 날짜 (예: 2022-12-31)", font_name='NotoSans')
        self.main_layout.add_widget(self.end_date)

        # 버튼 레이아웃
        self.button_layout = BoxLayout(size_hint=(1, 0.1), height=44, spacing=10)
        
        self.search_button = Button(text="검색", on_press=self.search, font_name='NotoSans')
        self.button_layout.add_widget(self.search_button)

        self.reset_button = Button(text="초기화", on_press=self.reset, font_name='NotoSans')
        self.button_layout.add_widget(self.reset_button)

        self.save_button = Button(text="결과 저장 (CSV)", on_press=self.save_results_as_csv, font_name='NotoSans')
        self.button_layout.add_widget(self.save_button)

        self.favorites_button = Button(text="즐겨찾기 보기", on_press=self.show_favorites, font_name='NotoSans')
        self.button_layout.add_widget(self.favorites_button)

        self.main_layout.add_widget(self.button_layout)

        # 검색 결과 미리보기 레이블 및 RecycleView
        self.preview_label = Label(text="검색 결과 미리보기:", font_size=18, font_name='NotoSans', size_hint=(1, 0.05))
        self.main_layout.add_widget(self.preview_label)

        self.preview_list = RecycleView(size_hint=(1, 0.5))
        self.preview_list.data = []
        self.main_layout.add_widget(self.preview_list)

        self.favorites = []  # 즐겨찾기 목록

        return self.main_layout

    def search(self, instance):
        # 이벤트 루프에서 비동기 작업을 수행
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.perform_search())

    async def perform_search(self):
        selected_engine = self.engine_spinner.text
        search_query = self.search_input.text.strip()
        search_image = self.image_checkbox.active
        search_content = self.content_checkbox.active
        filter_option = self.filter_spinner.text
        start_date = self.start_date.text
        end_date = self.end_date.text

        # 수식어 적용
        suffix = self.suffix_input.text.strip()
        if suffix:
            search_query += f" {suffix}"  # 검색어에 추가

        # URL 생성 및 결과 처리
        url = self.construct_url(selected_engine, search_query, search_image, search_content, filter_option, start_date, end_date)
        tasks = [self.fetch_search_results(f"{url}&start={10*page}", search_image) for page in range(1, 4)]
        await asyncio.gather(*tasks)

    async def fetch_search_results(self, url, search_image):
        try:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    response_text = await response.text()
                    if search_image:
                        self.parse_image_results(response_text)
                    else:
                        self.parse_text_results(response_text)
        except Exception as e:
            self.show_popup("오류", f"검색 중 오류가 발생했습니다: {str(e)}")

    @mainthread
    def parse_image_results(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        images = soup.find_all('img')
        image_sources = [img['src'] for img in images if img.get('src')]
        self.preview_list.data.extend([{'text': src} for src in image_sources])

    @mainthread
    def parse_text_results(self, response_text):
        keyword = self.search_input.text.strip()
        suffix = self.suffix_input.text.strip()
        relevant_results = []

        # HTML 파싱 및 키워드 기반 필터링
        soup = BeautifulSoup(response_text, 'html.parser')
        results = soup.select('.news_tit') or soup.select('.tit_main')
        
        for result in results:
            text = result.get_text()
            if keyword in text or suffix in text:  # 키워드 매칭
                relevant_results.append(text)

        # 미리보기 목록에 필터링된 결과 추가
        self.preview_list.data.extend([{'text': text} for text in relevant_results])
        self.show_results_popup(relevant_results)

    def show_results_popup(self, results):
        content = BoxLayout(orientation='vertical')
        for result in results:
            content.add_widget(Label(text=result, font_name='NotoSans'))
        
        popup = Popup(title="검색 결과", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def reset(self, instance):
        self.engine_spinner.text = '네이버'
        self.search_input.text = ''
        self.suffix_input.text = ''
        self.image_checkbox.active = False
        self.content_checkbox.active = False
        self.filter_spinner.text = '전체'
        self.start_date.text = ''
        self.end_date.text = ''
        self.preview_list.data = []

    def save_results_as_csv(self, instance):
        from tkinter import filedialog
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            with open(save_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Search Results"])
                for item in self.preview_list.data:
                    writer.writerow([item['text']])
            self.show_popup("저장 완료", "검색 결과가 CSV 파일로 저장되었습니다.")

    def show_favorites(self, instance):
        content = BoxLayout(orientation='vertical')
        for fav in self.favorites:
            content.add_widget(Label(text=fav, font_name='NotoSans'))
        
        popup = Popup(title="즐겨찾기 목록", content=content, size_hint=(0.8, 0.8))
        popup.open()

    def add_to_favorites(self, instance):
        if self.preview_list.data:
            selected = self.preview_list.data[0]['text']
            if selected not in self.favorites:
                self.favorites.append(selected)
                self.show_popup("즐겨찾기 추가", "즐겨찾기에 추가되었습니다.")
            else:
                self.show_popup("경고", "이미 즐겨찾기에 추가된 항목입니다.")
        else:
            self.show_popup("경고", "추가할 항목을 선택하세요.")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message, font_name='NotoSans'), size_hint=(None, None), size=(400, 200))
        popup.open()

    def construct_url(self, engine, query, image, content, filter_option, start_date, end_date):
        if engine == "네이버":
            base_url = "https://search.naver.com/search.naver"
            params = {"query": query}
            if image:
                params["where"] = "image"
            if filter_option == "뉴스":
                params["where"] = "news"
                if start_date and end_date:
                    params["ds"] = start_date.replace("-", ".")
                    params["de"] = end_date.replace("-", ".")
            elif filter_option == "블로그":
                params["where"] = "post"
                if start_date and end_date:
                    params["date_from"] = start_date.replace("-", "")
                    params["date_to"] = end_date.replace("-", "")
            elif filter_option == "카페":
                params["where"] = "article"
                if start_date and end_date:
                    params["ds"] = start_date.replace("-", ".")
                    params["de"] = end_date.replace("-", ".")
        elif engine == "다음":
            base_url = "https://search.daum.net/search"
            params = {"q": query}
            if image:
                params["w"] = "img"
            elif filter_option == "뉴스":
                params["w"] = "news"
                if start_date and end_date:
                    params["period"] = "d"
                    params["sd"] = start_date.replace("-", "")
                    params["ed"] = end_date.replace("-", "")
            elif filter_option == "블로그":
                params["w"] = "blog"
                if start_date and end_date:
                    params["period"] = "d"
                    params["sd"] = start_date.replace("-", "")
                    params["ed"] = end_date.replace("-", "")
            elif filter_option == "카페":
                params["w"] = "cafe"
                if start_date and end_date:
                    params["period"] = "d"
                    params["sd"] = start_date.replace("-", "")
                    params["ed"] = end_date.replace("-", "")
        else:
            base_url = "https://www.google.com/search"
            params = {"q": query}
            if image:
                params["tbm"] = "isch"
            elif content:
                params["tbm"] = "nws"
        
        url = f"{base_url}?{urlencode(params)}"
        return url

if __name__ == "__main__":
    SearchEngineSelectorApp().run()
