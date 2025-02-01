import streamlit as st
import os
import json
import re
import nest_asyncio
import pandas as pd
from modules.parse_document import parse_pdf
from modules.openai_requests import get_basic_info, get_financial_info
from openai import OpenAI

# Streamlit UI 설정
st.title("📑 Analyze the Analyst")
st.sidebar.header("설정")

OPENAI_API_KEY = st.sidebar.text_input("OpenAI API Key", type="password")
LLAMA_CLOUD_API_KEY = st.sidebar.text_input("LlamaParse API Key", type="password")
uploaded_file = st.sidebar.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file:
    st.success("파일이 업로드되었습니다! 분석을 시작합니다...")

    # 파일 저장
    file_path = os.path.join("temp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 문서 파싱
    doc_text = parse_pdf(file_path, LLAMA_CLOUD_API_KEY)

    if doc_text:
        st.sidebar.success("📄 리포트 데이터가 성공적으로 불러와졌습니다.")
    else:
        st.sidebar.warning("⚠️ 리포트 결과가 없습니다.")

    # 기본 정보 추출
    basic_info = get_basic_info(doc_text, OPENAI_API_KEY)
    
    # UI 개선: 탭 형태로 구성
    tab1, tab2 = st.tabs(["📑 기본 정보", "📊 재무 정보"])

    with tab1:
        if basic_info:
            st.subheader(f"**📑 제목:** {basic_info.get('report_title', 'N/A')}")
            st.markdown(f"{basic_info.get('report_text', 'N/A')}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**🏢 회사명:** {basic_info.get('company', 'N/A')}")
                st.markdown(f"**💹 티커:** {basic_info.get('ticker', 'N/A')}")
                st.markdown(f"**📍 상장 시장:** {basic_info.get('listed_market', 'N/A')}")

            with col2:
                st.markdown(f"**🏦 증권사:** {basic_info.get('house', 'N/A')}")
                st.markdown(f"**👨‍💼 애널리스트:** {basic_info.get('analyst', 'N/A')}")
                st.markdown(f"**📧 애널리스트 이메일:** {basic_info.get('analyst_email', 'N/A')}")
                st.markdown(f"**📢 투자 의견:** {basic_info.get('opinion', 'N/A')}")
                st.markdown(f"**💲 현재 주가:** {basic_info.get('current_price', 'N/A')}")

            # 🎯 목표 주가 테이블
            if 'target_price' in basic_info and isinstance(basic_info['target_price'], list):
                st.subheader("🎯 목표 주가 변화")
                target_price_df = pd.DataFrame(basic_info['target_price'])
                st.dataframe(target_price_df.style.format({"price": "{:.2f}"}))
        else:
            st.error("기본 정보 처리 중 오류 발생")

    with tab2:
        # 재무 정보 추출
        financial_info = get_financial_info(doc_text, OPENAI_API_KEY)
        if financial_info and "financial" in financial_info:
            st.subheader("📊 재무 정보")

            # 각 financial 데이터를 DataFrame으로 변환
            df_revenue = pd.DataFrame(financial_info["financial"].get("revenue", []))
            df_operating_income = pd.DataFrame(financial_info["financial"].get("operating_income", []))
            df_net_income = pd.DataFrame(financial_info["financial"].get("net_income", []))
            df_operating_cashflow = pd.DataFrame(financial_info["financial"].get("operating_cashflow", []))
            
            # 공통 키 기준으로 병합
            financial = df_revenue.merge(df_operating_income, on=["fiscal_year", "fiscal_quarter", "type", "unit"], how="outer")
            financial = financial.merge(df_net_income, on=["fiscal_year", "fiscal_quarter", "type", "unit"], how="outer")
            financial = financial.merge(df_operating_cashflow, on=["fiscal_year", "fiscal_quarter", "type", "unit"], how="outer")
            
            # 정렬 (연도 및 분기순)
            financial = financial.sort_values(by=["fiscal_year", "fiscal_quarter"])
            financial.rename(columns={
                "fiscal_year": "회계연도",
                "fiscal_quarter": "회계분기",
                "type": "유형",
                "unit": "단위",
                "revenue": "매출액",
                "operating_income": "영업이익",
                "net_income": "당기순이익",
                "operating_cashflow": "영업활동현금흐름"
            }, inplace=True)
            
            # 재무 데이터 시각화
            st.dataframe(financial.style.format({
                "매출액": "{:,.0f}",
                "영업이익": "{:,.0f}",
                "당기순이익": "{:,.0f}",
                "영업활동현금흐름": "{:,.0f}"
            }))

        else:
            st.error("재무 정보 처리 중 오류 발생")