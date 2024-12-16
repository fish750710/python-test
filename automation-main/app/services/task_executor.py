import json
import logging
from app.services.task_service import TaskService
from app.services.be_function import BeFunction
from app.services.member import create_account_hierarchy, create_batch_accounts, create_list_accounts, Member
from app.services.fe_bet import Bet
from app import db

logger = logging.getLogger(__name__)

def execute_task(app, task):
    with app.app_context():
        try:
            logger.info(f"Starting to execute task: {task.id}")
            TaskService.update_task_status(task.id, 'processing')  # 更新為處理中狀態

            login_params = {k: task.params[k] for k in ['site', 'url', 'busername', 'bpassword', 'key']}
            detailed_result = {}

            if task.task_type == "register_batch":
                detailed_result = execute_register_batch(task, login_params)
            elif task.task_type == "add_money":
                detailed_result = execute_add_money(task, login_params)
            elif task.task_type == "bet":
                detailed_result = execute_bet(task, login_params)
            elif task.task_type == "register_agent":
                detailed_result = execute_register_agent(task, login_params)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            # 檢查操作結果
            if detailed_result:
                # 檢查是否有錯誤信息
                if any(isinstance(v, dict) and 'error' in v for v in detailed_result.values()):
                    error_msg = next(v['error'] for v in detailed_result.values() if isinstance(v, dict) and 'error' in v)
                    TaskService.update_task_status(task.id, "failed", json.dumps(detailed_result, ensure_ascii=False), error_msg)
                # 檢查加錢結果
                elif 'add_money_result' in detailed_result and detailed_result['add_money_result'] != "操作成功":
                    TaskService.update_task_status(task.id, "failed", json.dumps(detailed_result, ensure_ascii=False), detailed_result['add_money_result'])
                # 檢查下注結果
                elif 'bet_result' in detailed_result and detailed_result['bet_result'] != "操作成功":
                    TaskService.update_task_status(task.id, "failed", json.dumps(detailed_result, ensure_ascii=False), detailed_result['bet_result'])
                # 檢查批量操作結果
                elif 'failed_count' in detailed_result and detailed_result['failed_count'] > 0:
                    TaskService.update_task_status(task.id, "failed", json.dumps(detailed_result, ensure_ascii=False), "Some operations failed")
                else:
                    TaskService.update_task_status(task.id, "completed", json.dumps(detailed_result, ensure_ascii=False))
            else:
                TaskService.update_task_status(task.id, "failed", json.dumps({"error": "No result returned"}, ensure_ascii=False))

            logger.info(f"Task {task.id} processed with result: {detailed_result}")

        except Exception as e:
            logger.error(f"Error executing task: {str(e)}", exc_info=True)
            TaskService.update_task_status(task.id, "failed", json.dumps({"error": str(e)}, ensure_ascii=False), str(e))
        finally:
            db.session.remove()  # 確保會話被清理

def execute_register_batch(task, login_params):
    if task.params['batch_type'] == 'number':
        start = int(task.params['start'])
        end = int(task.params['end'])
        result = create_batch_accounts(
            start, end, 
            login_params['site'], 
            login_params['url'],
            id_prefix=task.params['id_prefix'], 
            password=task.params['password'], 
            note=task.params['note']
        )
    else:  # list
        account_list = task.params['account_list'].split(',')
        result = create_list_accounts(
            account_list,
            login_params['site'],
            login_params['url'],
            password=task.params['password'],
            note=task.params['note']
        )

    success_accounts = [account for account in result if account.get('success', False)]
    failed_accounts = [account for account in result if not account.get('success', False)]
    
    detailed_result = {
        'success_count': len(success_accounts),
        'failed_count': len(failed_accounts),
        'failed_details': [{'id': account['id'], 'reason': account.get('reason', 'Unknown error')} for account in failed_accounts]
    }

    if task.params.get('add_money_after_register'):
        detailed_result['add_money_results'] = execute_add_money_for_accounts(task, login_params, success_accounts)

    if task.params.get('bet_after_register'):
        detailed_result['bet_results'] = execute_bet_for_accounts(task, login_params, success_accounts)

    return detailed_result

def execute_add_money(task, login_params):
    be_function = BeFunction(**login_params)
    try:
        operation_params = {
            'userid': task.params.get('userid'),
            'money': float(task.params.get('money', 0)),
            'betrate': float(task.params.get('betrate', 0)),
            'currency': task.params.get('currency', 'BRL'),
            'type': task.params.get('type', 'bonus')
        }
        be_function.add_money(userid = operation_params['userid'],
                            money=operation_params['money'],
                            betrate=operation_params['betrate'],
                            currency=operation_params['currency'],
                            type=operation_params['type'])
        return {"add_money_result": "操作成功"}
    except Exception as e:
        return {"add_money_result": str(e)}

def execute_bet(task, login_params):
    try:
        bet_function = Bet(login_params['site'], login_params['url'])
        bet_amount = task.params['bet_amount']
        
        member = Member(site=login_params['site'], url=login_params['url'])
        member.login_register(
            username=task.params['userid'],
            password=task.params['password']
        )
        
        bet_function.betssc(bet_amount, member.token, member.traceid)
        return {"bet_result": "操作成功"}
    except Exception as e:
        return {"bet_result": str(e)}

def execute_register_agent(task, login_params):
    try:
        structure = json.loads(task.params['structure'])
    except json.JSONDecodeError:
        structure = task.params['structure']  # 使用原始字符串
    
    result = create_account_hierarchy(
        structure=structure,
        site=login_params['site'],
        url=login_params['url'],
        id_prefix=task.params['id_prefix'],
        password=task.params['password'],
        note=task.params['note']
    )

    success_accounts = [account for account in result if account.get('success', False)]
    failed_accounts = [account for account in result if not account.get('success', False)]
    
    detailed_result = {
        'success_count': len(success_accounts),
        'failed_count': len(failed_accounts),
        'failed_details': [{'id': account['id'], 'reason': account.get('reason', 'Unknown error')} for account in failed_accounts]
    }

    if task.params.get('add_money_after_register'):
        detailed_result['add_money_results'] = execute_add_money_for_accounts(task, login_params, success_accounts)

    if task.params.get('bet_after_register'):
        detailed_result['bet_results'] = execute_bet_for_accounts(task, login_params, success_accounts)

    return detailed_result

def execute_add_money_for_accounts(task, login_params, accounts):
    be_function = BeFunction(**login_params)
    money_amount = float(task.params.get('money_amount', 0))
    currency = task.params.get('currency', 'BRL')
    money_type = task.params.get('type', 'bonus')
    betrate = float(task.params.get('betrate', 0))
    
    add_money_results = []
    for account in accounts:
        try:
            result = be_function.add_money(
                userid=account['id'], 
                money=money_amount,
                currency=currency,
                type=money_type,
                betrate=betrate
            )
            add_money_results.append({"id": account['id'], "result": "Success"})
        except Exception as e:
            add_money_results.append({"id": account['id'], "result": "Failed", "error": str(e)})
    
    return add_money_results

def execute_bet_for_accounts(task, login_params, accounts):
    bet_function = Bet(login_params['site'], login_params['url'])
    bet_amount = float(task.params.get('bet_amount', 0))
    
    bet_results = []
    for account in accounts:
        try:
            result = bet_function.betssc(
                bet_amount,
                account['token'],
                account['traceid']
            )
            bet_results.append({"id": account['id'], "result": "Success"})
        except Exception as e:
            bet_results.append({"id": account['id'], "result": "Failed", "error": str(e)})
    
    return bet_results
