
from selenium import webdriver
import chromedriver_binary
import functions
import time


# WebDriver のオプションを設定する
options = webdriver.ChromeOptions()
#画像読み込みを省略して軽量化
#options.add_argument('--blink-settings=imagesEnabled=false')
#↓動作確認のためコメントアウト
#options.add_argument('--headless') 

print('connecting to remote browser...')
#chromedriver起動
driver = webdriver.Chrome(options=options)
#ページロード中などfind_elementで要素が見つからない際の暗黙的な待機を最大30秒に設定　▶各処理に対する明示的待機にて上書き不能のため、全体に適用される暗黙待機は実装しない
#driver.implicitly_wait(30)

functions.login(driver)
functions.move_to_top_page(driver, False)

# ブラウザを終了する(最終画面からの操作猶予30分)
time.sleep(1800)
driver.quit()

