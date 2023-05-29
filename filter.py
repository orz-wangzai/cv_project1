# -*- coding:utf-8 -*-
import numpy as n1
import cv2
#读取图片
img = cv2.imread("test.jpg")

#显示图像
cv2.imshow("test", img)

#等待显示
cv2.waitKey(0)
cv2.destroyAllWindows()

#写入图像
cv2.imwrite("test.jpg", img)
