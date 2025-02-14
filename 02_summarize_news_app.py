import os
import requests
import pages as pg
from openai import OpenAI
from bs4 import BeautifulSoup

import streamlit as st
from streamlit_navigation_bar import st_navbar

from deep_translator import GoogleTranslator

client = OpenAI(api_key="")

##### 사이드 바 #####
def navigation_bar():
    with st.sidebar:
        # Open AI API 키 입력받기
        api_key = st.text_input(label='OPENAI API KEY', placeholder='Enter Your API Key', value='',type='password')
        # 입력받은 API 키 표시
        if api_key:
            client.api_key  = api_key 
        st.markdown('---')

##### BBC 최신 뉴스 5개 조회 #####
def get_bbc_news():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get("https://www.bbc.com/news", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        news_list = []

        # <a> 태그의 href 속성을 이용하여 뉴스 URL 추출
        i = 0
        for a in soup.select("a"):
            if i >= 5:
                break
            if a["href"].startswith("/news/articles"):
                news_url = 'https://www.bbc.com' + a["href"]
                news_title = a.select_one("h2").get_text()
                
                # 중복 항목 검사
                if any(news["title"] == news_title for news in news_list):
                    continue
                
                news_list.append({"title": news_title, "url": news_url})
                i += 1

        return news_list
    
    except Exception as e:
        return f"오류 발생: {e}"

##### BBC 최신 뉴스 5개 띄우기 #####
def show_bbc_news():
    st.write("### BBC News")
    news_list = get_bbc_news()
    for news in news_list:
        st.write(f"- [{news['title']}]({news['url']})")

##### 웹 스크래핑을 통한 기사 본문 추출 함수 #####
def extract_news_text(url):
    if not url:
        st.warning("Please enter news url.")
        return
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        article_text = None

        # BBC 뉴스 본문 추출 (사이트별로 변경 필요)
        if url.startswith("https://www.bbc.com"):
            # <article> 태그 내부의 <p> 태그 내용만 추출하여 리스트로 저장
            article = soup.find('article') 
            p_contents = [p.get_text() for p in article.find_all('p')] 
            article_text = ' '.join(p_contents)
            
        return article_text if article_text else "기사 본문을 찾을 수 없습니다."
    
    except Exception as e:
        return f"오류 발생: {e}"
    
##### 뉴스 요약 함수 #####
def summarize_news(news_url):
    # 기사 본문 추출
    extrated_news_content = extract_news_text(news_url)
    # 요약 요청 문구 생성
    prompt = f"""Summarize the news article below in 2-3 lines
    
    {extrated_news_content}"""
    
    # GPT에게 요약 요청
    return ask_gpt(prompt)

##### GPT에게 질문하고 응답을 리턴하는 함수 #####
def ask_gpt(prompt):
    if not client.api_key:
        st.warning("Please enter your api key.")
        return 
    
    messages_prompt = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(model='gpt-3.5-turbo', messages=messages_prompt)
    gptResponse = response.model_dump()["choices"][0]["message"]["content"]
    calculate_price(response) # 금액 계산
    return gptResponse

##### GPT 사용료 계산 #####
def calculate_price(response):
    completion_token = response.usage.completion_tokens
    prompt_token = response.usage.prompt_tokens
    
    token_price = 0.06 if st.session_state.model == "gpt-4" else 0.02
    prompt_price = 0.03 if st.session_state.model == "gpt-4" else 0.015
    total_bill = (completion_token * token_price + prompt_token * prompt_price) * 0.001

    st.info(f"금액 : {convert_usd_to_krw(total_bill)}원")
    
##### 네이버 금융에서 실시간 USD → KRW 환율 가져오기 #####
def get_exchange_rate():
    url = "https://api.manana.kr/exchange/rate/KRW/USD.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()[0]["rate"]  # 환율 값 반환
    else:
        raise Exception("환율 정보를 가져오는 데 실패했습니다.")

##### USD 금액을 실시간 환율을 적용하여 KRW로 변환 #####
def convert_usd_to_krw(amount_in_usd):
    try:
        exchange_rate = get_exchange_rate()  # 실시간 환율 가져오기
        amount_in_krw = amount_in_usd * exchange_rate
        return round(amount_in_krw, 2)  # 소수점 2자리까지 반올림
    except Exception as e:
        return f"오류 발생: {e}"
                
##### 문장을 기준으로 5000자 이하로 나눔 #####
def split_text_by_sentence(text, max_length=5000):
    sentences = text.replace("!", "!|").replace("?", "?|").replace(". ", ".|").split("|")  # 문장 분리
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "  # 현재 블록에 추가
        else:
            chunks.append(current_chunk.strip())  # 새 블록 저장
            current_chunk = sentence + " "

    if current_chunk:  # 마지막 블록 추가
        chunks.append(current_chunk.strip())

    return chunks

##### 구글 번역 함수 #####
@st.cache_data  # 동일한 입력값이면 API 호출 없이 캐싱된 결과 반환
def google_trans(content):
    if not content:
        st.warning("There is nothing to translate.")
        return
    
    try:
        chunks = split_text_by_sentence(content, max_length=5000)  # 문장 기준으로 나누기
        translated_chunks = [GoogleTranslator(source='auto', target='ko').translate(chunk) for chunk in chunks]
        return " ".join(translated_chunks)  # 번역된 문장 합치기
    except Exception as e:
        return f"오류 발생: {e}"
    
##### 세션에 존재하면 화면에 노출 #####
def show_session_state(session_state):
    if st.session_state[session_state]:
        st.info(st.session_state[session_state])

def main():

    ## 변수 초기화 시작 
    # GPT 모델 
    if "model" not in st.session_state:
        st.session_state["model"] = "gpt-3.5-turbo"
    # 뉴스 요약
    if "ai_summary" not in st.session_state:
        st.session_state["ai_summary"] = ""
    # 뉴스 요약
    if "translated_ai_summary" not in st.session_state:
        st.session_state["translated_ai_summary"] = ""
    # 뉴스 전문 
    if "news_content" not in st.session_state:
        st.session_state["news_content"] = ""
    # 전체 뉴스 번역본
    if "translated_news_content" not in st.session_state:
        st.session_state["translated_news_content"] = ""
    # 내 요약 AI 수정본
    if "edited_ai_summary" not in st.session_state:
        st.session_state["edited_ai_summary"] = ""
    # 내 요약 AI 수정본 번역본 
    if "translated_edited_ai_summary" not in st.session_state:
        st.session_state["translated_edited_ai_summary"] = ""
    ## 변수 초기화 끝

    # 사이드바
    navigation_bar()
    # BBC 뉴스 5개 출력
    show_bbc_news()

    # 기사 URL 입력
    news_url = st.text_input("NEWS URL")
    
    col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=False)
    with col1:
        # AI 요약
        if st.button("MAKE AI SUMMARY"):
            if not news_url:
                st.warning("Please enter news url.")
            if not client.api_key:
                st.warning("Please enter your api key.")
            else:
                # 뉴스 요약
                st.session_state.ai_summary = summarize_news(news_url)
                
        # 요약본 띄우기
        show_session_state("ai_summary")
            
    with col2:
        # 요약 번역
        if st.button("TRANSLATE AI SUMMARY"):
            if not news_url:
                st.warning("Please enter news url.")
            if not client.api_key:
                st.warning("Please enter your api key.")
            else:
                st.session_state.translated_ai_summary = google_trans(st.session_state["ai_summary"])
            
        # 번역본 띄우기
        show_session_state("translated_ai_summary")
                
    col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=False)
    with col1:
        # 기사 전문
        if st.button("VIEW FULL ARTICLE"):
            st.session_state.news_content = extract_news_text(news_url)
            
        # 기사 전문 띄우기
        show_session_state("news_content")

    with col2:
        # 기사 전문 번역
        if st.button("TRANSLATE FULL ARTICLE"):
            if not st.session_state.news_content:
                st.session_state.news_content = extract_news_text(news_url)
            st.session_state.translated_news_content = google_trans(st.session_state.news_content)
            
        # 번역본 띄우기
        show_session_state("translated_news_content")
        
    # 내 요약 입력
    user_summary = st.text_area("MY SUMMARY")
    
    col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=False)
    with col1:
        # 내 요약 AI 수정
        if st.button("FIX MY SUMMARY"):
            if not news_url:
                st.warning("Please enter news url.")
            if not client.api_key:
                st.warning("Please enter your api key.")
            if not user_summary:
                st.warning("Please enter your summary.")
            else:
                if not st.session_state["ai_summary"]:
                    ai_summary = summarize_news(news_url)
                    st.session_state["ai_summary"] = ai_summary

                prompt = f"""
                    Compare the AI ​​summary below with the user's summary, and correct any missing or distorted information in the user's summary, so that only 2-3 lines are displayed as the result. Also, correct any grammatical errors.

                    AI summary: [{st.session_state["ai_summary"]}]
                    User summary: [{user_summary}]
                """

                # AI 수정본 요청 
                st.session_state.edited_ai_summary = ask_gpt(prompt)
                
        # 수정본 띄우기
        show_session_state("edited_ai_summary")
                
    with col2:
        if st.button("TRANSLATE MY FIXED SUMMARY"):
            st.session_state.translated_edited_ai_summary = google_trans(st.session_state.edited_ai_summary)
            
        # 번역본 띄우기
        show_session_state("translated_edited_ai_summary")

if __name__ == "__main__":
    main()