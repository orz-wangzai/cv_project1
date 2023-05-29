import tkinter as tk  # 使用Tkinter前需要先导入
from tkinter import filedialog
from PIL import Image,ImageTk
import cv2 as cv
from threading import Thread
Image.MAX_IMAGE_PIXELS = None
# 第1步，实例化object，建立窗口window
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
    file_path = filedialog.askopenfilename()  #
    image = Image.open(file_path)   #载入图片
    image = image.resize((300,200)) #重新定义图片大小以适应label大小
    tk_image = ImageTk.PhotoImage(image)  # 转格式
    if a == None:
        a = tk.Label(window, image = tk_image)
        a.image = tk_image
        a.grid(row = 2, column = 2)
    else:
        a.config(image = tk_image)
        a.image = tk_image
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
    img = cv.imread(file_path)
    angle = agl.get()
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    rotedimg = cv.warpAffine(img, M, (w, h))
    rgb_img = cv.cvtColor(rotedimg, cv.COLOR_BGR2RGB)
    img = Image.fromarray(rgb_img)
    img = img.resize((300, 200))
    return img
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
#1.5 、实现局部放大(这里也是个难点)

def display_roi(event):
    global tkimg

    if image:
        tkimg = ImageTk.PhotoImage(image)
        cropped_lbl.config(image=tkimg)

def select_roi():
    global image

    img = cv.imread(file_path)
    scale_factor = 0.05 # 缩放因子
    resized_img = cv.resize(img, None, fx=scale_factor, fy=scale_factor)
    # 等比例缩放
    roi = cv.selectROI(resized_img)  # 在缩放图像上选择ROI
    imCrop = resized_img[int(roi[1] ):int((roi[1] + roi[3]) ),
               int(roi[0] ):int((roi[0] + roi[2]) )]
    if len(imCrop) > 0:
        image = Image.fromarray(cv.cvtColor(imCrop, cv.COLOR_BGR2RGB))


        cv.destroyAllWindows()
        window.event_generate("<<ROISELECTED>>")

def start_thread():
    thread = Thread(target=select_roi, daemon=True)
    thread.start()

cropped_lbl = tk.Label(window)
cropped_lbl.grid(row = 3, column = 3)

tk.Button(window, text="select ROI", command=start_thread).grid(row=2,column=0)
window.bind("<<ROISELECTED>>", display_roi)

#2、选中感兴趣区域(这里可能是个难点)

#3、滤波、形态学处理，图像拼接等，这里应该很简单 调用opencv的库就可以了
#4、利用cellpose 对荧光细胞进行分割和处理、图形检测/细胞计数(这里也应该是个难点）
#5、图像合并，图像转换格式
#6、平均荧光强度检测/定量/面积测量（差不多得了 流汗黄豆）



# 主窗口循环显示
window.mainloop()
