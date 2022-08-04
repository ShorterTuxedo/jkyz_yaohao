# -*- coding: utf-8 -*-
"""
@author:Pineapple

@contact:cppjavapython@foxmail.com

@time:2020/8/2 17:29

@file:login.py

@desc: login with Tencen .
"""

from selenium.webdriver.support import expected_conditions as EC  # 显性等待
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import cv2 as cv
import requests
import ddddocr
import random
import time
import pyautogui
from PIL import Image, ImageEnhance


class Tencent:
    """
    识别腾讯验证码
    """
    @staticmethod
    def save_img(bk_block):
        """
        保存

        :param bk_block: 图片url
        :return: bool类型，是否被保存
        """
        try:
            img = requests.get(bk_block).content
            with open('bg.jpeg', 'wb') as f:
                f.write(img)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def save_target(tg_block):
        """
        保存图片

        :param bk_block: 图片url
        :return: bool类型，是否被保存
        """
        try:
            img = requests.get(tg_block).content
            with open('target.png', 'wb') as f:
                f.write(img)
            myPuzzlePiece = cv.imread("target.png")
            myDim = myPuzzlePiece.shape
            xPos = 140
            yPos = 490
            xWid = 120
            yWid = 120
            x2Pos = xPos + xWid
            y2Pos = yPos + yWid
            myEdge = myPuzzlePiece[yPos:y2Pos,xPos:x2Pos]
            cv.imwrite("target.png", myEdge)
            img = Image.open('target.png')
            img = img.convert("RGBA")
            datas = img.getdata()
            newData = []
            for item in datas:
                if item[0] == 0 and item[1] == 0 and item[2] == 0:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            img.save("target.png", "PNG")
            return True
        except Exception as e:
            print(e)
            return False

    def __init__(self, driver):
        """
        初始化浏览器配置，声明变量

        :param url: 要登录的网站地址
        :param username: 账号
        :param password: 密码
        """
        # profile = webdriver.FirefoxOptions()  # 配置无头
        # profile.add_argument('-headless')
        self.browser = driver

    def end(self):
        """
        结束后退出，可选

        :return:
        """
        self.browser.quit()

    def set_info(self):
        """
        填写个人信息，在子类中完成

        """
        pass

    def tx_code(self):
        """
        主要部分，函数入口

        :return:
        """
        self.set_info()

        #WebDriverWait(self.browser, 20, 0.5).until(
        #    EC.presence_of_element_located((By.ID, 'tcaptcha_iframe')))  # 等待 iframe
        while True:
            try:
                x=False
                try:
                    c=self.browser.find_element_by_id("tcOperation")
                    x=True
                except Exception as e:
                    print(e)
                    x=False
                if x:
                    break
                print(self.browser.execute_script("return document.documentElement.innerHTML;"))
                self.browser.switch_to.frame(self.browser.find_element_by_id('tcaptcha_iframe_dy'))  # 加载 iframe
                break
            except Exception as e:
                print(e)
                continue
        #time.sleep(0.25) #等待加載
        bk_block=""
        # print(self.browser.execute_script("return document.documentElement.innerHTML;"))
        while True:
            try:
                bk_block = self.browser.find_element_by_css_selector('#slideBg').value_of_css_property("background-image").split('"')[1]
                if bk_block != None:
                    break
            except Exception:
                continue
        print("[信息] 背景图片为 "+bk_block)
        slideBlock = ""
        while True:
            try:
                slideBlock = self.browser.find_elements_by_css_selector("div[aria-label=\"拖动下方滑块完成拼图\"]")[1].value_of_css_property("background-image").split('"')[1]
                print(slideBlock)
                if slideBlock != None and slideBlock != "none":
                    break
            except Exception as e:
                print(e)
                continue
        print("[信息] 滑块为"+slideBlock)
        if self.save_img(bk_block) and self.save_target(slideBlock):
            dex = self.get_pos()
            if dex:
                track_list = self.get_track(dex)
                #time.sleep(0.5)
                #slid_ing = self.browser.find_element_by_xpath(
                #    '//div[@id="tcaptcha_drag_thumb"]')  # 滑块定位
                '''slideLoc=None
                while slideLoc == None:
                    slideLoc = pyautogui.locateOnScreen("sliderImage.png") #打開Selenium時,請到confirmOrder點擊驗證按鈕截圖獲取這個圖片
                slideLoc=(slideLoc.top, slideLoc.left)'''
                #action = webdriver.ActionChains(self.browser)
                #action.move_to_element(slid_ing).click_and_hold().perform()
                #slideLoc=pyautogui.position()
                slideLoc=(740, 631) # 這個數字是基於Selenium打開的默認位置，每一臺電腦有少許不同
                pyautogui.moveTo(y=slideLoc[0],x=slideLoc[1])
                #time.sleep(0.2)
                print('[信息] 鼠标移动轨迹:', track_list)
                pyautogui.mouseDown()
                time.sleep(0.2)
                for track in track_list:
                    currentLoc = pyautogui.position()
                    pyautogui.moveTo(x=currentLoc[0]+track,y=slideLoc[0])
                pyautogui.mouseUp()
                if self.browser.get_element_by_css_selector("#guideText").get_attribute("innerHTML") == "验证错误，请重试":
                    # 验证错误
                    while True:
                        try:
                            self.browser.get_element_by_css_selector("#reload").click()
                            break
                        except Exception:
                            pass
                    self.browser.switch_to.default_content()
                    self.tx_code()
                #     识别图片
                return True
            else:
                #self.re_start()
                pass
        else:
            print('缺口图片捕获失败')
            return False

    @staticmethod
    def get_pos():
        target=cv.imread("target.png")
        print(target.shape)
        r,target=cv.threshold(target,254,255,cv.THRESH_BINARY)
        #cv.imshow("target",target)
        #cv.waitKey(0)
        #target=cv.bitwise_not(target)
        bg=cv.imread("bg.jpeg")

        cv.GaussianBlur(bg, (5, 5), 0)
        r,bg=cv.threshold(bg,83,255,cv.THRESH_BINARY)
        r,bg=cv.threshold(bg,83,255,cv.THRESH_BINARY)
        r,bg=cv.threshold(bg,83,255,cv.THRESH_BINARY)
        cv.GaussianBlur(bg, (5, 5), 0)
        #cv.imshow('bg',bg)
        #cv.waitKey(0)

        
        #cv.GaussianBlur(target, (5, 5), 0)
        #cv.imshow("target",target)
        #cv.waitKey(0)

        bg_edge = cv.Canny(bg, 100, 200)#获取图像的边缘，Canny（图，阈值，阈值）
        tg_edge = cv.Canny(target, 100, 200)

        bg_pic = cv.cvtColor(bg_edge, cv.COLOR_GRAY2RGB)#颜色空间转换函数，cvtColor（图，要变成的格式）
        tg_pic = cv.cvtColor(tg_edge, cv.COLOR_GRAY2RGB)
        # 缺口匹配
        res = cv.matchTemplate(bg_pic, tg_pic, cv.TM_CCOEFF_NORMED)#模板匹配函数，mathTemplate(图，图，匹配类型【一般用cv.TM_CCOEFF_NORMED】）
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res) # 寻找最优匹配
        print("[缺口识别] 识别结果为 ", min_val, max_val, min_loc, max_loc)
        print("[MaxLoc] MaxLoc 为 ", max_loc)
        print("[MinLoc] MinLoc 为 ", min_loc)
        return max_loc[0] * 360/552
        

    '''def get_pos():
        """
        识别缺口
        注意：网页上显示的图片为缩放图片，缩放 50% 所以识别坐标需要 0.5

        :return: 缺口位置
        """
        image = cv.imread("bg.jpeg")
        blurred = cv.GaussianBlur(image, (7, 7), 0)
        canny = cv.Canny(blurred, 200, 400)
        cv.imshow('img', canny)
        cv.waitKey(0)
        # 轮廓检测
        contours, hierarchy = cv.findContours(
            canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            m = cv.moments(contour)
            if m['m00'] == 0:
                cx = cy = 0
                print("[日志] cx, cy为", cx , ",", cy)
            else:
                cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
                print("[日志] cx, cy为", cx , ",", cy)
            x, y, w, h = cv.boundingRect(contour)  # 外接矩形
            #image2 = image
            #cv.rectangle(image2, (x, y), (x + w, y + h), (0, 0, 255), 2)
            print("[信息] contour面积:", cv.contourArea(contour), ", contour方形面积: ", w*h)
            print("[信息] contour高宽:", w, h)
            print("[信息] contour弧形长度: ", cv.arcLength(contour, True))
            rectArea = w * h
            #cv.imshow('image', image2)  # 显示识别结果
            #cv.waitKey(0)
            #if 6000 < cv.contourArea(contour) < 8000 and 330 < cv.arcLength(contour, True) < 390:
            if ((w >= 80 and w <= 126) and (h >= 80 and h <= 126)) and (cx >= 400 and (w/h >= 0.8 and w/h <= 1.25)):
                if cx < 400:
                    continue
                x, y, w, h = cv.boundingRect(contour)  # 外接矩形
                # cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                print('[缺口识别] {x}px'.format(x=x / 2))
                return x / 2
        return 0'''

    @staticmethod
    def get_track(distance_):
        distance = distance_
        distance -= 17.5
        myTrack = []
        while distance > 0:
            if distance > 20:
                # 如果距离大于20，就让他移动快一点
                span = random.randint(60, 70)#
            else:
                # 快到缺口了，就移动慢一点
                span = random.randint(45, 50)
            myTrack.append(span)
            distance -= span
        return myTrack

    def move_to(self, index):
        """
        移动滑块

        :param index:
        :return:
        """
        pass

    def re_start(self):
        """
        准备开始

        :return: None
        """
        self.tx_code()
        # self.end()