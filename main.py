import aiohttp, asyncio, re, json, zoneinfo
from bs4 import BeautifulSoup
from datetime import datetime as dt

Taipei = zoneinfo.ZoneInfo("Asia/Taipei")

class LoginClass():
    def __init__(self):
        self.url = "http://connectivitycheck.gstatic.com/"

        try:
            with open("./userdata.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                self.account = data.get("account", "")
                self.password = data.get("password", "")
            # self.account = input("請輸入帳號：s你的學號@student.ncut.edu.tw\n")
            # self.password = input("請輸入密碼：預設身份證字號\n")
            # self.initial()
        except:
            print(">> 無法讀取 userdata.json，請確保檔案存在且格式正確 <<")

    # def initial(self):
    #     with open("./main.py", mode='r', encoding='utf-8') as jfile:
    #         jdata = jfile.readlines()

    #     for i, data in enumerate(jdata.copy()):
    #         if data.startswith("            self.account = input"):
    #             jdata[i] = re.sub(r"input\(\"請輸入帳號：s你的學號@student.ncut.edu.tw\\n\"\)", f"'{self.account}'", data, flags=re.M)
    #         if data.startswith("            self.password = input"):
    #             jdata[i] = re.sub(r"input\(\"請輸入密碼：預設身份證字號\\n\"\)", f"'{self.password}'", data, flags=re.M)

    #     tempList = jdata.copy()[21:41]
    #     tempList.append(jdata[17])
    #     for temp in tempList:
    #         jdata.remove(temp)

    #     fullstr = "".join(jdata)

    #     with open("./main.py", mode='w', encoding='utf-8') as wfile:
    #         wfile.write(fullstr)

    async def getLoginScript(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url) as resp:
                if resp.ok:
                    soup = BeautifulSoup(await resp.text(), features="html.parser")
                    print(f"已抓到登入頁面腳本 -> {await resp.text()}")
                    return soup
                else:
                    return None
                
    async def getLoginUrl(self, soup: BeautifulSoup):
        soup = soup.find_all("script")[0]
        
        loginUrl = re.search(r'"(.*?)"', soup.getText(), re.M).group().strip('"').strip("'")
        print(f"拿取登入頁面連結 -> {loginUrl}")
        return loginUrl

    async def getLoginHTML(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                if resp.ok:
                    soup = BeautifulSoup(await resp.text(), features="html.parser")
                    print(f"請求登入頁面HTML -> {await resp.text()}")
                    return soup
                else:
                    return None

    async def getLoginForm(self, soup: BeautifulSoup):
        magic_value = soup.find('input', {'name': 'magic'})
        redir_value = soup.find('input', {'name': '4Tredir'})

        if magic_value is None or redir_value is None:
            print(">> 無法找到 magic 或 4Tredir 的值 <<")
            return False
        
        if self.account == "" or self.password == "":
            print(">> 請在 userdata.json 中填寫帳號和密碼 <<")
            return False

        payload = {
            '4Tredir': redir_value['value'],
            'magic': magic_value['value'],
            'username': self.account,
            'password': self.password
        }

        return payload

    async def submitLogin(self, url, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=payload) as resp:
                if resp.ok:
                    print(f"✅登入成功 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")
                else:
                    print(f"❌登入失敗 - 請確認帳號密碼有無輸入正確 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")

async def main():
    login = LoginClass()

    while True:
        try:
            soup = await login.getLoginScript()
            if soup:
                loginUrl = await login.getLoginUrl(soup)
                soup2 = await login.getLoginHTML(loginUrl)
                payload = await login.getLoginForm(soup2)

                if not payload: break

                await login.submitLogin(loginUrl, payload)
                await asyncio.sleep(10)
            else:
                print(f"目前為連線狀態 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")
                await asyncio.sleep(10)
        except:
            print(f"抓取登入頁面錯誤，靜待10秒後重連 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")

    input("按下 Enter 鍵以結束程式...")

if __name__ == "__main__":
    asyncio.run(main())