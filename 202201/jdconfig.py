#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

APPIUM_LOG = "logs/jd.log"

DEVICE_NAME = 'xiaomi'
DEVICE_PORT = '4723'

# 安卓版本
ANDROID_VERSION = "11"
# 此值取自adb devices，没配置默认取第一条记录。连多台手机需要这个值，未试验。
UUID = "c7106c90"
DESIRED_CAPS = {
    "platformName": "Android",
    "platformVersion": ANDROID_VERSION,
    # "deviceName": "Android Emulator",
    "deviceName": DEVICE_NAME,
    # "udid": UUID,
    "appPackage": "com.jingdong.app.mall",
    "appActivity": ".main.MainActivity",
    # 再次启动不需要再次安装
    "noReset": True,
    # unicode键盘 我们可以输入中文
    "unicodeKeyboard": True,
    # 操作之后还原回原先的输入法
    "resetKeyboard": True
}

# 调试写入html
DEBUG_HTML = False

# 找不到元素的时间
TIME_OUT = 10

# 第一次处理弹窗
# FIRST_WINDOWS_FLAG = True
FIRST_WINDOWS_FLAG = False

# 执行每日签到
DO_SIGN_FLAG = True
# DO_SIGN_FLAG = False

# 执行任务
DO_TASKS_FLAG = True
# DO_TASKS_FLAG = False

# 执行任务:收取爆竹
RECEIVE_BOMB_FLAG = True
# RECEIVE_BOMB_FLAG = False

# 执行中间按钮进行升级
DO_DA_KA_FLAG = True
# DO_DA_KA_FLAG = False

# 打卡领红包 循环执行次数
DA_KA_LOOP = 10

# 第6个位置
WINDOWS_XPATH = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[6]/android.view.View[2]/android.view.View'''

# 第7个位置
WINDOWS_XPATH2 = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[7]/android.view.View[2]/android.view.View'''

# 金融app任务列表按钮
JR_TASK_LISTS_BUTTON_XPATH = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[3]'''

# WX app任务列表按钮，暂时随便写的
WX_TASK_LISTS_BUTTON_XPATH = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[3]'''


# 任务列表
TASK_LIST = [
    '去种草城',
    '去浏览',
    '浏览并关注可得',
    '浏览并关注',
    '浏览8s可得',
    '浏览可得3000',
    '浏览可得5000',
    '累计浏览',
    '去领取',
    '去小程序玩',
    '参与城城点击',
    '去组队可得',
    #'成功入会并浏览',
    #'底部跳转app',
    '关闭'
]

# 过滤的任务列表
SKIP_LIST = [
    # '参与城城点击',
    # '去小程序玩',
    '去加购',
]

# 金融任务列表
JR_TASK_LIST = [
    '浏览8秒领',
    '浏览领',
    '浏览分期年货节',
    '浏览活动',
    '浏览',
    '去领取',
    '关闭'
]
