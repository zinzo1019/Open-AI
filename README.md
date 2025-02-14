# 📝 01_summarize_text_app.py: Streamlit 요약 프로그램

**Streamlit**과 **OpenAI GPT**를 활용하여 문서를 요약하는 프로그램입니다.

사이드바에서 OpenAI API 키를 입력하고 요약할 문서를 입력하면, GPT 요약 결과를 보여줍니다. 

평이한 내용을 제거하고, 검증 연구복이를 제외하며, 3 행의 보기 좋은 요약문을 제공합니다.

---

## ✨ **프로젝트 개요**
파일 명: `summary_app.py`

프로그램은 다음과 같은 복제를 가지고 있습니다:

- ✨ **OpenAI API**를 사용하여 GPT-3.5 Turbo로 문서 요약
- ✨ **Streamlit 기능**을 활용하여 간단한 웹 기능 제공
- ✨ **API 키 입력 경로**를 사용하여 사용자가 보유한 OpenAI API Key에 따르여 요약 결과 제공
- ✨ **평이한 내용의 제거**를 통해 복증 발이 및 다양한 여론 결과 제외
- ✨ **3 행의 보기 좋은 요약문 제공** (블록트러 형식)

---

## 프로젝트 설치 및 실행 방법

### 필수 서비스 및 보안
- **Python 3.8+**
- **OpenAI API Key** (필수)
- **Streamlit** (다음 명령으로 설치)

### 1. **필수 패키지 설치**
다음 명령을 입력하여 Streamlit 및 OpenAI 보안 패키지를 설치합니다.
```bash
pip install streamlit openai
```

### 2. **파일 실행**
다음 명령을 입력하여 Streamlit 요약 프로그램을 실행합니다.
```bash
streamlit run summary_app.py
```

---

## 프로그램 사용법

1. **OpenAI API Key** 입력
   - 사용자가 제공하는 OpenAI API Key를 사용.
2. **문서 입력**
   - 요약할 문서를 입력합니다.
3. **[확인] 버튼 클릭**
   - 복증 여론복이를 제외하고 3 행의 블록트러 형식으로 요약.

---

## 프로그램 구조

1. **`문서 입력`** (`st.text_area`)
2. **`요약버튼`** (`st.button("요약")`)
3. **`OpenAI GPT-3.5 문서 요약`** (`askGpt(prompt)`)
4. **`결과 제공`** (`st.info()`)

---

## 해당 파일 소스 자바 선언

다음은 보통복이 해당 파일에서 실행되는 주요 함수입니다.

- **`askGpt(prompt)`**: OpenAI GPT API에 문자를 전달하고 요약된 본문을 반환.
- **`st.text_input()`**: OpenAI API 키의 입력 카드 개본.
- **`st.text_area()`**: 요약할 문서 입력.
- **`st.button()`**: 버튼 클릭으로 GPT 요약 시작.

---
