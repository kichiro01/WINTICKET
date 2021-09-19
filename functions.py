import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
import time

flag = True

def send_notificateion(message):
    header= {"Authorization": f"Bearer {config.ACCESS_TOKEN}"}
    requests.post(config.API_URL, headers=header, data={'message': message},
)

def is_right_page(driver, page):
    if page == config.LOGIN_PAGE_URL:
        #5秒間の間にユーザーID入力フォームが表示されなければログイン画面に遷移していないと判断する
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, '_userId')))
        except Exception as e:
            print(e)
            return False
        else:
            return True
    else:
        print('target_URLが不正です。')
        return False
    
def loop_access(driver, target_url):
    while(True):
        print('Accessing to target URL...')
        driver.get(target_url)
        print('Current URL：{0}'.format(driver.current_url))
        #ターゲットURLじゃなかったらリロードにした方がいいかも
        if driver.current_url != config.LOGIN_PAGE_URL:
            print('アクセス集中ページにリダイレクトされました。')
            send_notificateion('【log】アクセス集中ページにリダイレクトされました。')
            continue
        #一応表示要素で２重チェック
        if is_right_page(driver, target_url):
            print('ACCESS SUCCEED')
            send_notificateion('【log】ログイン画面が表示されました。')
            break
        else:
            print('ロードに時間がかかっているか、アクセス集中ページにリダイレクトされました。')
            send_notificateion('【log】ログイン画面のロードに時間がかかっているか、アクセス集中ページにリダイレクトされました。')
    return

#ログイン処理
def login(driver):
    #ログインページにたどり着くまでループアクセス
    print('Accessing to login page...')
    loop_access(driver, config.LOGIN_PAGE_URL)

    #全てのエレメントが表示されるまで待つ（30秒でタイムアウト）
    WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located)
    #ログイン情報入力
    driver.find_element_by_id('_userId').send_keys(config.LOGIN_USER_ID)
    driver.find_element_by_id('_password').send_keys(config.LOGIN_PW)

    #ログインボタンがクリックできる状態まで明示的に待機。30秒でタイムアウト
    try:
        element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, 'confirm')))
    except:
        print('ログインボタン活性化タイムアウト')
    else:
        #ログインボタン押下
        driver.execute_script('arguments[0].click();', element)
    return

def move_to_top_page(driver):
    element = None
    #トップページにあるはずのチケットボタンが確認できない場合ログインからやり直し続ける
    while(True):
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//img[@alt="チケット"]')))
        except:
            #再度ログイン
            print('再ログインします。')
            send_notificateion('【log】再ログインします。')
            login(driver)
            continue
        else:
            break
    
    send_notificateion('【log】ログイン成功')
    #該当ページに到達するまで10個ずつタブを開いてはチェックして消すを繰り返す
    i = 0
    global flag
    while(flag):
        i += 1
        print('３タブ展開{0}回目....'.format(i))
        send_notificateion('【log】３タブ展開{0}回目....'.format(i))
        driver.switch_to.window(driver.window_handles[0])
        open_ticket_page(driver)
    
    #チケットのページへのリンクをクリック
    # ActionChains(driver).move_to_element(element).perform()
    # driver.find_element_by_link_text('パークチケット').click()
    return

def open_ticket_page(driver):
    #新規タブを３つ開いてでチケットページにアクセス
    for i in range(3):
        driver.execute_script("window.open(arguments[0], '_blank')", config.TICKET_PAGE_URL)
        #一応人が手で連打するくらいの感覚は開けてアクセス
        time.sleep(0.2)

    #タブが全て開かれるのを待つ
    WebDriverWait(driver, 30).until(EC.number_of_windows_to_be(4))
    #ちゃんとチケットページが表示されているタブまで移動し続ける
    for i in range(3):
        print('i')
        print(i)
        #操作可能なタブを取得し、２つ目のタブに移動
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        try:
            #画面前要素表示を待機後次へボタンがあるかどうか確認（1秒でタイムアウト）
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located)
            element = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-next')))
        except:
            #次へボタンがなければタブを閉じて次のタブ（閉じているから再度２つ目のタブ）へ
            print('このタブには次へボタンがない。')
            driver.close()
        else:
            #LINEで通知
            send_notificateion('【祝】チケット購入ページが表示されました。')
            #タプ展開＆チェックの無限ループを終了しチケット選択処理へ
            global flag
            flag = False
            select_conditions(driver)
            break
            
    return

def select_conditions(driver):
    #カレンダーを捲るボタン、日程選択ボタン、自宅でプリントボタンはそれぞれ離れた場所にあり、クリックのタイミングで次のボタンがウィンドウ外にあるためjavascriptからクリックを実行。
    next_button = driver.find_element_by_class_name('slick-next')
    day_button = driver.find_element_by_xpath('//a[@data-daynumbercount="60"]')
    search_button = driver.find_element_by_id("searchEticket")
    driver.execute_script('arguments[0].click(); arguments[1].click(); arguments[2].click()', next_button, day_button, search_button)
    return