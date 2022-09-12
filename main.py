from speedtest import InternetSpeedTwitterBot

with InternetSpeedTwitterBot(teardown=True) as bot:
    bot.get_internet_speed()
    bot.tweet_complaint()
