import schedule
import time
import logging
from datetime import datetime, timedelta
from viptest import main, check_previous_accounts

# 設置日誌 建立 viptest.log
logger = logging.getLogger('scheduler')
logger.setLevel(logging.INFO)

# 創建文件處理器 建立 scheduler.log
file_handler = logging.FileHandler('scheduler.log', encoding='utf-8')
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

# 保存已執行的時間點
executed_time_slots = []

def register_job():
    time_slot = datetime.now().strftime('%Y%m%d_%H%M')
    logger.info(f"開始執行註冊腳本... 時間點: {time_slot}")
    main(time_slot)
    executed_time_slots.append(time_slot)
    
    # 檢查之前註冊的帳號
    if len(executed_time_slots) > 1:
        logger.info("開始檢查之前註冊的帳號...")
        check_previous_accounts(executed_time_slots[:-1])  # 不包括最新的時間點

 # 設置定時任務
timeArray = ['13:35', '13:47','13:55', '14:00']
for sTime in timeArray:
    schedule.every().day.at(sTime).do(register_job)

def get_next_run_time():
    next_run = schedule.next_run()
    if next_run:
        return next_run
    return None

wait_time = 1 # 等待的秒數
while True:
    nowTime = datetime.now()
    schedule.run_pending()
    next_run = get_next_run_time()
    time_difference = next_run - nowTime    
    timeLeft = time_difference.total_seconds()

    if next_run:
        if (timeLeft > 0 ):
            time.sleep(wait_time)
            wait_time = timeLeft
            mins, secs = divmod(time_difference.seconds, 60)
            hours, mins = divmod(mins, 60)
            timeFormat = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
            logger.info(f"距離下一次執行還有: {timeFormat}")
    else:
        wait_time = 1
        logger.info('排程結束')
        break

# schedule.every().day.at("23:48").do(register_job)
# schedule.every().day.at("23:58").do(register_job)
# schedule.every().day.at("00:08").do(register_job)
# schedule.every().day.at("00:30").do(register_job)
# schedule.every().day.at("00:48").do(register_job)
# schedule.every().day.at("00:58").do(register_job)
# schedule.every().day.at("01:08").do(register_job)
# schedule.every().day.at("01:18").do(register_job)
# schedule.every().day.at("10:48").do(register_job)
# schedule.every().day.at("10:58").do(register_job)
# schedule.every().day.at("11:08").do(register_job)
# schedule.every().day.at("11:18").do(register_job)
# schedule.every().day.at("11:30").do(register_job)
# schedule.every().day.at("11:48").do(register_job)
# schedule.every().day.at("11:58").do(register_job)
# schedule.every().day.at("12:08").do(register_job)
# schedule.every().day.at("12:18").do(register_job)

# def countdown_to_next_run():
#     next_run = get_next_run_time()
#     print(next_run, 'next_run')
#     if next_run:
#         while True:
#             now = datetime.now()
#             if now >= next_run:
#                 break
#             remaining_time = next_run - now
#             mins, secs = divmod(remaining_time.seconds, 60)
#             hours, mins = divmod(mins, 60)
#             timeformat = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
#             logger.info(f"距離下一次執行還有: {timeformat}")
#             time.sleep(1)

# while True:
#     schedule.run_pending()
#     countdown_to_next_run()



