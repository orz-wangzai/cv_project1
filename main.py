import tkinter as tk  # 使用Tkinter前需要先导入
from tkinter import filedialog
from PIL import Image,ImageTk
import cv2 as cv
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
Image.MAX_IMAGE_PIXELS = None
imCrop = None
result = None

# 第1步，例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('荧光图像处理小软件')

# 第3步，设定窗口的大小(长 * 宽)
#window.geometry('800x650')
#window.update()  #一定要刷新界面，否则打印出的值是1
#print("当前窗口的宽度为", window.winfo_width())
#print("当前窗口的高度为", window.winfo_height())

# 第4步，在图形界面上设定标签
sub_title = tk.Label(window, text='你好！欢迎使用这个小软件', bg='purple', font=('Arial', 12))
# 说明： bg为背景，font为字体，width为长，height为高，这里的长和高是字符的长和高，比如height=2,就是标签有2个字符这么高
# 第5步，放置标签
sub_title.grid(row = 0,column = 1) # Label内容content区域放置位置，自动调节尺寸
# 放置lable的方法有：1）l.pack(); 2)l.place();
def open_image():
    global a
    global file_path
    global imCrop
    file_path = filedialog.askopenfilename()  #读取图片路径
    origin_image = Image.open(file_path)   #载入图片
    scale_factor = 1
    width, height = origin_image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    origin_image = origin_image.resize((new_width,new_height)) #重新定义图片大小以适应label大小 这里有点问题
    tk_image = ImageTk.PhotoImage(origin_image)  # 转格式
    if a == None:
        a = tk.Label(window, image = tk_image)
        a.image = tk_image
        a.grid(row = 2, column = 2)
    else:
        a.config(image = tk_image)
        a.image = tk_image
    imCrop = None
a = None
import_picture = tk.Button(window, text='导入图片',command= open_image)
import_picture.grid(row = 0 , column=0)#这里写的是导入图片的按键

#图像处理步骤
#1、先学习一下怎么旋转图片 然后再学习一下怎么缩放图片
#def rotate():
agl = tk.IntVar()
agl.set(0)
# 定义setangle函数，为滑块提供反馈
def setangle(value):
    agl.set(value)
# 滑块
scale24 = tk.Scale(a, from_=0, to=360, orient=tk.HORIZONTAL, showvalue=0, tickinterval=45,length = 360,
                   resolution=1, command=setangle)
scale24.grid(row=0, column=2, stick=tk.EW)
# 按钮函数组件1：旋转图像函数
def rotimg():
    # angle.path
    rot_img = cv.imread(file_path)
    angle = agl.get()
    (h, w) = rot_img.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    rotedimg = cv.warpAffine(rot_img, M, (w, h))
    rgb_img = cv.cvtColor(rotedimg, cv.COLOR_BGR2RGB)
    rot_img = Image.fromarray(rgb_img)
    return rot_img
# 利用组件函数，构建按钮函数
def show_rotate():
    img = rotimg()
    # img.show()
    img = ImageTk.PhotoImage(img)
    a.config(image=img)
    window.mainloop()
# 按钮控件
show_rotate_button = tk.Button(window, width=20, command=show_rotate, text='显示旋转图')
show_rotate_button.grid(row=1, column=1, stick=tk.EW)
# 角度显示盘
show_angle = tk.Label(window, textvariable=str(agl), bg='pink')
show_angle.grid(row=1, column=0, stick=tk.EW)
#1.5 、实现局部放大(这里也是个难点) #我感觉这个功能有点没必要



#2、选中感兴趣区域(这里可能是个难点)
def display_roi(event):
    global tkimg
    global roi_image

    if roi_image:
        tkimg = ImageTk.PhotoImage(roi_image)
        a.config(image=tkimg)

def select_roi():
    global roi
    global roi_image
    global imCrop
    roi_img = cv.imread(file_path)
    scale_factor = 1 # 缩放因子
    resized_img = cv.resize(roi_img, None, fx=scale_factor, fy=scale_factor)
    # 等比例缩放
    roi = cv.selectROI(resized_img)  # 在缩放图像上选择ROI
    imCrop = resized_img[int(roi[1] ):int((roi[1] + roi[3]) ),
               int(roi[0] ):int((roi[0] + roi[2]) )]
    if len(imCrop) > 0:
        roi_image = Image.fromarray(cv.cvtColor(imCrop, cv.COLOR_BGR2RGB))


        cv.destroyAllWindows()
        window.event_generate("<<ROISELECTED>>")
def start_thread():
    thread = Thread(target=select_roi, daemon=True)
    thread.start()

#cropped_lbl = tk.Label(window)
#cropped_lbl.grid(row = 3, column = 3)

tk.Button(window, text="select ROI", command=start_thread).grid(row=2,column=0)
window.bind("<<ROISELECTED>>", display_roi)
#3、滤波、形态学处理，图像拼接等，这里应该很简单 调用opencv的库就可以了（简单个der啊，我真要吐了)
#这里进行滤波处理 但是感觉边缘有点问题 最好进行Image Enhancement
def filter_image():
    global imCrop
    global result
    if imCrop is not None: #假如选取了roi区域就对roi区域进行处理
        average_img = cv.blur(result,(3,3))
        gaussian_img = cv.GaussianBlur(result,(3,3),0)
        # average_img = cv.cvtColor(average_img, cv.COLOR_BGR2RGB) #假如用了result就不用再反转了
        # gaussian_img= cv.cvtColor(gaussian_img, cv.COLOR_BGR2RGB)
        gray_image = cv.cvtColor(imCrop, cv.COLOR_BGR2GRAY)
        filtered_image = cv.bilateralFilter(gray_image, d=3, sigmaColor=5, sigmaSpace=5)
        filtered_image = cv.cvtColor(filtered_image, cv.COLOR_BGR2RGB)
    else: #假如没有就对原图进行处理
        img = cv.imread(file_path)
        average_img = cv.blur(result, (3, 3))
        gaussian_img = cv.GaussianBlur(result, (3, 3), 0)
        # average_img = cv.cvtColor(average_img, cv.COLOR_BGR2RGB)
        # gaussian_img = cv.cvtColor(gaussian_img, cv.COLOR_BGR2RGB)#这里还可以多加一点滤波操作
        gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        filtered_image = cv.bilateralFilter(gray_image, d=3, sigmaColor=5, sigmaSpace=5)
        filtered_image = cv.cvtColor(filtered_image, cv.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 8))
    imgs=[average_img,gaussian_img,filtered_image]

    plt.subplot(1, 3, 1)
    plt.imshow(imgs[0])
    plt.title("average_filter")


    plt.subplot(1, 3, 2)
    plt.imshow(imgs[1])
    plt.title("gaussian_filter")

    plt.subplot(1, 3, 3)
    plt.imshow(imgs[2])
    plt.title("bilateral_filter")

    plt.suptitle("Images")
    plt.show()


filter_btn = tk.Button(window, text='Filter', command=filter_image)
filter_btn.grid(row =3,column=0)


def Enhancement_image():
    global imCrop
    global result
    img = cv.imread(file_path)
    if imCrop is  None: #假如选取了roi区域就对roi区域进行处理 #假如没有就对原图进行处理
        SobelX = cv.Sobel(img, cv.CV_16S, 1, 0)  # 计算 x 轴方向
        SobelY = cv.Sobel(img, cv.CV_16S, 0, 1)  # 计算 y 轴方向
        absX = cv.convertScaleAbs(SobelX)  # 转回 uint8
        absY = cv.convertScaleAbs(SobelY)  # 转回 uint8
        SobelXY = cv.addWeighted(absX, 0.5, absY, 0.5, 0)  # 用绝对值近似平方根
        SobelXY = cv.cvtColor(SobelXY, cv.COLOR_BGR2RGB)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        result = cv.add(img, SobelXY)
    else:
        SobelX = cv.Sobel(imCrop, cv.CV_16S, 1, 0)  # 计算 x 轴方向
        SobelY = cv.Sobel(imCrop, cv.CV_16S, 0, 1)  # 计算 y 轴方向
        absX = cv.convertScaleAbs(SobelX)  # 转回 uint8
        absY = cv.convertScaleAbs(SobelY)  # 转回 uint8
        SobelXY = cv.addWeighted(absX, 0.5, absY, 0.5, 0)  # 用绝对值近似平方根
        SobelXY = cv.cvtColor(SobelXY, cv.COLOR_BGR2RGB)
        imCrop = cv.cvtColor(imCrop, cv.COLOR_BGR2RGB)
        result = cv.add(imCrop, SobelXY)



    # result = cv.seamlessClone(SobelXY, imCrop, np.ones(SobelXY.shape, dtype=np.uint8) * 2, (0, 0), cv.NORMAL_CLONE)

    pil_img = Image.fromarray(result)
    img = ImageTk.PhotoImage(pil_img)
    a.config(image=img)
    window.mainloop()


Enhancement_btn = tk.Button(window, text='Enhancement', command=Enhancement_image)
Enhancement_btn.grid(row =4,column=0)

def cal_mean_light():
    global result
    img = cv.imread(file_path)
    img= cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(img, 0, 255, cv.THRESH_OTSU)#进行阈值化处理
    cell_area = cv.bitwise_and(img, img, mask=thresh)
    cell_pixels = cv.countNonZero(cell_area)
    image_pixels = img.shape[0] * img.shape[1]


    cell_mean = cv.mean(cell_area)[0]
    intensity = cell_mean * cell_pixels / image_pixels
    plt.figure(figsize=(12, 8))
    img = cv.cvtColor(img,cv.COLOR_BGR2RGB)
    plt.imshow(img)

    plt.suptitle("Images")
    plt.show()
    cal_mean_light.config(text=intensity)
    window.mainloop()


cal_mean_light_btn = tk.Button(window, text='cal_mean_light', command=cal_mean_light)
cal_mean_light_btn.grid(row =5,column=0)
cal_mean_light= tk.Label(window, text='这里是放平均荧光强度的地方', bg='green', font=('Arial', 12))
cal_mean_light.grid(row = 6,column =0)


#4、利用cellpose 对荧光细胞进行分割和处理、图形检测/细胞计数(这里也应该是个难点）不可能做的

#5、图像合并，图像转换格式
# 已经做完了
#6、平均荧光强度检测/定量/面积测量（差不多得了 流汗黄豆）这个还真得做

#7、保存图像



# 主窗口循环显示
window.mainloop()