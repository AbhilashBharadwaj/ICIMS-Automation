import pickle


class CookieManager:
    def __init__(self, driver, cookies_path):
        self.driver = driver
        self.cookies_path = cookies_path

    def save_cookies(self):
        with open(self.cookies_path, "wb") as filehandler:
            cookies_dump = self.driver.get_cookies()
            print(cookies_dump)
            pickle.dump(cookies_dump, filehandler)

    def load_cookies(self):
        with open(self.cookies_path, "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                if "expiry" in cookie:
                    del cookie["expiry"]
                self.driver.add_cookie(cookie)
