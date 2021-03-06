#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

MIAO_LOG = "logs/jd.log"

DEVICE_NAME = 'xiaomi'
DEVICE_PORT = '4723'

# 安卓版本
ANDROID_VERSION = "11"
DESIRED_CAPS = {
    "platformName": "Android",
    "platformVersion": ANDROID_VERSION,
    # "deviceName": "Android Emulator",
    "deviceName": DEVICE_NAME,
    "appPackage": "com.jingdong.app.mall",
    "appActivity": ".main.MainActivity",
    # 再次启动不需要再次安装
    "noReset": True,
    # unicode键盘 我们可以输入中文
    "unicodeKeyboard": True,
    # 操作之后还原回原先的输入法
    "resetKeyboard": True
}

# 找不到元素的时间
TIME_OUT = 10

# 首页是否使用XPATH找入口
HOME_XPATH_FLAG = True


# 执行每日签到
# DO_SIGN_FLAG = True
DO_SIGN_FLAG = False

# 执行任务
DO_COINS_FLAG = True
#DO_COINS_FLAG = False

# 执行任务:收取生产的币
# RECEIVE_COINS_FLAG = True
RECEIVE_COINS_FLAG = False

# 执行中间按钮的打卡按钮
#DO_DA_KA_FLAG = True
DO_DA_KA_FLAG = False

# 打卡领红包 循环执行次数
DA_KA_LOOP = 10

# 第6个位置
WINDOWS_XPATH = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[6]/android.view.View[2]/android.view.View'''

# 第7个位置
WINDOWS_XPATH2 = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[7]/android.view.View[2]/android.view.View'''

# 任务列表
TASK_LIST = [
    '浏览并关注',
    '浏览8s可得',
    '浏览可得3000',
    '去领取',
    '关闭'
]

# 过滤的任务列表
SKIP_LIST = [
    '去玩城城分千元现金(0/1)',
]

