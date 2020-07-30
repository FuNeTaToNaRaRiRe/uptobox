import math
import time
import requests
import json
import re
import sys
import os

from requests_toolbelt import MultipartEncoder

def convert_size(bytes_size: int):
    if bytes_size == 0:
        return "0B"
    name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes_size, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_size/p, 2)
    return f"{s} {name[i]}"

def countdown(wait_time: int):
    while wait_time:
        minutes, seconds = divmod(wait_time, 60)
        timer = f"{minutes}:{seconds}"
        print(timer, end="\r")
        time.sleep(1)
        wait_time -= 1
    return timer

class Uptobox(object):
    def __init__(self, token):
        self.api_url = "https://uptobox.com/api"
        # Put your token here, find it here: https://uptobox.com/my_account
        self.token = token
        self.regex = r"https?:\/\/uptobox\.com\/(?P<code>[a-zA-Z0-9]+)"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"
        }

    def get_user_status(self):
        request = requests.get(f"{self.api_url}/user/me?token={self.token}").text
        info = json.loads(request)
        premium_check = info["data"]["premium"]
        return premium_check

    def get_file_info(self, code: str):
        if code.startswith("https://uptobox.com"):
            code = re.findall(self.regex, code)[0]
        request = requests.get(f"{self.api_url}/link/info?fileCodes={code}").text
        info = json.loads(request)
        file_name = info["data"]["list"][0]["file_name"]
        file_size = convert_size(info["data"]["list"][0]["file_size"])
        return file_name, file_size

    def file_search(self, path: str, limit: int, search: str):
        request = requests.get(f"{self.api_url}/user/files?token={self.token}&path={path}&limit={limit}&searchField=file_name&search={search}").text
        info = json.loads(request)
        for element in info["data"]["files"]:
            file_name = element["file_name"]
            file_size = element["file_size"]
            file_code = element["file_code"]
            return file_name, file_size, file_code

    def get_download_link(self, code: str):
        if code.startswith("https://uptobox.com"):
            code = re.findall(self.regex, code)[0]
        if self.get_user_status() == 1:
            request = requests.get(f"{self.api_url}/link?token={self.token}&file_code={code}").text
            info = json.loads(request)
            download_link = info["data"]["dlLink"]
            return download_link
        else:
            request = requests.get(f"{self.api_url}/link?token={self.token}&file_code={code}").text
            info = json.loads(request)
            waitingTime = info["data"]["waiting"] + 1
            waitingToken = info["data"]["waitingToken"]
            print(f"[Uptobox] You have to wait {waitingTime} seconds to generate a new link.\n[Uptobox] Do you want to wait ?")
            answer = input("Y for yes, everything else to quit: ")
            if answer.upper() == "Y":
                countdown(waitingTime)
                request = requests.get(f"{self.api_url}/link?token={self.token}&file_code={code}&waitingToken={waitingToken}").text
                info = json.loads(request)
                download_link = info["data"]["dlLink"]
                return download_link
            else:
                sys.exit(1)

    def get_upload_url(self):
        request = requests.get(f"{self.api_url}/upload?token={self.token}").text
        info = json.loads(request)
        upload_url = info["data"]["uploadLink"]
        return upload_url

    def upload(self, file: str):
        field = os.path.basename(file), open(file, "rb")
        multi = MultipartEncoder(fields={
            "files": (field)
        })
        self.headers["Content-Type"] = multi.content_type
        request = requests.post(f"https:{self.get_upload_url()}", data=multi, headers=self.headers).text
        info = json.loads(request)
        return info["files"][0]["url"]
