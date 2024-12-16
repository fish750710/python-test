
import requests
from datetime import datetime
import json
import os
import logging
import schedule
import time

class Spider():
  def __init__(self):    
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    # 設置日誌
    self.logger = logging.getLogger('house')
    self.logger.setLevel(logging.INFO)

    # 創建文件處理器
    file_handler = logging.FileHandler('house.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 設置日誌格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 添加處理器到日誌器
    self.logger.addHandler(file_handler)
  
  def getOldHouseList(self, option):
    """獲取舊的房屋列表"""
    try:
      filename = f'house/house_data_{option}.json'
      if (not os.path.exists(filename)):
        return []
      with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f);
    except FileExistsError:
      self.logger.warning(f"找不到房屋文件: {filename}")
      return []
  
  def saveHouseList(self, data, option):
    """保存房屋列表"""
    try:
    # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # filename = f'house/house_{timestamp}.json'
      filename = f'house/house_data_{option}.json'
      with open(filename, 'w', encoding='utf-8') as f: # w:寫 r:讀 a:追加
        json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"房屋信息保存到: {filename}")
    except FileExistsError:
      self.logger.warning(f"儲存失敗: {filename}")

  def send_tg_message(self, message):
    
    tg_token = '7278668891:AAGywDZYzmwO5HkK5ukcudFD5S8dYi2eZfE'
    tg_chat_id = '6075365477' # 取ID: https://api.telegram.org/bot7278668891:AAGywDZYzmwO5HkK5ukcudFD5S8dYi2eZfE/getUpdates
    message = f"有新房屋: {message}"
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    params = {
      'chat_id': tg_chat_id,
      'text': message
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
      self.logger.info("Telegram message sent successfully.")
    else:
      self.logger.error(f"Failed to send Telegram message. Status code: {response.status_code}")

  def search(self, filter_params = None, sort_params = None, option = 'sale'):
    """591搜索"""
    total_count = 0
    house_list = []
    page = 0
    new_house_list = []
    response = None

    params = {
      **filter_params,
      **sort_params
    }

    url = f'https://{option}.591.com.tw/home/housing/list-search'
    print(url, 'url')

    try:
      response = requests.get(url, headers=self.headers, params=params)
      if (response.status_code == 200):
        print("SUCCESS!")
        data = response.json()
        total_count = data['data']['total']
        house_list.extend(data['data']['items'])

        # 建立目錄
        if not os.path.exists('house'):
          os.makedirs('house')

        old_house_list = self.getOldHouseList(option)

        old_house_dict = {h['hid']: h for h in old_house_list if 'hid' in h} # 產生字典
        new_house_list = [h for h in house_list if 'hid' in h and h['hid'] not in old_house_dict] # 新的列表比對舊的列表，有沒有新的房屋

        # self.send_tg_message('https://sale.591.com.tw/home/house/detail/2/16852445.html')
        if (len(new_house_list) > 0):
          message = ""
          for new_house in new_house_list:
            if (option == 'sale'):
              message += f"\nhttps://sale.591.com.tw/home/house/detail/2/{new_house['hid']}.html\n"
            else:
              message += f"\nhttps://{option}.591.com.tw/{new_house['hid']}\n"

          self.send_tg_message(message)
          self.logger.info(f"有新的房屋: {len(new_house_list)}")

        self.saveHouseList(house_list, option)

      else:
        print("FAILED!")
    except requests.RequestException as e:
      print(f"請求錯誤：{e}")
      return None

    return total_count, house_list

def job():
  print("Cron job is running...")

  house591 = Spider()

  # 中古屋和出租返回是html，無法使用
  option = 'newhouse' # sale:中古屋 rent:出租 newhouse:新建案

  filter_params = {
    'keyword': '',
    'regionid': '3', #地區 1: 台北 3: 新北
    'sectionid': '47,43', #分區 47: 蘆洲, 43: 三重

    # 'room': '3', # 房數
    # 'total_price': '2', # 2:1000~1500 3:1500~2500
    #'shape': '7' # 7:電梯 10:華夏 3:住宅
  }

  # 排序
  sort_params = {
    # 'sort': '1', #金額低到高
    # 'order': 'asc'
  }

  total_count, houses = house591.search(filter_params, sort_params, option)
  print('總筆數:', total_count)
  # print('房屋清單:', houses)

if __name__ == '__main__':
  # schedule.every().hour.do(job) # 每小時執行
  try:
  
    while True:
      # schedule.run_pending()
      # time.sleep(1)
      job()
      time.sleep(60 * 60) # 每小時執行
  except KeyboardInterrupt:
    print("結束執行")
  