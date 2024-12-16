import ddddocr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re

class captcha():
  def __init__(self):
    self.driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--start-maximized'))
    self.wait = WebDriverWait(self.driver, 10)

  def openWindow(self, id, url):
    self.driver.get(url)
    time.sleep(2)
    self.handler(id)
  
  def handler(self, id):
    # 輸入ID
    id_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='txtUID']")))
    id_input.send_keys(id)

    # 獲取驗證碼 避免重複請求驗證碼，使用截圖方式辨識
    captcha_img = self.driver.find_element(By.XPATH, "//img[@id='img_valid']")
    captcha_img.screenshot('captcha.png')
    captcha_code = self.getAuthCode()
    captcha_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='validCode']")))
    captcha_input.send_keys(captcha_code)

    # 點擊登錄按鈕
    submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='submit']")))
    submit_button.click()
    
    time.sleep(1)

    # html = self.driver.page_source # 獲取網頁 HTML
    # soup = self.parse_page(html)
    # inputs = soup.find_all('input', attrs={"campaignname": re.compile(r".*保費.*")}) # 正則表達
    
    # for input_tag in inputs:
    #   print(input_tag, 'input_tag ***************')

    checkbox = self.driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][value="2024004703"]') # CSS 選擇器效能高
    checkbox.click()

    time.sleep(100)

  def getAuthCode(self):    
    ocr = ddddocr.DdddOcr() # ddddocr.DdddOcr(beta=True) #第二套 ocr 模型

    with open("captcha.png", 'rb') as f: # with 自動關閉檔案
      return ocr.classification(f.read())
    
  def parse_page(self, html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def job():
  url = 'https://www.bankchb.com/frontend/CampaignLog.html' # 彰銀
  # url = 'https://card.esunbank.com.tw/EsunCreditweb/txnservice/identify?PRJCD=ALLACTIV#b' # 玉山

  id = 'A123456789'
  c = captcha()
  c.openWindow(id, url)

if __name__ == "__main__":
  try:
    job()
  except KeyboardInterrupt:
    print("結束執行")