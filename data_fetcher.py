import requests
import json
from datetime import datetime, timedelta
import os
import pandas as pd
from config import KAMIS_API_KEY, KAMIS_API_ID

class KamisFetcher:
    def __init__(self):
        self.cert_key = KAMIS_API_KEY
        self.cert_id = KAMIS_API_ID
        self.base_url = "http://www.kamis.or.kr/service/price/xml.do"

    def _get_base_params(self, action="dailyPriceByCategoryList"):
        return {
            "p_cert_key": self.cert_key,
            "p_cert_id": self.cert_id,
            "p_returntype": "json",
            "action": action
        }

    def get_daily_price(self, date=None):
        """
        Fetches daily price data. If date is None, uses today's date.
        """
        # In a real scenario, this would call the API.
        # Since we might not have a valid key at development, we will also provide mock data later.
        url = self.base_url
        params = self._get_base_params("dailyPriceByCategoryList")
        
        target_date = date if date else datetime.now().strftime("%Y-%m-%d")
        params["p_regday"] = target_date
        params["p_item_category_code"] = "100" # Examples: 100 식량작물, 200 채소류, 300 특작류, 400 과일류...
        
        try:
            # We add timeout to prevent hanging
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"Error fetching KAMIS API: {e}")
            return None

    def get_mock_daily_data(self):
        """Returns mock daily price data for Top 5 Fluctuations (09:00 chart)"""
        return pd.DataFrame({
            'Item': ['사과', '배', '양파', '대파', '감자'],
            'Standard': ['10kg', '15kg', '20kg', '1kg', '20kg'],
            'Today_Price': [85000, 80000, 25000, 4000, 32000],
            'Yesterday_Price': [70000, 64000, 27000, 5000, 30000]
        })
        
    def get_mock_regional_data(self):
        """Returns mock regional data for 13:00 chart"""
        return pd.DataFrame({
            'Region': ['서울', '부산', '대구', '광주', '대전'],
            'Price': [85000, 82000, 79000, 80000, 81000]
        })
        
    def get_mock_trend_data(self):
        """Returns mock trend data for 17:00 chart"""
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        return pd.DataFrame({
            'Date': dates,
            'Price': [72000, 75000, 74000, 78000, 80000, 81000, 85000]
        })
        
    def get_mock_yoy_data(self):
        """Returns mock YoY data for 21:00 chart"""
        return pd.DataFrame({
            'Month': ['1월', '2월', '3월', '4월', '5월', '6월'],
            'This_Year': [60000, 65000, 75000, 85000, None, None],
            'Last_Year': [55000, 58000, 57000, 60000, 62000, 65000]
        })

if __name__ == "__main__":
    fetcher = KamisFetcher()
    print(fetcher.get_mock_daily_data())
