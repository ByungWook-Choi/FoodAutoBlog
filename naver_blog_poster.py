import os
import json
import time
import random
import argparse
import markdown2
import pyperclip
import re
from playwright.sync_api import sync_playwright

NAVER_ID = "dreampapa131"
NAVER_PW = "medison@0505"
AUTH_FILE = "auth.json"

def random_sleep(min_val=1.0, max_val=3.0):
    time.sleep(random.uniform(min_val, max_val))

def convert_md_to_html(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Extract title from the first line (# Title)
    lines = md_text.split('\n')
    title = ""
    if lines and lines[0].startswith('#'):
        title = lines[0].replace('#', '').strip()
        md_text = '\n'.join(lines[1:]).strip()

    # Aggressively convert **bold** syntaxes using Regex before markdown processing
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight:bold;">\1</strong>', md_text, flags=re.DOTALL)
    
    # Escape any remaining hashtag '#' characters so markdown2 doesn't parse them as H1 headings
    md_text = md_text.replace('#', '\\#')

    html_content = markdown2.markdown(md_text, extras=['fenced-code-blocks', 'tables'])
    
    # Remove dummy Markdown image tags since Playwright uploads images manually
    html_content = re.sub(r'<p>\s*<img[^>]+>\s*</p>', '', html_content)
    html_content = re.sub(r'<img[^>]+>', '', html_content)
    
    return title, html_content

def run_poster(md_path, images=None, headless=False):
    title, html_content = convert_md_to_html(md_path)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=['--disable-blink-features=AutomationControlled'])
        
        needs_login = True
        
        if os.path.exists(AUTH_FILE):
            print("기존 세션 정보를 불러옵니다.")
            context = browser.new_context(storage_state=AUTH_FILE, permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()
            
            postwrite_url = f"https://blog.naver.com/{NAVER_ID}/postwrite"
            page.goto(postwrite_url)
            random_sleep(3, 5)
            
            if "nidlogin.login" in page.url or "userNotFound" in page.url:
                print("세션이 만료되었습니다. 다시 로그인합니다.")
                needs_login = True
            else:
                needs_login = False
        else:
            print("세션 정보가 없어 새로 로그인을 진행합니다.")
            context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()
            needs_login = True
            
        if needs_login:
            page.goto("https://nid.naver.com/nidlogin.login")
            random_sleep(2, 3)
            
            # Clipboard injection to avoid captcha
            page.click('#id')
            pyperclip.copy(NAVER_ID)
            page.keyboard.press('Control+V')
            random_sleep(0.5, 1.5)
            
            page.click('#pw')
            pyperclip.copy(NAVER_PW)
            page.keyboard.press('Control+V')
            random_sleep(0.5, 1.5)
            
            page.click('.btn_login')
            print("로그인 진행 중... 캡차나 보안 화면이 나타나면 직접 해결해주세요. (최대 60초 대기)")
            # 캡차 수동 해결 대기 (최대 60초)
            for _ in range(30):
                if "nidlogin" not in page.url and "userNotFound" not in page.url:
                    break
                page.wait_for_timeout(2000)
            
            page.screenshot(path="output/debug_after_login.png")
            context.storage_state(path=AUTH_FILE)
            print("세션 저장 완료 및 글쓰기 페이지 진입 시도")
            
            postwrite_url = f"https://blog.naver.com/{NAVER_ID}/postwrite"
            page.goto(postwrite_url)
            page.wait_for_timeout(5000)
            page.screenshot(path="output/debug_editor_load.png")
            
        # Naver Blog Smart Editor ONE uses an iframe id #mainFrame
        # 하지만 최근 업데이트로 메인 페이지에 직접 렌더링될 수도 있습니다.
        if page.locator("#mainFrame").count() > 0:
            print("iframe(#mainFrame) 기반으로 에디터를 인식했습니다.")
            editor_context = page.frame_locator("#mainFrame")
        else:
            print("메인 페이지 기반으로 에디터를 인식했습니다.")
            editor_context = page
        
        # Handle popups
        try:
            cancel_btn = editor_context.locator("button.se-popup-button.se-popup-button-cancel")
            if cancel_btn.count() > 0:
                cancel_btn.first.click(timeout=3000)
                print("팝업 닫기: 작성중인 글 취소")
                random_sleep()
        except:
            pass
            
        try:
            help_close = editor_context.locator("button.se-help-panel-close-button")
            if help_close.count() > 0:
                help_close.first.click(timeout=3000)
                print("팝업 닫기: 도움말 패널 닫기")
                random_sleep()
        except:
            pass

        # Input Title
        print("제목 입력...")
        title_loc = editor_context.locator(".se-documentTitle").first
        title_loc.click(timeout=30000)
        # Using keyboard.type instead of fill since the wrapper div isn't contenteditable
        page.keyboard.type(title, delay=50)
        random_sleep(1, 2)
        
        # Click exactly below the title to focus the empty canvas!
        print("본문 캔버스로 포커스 이동...")
        try:
            # If we know the title's location, click physically below it
            box = title_loc.bounding_box()
            if box:
                # Add offset to click inside the main body container
                page.mouse.click(box["x"] + 50, box["y"] + box["height"] + 150)
                random_sleep(1.0, 2.0)
            else:
                title_loc.press('Enter')
                random_sleep(1.0, 2.0)
        except Exception as e:
            print("캔버스 클릭 시도 오류:", e)
            title_loc.press('Enter')
        
        # Writing HTML to clipboard via javascript inside the browser context
        print("본문 HTML 삽입 중...")
        
        parts = html_content.split('&lt;p&gt;[차트 이미지 삽입 위치]&lt;/p&gt;')
        if len(parts) == 1:
            # Fallback if markdown didn't wrap it in <p>
            parts = html_content.split('[차트 이미지 삽입 위치]')
            
        images_list = images if images else []
        
        for i, part in enumerate(parts):
            if part.strip():
                # Apply center alignment and line-height directly to HTML tags
                for tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']:
                    part = part.replace(f'<{tag}>', f'<{tag} style="text-align:center; line-height:1.8;">')
                
                safe_html = part.replace('`', '\\`').replace('$', '\\$')
                # Naver Editor compatibility: 1. Bold formatting, 2. Add explicit empty line block after each paragraph
                safe_html = safe_html.replace('<strong>', '<strong style="font-weight:bold;">').replace('<b>', '<b style="font-weight:bold;">')
                safe_html = safe_html.replace('</p>', '</p><p style="text-align:center;"><br></p>')
                
                script = f"""
                async () => {{
                    const blob = new Blob([`{safe_html}`], {{type: 'text/html'}});
                    const clipboardItem = new window.ClipboardItem({{ 'text/html': blob }});
                    await navigator.clipboard.write([clipboardItem]);
                }}
                """
                page.evaluate(script)
                random_sleep(0.5, 1.0)
                
                # Paste it in the body locator
                page.keyboard.press('Control+V')
                random_sleep(1.5, 2.5)
            
            # Upload image if available and expected at this position
            if i < len(parts) - 1 and i < len(images_list):
                img_path = images_list[i]
                abs_img_path = os.path.abspath(img_path)
                print(f"이미지 업로드 중: {abs_img_path}")
                try:
                    with page.expect_file_chooser(timeout=10000) as fc_info:
                        editor_context.locator('button.se-image-toolbar-button, button[data-tooltip="사진"], button:has-text("사진")').first.click()
                    
                    file_chooser = fc_info.value
                    file_chooser.set_files(abs_img_path)
                    print("이미지 업로드 완료. 렌더링 대기 중...")
                    random_sleep(5, 7) # Wait for image rendering
                    
                    # Prevent text clashing with the image by moving cursor down
                    page.keyboard.press('ArrowDown')
                    page.keyboard.press('Enter')
                    random_sleep(0.5, 1.0)
                except Exception as e:
                    print(f"이미지 업로드 실패 ({img_path}): {e}")
            
        print("본문 입력 완료")
        
        # Click Save as Draft (임시저장)
        print("임시저장 중...")
        save_btn = page.locator("button:has-text('저장'), button.btn_save, button.se-btn-save").first
        save_btn.click()
        random_sleep(3, 5)
        
        print("네이버 블로그 임시저장(Draft) 처리가 완료되었습니다!")
        
        context.storage_state(path=AUTH_FILE)
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naver Blog Auto Poster")
    parser.add_argument('--file', type=str, default='output/post_0900_20260413.md', help="Markdown file to post")
    parser.add_argument('--images', nargs='+', help="List of image paths to upload")
    parser.add_argument('--headless', action='store_true', help="Run without UI")
    args = parser.parse_args()
    
    run_poster(args.file, images=args.images, headless=args.headless)
