import json
import re
import os

from openai import OpenAI

# 프롬프트 파일을 로드하는 함수
def load_prompt(file_name):
    """prompt 파일을 불러오는 함수"""
    prompt_path = os.path.join("prompts", file_name)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def get_basic_info(doc_text, api_key):
    client = OpenAI(api_key=api_key)

    # 리포트 발간일자 추가
    report_date = load_prompt("report_date.txt").strip()
    report_date_prompt = f"# 리포트 발간일자: {report_date}\n"

    # 기본 정보 추출 프롬프트 로드
    prompt = report_date_prompt + load_prompt("basic_info.txt")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        top_p=0.3,
        messages=[
            {"role": "developer", "content": prompt},
            {"role": "user", "content": doc_text}
        ]
    )
    response_text = re.sub(r"```json\n?|```", "", completion.choices[0].message.content).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None

def get_financial_info(doc_text, api_key):
    client = OpenAI(api_key=api_key)

    # 리포트 발간일자 추가
    report_date = load_prompt("report_date.txt").strip()
    report_date_prompt = f"# 리포트 발간일자: {report_date}\n"

    # 재무 정보 전처리 프롬프트 로드
    financial_pre_prompt = load_prompt("financial_preprocess.txt")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=1,
        top_p=0.3,
        messages=[
            {"role": "developer", "content": financial_pre_prompt},
            {"role": "user", "content": doc_text}
        ]
    )
    financial_pre_response = completion.choices[0].message.content

    # 재무 정보 추출 프롬프트 로드
    financial_prompt = report_date_prompt + load_prompt("financial_info.txt")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=1,
        top_p=0.3,
        messages=[
            {"role": "developer", "content": financial_prompt},
            {"role": "user", "content": financial_pre_response}
        ]
    )
    response_text = re.sub(r"```json\n?|```", "", completion.choices[0].message.content).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None
