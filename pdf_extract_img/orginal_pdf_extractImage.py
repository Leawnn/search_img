# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 09:54:51 2020

@author: leawnn
"""
'''
----------------适用于原pdf（非图片型pdf）---------------
'''

import fitz
import re
import os


def pdf2pic(path, pic_path):

    # 从pdf中提取图片
    #:param path: pdf的路径
    #:param pic_path: 图片保存的路径
    # :return:
    # 打开pdf
    doc = fitz.open(path)
    nums = doc._getXrefLength()
    imgcount = 0 # 图像计数
   
    # 遍历每一个对象
    for i in range(1, nums):
        text = doc._getXrefString(i)
        # print(i, text)          
	    # 使用正则表达式来查找图片
        checkXO = r"/Type(?= */XObject)"
        checkIM = r"/Subtype(?= */Image)"
	    
        isXObject = re.search(checkXO, text)
        isImage = re.search(checkIM, text)
        
        # 不符合条件, continue
        if not isXObject or not isImage:
            continue
        imgcount += 1

        # 生成图像
        pix = fitz.Pixmap(doc, i)
		
		# 保存图像名
        img_name = "img{}.png".format(imgcount)
        
        # 如果pix.n<5,可以直接存为PNG
        if pix.n < 5:
            try:
                pix.writePNG(os.path.join(pic_path, img_name))
                pix = None
            except:
                pix0 = fitz.Pixmap(fitz.csRGB, pix)
                pix0.writePNG(os.path.join(pic_path, img_name))
                pix0 = None

if __name__ == '__main__':
    # pdf路径
    path = r'基于Q-learning的自适应学习.pdf'
	# 保存的图片路径
    pic_path = 'orginal_pdf_Image'
    pdf2pic(path, pic_path)
