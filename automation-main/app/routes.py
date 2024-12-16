import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.task_service import TaskService
from threading import Thread

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_task':
            thread = Thread(target=add_task_async, args=(current_app._get_current_object(), request.form))
            thread.start()
            return jsonify({'result': 'Task addition started'})
    
    all_tasks = TaskService.get_all_tasks()
    return render_template('task.html', tasks=all_tasks)

@bp.route('/upay')
def upay():
    return render_template('upay.html')

def add_task_async(app, form_data):
    with app.app_context():
        try:
            task_type = form_data.get('task_type')
            app.logger.debug(f"Received task_type: {task_type}")
            app.logger.debug(f"Form data: {form_data}")

            login_params = {
                'site': form_data.get('site'),
                'url': form_data.get('url'),
                'busername': form_data.get('busername'),
                'bpassword': form_data.get('bpassword'),
                'key': form_data.get('key')
            }
            
            if task_type == 'add_money':
                operation_params = {
                    'userid': form_data.get('userid'),
                    'money': form_data.get('money'),
                    'betrate': form_data.get('betrate', 0),
                    'currency': form_data.get('currency', 'CNY'),
                    'type': form_data.get('type', 'bonus')
                }
            elif task_type == 'register_batch':
                operation_params = {
                    'batch_type': form_data.get('batch_type'),
                    'id_prefix': form_data.get('id_prefix'),
                    'password': form_data.get('password'),
                    'note': form_data.get('note'),
                    'add_money_after_register': form_data.get('add_money_after_register') == 'on',
                    'bet_after_register': form_data.get('bet_after_register') == 'on'
                }
                
                if operation_params['batch_type'] == 'number':
                    operation_params['start'] = form_data.get('start')
                    operation_params['end'] = form_data.get('end')
                elif operation_params['batch_type'] == 'list':
                    operation_params['account_list'] = form_data.get('account_list')
                
                if operation_params['add_money_after_register']:
                    operation_params.update({
                        'money_amount': form_data.get('money_amount'),
                        'currency': form_data.get('currency', 'BRL'),
                        'betrate': form_data.get('betrate', 0),
                        'type': form_data.get('type', 'bonus')
                    })
                
                if operation_params['bet_after_register']:
                    operation_params['bet_amount'] = form_data.get('bet_amount')
            
            elif task_type == 'register_agent':
                operation_params = {
                    'structure': form_data.get('structure'),
                    'id_prefix': form_data.get('id_prefix'),
                    'password': form_data.get('password'),
                    'note': form_data.get('note'),
                    'add_money_after_register': form_data.get('add_money_after_register') == 'on',
                    'bet_after_register': form_data.get('bet_after_register') == 'on'
                }
                
                if operation_params['add_money_after_register']:
                    operation_params.update({
                        'money_amount': form_data.get('money_amount'),
                        'currency': form_data.get('currency', 'BRL'),
                        'betrate': form_data.get('betrate', 0),
                        'type': form_data.get('type', 'bonus')
                    })
                
                if operation_params['bet_after_register']:
                    operation_params['bet_amount'] = form_data.get('bet_amount')
            
            elif task_type == 'bet':
                operation_params = {
                    'userid': form_data.get('userid'),
                    'password': form_data.get('password'),
                    'bet_amount': form_data.get('bet_amount')
                }
            
            params = {**login_params, **operation_params}
            TaskService.add_task(task_type, params)
        except Exception as e:
            app.logger.error(f'Error adding task: {str(e)}')

@bp.route('/tasks', methods=['GET'])
def get_tasks_status():
    tasks = TaskService.get_all_tasks()
    return jsonify({'tasks': [task.to_dict() for task in tasks]})

@bp.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        with current_app.app_context():
            TaskService.cleanup_completed_tasks()
        logger.info("Database cleaned up successfully")
        return jsonify({'result': 'Database cleaned up successfully'})
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")
        return jsonify({'error': 'Failed to clean up database'}), 500
