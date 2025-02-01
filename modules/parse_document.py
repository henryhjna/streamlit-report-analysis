from llama_parse import LlamaParse

def parse_pdf(file_path, api_key):
    parser = LlamaParse(
        api_key=api_key,
        use_vendor_multimodal_model=False,
        #vendor_multimodal_model_name="openai-gpt4o",
        #vendor_multimodal_api_key=OPENAI_API_KEY,
        result_type="markdown",
        language="ko",
        debug=True,
        page_separator="\n=================\n",
        content_guideline_instruction=(
            "🚨 [중요] 문서의 원본 텍스트와 숫자를 100% 그대로 유지하시오. "
            "🚨 [중요] 원본 내용을 요약하거나 바꾸지 말고, 문서의 원문 그대로 추출하시오. "
            "⚠️ 숫자(단위 포함), 표(Table), 그래프(Graph)의 형식을 유지하시오. "
            "⚠️ 표 안이나 위 또는 근처에 기재된 단위 정보(백만원, 억원, 십억원 등)를 절대 바꾸지 마시오."
            "⚠️ 재무제표, 손익계산서, 재무상태표, 현금흐름표, 대차대조표 등의 기재된 단위(억원, 십억원 등)를 그대로 유지하시오."
        )
    )
    parsed_docs = parser.load_data(file_path=str(file_path))

    return "\n".join(doc.text for doc in parsed_docs) if parsed_docs else ""
