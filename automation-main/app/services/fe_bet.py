import requests
import uuid
import json
import datetime
from urllib.parse import urlparse
from cryptmodel.encrypt import encrypt_ecb
from cryptmodel.decrypt import decrypt_aes

class Bet:
    LGET_URL = "/v1/y/a"
    BET_URL = "/v1/y/d"
    GET_URL = "/v1/y/c"
    def __init__(self,site,url):
        self.url=url
        self.host=urlparse(self.url).netloc
        self.sscid=None
        self.site=site
        self.Sitetime= str(int(datetime.datetime.now().timestamp()*1000))
        self.headers = {
            'Connection': 'keep-alive',
            'Channelid': '4',
            'Content-Type': 'application/json',
            'Host': urlparse(self.url).netloc,
            'Site': self.site,
            'Languagecode': 'pt_BR',
            'Traceid': None,
            'Origin': self.url,
            'Referer': self.url,
            'Sitetime' : self.Sitetime,
            'Uuid': str(uuid.uuid4()),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }

    def getssc(self,token):
        headers = self.headers
        headers["X-Auth-Token"] = token
        payload={"lotteryCode":"SSCJS","page":{"current":1,"size":20}}
        url=self.url+self.GET_URL
        encrypt_payload=json.dumps({"data":encrypt_ecb(payload,self.site,self.Sitetime)})
        response = requests.post(url=url, headers=headers, data=encrypt_payload)
        response_data = decrypt_aes(response.text,self.site,self.Sitetime)
        rowId = response_data.get('result').get('records')[0].get('rowId')
        return rowId
        
    def betssc(self, unitAmount, token, traceid):
        headers = self.headers
        headers["X-Auth-Token"] = token
        headers["Traceid"] = traceid
        payload=[{"issueId":int(self.getssc(token))+1,"lotteryCode":"SSCJS","playCode1":"SSC","playCode2":"LM","playCode3":"LH","betContent":["P17"],"unitAmount":str(unitAmount),"playCode2Name":"两面","playCode3Name":"总和","betOdds":"1.96"}]
        url=self.url+self.BET_URL
        encrypt_payload=json.dumps({"data":encrypt_ecb(payload,self.site,self.Sitetime)})
        response = requests.post(url=url, headers=headers, data=encrypt_payload)
        try:
            response_data = decrypt_aes(response.text,self.site,self.Sitetime)
            message = response_data.get('message')
            if message == "操作成功":
                print("下注成功")
                return True
            else:
                raise Exception(f"下注失败: {message}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"下注请求错误: {str(e)}")
        except Exception as e:
            raise Exception(f"下注过程中发生错误: {str(e)}")
