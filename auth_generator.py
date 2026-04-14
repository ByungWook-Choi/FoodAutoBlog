from playwright.sync_api import sync_playwright

def generate_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://nid.naver.com/nidlogin.login")
        print("브라우저가 열렸습니다. 직접 로그인을 진행해주세요.")
        print("로그인이 완료되고 네이버 메인화면으로 이동하면, 로그인 세션(auth.json)이 자동으로 저장됩니다.")
        
        # Wait indefinitely until login is complete and it redirects to naver.com main page
        try:
            page.wait_for_url("https://www.naver.com/**", timeout=0)
            context.storage_state(path="auth.json")
            print("세션 정보(auth.json) 저장이 완료되었습니다!")
        except Exception as e:
            print(f"오류: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    generate_auth()
