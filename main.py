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
        except:
            print(">> 無法讀取 userdata.json，請確保檔案存在且格式正確 <<")

    async def getLoginScript(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url) as resp:
                if resp.ok:
                    soup = BeautifulSoup(await resp.text(), features="html.parser")
                    print(f"已抓到登入頁面連結")
                    return soup
                else:
                    print(f">> 未抓到登入頁面連結 <<")
                    return None
                
    async def getLoginUrl(self, soup: BeautifulSoup):
        soup = soup.find_all("script")[0]
        
        loginUrl = re.search(r'"(.*?)"', soup.getText(), re.M).group()
        return loginUrl.strip('"')

    async def getLoginHTML(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                if resp.ok:
                    soup = BeautifulSoup(await resp.text(), features="html.parser")
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
                    print(f"登入成功 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")
                else:
                    print(f"登入失敗 - 請確認帳號密碼有無輸入正確 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")

async def main():
    login = LoginClass()

    while True:
        soup = await login.getLoginScript()
        if soup:
            loginUrl = await login.getLoginUrl(soup)
            soup2 = await login.getLoginHTML(loginUrl)
            payload = await login.getLoginForm(soup2)

            if not payload: break

            await login.submitLogin(loginUrl, payload)
        else:
            print(f"目前為連線狀態 - {dt.now(Taipei).strftime('西元%Y | %m月 | %d日 -> %H:%M:%S')}")
            await asyncio.sleep(10)

    input("按下 Enter 鍵以結束程式...")

if __name__ == "__main__":
    asyncio.run(main())