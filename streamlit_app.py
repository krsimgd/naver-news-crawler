import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

st.title('네이버 뉴스 크롤러')

# 결과 저장할 리스트 선언
title_text=[]
link_text=[]
source_text=[]
date_text=[]
contents_text=[]
result={}

# 날짜 정제화 함수 - 원본 그대로 유지
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

# 내용 정제화 함수 - 원본 그대로 유지
def contents_cleansing(contents):
   first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '', str(contents)).strip()
   second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '', first_cleansing_contents).strip()
   third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
   contents_text.append(third_cleansing_contents)

# 크롤링 함수 - 원본 로직 유지
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
       
   result = {"date" : date_text, "title":title_text, "source" : source_text, "contents": contents_text, "link":link_text}
   df = pd.DataFrame(result)
   return df

# Streamlit 입력 위젯들
st.header('검색 조건 입력')
maxpage = st.number_input("최대 크롤링할 페이지 수:", min_value=1, max_value=50, value=1)
query = st.text_input("검색어:")
sort = st.selectbox("뉴스 검색 방식:", 
                  options=['0', '1', '2'],
                  format_func=lambda x: {
                      '0': '관련도순',
                      '1': '최신순',
                      '2': '오래된순'
                  }[x])
s_date = st.text_input("시작날짜 (예: 2024.01.04):")
e_date = st.text_input("끝날짜 (예: 2024.01.05):")

if st.button("뉴스 크롤링 시작"):
   if query and s_date and e_date:
       with st.spinner('크롤링 중...'):
           df = crawler(maxpage,query,sort,s_date,e_date)
           st.success('크롤링 완료!')
           
           # 결과 표시
           st.header('크롤링 결과')
           st.dataframe(df)
           
           # CSV 다운로드 버튼
           csv = df.to_csv(index=False).encode('utf-8-sig')
           st.download_button(
               "크롤링 결과 CSV 다운로드",
               csv,
               f"naver_news_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
               "text/csv"
           )
   else:
       st.error('모든 필수 항목을 입력해주세요.')
