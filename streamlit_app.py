import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

# 페이지 전체 스타일링
st.set_page_config(
   page_title="네이버 뉴스 크롤러",
   page_icon="📰",
   layout="wide"
)

# CSS 스타일 추가
st.markdown("""
   <style>
   .main-header {
       font-size: 3em;
       font-weight: bold;
       text-align: center;
       color: #1a73e8;
       margin-bottom: 1em;
   }
   .sub-header {
       font-size: 1.5em;
       color: #666;
       text-align: center;
       margin-bottom: 2em;
   }
   .stButton>button {
       width: 100%;
       background-color: #1a73e8;
       color: white;
       font-weight: bold;
       padding: 0.5em;
   }
   </style>
   """, unsafe_allow_html=True)

# 헤더
st.markdown("<h1 class='main-header'>📰 네이버 뉴스 크롤러</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>원하는 키워드의 네이버 뉴스를 쉽게 수집하세요</p>", unsafe_allow_html=True)

# 기존 크롤링 함수들
[이전 코드와 동일한 함수들...]

# 2개의 컬럼으로 입력 폼 나누기
col1, col2 = st.columns(2)

with col1:
   st.markdown("### 🔍 검색 설정")
   maxpage = st.number_input("📄 크롤링할 페이지 수", 
                           min_value=1, 
                           max_value=50, 
                           value=1,
                           help="한 페이지당 10개의 뉴스가 수집됩니다")
   
   query = st.text_input("🔤 검색어를 입력하세요",
                        placeholder="예: 인공지능")
   
   sort = st.selectbox("📋 정렬 방식", 
                      options=['0', '1', '2'],
                      format_func=lambda x: {
                          '0': '💡 관련도순',
                          '1': '⏰ 최신순',
                          '2': '📅 오래된순'
                      }[x])

with col2:
   st.markdown("### 📅 날짜 설정")
   s_date = st.date_input("시작 날짜", 
                         value=datetime.now(),
                         help="뉴스 검색 시작 날짜")
   
   e_date = st.date_input("종료 날짜",
                         value=datetime.now(),
                         help="뉴스 검색 종료 날짜")

# 구분선
st.markdown("---")

# 중앙 정렬된 검색 버튼
col1, col2, col3 = st.columns([2,1,2])
with col2:
   search_button = st.button("🔎 뉴스 검색 시작")

if search_button:
   if query:
       with st.spinner('뉴스를 수집하고 있습니다... 🔄'):
           # 날짜 형식 변환
           s_date_str = s_date.strftime("%Y.%m.%d")
           e_date_str = e_date.strftime("%Y.%m.%d")
           
           df = crawler(maxpage, query, sort, s_date_str, e_date_str)
           
           st.success('뉴스 수집이 완료되었습니다! ✨')
           
           # 결과 표시
           st.markdown("### 📊 크롤링 결과")
           st.markdown(f"**총 {len(df)}개**의 뉴스를 찾았습니다.")
           
           # 데이터프레임 스타일링
           st.dataframe(df.style.highlight_max(axis=0), height=400)
           
           # CSV 다운로드 버튼
           csv = df.to_csv(index=False).encode('utf-8-sig')
           st.download_button(
               "📥 결과 다운로드 (CSV)",
               csv,
               f"naver_news_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
               "text/csv"
           )
   else:
       st.error('검색어를 입력해주세요! ⚠️')

# 페이지 하단 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1em;'>
Made with ❤️ by Streamlit<br>
최근 업데이트: 2024.01
</div>
""", unsafe_allow_html=True)
