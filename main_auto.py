import argparse
import os
import random
from datetime import datetime
from data_fetcher import KamisFetcher
from data_processor import DataProcessor
from visualizer import KamisVisualizer
from blog_generator import BlogGenerator
from config import OUTPUT_DIR

def run_automation():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting KAMIS Blog Automation...")
    
    fetcher = KamisFetcher()
    processor = DataProcessor()
    viz = KamisVisualizer(theme='dark')
    blog = BlogGenerator()
    
    # 1. Topic Alternation: Read last topic
    last_item_path = os.path.join(OUTPUT_DIR, "last_topic.txt")
    exclude_item = None
    if os.path.exists(last_item_path):
        with open(last_item_path, 'r', encoding='utf-8') as f:
            exclude_item = f.read().strip()

    # 2. Fetch All Data for Analysis
    daily_data = fetcher.get_mock_daily_data()
    regional_data = fetcher.get_mock_regional_data()
    trend_data = fetcher.get_mock_trend_data()
    
    # 3. Analyze Market Context and Select Category
    category, findings, selected_item = processor.analyze_market_context(daily_data, regional_data, trend_data, exclude_item=exclude_item)
    print(f"Selected Category: {category}, Focus Item: {selected_item}")

    # 4. Generate Chart
    if category == "D":
        img_path = viz.plot_1300_regional_comparison(regional_data)
        data_for_blog = regional_data
    elif category == "E":
        img_path = viz.plot_1700_trend_line(processor.process_trend_data(trend_data))
        data_for_blog = daily_data
    else:
        processed_daily = processor.process_daily_fluctuations(daily_data)
        img_path = viz.plot_0900_daily_fluctuation(processed_daily)
        data_for_blog = processed_daily

    # 5. Generate Content dynamically
    try:
        markdown = blog.generate_post(category, findings, data_for_blog)
    except Exception as e:
        if "Gemini API Error" in str(e):
            from telegram_notifier import send_telegram_message
            send_telegram_message(f"🚨 Gemini API 오류 발생!\n에러 내용: {e}")
            return
        else:
            raise
    
    # Save RAW markdown for history
    raw_filename = f"raw_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    raw_filepath = os.path.join(OUTPUT_DIR, raw_filename)
    with open(raw_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # 6. Extract and Clean Content for Naver Blog
    try:
        import re
        sections = {}
        current_section = None
        
        # Section markers matching (case-insensitive, flexible spacing/asterisks)
        markers = {
            'category': r'1\..*선정된 주제',
            'title': r'2\..*블로그 제목',
            'summary': r'핵심요약',
            'body': r'4\..*본문 콘텐츠',
            'recommendation': r'5\..*상품 추천',
            'hashtags': r'6\..*관련 해시태그',
            'viz': r'7\..*데이터 시각화'
        }

        for line in markdown.split('\n'):
            line_clean = line.strip().replace('**', '').replace('### ', '')
            
            matched = False
            for sec_name, pattern in markers.items():
                if re.search(pattern, line_clean):
                    current_section = sec_name
                    matched = True
                    break
            
            if not matched and current_section:
                # Add line but strip leading/trailing whitespace for each line to avoid nested indents
                sections[current_section] = sections.get(current_section, "") + line.strip() + "\n"

        title = sections.get('title', '오늘의 농산물 분석').strip().replace('"', '')
        summary = sections.get('summary', '').strip()
        body = sections.get('body', '').strip()
        recommendation = sections.get('recommendation', '').strip()
        hashtags = sections.get('hashtags', '').strip()
        
        # 6a. Title Date Injection
        now = datetime.now()
        date_str = f"({now.strftime('%m/%d')})"
        # Insert date into title if it contains '오늘'
        if '오늘' in title:
            title = title.replace('오늘', f"오늘{date_str}")
        
        # Cleaned Markdown for publication
        disclosure = '"이 포스팅은 토스쇼핑 쉐어링크 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."'
        
        def clean_sec(text):
            lines = text.strip().split('\n')
            while lines and (lines[0].strip() == '---' or not lines[0].strip()): lines.pop(0)
            while lines and (lines[-1].strip() == '---' or not lines[-1].strip()): lines.pop()
            return '\n'.join(lines).strip()

        title = title.strip()
        summary = clean_sec(summary)
        body = clean_sec(body)
        recommendation = clean_sec(recommendation)
        hashtags = clean_sec(hashtags)
        
        cleaned_markdown = f"# {title}\n\n"
        cleaned_markdown += f"{disclosure}\n\n"
        if summary:
            cleaned_markdown += f"> **\"핵심요약\"**\n{summary}\n\n"
        
        cleaned_markdown += "---\n\n"
        cleaned_markdown += body
        
        if recommendation:
            cleaned_markdown += f"\n\n---\n\n{recommendation}"
            
        if hashtags:
            cleaned_markdown += f"\n\n---\n\n{hashtags}"
        
        clean_filepath = os.path.join(OUTPUT_DIR, f"clean_{raw_filename}")
        with open(clean_filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_markdown)
            
    except Exception as e:
        print(f"Error parsing content: {e}")
        clean_filepath = raw_filepath
        title = "블로그 포스팅"

    # 7. Naver Blog Auto Poster & Telegram Notification
    from naver_blog_poster import run_poster
    from telegram_notifier import send_telegram_message
    
    print("네이버 블로그 자동 임시저장을 시작합니다...")
    try:
        run_poster(clean_filepath, images=[img_path], headless=True)
        # 8. Success: Update last topic
        if selected_item:
            with open(last_item_path, 'w', encoding='utf-8') as f:
                f.write(selected_item)
                
        notification = f"✅ 네이버 블로그 임시저장 성공!\n\n📌 제목: {title}\n\n📝 요약:\n{summary[:200]}..."
        send_telegram_message(notification)
    except Exception as e:
        send_telegram_message(f"❌ 네이버 블로그 임시저장 중 오류 발생!\n에러: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_automation()

if __name__ == "__main__":
    main()
