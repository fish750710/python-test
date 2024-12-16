# 使用虛擬環境pyenv,查詢執行路徑
import os,sys
print(sys.prefix)
print(sys.path)
# 修正路徑
# sys.path[0] = "C:\\Users\\USER\\Desktop\\my-electron-app\\for_electron_pyenv\\Lib\\site-packages"
# print(sys.path)
# 自動化模組
from selenium import webdriver
from selenium.webdriver.common.by import By
# 時間模組
from datetime import datetime, timedelta
import time
# 圖像模組
from PIL import Image
# 驗證碼辨識模組
import ddddocr
#正則表示模組
import re
# 隨機亂數模組
import random

import configparser
import subprocess
import psutil
import winreg
from selenium.webdriver.chrome.options import Options

# 產生符合註冊帳號&密碼規則的亂數
# def randomlist():
#     randomlist = (
#     random.choices('abcdefghijklmnopqrstuvwxyz',k=1)[0], #小寫取1位
#     random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=1)[0], #大寫取1位
#     str(random.randrange(100000,1000000,1))              #數字取1個6-7位數的數字
#     )
#     result = "".join(randomlist)#處理成一個字串
#     return result

def regular_account(loop, Account):
    # 將 loop 轉換為字符串然後用零填充到4位
    number_part = str(loop).zfill(4)
    return Account + number_part

def create_phone():
    second = random.choice([3, 4, 5, 7, 8])
    third = random.choice([0, 1, 2, 3, 5, 6, 7, 8, 9]) if second != 4 else random.choice([5, 7, 9])
    suffix = ''.join(str(random.randint(0, 9)) for _ in range(8))
    return f"1{second}{third}{suffix}"

def deal_prove_code(img):
    ocr = ddddocr.DdddOcr()
    with open(img, 'rb') as f:
        return ocr.classification(f.read())

def catch_prove_code_picture(driver, imgpath):
    charts = driver.find_element(By.XPATH, imgpath)
    location = charts.location
    size = charts.size
    driver.save_screenshot("screenshot.png")
    image = Image.open("screenshot.png")
    left, top = location['x'], location['y']
    right, bottom = left + size['width'], top + size['height']
    image.crop((left, top, right, bottom)).save("cropped.png")

def log_request_response(request, response, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"Request URL: {request.url}\n")
        f.write(f"Request Method: {request.method}\n")
        f.write(f"Request Headers: {request.headers}\n")
        f.write(f"Request Body: {request.body}\n")
        f.write(f"Response Status: {response.status_code}\n")
        f.write(f"Response Headers: {response.headers}\n")
        f.write(f"Response Body: {response.body}\n")
        f.write("-" * 50 + "\n")

import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_config_value(config, section, key, fallback):
    value = config.get(section, key, fallback=fallback)
    return fallback if value == '' else value

def auto_signup_main_4(url, AccountNumber, Counts, Account, money, Password=None, Username=None):
    AccountNumber = int(AccountNumber)
    Counts = int(Counts)
    target = AccountNumber + Counts
    loop = AccountNumber

    config = configparser.ConfigParser()
    config.read('config.ini')

    # 添加這些行來打印 config 的內容
    logging.info("Config sections: %s", config.sections())
    for section in config.sections():
        logging.info("Section: %s", section)
        for key, value in config.items(section):
            logging.info("  %s = %s", key, value)

    # 為每個 XPath 設置一個有效的默認值
    imgpath = get_config_value(config, 'Xpath4', 'imgpath', "//img[@class='__TRv7h']")
    toastinfopath = get_config_value(config, 'Xpath4', 'toastinfopath', "//*[@id='root']/div[2]/div/div/div/span")
    accountpath = get_config_value(config, 'Xpath4', 'accountpath', "//input[@placeholder='6-15位，字母开头的字母与数字']")
    passwordpath = get_config_value(config, 'Xpath4', 'passwordpath', "//input[@placeholder='8-16位，包含大小写字母与数字']")
    confirmpasswordpath = get_config_value(config, 'Xpath4', 'confirmpasswordpath', "//input[@placeholder='确认密码']")
    chechcodepath = get_config_value(config, 'Xpath4', 'chechcodepath', "//input[@placeholder='请输入验证码']")
    phonepath = get_config_value(config, 'Xpath4', 'phonepath', "//input[@placeholder='请输入手机号']")
    usernamepath = get_config_value(config, 'Xpath4', 'usernamepath', "//input[@placeholder='请输入真实姓名']")
    submitpath = get_config_value(config, 'Xpath4', 'submitpath', "//div[@class='__aV66w']/p[1]")
    loginid = get_config_value(config, 'Xpath4', 'loginid', "//*[@id='root']/div[2]/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div[2]/span")
    url_04_mine = get_config_value(config, 'Url', 'url_04_mine', url)

    # 記錄所有 XPath
    logging.info(f"imgpath: {imgpath}")
    logging.info(f"toastinfopath: {toastinfopath}")
    logging.info(f"accountpath: {accountpath}")
    logging.info(f"passwordpath: {passwordpath}")
    logging.info(f"confirmpasswordpath: {confirmpasswordpath}")
    logging.info(f"chechcodepath: {chechcodepath}")
    logging.info(f"phonepath: {phonepath}")
    logging.info(f"usernamepath: {usernamepath}")
    logging.info(f"submitpath: {submitpath}")
    logging.info(f"loginid: {loginid}")
    logging.info(f"url_04_mine: {url_04_mine}")

    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(468, 1000)

    while loop < target:
        try:
            logging.info(f"Starting registration for account number {loop}")
            logging.info(f"Navigating to URL: {url}")
            driver.get(url)
            time.sleep(3)  # 等待頁面加載
            
            if toastinfopath:
                try:
                    logging.info(f"Attempting to click toast info at: {toastinfopath}")
                    driver.find_element(By.XPATH, toastinfopath).click()
                    time.sleep(1)
                except Exception as e:
                    logging.warning(f"Toast info not found or not clickable: {e}")

            if imgpath:
                try:
                    logging.info(f"Attempting to catch prove code picture at: {imgpath}")
                    catch_prove_code_picture(driver, imgpath)
                    text = deal_prove_code("cropped.png")
                    logging.info(f"Prove code text: {text}")

                    if len(text) != 4:
                        logging.warning("Invalid prove code length, continuing to next iteration")
                        continue
                except Exception as e:
                    logging.error(f"Error in catching or processing prove code: {e}")
                    continue

            input_fields = {
                "Account": accountpath,
                "Password": passwordpath,
                "Confirm Password": confirmpasswordpath,
                "Check Code": chechcodepath
            }

            elements = {}
            for field, xpath in input_fields.items():
                if xpath:
                    try:
                        logging.info(f"Finding {field} input field at: {xpath}")
                        elements[field] = driver.find_element(By.XPATH, xpath)
                    except Exception as e:
                        logging.error(f"Error finding {field} input field: {e}")
                else:
                    logging.error(f"{field} XPath is empty")

            if len(elements) != 4:
                logging.error("One or more required input fields not found")
                continue
            
            if phonepath:
                try:
                    logging.info(f"Finding phone input field at: {phonepath}")
                    e5 = driver.find_element(By.XPATH, phonepath)
                    e5.clear()
                    phone = create_phone()
                    logging.info(f"Entering phone number: {phone}")
                    e5.send_keys(phone)
                except Exception as e:
                    logging.warning(f"No phone selection or error: {e}")

            if usernamepath:
                try:
                    logging.info(f"Finding username input field at: {usernamepath}")
                    e6 = driver.find_element(By.XPATH, usernamepath)
                    e6.clear()
                    username = Username if Username else "Default_username"
                    logging.info(f"Entering username: {username}")
                    e6.send_keys(username)
                except Exception as e:
                    logging.warning(f"No real name selection or error: {e}")

            useraccount = regular_account(loop, Account)
            pw = Password if Password else "Aa1234567"

            logging.info(f"Attempting to register account: {useraccount}")

            # 填寫表單
            for field, element in elements.items():
                element.clear()
                if field == "Account":
                    element.send_keys(useraccount)
                elif field in ["Password", "Confirm Password"]:
                    element.send_keys(pw)
                elif field == "Check Code":
                    element.send_keys(text)

            # 點擊提交按鈕
            if submitpath:
                try:
                    logging.info(f"Clicking submit button at: {submitpath}")
                    driver.find_element(By.XPATH, submitpath).click()
                    time.sleep(3)  # 等待註冊過程完成
                except Exception as e:
                    logging.error(f"Error clicking submit button: {e}")
                    continue

            # 驗證註冊是否成功
            logging.info(f"Navigating to URL to verify registration: {url_04_mine}")
            driver.get(url_04_mine)
            time.sleep(3)  # 等待頁面加載
            
            if loginid:
                try:
                    name = driver.find_element(By.XPATH, loginid)
                    if name.text == useraccount:
                        logging.info(f"Registration successful for account: {useraccount}")
                        # 註冊成功，記錄賬號信息
                        now = datetime.now()
                        with open('output4.txt', 'a') as f:
                            f.write('\n'.join([str(now), useraccount, pw, money, '\n']))
                        loop += 1  # 只有在確認註冊成功後才增加 loop
                    else:
                        logging.warning(f"Registration failed for account: {useraccount}")
                except Exception as e:
                    logging.warning(f"Unable to verify registration: {e}")
            else:
                logging.warning("Login ID XPath is empty, unable to verify registration")

        except Exception as e:
            logging.error(f"An error occurred during registration: {e}")

        logging.info(f"Completed attempt for account number {loop}")
        time.sleep(3)  # 在嘗試下一個註冊之前稍作等待

    driver.quit()
    logging.info(f"Signup process completed. Registered {loop - AccountNumber} accounts.")

# Uncomment and modify the following line to run the function
# auto_signup_main_4(url='https://sporttest.8betest4qnbh.com/#/register', AccountNumber="8", Counts="2", Account="Thedog", money="200000", Password="Aa1234567", Username="")

# 在文件末尾添加以下測試代碼
if __name__ == "__main__":
    # 測試參數
    test_url = 'https://sporttest.btest4wohjelay.com/#/register'
    test_account_number = "1"
    test_counts = "3"
    test_account = "zxbbsev"
    test_money = "100000"
    test_password = "Aa1234567"  # 這裡可以設置自定義密碼
    test_username = "TestUser"

    print("Starting test of auto_signup_main_4 function...")
    
    try:
        auto_signup_main_4(
            url=test_url,
            AccountNumber=test_account_number,
            Counts=test_counts,
            Account=test_account,
            money=test_money,
            Password=test_password,
            Username=test_username
        )
        print("Test completed successfully.")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

    print("Test finished.")