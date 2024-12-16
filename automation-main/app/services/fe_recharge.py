import requests
import uuid
import json
import datetime
from urllib.parse import urlparse
from cryptmodel.encrypt import encrypt_ecb
from cryptmodel.decrypt import decrypt_aes

class Recharge:
    RECHARGE_URL = "/v1/pc/submitPayOrder"
    def __init__(self, site, url):
        self.url=url
        self.host=urlparse(self.url).netloc
        self.sscid=None
        self.site=site
        self.order_id = None
        self.Sitetime = None
        self.headers = {
            'Connection': 'keep-alive',
            'Channelid': '4',
            'Content-Type': 'application/json',
            'Host': urlparse(self.url).netloc,
            'Site': self.site,
            'Languagecode': 'pt_BR',
            'X-Auth-Token': None,
            'Traceid': None,
            'Origin': self.url,
            'Referer': self.url,
            'Sitetime' : None,
            'Uuid': None,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }
    
    def update_headers(self, token, traceid):
        self.Sitetime = str(int(datetime.datetime.now().timestamp() * 1000))
        self.headers["Traceid"] = traceid
        self.headers["X-Auth-Token"] = token
        self.headers["Sitetime"] = self.Sitetime
        self.headers["Uuid"] = str(uuid.uuid4())
        

    def recharge(self, busiAmount, channelId, subColumnCode, token, traceid):
        url=self.url+self.RECHARGE_URL
        self.update_headers(token, traceid)
        print(self.headers)
        payload={
            "busiAmount":busiAmount,
            "channelId":channelId,
            "subColumnCode":subColumnCode,
        }
        encrypt_payload=json.dumps({"data":encrypt_ecb(payload,self.site,self.Sitetime)})
        response = requests.post(url=url, headers=self.headers, data=encrypt_payload)
        try:
            response_data = decrypt_aes(response.text,self.site,self.Sitetime)
            print(response_data)
            if response_data.get('message') == '操作成功':
                self.order_id = response_data.get('result').get('orderId')
                print(self.order_id)
                return True
        except Exception as e:
            raise Exception(f"充值失败: {str(e)}")
