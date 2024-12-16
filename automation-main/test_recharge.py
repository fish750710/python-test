from app.services.fe_recharge import Recharge
from app.services.fe_member import Member
from app.services.be_function import BeFunction
from concurrent.futures import ThreadPoolExecutor, wait
import time
import random


def process_recharge(token, traceid, site, url, amount):
    start_time = time.time()
    try:
        recharge = Recharge(site, url)
        if recharge.recharge(amount, "4", 396, token, traceid):
            end_time = time.time()
            return recharge.order_id, end_time - start_time
    except Exception as e:
        print(f"Recharge error: {e}")
    return None, 0

def process_pass_order(order, be):
    start_time = time.time()
    try:
        result = be.pass_third_recharge(order)
        end_time = time.time()
        if result:   
            return True, end_time - start_time
        else:
            return False, 0
    except Exception as e:
        print(f"Pass order error for order {order}: {e}")
        return False, 0

if __name__ == "__main__":  
    url = "https://web.5b0iza.top"
    site = "aac60615"
    busername = "QA_script"
    bpassword = "Aa1234567"
    key = "LZIKYCPMXUMGVBQT"

    register_sucess = []
    sucess_order = []
    processing_times = []  # 存储充值处理时间
    backend_times = []     # 存储后台处理时间
    
    # 第一部分：注册用户（保持原样）
    count = 0
    success_count = 0
    for i in range(1,101):
        member = Member(site,url)
        try:
            username = f"testRecharge{i}"
            password = "Aa123456"
            count += 1
            if member.login_register(username, password):
                register_sucess.append([member.token,member.traceid,i])
                success_count += 1
            else:
                time.sleep(1)
                member.login_register(username, password)
                register_sucess.append([member.token,member.traceid,i])
                success_count += 1
                
        except Exception as e:
            print(e)
            continue
    print(f"Register success count: {success_count}/{count}")
    print("sleeping seconds")
    print("Starting concurrent recharge processes...")
    recharge_start_time = time.time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        # 提交充值任务
        recharge_futures = [
            executor.submit(process_recharge, token, traceid, site, url, i)
            for token, traceid, i in register_sucess
        ]
        
        # 等待所有充值任务完成
        wait(recharge_futures)
        
        # 收集成功的订单和处理时间
        for future in recharge_futures:
            order_id, process_time = future.result()
            if order_id:
                sucess_order.append(order_id)
                processing_times.append(process_time)
    
    recharge_total_time = time.time() - recharge_start_time
    avg_recharge_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    print(f"All recharge processes completed : {len(sucess_order)}/{len(register_sucess)}")
    print(f"Total recharge time: {recharge_total_time:.2f} seconds")
    print(f"Average recharge time per order: {avg_recharge_time:.2f} seconds")
    
    print("sleeping seconds")
    # 后台登录
    print("Logging into backend...")
    be = BeFunction(site, url, busername, bpassword, key)
    be.login()
    # 第三部分：并发处理订单
    print("Starting concurrent order processing...")
    backend_start_time = time.time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        # 提交订单处理任务
        pass_futures = [
            executor.submit(process_pass_order, order, be)
            for order in sucess_order
        ]
        
        # 等待所有订单处理任务完成
        wait(pass_futures)
        
        # 统计成功处理的订单数和处理时间
        success_count = 0
        for future in pass_futures:
            success, process_time = future.result()
            if success:
                success_count += 1
                backend_times.append(process_time)
    
    backend_total_time = time.time() - backend_start_time
    avg_backend_time = sum(backend_times) / len(backend_times) if backend_times else 0
    
    print(f"All order processing completed. Successfully processed: {success_count}/{len(sucess_order)}")
    print(f"Total backend processing time: {backend_total_time:.2f} seconds")
    print(f"Average backend processing time per order: {avg_backend_time:.2f} seconds")

    # 输出总体统计
    print("\nPerformance Summary:")
    print(f"总生成订单数量: {len(register_sucess)}")
    print(f"提交成功订单数量: {len(sucess_order)}")
    print(f"出款成功订单数量: {success_count}")
