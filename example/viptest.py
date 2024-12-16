import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string
import os
from datetime import datetime
import json

# 設置日誌
logger = logging.getLogger('viptest')
logger.setLevel(logging.INFO)

# 創建文件處理器
file_handler = logging.FileHandler('viptest.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 創建終端處理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 設置日誌格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加處理器到日誌器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def generate_random_credentials():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 12)))
    password = 'Aa1234567'
    return username, password

def take_screenshot(driver, filename, folder_name):
    # 創建指定的資料夾
    folder_path = os.path.join('screenshots', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # 生成帶時間戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_filename = os.path.join(folder_path, f'{filename}_{timestamp}.png')
    driver.save_screenshot(full_filename)
    logger.info(f"截圖已保存: {full_filename}")

def save_accounts(accounts, time_slot):
    # 確保accounts目錄存在
    if not os.path.exists('accounts'):
        os.makedirs('accounts')
    
    # 保存帳號信息
    filename = f'accounts/accounts_{time_slot}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)
    logger.info(f"帳號信息已保存到: {filename}")

def login_and_claim(username, password, folder_name):
    driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--start-maximized'))
    wait = WebDriverWait(driver, 10)
    
    try:
        # 訪問登入頁面
        driver.get("https://h5.cad2sg.top/#/mine")
        time.sleep(2)
        # 點擊登錄按鈕
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='登录' or text()='Login' or text()='Entrar']")))
        login_button.click()
        time.sleep(1)

        # 輸入帳號密碼
        username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入用户名' or @placeholder='Por favor insira o nome de usuario' or @placeholder='Please enter user name']")))
        username_input.send_keys(username)
        
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入密码' or @placeholder='Por favor insira a senha' or @placeholder='Please enter password']")))
        password_input.send_keys(password)

        # 點擊登入
        submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'loginRegister_start')]//span[text()='登录' or text()='Log In' or text()='Entrar']")))
        driver.execute_script("arguments[0].click();", submit_button)

        # 訪問VIP頁面
        driver.get("https://h5.cad2sg.top/#/vip")
        time.sleep(5)

        # 點擊獎勵
        rewards = ['日獎勵', '周獎勵', '月獎勵']
        for reward in rewards:
            try:
                reward_element = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(text(), '可领取') or contains(text(), 'Receber') or contains(text(), 'Receive')]")))
                reward_element.click()
                time.sleep(1)
            except:
                logger.warning(f"無法點擊 {reward}")

        # 登入後截圖
        take_screenshot(driver, f'login_vip_{username}', folder_name)
        
    except Exception as e:
        logger.error(f"登入失敗 {username}: {str(e)}")
        take_screenshot(driver, f'login_error_{username}', folder_name)
    finally:
        driver.quit()

def main(time_slot=None):
    if time_slot is None:
        time_slot = datetime.now().strftime('%Y%m%d_%H%M')
    
    folder_name = f'register_{time_slot}'
    success_count = 0
    retry_count = 0
    accounts = []

    while success_count < 4 and retry_count < 10:
        driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--start-maximized'))
        wait = WebDriverWait(driver, 10)

        try:
            driver.get("https://h5.cad2sg.top/#/mine")
            time.sleep(2)

            register_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='注册' or text()='Register' or text()='Registrar-Se']")))
            register_button.click()
            time.sleep(1)

            username, password = generate_random_credentials()

            # 註冊子類別
            sub_register_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='账号注册']")))
            sub_register_button.click()
            time.sleep(1)

            username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入用户名']")))
            username_input.send_keys(username)

            password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入密码' or @placeholder='Por favor insira a senha' or @placeholder='Please enter password']")))
            password_input.send_keys(password)

            confirm_password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请确认密码' or @placeholder='Confirme sua senha' or @placeholder='Please confirm your password']")))
            confirm_password_input.send_keys(password)

            take_screenshot(driver, f'register_{username}', folder_name)

            submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'loginRegister_start')]//span[text()='立即注册' or text()='Register' or text()='Registrar-Se']")))
            driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(5)

            vip_success = False
            vip_retry_count = 0

            while not vip_success and vip_retry_count < 10:
                try:
                    driver.get("https://h5.cad2sg.top/#/vip")
                    time.sleep(5)

                    rewards = ['日獎勵', '周獎勵', '月獎勵']
                    for reward in rewards:
                        try:
                            reward_element = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, "//div[contains(text(), '可领取') or contains(text(), 'Receber') or contains(text(), 'Receive')]")))
                            reward_element.click()
                            time.sleep(1)
                        except:
                            logger.warning(f"無法點擊 {reward}")

                    take_screenshot(driver, f'register_vip_{username}', folder_name)
                    vip_success = True
                except:
                    logger.warning("無法訪問VIP頁面，重試中...")
                    vip_retry_count += 1
                    time.sleep(60)

            if vip_success:
                success_count += 1
                accounts.append({"username": username, "password": password})
                logger.info(f"完成一次循環，用戶名: {username}, 密碼: {password}")
            else:
                logger.error("VIP頁面重試次數達到上限，結束此帳號操作")
                break

        except Exception as e:
            logger.error(f"發生錯誤: {str(e)}")
            take_screenshot(driver, 'error', folder_name)
            retry_count += 1
            time.sleep(60)

        finally:
            driver.quit()

    logger.info(f"成功次數: {success_count}, 失敗次數: {retry_count}")
    save_accounts(accounts, time_slot)
    return accounts

def check_previous_accounts(time_slots):
    for time_slot in time_slots:
        try:
            # 讀取之前保存的帳號
            filename = f'accounts/accounts_{time_slot}.json'
            if not os.path.exists(filename):
                logger.warning(f"找不到帳號文件: {filename}")
                continue
                
            with open(filename, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            folder_name = f'login_{datetime.now().strftime("%Y%m%d_%H%M")}'
            
            # 為每個帳號執行登入檢查
            for account in accounts:
                login_and_claim(account["username"], account["password"], folder_name)
                time.sleep(2)  # 避免請求過於頻繁
                
        except Exception as e:
            logger.error(f"檢查時段 {time_slot} 的帳號時發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()