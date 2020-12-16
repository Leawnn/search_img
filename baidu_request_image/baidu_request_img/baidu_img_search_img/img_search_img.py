# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 10:55:47 2020

@author: leawnn
"""
"""
Created on Sun Sep 15 20:24:25 2019
这是一个借助百度识图功能获取大量相似图片的示例程序
如果你不了解百度识图，不妨尝试使用下：
https://graph.baidu.com/pcpage/index?tpl_from=pc
本程序的大致思路如下：
seed_imgs中放置想要搜索相似图的原始图片
程序将会依次获取seed_imgs中的图片作为搜索种子，
借助爬虫来模拟使用百度识图的过程，达到自动化搜索大量相似图片的目的
搜索的结果将会保存在similar_search_result中
使用方法如下：
1.准备种子图片
收集所有想要用来搜索相似图片的原始图片，放置在seed_imgs中
2.使本地图片可以被url访问
将seed_imgs中的图片做成可供外界访问的url形式，你可以使用任何可能的方法
例如我的解决办法是将这些图片上传到github上，将github作为一个临时的图床使用
根据你制作的图床的url前缀，修改变量base_url
3.安装chromedriver
教程: https://www.jb51.net/article/162903.htm
查看谷歌浏览器版本命令: chrome://version/
下载链接（需选择对应版本） http://chromedriver.storage.googleapis.com/index.html
4.运行本程序，耐心等待
python version: python3.5
@author: zyb_as
"""
import os
import cv2
import time
import requests
import numpy as np
from selenium import webdriver
import urllib.request
import json
from bs4 import BeautifulSoup    #网页解析，获取数据
import re         #正则表达，进行文字匹配
import urllib.request,urllib.error      #制定URL，获取网页数据
# TODO: set parameters
# These two parameters needs to be modified according to your actual situation.
chrome_driver_path = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
home_page = 'https://graph.baidu.com/pcpage/index?tpl_from=pc'
seed_imgs_dir = 'seed_imgs'
save_dir = 'similar_search_result'
#爬取网页
def getData(baseurl):
    datalist = []
    
    html = askURL(baseurl)
    
    data = json.loads(html)
    list_ = data['data']['list']
    for list_page in list_:
        datalist.append(list_page['thumbUrl'])
    return datalist
#得到指定一个URl的网页内容
def askURL(url):
    head = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
    request = urllib.request.Request(url = url,headers=head)
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)
    return html


def search_similar_images(browser, image_url, max_page):
    print("start find similar image of {}".format(image_url))
    
    search_failed = True
    try_num = 0
    while(search_failed):
        if try_num >= 2:
            break
        try:
            browser.get(home_page)
            
            # 拖拽图片到此处或粘贴图片网址
            url_upload_textbox = browser.find_element_by_css_selector('#app > div > div.page-banner > div.page-search > div > div > div.graph-search-left > input')
            url_upload_textbox.send_keys(image_url)
        #url_upload_textbox.
            # 识图一下
            search_image_button = browser.find_element_by_css_selector('#app > div > div.page-banner > div.page-search > div > div > div.graph-search-center')
            search_image_button.click()
        
            # 等待百度识图结果
            time.sleep(5)
        
            # 切换到当前窗口(好像可有可无)
            browser.current_window_handle
        
            # 测试是否成功
            graph_similar = browser.find_element_by_class_name('graph-similar-list')
            
            # 运行到这里说明模拟使用百度识图功能成功，页面已正常加载
            search_failed = False
        except Exception as e:
            #print("ERROR:" + traceback.format_exc())
            print("ERROR: error when request baidu image search.")
        finally:
            try_num += 1
    #browser.switch_to_window(browser.window_handles[1])
    #print(browser.page_source)
    
          
    if search_failed:
        print("give up current image")
        return []
    recognition_img_url = browser.current_url#识别完后的URL界面链接
    #print(recognition_img_url)
    datalist = getData(str(recognition_img_url).replace('/s' , '/ajax/pcsimi'))
    return datalist
    
def download_search_images(url_list, cur_save_dir):
    print("start downloading...")
    i=0
    for img_url in url_list:
        skin_file =os.path.join(cur_save_dir,(str(i)+'.jpg'))
        request = urllib.request.Request(img_url)
        response = urllib.request.urlopen(request)
        get_img = response.read()
        with open(skin_file, 'wb') as fb:
            fb.write(get_img)
        i = i+1      

if __name__ == "__main__":
    browser = webdriver.Chrome(executable_path=chrome_driver_path)
    browser.set_page_load_timeout(30)

    #seed_imgs_url_list, save_dir_list = prepare_seed_imgs()
    seed_imgs_url_list = ['http://m.qpic.cn/psc?/V523O8Jq2ClKcy19Gc734SngRL35XjEW/ruAMsa53pVQWN7FLK88i5spkoVQsw5LZXvuSNXmqryz.L7YcyvGrWfmSlkZKqZHnF84LLgm1Uh4cGUGrqbvPue*kNq7*utpkYpPQD*olw.4!/mnull&bo=QgLuAgAAAAABB4w!&rf=photolist&t=5']
    #save_dir_list = ['similar_search_result/tank1','similar_search_result/tank2']
    save_dir_list = ['./img']
    for idx, seed_url in enumerate(seed_imgs_url_list):
        print(idx)
        
        # 获取百度识图结果
        url_list = search_similar_images(browser, seed_url, max_page=30)
        
        if len(url_list) == 0:
            continue
        
        # 下载图片
        cur_save_dir= save_dir_list[idx]
        download_search_images(url_list, cur_save_dir)
