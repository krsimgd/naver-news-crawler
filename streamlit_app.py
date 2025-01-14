import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title('네이버 뉴스 크롤러')

# 검색어 입력받기
keyword = st.text_input('검색어를 입력하세요')

if st.button('검색'):
    # 네이버 뉴스 검색
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 뉴스 제목 추출
    news_titles = soup.select('.news_tit')
    
    # 결과 출력
    for title in news_titles:
        st.write(title.get('title'))
