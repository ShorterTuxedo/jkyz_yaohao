from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageEnhance
import datetime
import ddddocr # 查看结果 + 申请摇号
import crack_qq # 破解滑块验证
import json
import random
import base64
import hashlib
import time
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

adstr_2_myD = lambda adstr: adstr[:-1][:4] + "-" + adstr[:-1][4:6] + "-" + adstr[:-1][6:]

'''
别瞎折腾了

一般摇中机率为10%

连续摇21天有90%摇中机率

该脚本不支持简体界面！请将您的健康驿站界面切换成繁体！

'''

def wait_until(condition_lambda_1arg):
    while not condition_lambda_1arg(0):
        pass

siteURL = "https://hk.sz.gov.cn"

dateFormat = "%Y-%m-%d"

def writeLog(text):
  _text="["+time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))+"] "+text
  print(_text)
  log = open("log.txt", "a", encoding="UTF-8")
  myLog = (_text+"\n")
  log.write(myLog)
  log.close()

def appendToDict(_dict, k, v):
    _dict[k] = v

def parse_dict_cookies(_dict, cookies):
    for item in cookies.split(';'):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            _dict[item] = ""
            continue
        name, value = item.split('=', 1)
        _dict[name] = value


def dict_2_cookies(_dict):
    finished_str = ""
    for cookie in _dict.keys():
        finished_str += cookie + "="
        finished_str += _dict[cookie] + ";"
    return finished_str[:-1]

info = json.loads(open("info.json", "r").read())

CHROME_DRIVER_PATH = "chromedriver.exe" if os.name == "nt" else "chromedriver"

yaohaocontents = []

yaohaofile = None

if not os.path.exists("yaohaodates"):
    yaohaofile = open("yaohaodates", "a")
else:
    yaohaofile = open("yaohaodates", "a")
    yaohaocontents = open("yaohaodates", "r").read().split("\n")

def add_my_date(date):
    global yaohaofile
    global yaohaocontents
    yaohaocontents.append(date)
    if len(yaohaocontents) > 0:
        yaohaofile.write("\n" + date)
    else:
        yaohaofile.write(date)
    yaohaofile.close()
    yaohaofile = open("yaohaodates", "a")

loggedInForTheDay = False
checkedForTheDay = False
won = False

writeLog("="*20+"开始运行"+"="*20)
writeLog("[警告] 注意！请于运行此脚本前完成您的身份认证！")

while (not won):
    winningDates = []
    # 一直运行到抽到为止
    now = datetime.datetime.now()
    if now.strftime(dateFormat) in yaohaocontents:
        loggedInForTheDay = True
    if (now.hour >= 9 and now.hour < 18) and loggedInForTheDay == False:
        loggedInForTheDay = True
        checkedForTheDay = False
        # 可以摇号
        writeLog("[信息] 开始摇号了。")
        browser = webdriver.Chrome(CHROME_DRIVER_PATH)
        url=siteURL+"/userPage/login"
        browser.get(url)
        #WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[onclick=\"closeLoginHint()\"]"))).click()
        while True:
            try:
                if "display: none" in browser.find_element_by_id("winLoginNotice").get_attribute("style"):
                    break
                browser.find_element_by_css_selector("[onclick=\"closeLoginHint()\"]").click()
                break
            except Exception:
                pass
        while True:
            try:
                if("請廣大入境旅客通過正規途徑參與“搖號”預約" in browser.find_element_by_css_selector("html").get_attribute("innerHTML")):
                    break
                zhengjianleixing=Select(browser.find_element_by_id('select_certificate'))
                zhengjianleixing.select_by_value(info["type"])

                zhengjianhaoma=browser.find_element_by_id('input_idCardNo')
                browser.execute_script("document.querySelector(\"#input_idCardNo\").value = \"\";")
                zhengjianhaoma.send_keys(info["id"])#需要在此输入通行证号码

                mima=browser.find_element_by_id('input_pwd')
                browser.execute_script("document.querySelector(\"#input_pwd\").value = \"\";")
                mima.send_keys(info["pwd"])#需要在此输入密码
                def is_mask_unseeable():
                    for element in browser.find_elements_by_class_name("mask"):
                        if not ("hidden=\"\"" in element.get_attribute("outerHTML") or "display: none;" in element.get_attribute("outerHTML")):
                            return False
                    return True
                while True:
                    #wait_until(lambda a: len(browser.find_elements_by_class_name("mask")) == 0 or is_mask_unseeable())
                    myFilePath = browser.find_element_by_css_selector("#img_verify").screenshot("spider\code.png")
                    '''browser.get_screenshot_as_file('spider\\screenshot.png')
                    element = browser.find_element_by_id('img_verify')
                    left = int(element.location['x'])
                    top = int(element.location['y']+OFFSET_Y)
                    right = int(element.location['x'] + element.size['width'])
                    bottom = int(element.location['y'] + element.size['height']+OFFSET_Y)
                    im = Image.open('spider\\screenshot.png')
                    im = im.crop((left, top, right, bottom))
                    im.save('spider\\code.png')'''
                    #验证码识别
                    im = Image.open("spider\\code.png")
                    newimdata = []
                    for color in im.getdata():
                        newimdata.append(tuple([rgb+75 for rgb in color]))
                    newim = Image.new(im.mode,im.size)
                    newim.putdata(newimdata)
                    myEnhancer = ImageEnhance.Contrast(newim)
                    im_new = myEnhancer.enhance(2)
                    im_new.save("spider\\code2.png")
                    det = ddddocr.DdddOcr(old=True)
                    #with open("spider\\code2.png", 'rb') as f:
                    with open("spider\\code2.png", 'rb') as f:
                        image=f.read()
                    res = det.classification(image)
                    res = res.upper()
                    if len(res) != 6 or ("I" in res or "O" in res): # 剔除不合格字母，減少錯誤機會
                        myImage = browser.find_element_by_id("img_verify")
                        print("[错误]　验证码识别时出现了错误。")
                        while True:
                            try:
                                if("請廣大入境旅客通過正規途徑參與“搖號”預約" in browser.find_element_by_css_selector("html").get_attribute("innerHTML")):
                                    break
                                myImage.click()
                                time.sleep(1) # 等待驗證碼加載
                                break
                            except Exception:
                                continue
                        continue
                    else:
                        break # 如果res長度是6，我們來試試吧。
                writeLog("[信息]: 验证码为 "+ res)
                browser.execute_script("document.querySelector(\"#input_verifyCode\").value = \"\";")
                yanzhengma=browser.find_element_by_id('input_verifyCode')
                yanzhengma.send_keys(res)
                wait_until(lambda a: not "圖形驗證碼錯誤" in browser.find_element_by_tag_name("html").get_attribute("outerHTML"))
                while True:
                    try:
                        if("請廣大入境旅客通過正規途徑參與“搖號”預約" in browser.find_element_by_css_selector("html").get_attribute("innerHTML")):
                            break
                        browser.find_element_by_id("btn_login").click()
                        break
                    except Exception:
                        continue
                wait_until(lambda a: not "圖形驗證碼錯誤" in browser.find_element_by_tag_name("html").get_attribute("outerHTML"))
            except Exception as e:
                print(e)
                if("請廣大入境旅客通過正規途徑參與“搖號”預約" in browser.find_element_by_css_selector("html").get_attribute("innerHTML")):
                    break
        writeLog("[信息] 登入完成。")
        browser.find_element_by_css_selector("button[onclick=\"closeHint()\"]").click()
        # 点击申报预约按钮
        browser.find_element_by_css_selector("#a_canReportLottery").click()
        # 选定所有日期
        mydates = []
        while len(mydates) == 0:
            mydates = browser.find_elements_by_css_selector('input[type="checkbox"][name="date"]')
        for i in range(len(mydates)):
            if i in info["dates"]:
                while True:
                    try:
                        # writeLog(browser.execute_script('return document.querySelectorAll("input[type=\\"checkbox\\"][name=\\"date\\"]").length;'))
                        browser.execute_script('document.querySelectorAll("input[type=\\"checkbox\\"][name=\\"date\\"]")[' + str(i) + '].scrollIntoView(true);')
                        if browser.execute_script('return (document.querySelectorAll("input[type=\\"checkbox\\"][name=\\"date\\"]")[' + str(i) + '].disabled ? "Disabled" : "Free");') == "Disabled":
                            break
                        mydates[i].click()
                        break
                    except Exception as e:
                        print(e)
                        pass
        # 点击抽签按钮
        while True:
            try:
                mysignupbtn = browser.find_element_by_css_selector('#reportLottery')
                mysignupbtn.click()
                break
            except Exception as e:
                print(e)
                pass
        # 完成预约流程
        while True:
            try:
                browser.execute_script('document.querySelector("button#TencentCaptcha").scrollIntoView(true);')
                browser.find_element_by_css_selector("button#TencentCaptcha").click()
                break
            except Exception as e:
                print(e)
                pass
        writeLog("[验证码] 我已经打开了验证码。")
        my_tx = crack_qq.Tencent(browser)
        my_tx.tx_code()
        # 验证码已搞定
        # 点击 "确认申报"
        while True:
            try:
                browser.switch_to.default_content()
                browser.find_element_by_id("btn_confirmReport").click()
                break
            except Exception:
                pass
        # 记录已完成并退出浏览器 (记录日期)
        add_my_date(now.strftime(dateFormat))
        browser.quit()
    elif checkedForTheDay == False and (now.hour >= 20 or now.hour < 9):
        loggedInForTheDay = False
        checkedForTheDay = True

        mySession = requests.Session()

        writeLog("[温馨提示] 別高兴的太早。")
        writeLog("[温馨提示] 請准备时间登录网页。")

        info = json.loads(open("info.json", "r").read())

        headers = {}

        appendToDict(headers, "Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
        appendToDict(headers, "Accept-Encoding", "gzip, deflate, br")
        appendToDict(headers, "Accept-Language", "zh-CN,zh;q=0.9")
        appendToDict(headers, "Connection", "keep-alive")
        appendToDict(headers, "Host", "hk.sz.gov.cn")
        appendToDict(headers, "Upgrade-Insecure-Requests", "1")
        appendToDict(headers, "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")

        url = ["https://hk.sz.gov.cn", "/"]

        jkyz = mySession.get("".join(url), headers=headers, allow_redirects=False)

        loc = jkyz.headers["Location"]

        url = url[:1]

        url.append(loc)

        jkyz = mySession.post("".join(url), headers=headers, allow_redirects=False)

        while True:
            url = url[:1]

            url.append("/user/getVerify?" + str(random.random()))

            writeLog("[信息] 验证码URL为"+"".join(url))

            jkyz = mySession.get("".join(url), headers=headers, allow_redirects=False)

            writeLog("[信息] 图片获取结果为 " + str(jkyz.status_code))

            with open("captcha.jpg", "wb") as cFile:
                #print(jkyz.content)
                cFile.write(jkyz.content)

            im = Image.open("captcha.jpg")
            newimdata = []
            for color in im.getdata():
                newimdata.append(tuple([rgb+75 for rgb in color]))
            newim = Image.new(im.mode,im.size)
            newim.putdata(newimdata)
            myEnhancer = ImageEnhance.Contrast(newim)
            im_new = myEnhancer.enhance(2)
            im_new.save("captcha2.png")
            det = ddddocr.DdddOcr(old=True)

            CAPTCHA_RESULT = ""

            #with open("spider\\code2.png", 'rb') as f:
            with open("captcha2.png", 'rb') as f:
                image=f.read()
                CAPTCHA_RESULT = det.classification(image)
                CAPTCHA_RESULT = CAPTCHA_RESULT.upper()

            writeLog("[信息] 验证码为" + CAPTCHA_RESULT)

            if len(CAPTCHA_RESULT) != 6 or ("I" in CAPTCHA_RESULT or "O" in CAPTCHA_RESULT):
                continue
            else:
                break

        data = {
            "certType": info["type"],
            "verifyCode": CAPTCHA_RESULT,
            "certNo": str(base64.b64encode(info["id"].encode('ascii')), encoding="ASCII"), #BASE64(證件號碼),
            "pwd": str(base64.b64encode(hashlib.md5(info["pwd"].encode('ascii')).hexdigest().encode('ascii')), encoding="ASCII"),
            "fkRes":"",
        }

        #print(json.dumps(data,indent=2))

        url = url[:1]
        url.append("/user/login")

        jkyz = mySession.post("".join(url), headers=headers, data=data, allow_redirects=False)

        #print(json.dumps(cookie, indent=2))

        #print(json.dumps(headers, indent=2))

        url = url[:1]

        url.append("/userPage/userCenter")

        jkyz = mySession.get("".join(url), headers=headers, allow_redirects=False)

        writeLog("[信息] 用户中心HTML代码为:\n"+jkyz.text)

        while True:
            #writeLog("[時間] 目前時間為" + nowTime)
            #print(hour)
            if now.hour >= 20 or now.hour < 9:
                writeLog("[提示] 我要显示摇号结果了。")
                url=url[:1]
                url.append("/lottery/getLotteryRecordList")
                page = 1
                myEndPage = float("inf")
                while page <= myEndPage:
                    myRes = mySession.post("".join(url), headers=headers, data={
                        "pageIndex": page,
                        "pageSize": 10
                    }, allow_redirects=False)
                    writeLog("[我的预约历史] " + str(myRes.content, encoding="UTF-8"))
                    myRes = myRes.json()
                    if myEndPage == float("inf"):
                        myEndPage = myRes["data"]["pages"]
                    writeLog("[查询中] 正在查询您的预约记录...")
                    for record in myRes["data"]["records"]:
                        myYaoTime = (datetime.datetime.now() if datetime.datetime.now().hour > 9 else (datetime.datetime.now() - datetime.timedelta(days=1))).strftime(dateFormat)
                        # writeLog("[今天] 今天摇号:"+myYaoTime)
                        # writeLog("[摇号日期] 摇号日期:"+adstr_2_myD(record["applyDateStr"]))
                        if adstr_2_myD(record["applyDateStr"]) == myYaoTime:
                            # 这是今天的
                            winningDates = []
                            if record["statusStr"] == "已中签":
                                won = True
                            if won:
                                writeLog("[恭喜中签] 已中签\t编号:" + record["applyNo"])
                            for aDate in record["applyDateList"]:
                                if aDate["winStatus"] == 1:
                                    won = True
                                    winningDates.append(aDate["applyDate"])
                            if not won:
                                writeLog("[对不起] 抱歉！您未中签。")
                            break
                    page += 1
                break


if won:
    myDates = ", ".join(winningDates)
    myEmailContent = open("JKYZ_Success_Email.html", "r", encoding="UTF-8").read()
    myEmailContent = myEmailContent.replace("[INSERT DATES HERE]", myDates)
    myEmailTContent = open("JKYZ_Success_Email.txt", "r", encoding="UTF-8").read()
    myEmailTContent = myEmailTContent.replace("[INSERT DATES HERE]", myDates)
    # 在这里输入 STMP 密码
    sender = info["mysendemail"] # 您的电邮
    receivers = info["emailreceivers"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEMultipart('alternative')
    subject = '您抽到了健康驿站！'
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ";".join(receivers)

    part1 = MIMEText(myEmailTContent, 'plain', 'utf-8')
    part2 = MIMEText(myEmailContent, 'html', 'utf-8')
    
    message.attach(part1)
    message.attach(part2)
    
    try:
        smtpObj = smtplib.SMTP_SSL(info["smtphost"], info["smtpport"])
        smtpObj.ehlo()
        # stmpObj.starttls()
        smtpObj.login(info["mysendemail"], info["stmppwd"])
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print("Error: 无法发送邮件")
    # 在这里输入 STMP 密码
