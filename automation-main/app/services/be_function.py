import requests
import json
import hashlib
import uuid
import pyotp
import datetime
import logging
from cryptmodel.encrypt import encrypt_ecb
from cryptmodel.decrypt import decrypt_aes
from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BeFunction:
    LOGIN_URL = "/v1/ad/login"
    RECHARGE_URL = "/v1/acct/manualRecharge"
    GET_ROWID_URL = "/v1/acct/queryAcctInfo"
    GIVE_BONUS_URL = "/v1/acct/giveBonus"

    def __init__(self, site, url, busername, bpassword, key):
        self.site = site
        self.url = url
        self.busername = busername
        self.bpassword = bpassword
        self.key = key
        self.headers = None
        self.Sitetime = None
        self.session = requests.Session()
        logger.info(f"Initializing BeFunction with: site={site}, url={url}, busername={busername}, key={key}")

    def login(self):
        logger.info("Attempting to login...")
        self.Sitetime = str(int(datetime.datetime.now().timestamp() * 1000))
        psmd5 = hashlib.md5(self.bpassword.encode()).hexdigest()
        validcode = pyotp.TOTP(self.key).now()
        url = self.url + self.LOGIN_URL
        payload = {
            "userId": self.busername,
            "password": psmd5,
            "verifyCode": validcode
        }
        logger.debug(f"Login payload: {payload}")
        self.headers = {
            "Bundleid": "20240702152053",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "channelId": "3",
            "Site": self.site,
            "Host": urlparse(self.url).netloc,
            "Origin": self.url,
            "Referer": self.url,
            "Sitetime": self.Sitetime,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Traceid": "ab90712b-7e45-459b-919e-d976fab7a1df",
            "Uuid": str(uuid.uuid4())
        }
        try:
            encrypt_payload = json.dumps({"data": encrypt_ecb(payload, self.site, self.Sitetime)})
            logger.debug(f"Encrypted payload: {encrypt_payload}")
        except Exception as e:
            logger.error(f"Error during payload encryption: {str(e)}")
            return "Login failed: Encryption error"

        try:
            response = self.session.post(url=url, headers=self.headers, data=encrypt_payload)
            logger.info(f"Login response status code: {response.status_code}")
            logger.debug(f"Login response headers: {response.headers}")
            logger.debug(f"Login response content: {response.text}")
            response.raise_for_status()
            self.headers["X-Auth-Token"] = response.headers.get("X-Auth-Token")
            print(self.headers["X-Auth-Token"])
            if not self.headers["X-Auth-Token"]:
                logger.error("X-Auth-Token not found in response headers")
                return "Login failed: No auth token received"
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during login: {str(e)}")
            return f"Login failed: {str(e)}"

        logger.info("Login attempt completed successfully")
        return "Login successful"

    def add_money(self, userid, money, betrate=0, currency="BRL", type="Bonus"):
        if not self.headers or not self.headers.get("X-Auth-Token"):
            logger.warning("No auth token, attempting to login again")
            login_result = self.login()
            if login_result != "Login successful":
                return login_result
        
        self.Sitetime = str(int(datetime.datetime.now().timestamp() * 1000))
        self.headers["Sitetime"] = self.Sitetime
        
        try:
            betrate = int(betrate) if betrate else 0
            currency = str(currency).upper() if currency else "BRL"
        except ValueError:
            betrate = 0
            currency = "BRL"
        
        payload = {
            "amount": int(money),
            "betRate": betrate,
            "currency": str(currency).upper(),
            "memberId": str(userid),
            "memberRowId": str(self.get_rowid(userid)),
            "platformGameCodes": None
        }
        if type.lower() == "manual":
            url = self.url + self.RECHARGE_URL
        elif type.lower() == "bonus":
            url = self.url + self.GIVE_BONUS_URL
        else:
            logger.error(f"Invalid type: {type}")
            return "Invalid type"
        
        try:
            encrypt_payload = json.dumps({"data": encrypt_ecb(payload, self.site, self.Sitetime)})
            logger.debug(f"Encrypted add_money payload: {encrypt_payload}")
        except Exception as e:
            logger.error(f"Error during add_money payload encryption: {str(e)}")
            return "Add money failed: Encryption error"

        try:
            response = self.session.post(url=url, headers=self.headers, data=encrypt_payload)
            logger.info(f"Add money response status code: {response.status_code}")
            logger.debug(f"Add money response content: {response.text}")
            response.raise_for_status()
            try:
                response_data = decrypt_aes(response.text, self.site, self.Sitetime)
            except Exception as e:
                response_data = response.text
            if response_data.get("message") == "操作成功":
                print(f"{userid} 加钱成功 {money}")
                return True
            else:
                print(f"{userid} 加钱失败 {response_data.get('message')}")
                raise Exception(f"加钱失败: {response_data.get('message')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"加钱请求错误: {str(e)}")
        except Exception as e:
            raise Exception(f"加钱过程中发生错误: {str(e)}")

    def get_rowid(self, userid):
        if not self.headers or not self.headers.get("X-Auth-Token"):
            logger.warning("No auth token, attempting to login again")
            login_result = self.login()
            if login_result != "Login successful":
                return login_result
        
        self.Sitetime = str(int(datetime.datetime.now().timestamp() * 1000))
        self.headers["Sitetime"] = self.Sitetime
        
        payload = {
            "memberId": str(userid),
        }
        url = self.url + self.GET_ROWID_URL
        try:
            encrypt_payload = json.dumps({"data": encrypt_ecb(payload, self.site, self.Sitetime)})
            logger.debug(f"Encrypted get_rowid payload: {encrypt_payload}")
        except Exception as e:
            logger.error(f"Error during get_rowid payload encryption: {str(e)}")
            return "Get rowid failed: Encryption error"

        try:
            response = self.session.post(url=url, headers=self.headers, data=encrypt_payload)
            logger.info(f"Get rowid response status code: {response.status_code}")
            logger.info(f"Get rowid response content: {response.text}")
            response.raise_for_status()
            response_data = decrypt_aes(response.text, self.site, self.Sitetime)
            logger.info(f"Decrypted get_rowid response: {response_data}")
            if response_data.get("message") == '操作成功':
                return response_data.get("result").get("memberRowId")
            else:
                raise Exception(response_data.get("message"))
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during get_rowid: {str(e)}")
            return f"Get rowid failed: {str(e)}"
