import hashlib
import json
import uuid
import datetime
import requests
from urllib.parse import urljoin
from cryptmodel.encrypt import encrypt_ecb
from cryptmodel.decrypt import decrypt_aes

class Member:
    LOGIN_URL = "/v1/mc/loginMember"
    REGISTER_URL = "/v1/mc/newMember"

    def __init__(self, site=None, url=None):
        self.url = url
        self.site = site
        self.username = None
        self.password = None
        self.token = None
        self.rowid = None
        self.note = None
        self.invitationCode = None
        self.headers = self.generate_headers()
        self.session = requests.Session()  
        self.last_operation_message = None

    def __str__(self):
        return f"username: {self.username}, token: {self.token}, rowID: {self.rowid}"

    def generate_headers(self):
        self.traceid = str(uuid.uuid4())
        headers = {
            "site": self.site,
            'bundleid': '2024.8.20',
            'channelid': '4',
            'content-type': 'application/json',
            "traceid": self.traceid,
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        }
        self.update_headers(headers)
        return headers
    
    def update_headers(self, headers=None):
        current_time = int(datetime.datetime.now().timestamp() * 1000)
        if headers is None:
            self.headers.update({
                "sitetime": str(current_time),
                "uuid": str(uuid.uuid4()),
                "x-auth-token": self.token if self.token else None
            })
        else:
            headers.update({
                "sitetime": str(current_time),
                "uuid": str(uuid.uuid4()),
                "x-auth-token": self.token if self.token else None
            })
        self.headers = headers

    def create_payload(self):
        return {
            "memberId": self.username,
            "memberPwd": self.md5_encrypt(self.password),
            "confirmPwd": self.md5_encrypt(self.password),
            "channelId": "4",
            "downloadSite": self.url,
            "telephone": "",
            "smsCode": "",
            "disableCodeDisabled": False,
            "memberName": "",
            "validateCode": "",
            "languageCode": "zh",
            "invitationCode": self.invitationCode,
            "requestMethod": 0,
            "areaCode": "",
            "currency": "BRL",
            "note": self.note
        }

    def login_register(self, username, password, note=None, invitationCode=None):
        if not username or not password:
            self.last_operation_message = "用户名和密码不能为空"
            return False
        self.username = username
        self.password = password
        self.note = note
        self.invitationCode = invitationCode
        headers = self.get_login_and_register_setting()
        payload = self.create_payload()
        register_url = urljoin(self.url, self.REGISTER_URL)
        login_url = urljoin(self.url, self.LOGIN_URL)
        self.update_headers(headers)

        encrypt_payload = json.dumps({"data": encrypt_ecb(payload, self.site, headers.get("sitetime"))})
        try:
            print("尝试注册")
            response = self.session.post(url=register_url, headers=headers, data=encrypt_payload) 
            result, message = self.handle_response(response, headers)
            if result == False:
                if message == "数据已存在,请重新输入":
                    print("数据已存在,尝试登录")
                    response = self.session.post(url=login_url, headers=headers, data=encrypt_payload) 
                    result, message = self.handle_response(response, headers)
                    if result:
                        self.last_operation_message = f"{username} 登录成功"
                        print("登录成功")
                        return True
                    else:
                        self.last_operation_message = f"{username} 登录失败: {message}"
                        print("登录失败")
                    return False
                else:
                    self.last_operation_message = f"{username} 注册失败: {message}"
                    return False
            elif result == True:
                self.last_operation_message = f"{username} 注册成功"
                print("注册成功")
                return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求错误：{str(e)}")

    def handle_response(self, response, headers):
        try:
            response.raise_for_status()
            response_data = decrypt_aes(response.text, self.site, headers.get("sitetime"))
            if not isinstance(response_data, dict):
                return False, "解密后的响应数据格式不正确"
            result = response_data.get("result", {})
            message = response_data.get("message")
            if message == "操作成功":
                self.rowid = result.get("rowId")
                self.token = headers.get("x-auth-token")  # 更新 token
                return True, message
            else:
                return False, message
        except requests.exceptions.HTTPError as http_err:
            return False, f"HTTP 错误发生：{http_err}"
        except Exception as err:
            return False, f"其他错误发生：{err}"

    def get_login_and_register_setting(self):
        headers = self.headers.copy()
        self.update_headers(headers)
        token_url = urljoin(self.url, "/v1/ad/getLoginAndRegisterSetting")
        payload = {}
        encrypt_payload = json.dumps({
            "data": encrypt_ecb(payload, self.site, headers.get("sitetime")),
            "data1": "{}",
            "keyStr": "1111test" + headers.get("sitetime")[-8:],
        })
        try:
            response = self.session.post(url=token_url, headers=headers, data=encrypt_payload)  # 使用 session
            response.raise_for_status()
            xtoken = response.headers.get("X-Auth-Token")
            content_length = response.headers.get("Content-Lengths")
            if not xtoken:
                print("未能獲取 X-Auth-Token")
                return {}
            else:
                self.token = xtoken
            authr = self.get_auth(xtoken, content_length)
            headers.update({
                "authorization": authr
            })
            return headers
        except requests.exceptions.RequestException as e:
            print(f"請求錯誤：{e}")
            return {}

    def get_auth(self, xtoken, content_length):
        if xtoken is None:
            return None
        second_char = content_length[1] if len(content_length) > 1 else None
        if second_char:
            modified_xtoken = xtoken.replace(second_char, '')
        else:
            modified_xtoken = xtoken
        md5_hash = self.md5_encrypt(modified_xtoken)
        return md5_hash

    @staticmethod
    def md5_encrypt(text):
        if not isinstance(text, str):
            text = str(text)
        md5 = hashlib.md5()
        md5.update(text.encode("utf-8"))
        return md5.hexdigest()

def create_account_hierarchy(structure, site, url, parent_rowid=None, id_prefix='test', password='Aa123456', note=None):
    accounts = []
    
    if isinstance(structure, str):
        handler = Member(site=site, url=url)
        success = handler.login_register(id_prefix + structure, password, note, invitationCode=parent_rowid)
        if success:
            return [{
                'id': id_prefix + structure,
                'rowid': handler.rowid,
                'token': handler.token,
                'traceid': handler.traceid,
                'children': [],
                'success': True
            }]
        else:
            return [{
                'id': id_prefix + structure,
                'success': False,
                'reason': handler.last_operation_message
            }]
    
    elif isinstance(structure, list):
        for item in structure:
            accounts.extend(create_account_hierarchy(item, site, url, parent_rowid, id_prefix, password, note))
        return accounts
    
    elif isinstance(structure, dict):
        for parent, children in structure.items():
            handler = Member(site=site, url=url)
            success = handler.login_register(id_prefix + parent, password, note, invitationCode=parent_rowid)
            if success:
                parent_account = {
                    'id': id_prefix + parent,
                    'rowid': handler.rowid,
                    'token': handler.token,
                    'traceid': handler.traceid,
                    'children': create_account_hierarchy(children, site, url, handler.rowid, id_prefix, password, note),
                    'success': True
                }
            else:
                parent_account = {
                    'id': id_prefix + parent,
                    'success': False,
                    'reason': handler.last_operation_message,
                    'children': []
                }
            accounts.append(parent_account)
        return accounts

def create_batch_accounts(start, end, site, url, id_prefix='test', password='Aa123456', note=None):
    accounts = []
    for i in range(start, end + 1):
        handler = Member(site=site, url=url)
        account_id = f"{id_prefix}{i}"
        success = handler.login_register(account_id, password, note)
        if success:
            accounts.append({
                'id': account_id,
                'rowid': handler.rowid,
                'token': handler.token,
                'traceid': handler.traceid,
                'children': [],
                'success': True
            })
        else:
            accounts.append({
                'id': account_id,
                'success': False,
                'reason': handler.last_operation_message
            })
    return accounts

def create_list_accounts(account_list, site, url, password, note=None):
    accounts = []
    for account in account_list:
        member = Member(site=site, url=url)
        success = member.login_register(username=account, password=password, note=note)
        if success:
            accounts.append({
                'id': account,
                'rowid': member.rowid,
                'token': member.token,
                'traceid': member.traceid,
                'children': [],
                'success': True
            })
        else:
            accounts.append({
                'id': account,
                'success': False,
                'reason': member.last_operation_message  # 假设 Member 类有这个属性来存储最后一次操作的消息
            })
    return accounts


if __name__ == "__main__":
    print(create_list_accounts(1, 3, 'gvtst0fo', 'https://h5.cad2sg.top', id_prefix='testaws', password='Aa123456'))