##### 기본 정보 불러오기 ####
# Streamlit 패키지 추가
import streamlit as st
# OpenAI 패키기 추가
from openai import OpenAI

##### 기능 구현 함수 #####
client = OpenAI(api_key="MY API KEY")

def askGpt(prompt):
    messages_prompt = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(model='gpt-3.5-turbo', messages=messages_prompt)
    gptResponse = response.model_dump()["choices"][0]["message"]["content"]
    return gptResponse

##### 메인 함수 #####
def main():
    st.write(page_title="요약 프로그램")
    # 사이드바
    with st.sidebar:
        # Open AI API 키 입력받기
        open_apikey = st.text_input(label='OPENAI API 키', placeholder='Enter Your API Key', value='',type='password')    
        # 입력받은 API 키 표시
        if open_apikey:
            client.api_key  = open_apikey 
        st.markdown('---')

    st.header("📃 요약 프로그램")
    st.markdown('---')
    
    text = st.text_area("요약 할 글을 입력하세요")
    if st.button("요약"):
        # 프롬포트 엔지니어링
        # ai 답변에 대한 자세한 요구 지정 (주의사항 등))
        prompt = f'''
        **Instructions** :
    - You are an expert assistant that summarizes text into **Korean language**.
    - Your task is to summarize the **text** sentences in **Korean language**.
    - Your summaries should include the following :
        - Omit duplicate content, but increase the summary weight of duplicate content.
        - Summarize by emphasizing concepts and arguments rather than case evidence.
        - Summarize in 3 lines.
        - Use the format of a bullet point.
    -text : {text}
    '''
        st.info(askGpt(prompt))

if __name__=="__main__":
    main()
