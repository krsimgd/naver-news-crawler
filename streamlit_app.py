import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

# 페이지 설정
st.set_page_config(
    page_title="네이버 뉴스 크롤러",
    page_icon="📰",
    layout="wide"
)

# CSS 스타일
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5em;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 1em;
        padding: 1em;
        border-radius: 10px;
        background: #f5f7fa;
    }
    .stButton>button {
        background-color: #1e3d59;
        color: white;
        padding: 0.5em 2em;
        border-radius: 5px;
        border: none;
        width: 100%;
    }
    .search-section {
        background-color: #f5f7fa;
        padding: 2em;
        border-radius: 10px;
        margin-bottom: 2em;
    }
    .results-section {
        background-color: #f5f7fa;
        padding: 2em;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("<h1 class='main-header'>📰 네이버 뉴스 크롤러</h1>", unsafe_allow_html=True)

# 결과 저장할 리스트 선언
title_text=[]
link_text=[]
source_text=[]
date_text=[]
contents_text=[]
result={}

# 날짜 정제화 함수
def date_cleansing(test):
    try:
        pattern = '\d+.(\d+).(\d+).'
        r = re.compile(pattern)
        match = r.search(test).group(0)
        date_text.append(match)
    except AttributeError:
        pattern = '\w* (\d\w*)'
        r = re.compile(pattern)
        match = r.search(test).group(1)
        date_text.append(match)

# 내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '', str(contents)).strip()
    second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '', first_cleansing_contents).strip()
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)

# 크롤링 함수
def crawler(maxpage,query,sort,s_date,e_date):
    # 리스트 초기화
    title_text.clear()
    link_text.clear()
    source_text.clear()
    date_text.clear()
    contents_text.clear()
    
    s_from = s_date.replace(".","")
    e_to = e_date.replace(".","")
    page = 1  
    maxpage_t = (int(maxpage)-1)*10+1
    
    while page <= maxpage_t:
        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort="+sort+"&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(page)
        
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
 
        atags = soup.select('.news_tit')
        for atag in atags:
            title_text.append(atag.text)
            link_text.append(atag['href'])
            
        source_lists = soup.select('.info_group > .press')
        for source_list in source_lists:
            source_text.append(source_list.text)
        
        date_lists = soup.select('.info_group > span.info')
        for date_list in date_lists:
            if date_list.text.find("면") == -1:
                date_text.append(date_list.text)
        
        contents_lists = soup.select('.news_dsc')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)
        
        page += 10
        
    result = {"날짜" : date_text, "제목":title_text, "언론사" : source_text, "내용요약": contents_text, "링크":link_text}
    df = pd.DataFrame(result)
    return df

# 검색 섹션
st.markdown("<div class='search-section'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 검색 설정")
    maxpage = st.number_input("📑 크롤링할 페이지 수", 
                            min_value=1, 
                            max_value=50, 
                            value=1,
                            help="한 페이지당 10개의 뉴스가 수집됩니다")
    
    query = st.text_input("🔤 검색어를 입력하세요",
                         placeholder="예: 인공지능")

with col2:
    st.markdown("### ⚙️ 상세 설정")
    sort = st.selectbox("정렬 방식", 
                       options=['0', '1', '2'],
                       format_func=lambda x: {
                           '0': '💡 관련도순',
                           '1': '⏰ 최신순',
                           '2': '📅 오래된순'
                       }[x])
    
    s_date = st.text_input("📅 시작날짜 (예: 2024.01.04)")
    e_date = st.text_input("📅 종료날짜 (예: 2024.01.05)")

st.markdown("</div>", unsafe_allow_html=True)

# 검색 버튼
if st.button("🔎 뉴스 검색 시작"):
    if query and s_date and e_date:
        with st.spinner('뉴스를 수집하고 있습니다... 🔄'):
            df = crawler(maxpage,query,sort,s_date,e_date)
            
            # 결과 섹션
            st.markdown("<div class='results-section'>", unsafe_allow_html=True)
            st.markdown("### 📊 크롤링 결과")
            st.success(f'✨ {len(df)}개의 뉴스를 찾았습니다!')
            
            # 데이터프레임 표시
            st.dataframe(df, height=400)
            
            # CSV 다운로드 버튼
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 결과 다운로드 (CSV)",
                csv,
                f"naver_news_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error('⚠️ 검색어와 날짜를 모두 입력해주세요!')

# 페이지 푸터
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1em;'>
    Made with ❤️ using Streamlit<br>
    Last Updated: 2024.01
    </div>
""", unsafe_allow_html=True)
