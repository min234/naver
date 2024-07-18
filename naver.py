from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pymysql

def naver():
    try:
        # 드라이버 설정
        path = r'C:\project\chromedriver-win64\chromedriver.exe'
        service = Service(path)
        options = Options()
        driver = webdriver.Chrome(service=service, options=options)

        url = 'https://shopping.naver.com/home'
        driver.get(url)

        time.sleep(3)
        conn = pymysql.connect(host='127.0.0.1', user='root', password='alsdnr7676', db='naver', charset='utf8')
        cur = conn.cursor()
        cur.execute("SELECT * FROM naver")

        time.sleep(2)
        # 검색어 입력
        key = input('keyword: ')
        keyword = driver.find_element(By.CLASS_NAME, '_searchInput_search_text_3CUDs')
        keyword.send_keys(key)
        driver.find_element(By.CLASS_NAME, '_searchInput_button_search_1n1aw').click()

        time.sleep(3)

        page_no = 1
        item_no = 0
        while True:
            # 스크롤 및 데이터 추출
            target_height = 12500
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                current_height = driver.execute_script("return document.body.scrollHeight")

                if current_height >= target_height:
                    break

            # 페이지 소스 가져오기
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            # 아이템 정보 추출
            items = soup.find_all("div", class_="product_info_area__xxCTi")
            
            for item in items:
                item_no += 1
                name_tag = item.find("a", class_="product_link__TrAac linkAnchor")
                
                if name_tag:
                    name = name_tag.get_text()
                    href = name_tag.get("href")
                    price_tag = item.find("em")
                    price = price_tag.get_text() if price_tag else "가격 정보 없음"

                    print(f"{item_no}. 제목: {name}")
                    print(f"가격: {price}원")
                    print(f"링크: {href}")
                    
                    try:
                        cur.execute(
                            "INSERT INTO naver (no, no_name, no_price, no_link) VALUES (%s, %s, %s, %s)",
                            (item_no, name, price, href)
                        )
                        conn.commit()
                    except Exception as e:
                        print(f"데이터 삽입 중 오류 발생: {e}")
                    
                    time.sleep(2)

            time.sleep(3)
            cur.close()
            conn.close()
                   
            
            try:
                page_xpath = f'//*[@id="content"]/div[1]/div[4]/div/a[{page_no}]'
                button = driver.find_element(By.XPATH, page_xpath)
                button.click()
                time.sleep(3)
                page_no += 1  # 다음 페이지로 이동
            except Exception as e:
                print(f"페이지 이동 중 오류 발생: {e}")
                break

               
    except Exception as e:
        print(f"오류 발생: {e}")

    finally:
        driver.quit()
        conn.close()
naver()
