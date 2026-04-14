import os
import random
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import pandas as pd

class BlogGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_post(self, category, market_findings, data):
        """
        Generates a markdown blog post using Gemini.
        Persona: Friendly 30s dad
        """
        
        system_prompt = f"""
        당신은 실속파 "30대 직장인"이자 농산물 시황 전문가입니다. 
        담백하고 위트 있는 어조로 동료 직장인들과 소통하듯 정보를 전달합니다.
        
        [필수 지침: 문장 길이 및 호흡]
        - **모든 문장은 반드시 20자 내외의 짧은 단문으로 작성하세요.** 
        - 긴 문장이나 나열식 문수(claus)는 피하고 호흡을 짧게 가져가세요.
        - 예: "사과 가격이 올랐네요. 정말 비쌉니다. 지갑이 웁니다." (O) / "최근 사과 가격이 갑자기 큰 폭으로 상승하면서 우리들의 장바구니에 큰 부담을 주고 있는 상황입니다." (X)

        [중요: 페르소나 주의 사항]
        - "아빠", "아버지", "데이터를 좋아하는", "가계부", "아이" 등의 표현을 절대로 사용하지 마세요.
        - 오직 "30대 직장인"의 시각에서 동료들과 소통하는 톤을 유지하세요.

        [선택 가능한 카테고리 가이드]
        - 카테고리 C (제철 식재료 및 생활 정보): 안정적인 제철 식재료와 생활 팁.
        - 카테고리 E (가격 변동 예측 및 전망): 과거 추이 기반 향후 전망 예측.

        [필수 작성 및 형식 규칙]
        1. **형식**: 반드시 아래 요소들을 포함하여 마크다운(.md)으로 작성하세요.
           - 1. 선정된 주제 및 카테고리
           - 2. 블로그 제목 (클릭을 부르는 흥미로운 제목)
           - 3. "핵심요약" (반드시 큰따옴표를 포함한 제목으로 작성하며, 바로 아래 줄에 체크 이모지(✅)를 사용하여 가독성 있게 적어주세요.)
           - 4. 본문 콘텐츠 (직장인 일상 소재를 섞어 20자 내외의 짧은 단문으로 위트 있게 작성하세요)
           - 5. 상품 추천 문구 (포스팅 주제와 어울리는 상품을 분석하여 자연스럽게 추천하세요)
           - 6. 관련 해시태그 (관련 키워드 7개를 콤마(,)로 구분하여 작성하세요)

        2. **제약 사항**:
           - 문장 사이 간격을 위해 한 문장이 끝날 때마다 엔터를 2번 연속 넣어주세요.
           - 데이터 출처(KAMIS)는 직접적으로 밝히지 마세요.
        """

        user_prompt = f"""
        현재 시장 분석 지표: {market_findings}
        데이터 요약: \n{data.to_string() if isinstance(data, pd.DataFrame) else str(data)}
        
        위 데이터를 바탕으로 카테고리에 맞는 매력적인 포스팅을 작성해 주세요.
        """

        # List of models to try sequentially. stable flash-latest is preferred for quota.
        models_to_try = [
            'gemini-flash-latest',
            'gemini-1.5-flash',
            'gemini-2.0-flash',
            'gemini-2.5-flash'
        ]
        
        content = ""
        last_error = None
        
        for model_name in models_to_try:
            try:
                print(f"Attempting to generate content using {model_name}...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
                content = response.text
                print(f"Successfully generated content using {model_name}.")
                break
            except Exception as e:
                print(f"Generative API failed for {model_name}: {e}")
                last_error = e
                
        if not content:
            raise Exception(f"Gemini API Error for all available models. Last Error: {last_error}")
            
        return content

if __name__ == "__main__":
    # Test blog generation with dummy data
    generator = BlogGenerator()
    dummy_data = pd.DataFrame({'Item': ['사과'], 'Today_Price': [10000], 'Yesterday_Price': [8000]})
    res = generator.generate_post("카테고리 A", ["폭등주의: 사과 가격 25% 상승"], dummy_data)
    print(res)
