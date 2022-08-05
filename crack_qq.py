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
import numpy as np
import pandas as pd
import math
from PIL import Image
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

    '''@staticmethod
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
            return False'''

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
        '''slideBlock = ""
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
        if self.save_img(bk_block) and self.save_target(slideBlock):'''
        if self.save_img(bk_block):
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
                time.sleep(0.25)
                if self.browser.find_element_by_css_selector("#guideText").get_attribute("innerHTML") != "拖动下方滑块完成拼图":
                    # 验证错误
                    while True:
                        try:
                            self.browser.find_element_by_css_selector("#reload").click()
                            break
                        except Exception:
                            #print(e)
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
        get_dx_median = lambda dx, x, y, w, h: np.median(dx[y: (y + h), x])

        img = cv.imread("bg.jpeg", 1)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 转成灰度图像

        _, binary = cv.threshold(img_gray, 127, 255, cv.THRESH_BINARY)  # 将灰度图像转成二值图像

        contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)  # 查找轮廓

        rect_area = []
        rect_arc_length = []
        cnt_infos = {}

        for i, cnt in enumerate(contours):
            # print(cv.contourArea(cnt))
            if (cv.contourArea(cnt) < 3450 or cv.contourArea(cnt) > 25500): #and (not (cv.contourArea(cnt) >= 3450 and cv.contourArea(cnt) <= 3455)):
                continue

            x, y, w, h = cv.boundingRect(cnt)
            cnt_infos[i] = {'rect_area': w * h,  # 矩形面积
                            'rect_arclength': 2 * (w + h),  # 矩形周长
                            'cnt_area': cv.contourArea(cnt),  # 轮廓面积
                            'cnt_arclength': cv.arcLength(cnt, True),  # 轮廓周长
                            'cnt': cnt,  # 轮廓
                            'w': w,
                            'h': h,
                            'x': x,
                            'y': y,
                            'mean': np.mean(np.min(img[y:(y + h), x:(x + w)], axis=2)),  # 矩形内像素平均
                            }
            rect_area.append(w * h)
            rect_arc_length.append(2 * (w + h))
        dx = cv.Sobel(img, -1, 1, 0, ksize=5)

        h, w = img.shape[:2]
        print("-"*20)
        print(cnt_infos)
        print("-"*20)
        df = pd.DataFrame(cnt_infos).T
        df.head()
        print("-"*20)
        print(df.apply(lambda x: get_dx_median(dx, x['x'], x['y'], x['w'], x['h']), axis=1))
        print(type(df.apply(lambda x: get_dx_median(dx, x['x'], x['y'], x['w'], x['h']), axis=1)))
        df['dx_mean'] = df.apply(lambda x: get_dx_median(dx, x['x'], x['y'], x['w'], x['h']), axis=1)
        df['rect_ratio'] = df.apply(lambda v: v['rect_arclength'] / 4 / math.sqrt(v['rect_area'] + 1), axis=1)
        df['area_ratio'] = df.apply(lambda v: v['rect_area'] / v['cnt_area'], axis=1)
        df['score'] = df.apply(lambda x: abs(x['rect_ratio'] - 1), axis=1)

        result = df.query('x>0').query('area_ratio<2').query('rect_area>=3450').query('rect_area<25500').sort_values(
            ['mean', 'score', 'dx_mean']).head(2)
        if len(result):
            x_left = result.x.values[0]
            # cv.line(img, (x_left, 0), (x_left, h), color=(255, 0, 255))
            # plt.imshow(img)
            # plt.show()

        # return result
        return x_left

        '''target=cv.imread("target.png")
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
        

    def get_pos():
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
        RATIO = 507 / 670
        BIAS = 39
        # BIAS = 118
        # RATIO = 1
        distance = distance_
        distance *= RATIO
        distance -= BIAS
        #myTrack = [distance]
        #return myTrack
        myTrack = []
        while distance > 0:
            if distance > 20:
                # 如果距离大于20，就让他移动快一点
                span = random.randint(20, 30)
                if span > distance:
                    span = distance
            else:
                # 快到缺口了，就移动慢一点
                span = random.randint(15, 20)
                if span > distance:
                    span = distance
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
