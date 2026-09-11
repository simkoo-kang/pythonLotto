import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 불필요한 시스템 경고 숨기기
sys.stderr = open(os.devnull, 'w')

def crawl_lotto_remodeling_final(drw_no):
    url = "https://dhlottery.co.kr/lt6645/result"
    
    print("🌐 리모델링 특수 UI 대응형 Selenium 브라우저를 구동합니다...")
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        print("🔄 메인 페이지 접속 완료. 화면 로딩 대기 중 (3초)...")
        time.sleep(3)
        
        # 💡 핵심 수정 1: 커스텀 드롭다운 메뉴 상자를 먼저 클릭하여 회차 목록을 엽니다.
        # 동행복권 새 디자인의 회차 선택 영역 버튼을 찾아 클릭합니다.
        print("🖱️ 회차 선택 드롭다운 메뉴를 클릭하여 엽니다...")
        dropdown_trigger = driver.find_element(By.CLASS_NAME, "d-trigger") # 혹은 구조에 맞는 클래스/ID로 매핑
        dropdown_trigger.click()
        time.sleep(1)
        
        # 💡 핵심 수정 2: 열린 <ul> 목록 안에서 내가 원하는 회차 <li> 요소를 정확히 찾아 클릭합니다.
        # 예: "1238회" 텍스트를 가진 요소를 바로 타겟팅하여 클릭을 유도합니다.
        target_round_text = f"{drw_no}회"
        print(f"🎯 회차 목록에서 [{target_round_text}] 요소를 찾아 클릭합니다...")
        
        # 텍스트 내용으로 li 요소를 찾는 xpath 문법을 활용합니다.
        target_li = driver.find_element(By.XPATH, f"//ul//li[contains(text(), '{target_round_text}')]")
        target_li.click()
        time.sleep(1)
        
        # 💡 핵심 수정 3: 회차가 선택되었으니 옆에 있는 '조회하기' 버튼을 누릅니다.
        search_btn = driver.find_element(By.ID, "searchBtn")
        search_btn.click()
        print("🚀 '조회하기' 버튼 클릭 완료! 데이터를 새로고침합니다...")
        
        # 자바스크립트가 서버에서 표 데이터를 다 받아와 화면을 새로 그릴 때까지 넉넉히 대기
        time.sleep(4)
        
        # 자바스크립트 최종 연산 결과가 반영된 HTML 소스 낚아채기
        html_content = driver.page_source
        driver.quit() # 브라우저 종료
        
        # BeautifulSoup 파싱 시작
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 1. 당첨번호 및 보너스 번호 추출
        win_balls = soup.select(".num.win span")
        bonus_ball = soup.select_one(".num.bonus span")
        
        if not win_balls:
            print("❌ 화면 파싱 실패: 자바스크립트 표가 리로딩되지 않았거나 태그 구조가 다릅니다.")
            return
            
        numbers = [ball.text.strip() for ball in win_balls]
        bonus = bonus_ball.text.strip() if bonus_ball else "N/A"
        
        # 2. 등수별 상세 당첨정보 테이블 파싱
        table_rows = soup.select("table.tbl_data tbody tr")
        
        print("\n========================================================")
        print(f"🎉 로또 6/45 제 {drw_no}회 상세 당첨 결과 (ul/li 메뉴 제어 성공)")
        print("========================================================")
        print(f"▶ 당첨 번호 : {', '.join(numbers)}  [보너스: {bonus}]")
        print("--------------------------------------------------------")
        print(f"{'순위':^4} | {'총 당첨금액':^14} | {'당첨자수':^7} | {'1인당 당첨금액':^14}")
        print("--------------------------------------------------------")
        
        for row in table_rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                rank = cols[0].text.strip()
                total_amount = cols[1].text.strip()
                winner_count = cols[3].text.strip()
                single_amount = cols[4].text.strip()
                
                if "명" in total_amount or "게임" in total_amount:
                    winner_count = cols[2].text.strip()
                    single_amount = cols[3].text.strip()
                    total_amount = "고정액지급"
                
                print(f"{rank:^5} | {total_amount:>13} | {winner_count:>6} | {single_amount:>13}")
                
        print("========================================================")
        
    except Exception as e:
        print(f"❌ 크롤링 제어 중 예외 에러 발생: {e}")
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == "__main__":
    target_round = 1238
    crawl_lotto_remodeling_final(target_round)
