from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from constants import *


class InternetSpeedTwitterBot(webdriver.Chrome):
    """Class to get your current internet upload and download speeds.
       If the speeds are below what is in your ISP contract, a tweet
       is sent to your ISP to complain about their service.
    """

    def __init__(self, driver_path: str = DRIVER_PATH, down: int = PROMISED_DOWN,
                 up: int = PROMISED_UP, teardown: bool = False) -> None:
        self.u_speed = None
        self.d_speed = None
        self.tweet = None
        self.driver_path = driver_path
        self.down = down
        self.up = up
        self.service = Service(self.driver_path)
        self.teardown = teardown
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super(InternetSpeedTwitterBot, self).__init__(service=self.service, options=options)
        self.maximize_window()
        self.implicitly_wait(15)

    def __str__(self):
        return f"InternetSpeedTwitterBot(promised_download={self.down}, promised_upload={self.up})"

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def get_internet_speed(self, url: str = SPEEDTEST_URL):
        """Function the checks the current internet speed of your ISP using speedtest.net"""
        self.get(url)
        start_speedtest = self.find_element(By.CLASS_NAME, "start-button")
        start_speedtest.click()
        sleep(60)

        d_speed_element = self.find_element(By.CLASS_NAME, "download-speed")
        self.d_speed = float(d_speed_element.get_attribute("innerHTML"))

        u_speed_element = self.find_element(By.CLASS_NAME, "upload-speed")
        self.u_speed = float(u_speed_element.get_attribute("innerHTML"))

        print(f"down: {self.d_speed}\nup: {self.u_speed}")

    def check_speed(self):
        """Function that checks current internet speeds vs ISP promised speeds"""
        if (self.d_speed < self.down) or (self.u_speed < self.up):
            self.tweet = f"Hey Internet Service Provider, why is my internet speed: {self.d_speed} down" \
                    f" and {self.u_speed} up when it is supposed to be {self.down} down and {self.up} up?"
            # print(self.tweet)
            return True
        return False

    def tweet_complaint(self, url: str = TWITTER_URL, username: str = TWITTER_USERNAME, passwd: str = TWITTER_PASSWD):
        """Function to sign in to Twitter and tweet a complaint at my ISP if my current internet
           speeds are less that their promised internet speeds"""
        if self.check_speed():
            self.get(url)
            sign_in = self.find_element(By.CSS_SELECTOR, 'a[data-testid="loginButton"]')
            sign_in.click()

            user_name = self.find_element(
                By.XPATH,
                '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div['
                '5]/label/div/div[2]/div/input')
            user_name.send_keys(username)
            user_name.send_keys(Keys.ENTER)

            password = self.find_element(
                By.XPATH,
                '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div['
                '3]/div/label/div/div[2]/div[1]/input')
            password.send_keys(passwd)

            login = self.find_element(By.CSS_SELECTOR, 'div[data-testid="LoginForm_Login_Button"]')
            login.click()

            tweet_btn = self.find_element(By.CSS_SELECTOR, 'a[aria-label="Tweet"]')
            tweet_btn.click()
            tweet_msg = self.find_element(By.CLASS_NAME, "public-DraftStyleDefault-block")
            tweet_msg.send_keys(self.tweet)
            send_tweet = self.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetButton"]')
            send_tweet.click()
        else:
            print(f"Your internet speeds, {self.d_speed} down and {self.u_speed} up, are where your ISP promised.")
