from typing import Tuple, Any

import math
import time
import json
import re
import sys
import os
import requests

from requests_toolbelt import MultipartEncoder



def _convert_size(bytes_size: int)-> str:
    if bytes_size == 0:
        return "0B"
    name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes_size, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_size/p, 2)
    return f"{s} {name[i]}"

def _countdown(wait_time: int)-> str:
    while wait_time:
        minutes, seconds = divmod(wait_time, 60)
        timer = f"{minutes}:{seconds}"
        print(timer, end="\r")
        time.sleep(1)
        wait_time -= 1
    return timer

class Uptobox(object):
    def __init__(self, token: str):
        self.api_url = "https://uptobox.com/api"
        # Put your token here, find it here: https://uptobox.com/my_account
        self.token = token
        self.regex = r"https?:\/\/uptobox\.com\/(?P<code>[a-zA-Z0-9]+)"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"}

    def get_user_status(self)-> int:
        request = requests.get(f"{self.api_url}/user/me?token={self.token}").text
        info = json.loads(request)
        premium_check = info["data"]["premium"]
        return premium_check

    def get_file_info(self, code: str)-> Tuple[Any, Any]:
        if code.startswith("https://uptobox.com"):
            code = re.findall(self.regex, code)[0]
        request = requests.get(f"{self.api_url}/link/info?fileCodes={code}").text
        info = json.loads(request)
        file_name = info["data"]["list"][0]["file_name"]
        file_size = _convert_size(info["data"]["list"][0]["file_size"])
        return file_name, file_size

    def file_search(self, path: str, limit: int, search: str)-> Tuple[Any, Any, Any]:
        request = requests.get(f"{self.api_url}/user/files?token={self.token}&path={path}&limit={limit}&searchField=file_name&search={search}").text
        info = json.loads(request)
        files_name, files_size, files_code = [], [], []
        for element in info["data"]["files"]:
            files_name.append(element["file_name"])
            files_size.append(element["file_size"])
            files_code.append(element["file_code"])
        return files_name, files_size, files_code

    def get_download_link(self, code: str)-> str:
        if code.startswith("https://uptobox.com"):
            code = re.findall(self.regex, code)[0]
        if self.get_user_status() == 1:
            request = requests.get(f"{self.api_url}/link?token={self.token}&file_code={code}").text
            info = json.loads(request)
            download_link = info["data"]["dlLink"]
        else:
            request = requests.get(f"{self.api_url}/link?token={self.token}&file_code={code}").text
            info = json.loads(request)
            waiting_time = info["data"]["waiting"] + 1
            waiting_token = info["data"]["waiting_token"]
            print(f"[Uptobox] You have to wait {waiting_time} seconds to generate a new link.\n[Uptobox] Do you want to wait ?")
            answer = input("Y for yes, everything else to quit: ")
            if answer.upper() == "Y":
                _countdown(waiting_time)
                request = requests.get(f"{self.api_url}/link?token={self.token}&file_code={code}&waiting_token={waiting_token}").text
                info = json.loads(request)
                download_link = info["data"]["dlLink"]
            else:
                sys.exit(1)
        return download_link

    def get_upload_url(self)-> str:
        request = requests.get(f"{self.api_url}/upload?token={self.token}").text
        info = json.loads(request)
        upload_url = info["data"]["uploadLink"]
        return upload_url

    def upload(self, file: str)-> str:
        field = os.path.basename(file), open(file, "rb")
        multi = MultipartEncoder(fields={"files": (field)})
        self.headers["Content-Type"] = multi.content_type
        request = requests.post(f"https:{self.get_upload_url()}", data=multi, headers=self.headers).text
        info = json.loads(request)
        return info["files"][0]["url"]
