#!/usr/bin/python
# coding=utf-8
# 公众号:testerzhang
__author__ = 'testerzhang'

import time
import traceback

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import parse
from loguru import logger

import jdconfig as config

logger.add(config.APPIUM_LOG)


def wait_time_bar(wait_sec):
    logger.debug(f"等待{wait_sec}秒")
    wait_value = 10 * wait_sec

    for i in tqdm(range(wait_value)):
        time.sleep(0.1)

    # logger.debug("")


class JD(object):
    def __init__(self):
        device_port = config.DEVICE_PORT

        desired_caps = config.DESIRED_CAPS

        self.skip_list = config.SKIP_LIST

        url = "http://localhost:{}/wd/hub".format(device_port)

        self.driver = webdriver.Remote(url, desired_caps)
        self.wait = WebDriverWait(self.driver, config.TIME_OUT)

        self.windows_xpath = config.WINDOWS_XPATH
        self.windows_xpath2 = config.WINDOWS_XPATH2

        logger.debug("1.打开京东")
        wait_time_bar(2)

    # 关闭
    def close(self):
        wait_time_bar(5)
        logger.debug("6.关闭app")
        self.driver.quit()

    # 判断某些任务是不是直接跳过
    def continue_task(self, content):
        is_continue = True
        for skip in self.skip_list:
            if skip in content:
                logger.warning(f"任务=[{content}]暂时不做")
                is_continue = False
                break

        return is_continue

    # 首页查找入口
    def active_page(self):
        search_result = False

        sleep_time = 5
        logger.debug(f"2.查找活动入口")
        # source = self.driver.page_source
        # logger.debug(f"首页source:{source}")

        if not config.HOME_XPATH_FLAG:
            wait_time_bar(sleep_time)
            logger.debug(f"使用位置来点击入口")
            # 目前，这个逻辑没去实现。
            # 每个手机位置不一样，需要根据bounds（(如：[26,1025][540,1290]）重新设定
            # self.driver.tap([(26, 1025), (540, 1290)], 100)
            # search_result = True
        else:
            try:
                # 搜索框
                search_div = '//android.widget.TextView[contains(@content-desc,"搜索")]'
                search = self.wait.until(EC.presence_of_element_located((By.XPATH, search_div)))
                search.click()
                wait_time_bar(2)

                # source = self.driver.page_source
                # logger.debug(f"搜索页面的source:{source}")
                # web_view = self.driver.contexts
                # logger.debug(web_view)

                # 输入搜索文本，这里目前只能是用ID，xpath解析异常 [182,114][942,170]
                search_text_id = 'com.jd.lib.search.feature:id/a53'
                box = self.wait.until(EC.presence_of_element_located((By.ID, search_text_id)))

                # search_text_xpath = '//android.view.View[contains(@content-desc, "搜索框")]'
                # search_text_xpath = '//android.widget.ImageView[@content-desc="拍照购"]/../android.view.View'
                # box = self.wait.until(EC.presence_of_element_located((By.XPATH, search_text_xpath)))

                box.set_text("炸年兽")

                # 点击搜索按钮
                search_btn_xpath = '//android.widget.TextView[@content-desc="搜索，按钮"]'
                button = self.wait.until(EC.presence_of_element_located((By.XPATH, search_btn_xpath)))
                button.click()

                door_xpath = '//androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout[@index="2"]'
                door_button = self.wait.until(EC.presence_of_element_located((By.XPATH, door_xpath)))
                door_button.click()
                search_result = True
                logger.debug("进入活动入口")
            except:
                raise Exception("找不到活动入口")

        if search_result:
            # 加载新页面时间
            wait_time_bar(5)

        return search_result

    def close_windows(self):
        try:
            count_div = f'//*[@text="累计任务奖励"]/../../android.view.View[1]'
            count_elm = self.driver.find_element(By.XPATH, count_div)
            logger.debug(f"点击关闭按钮")
            count_elm.click()

        except:
            logger.warning(f"点击关闭异常")
            # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")

    #  gzh:testerzhang 做任务列表，还不能做全部，后续再看看。
    def do_task(self):
        # source = self.driver.page_source
        # logger.debug(f"做任务source:{source}")

        # 配置文件配置需要执行的任务清单
        task_list = config.TASK_LIST

        for task in task_list:

            while True:
                # 开始做任务
                logger.debug(f"开始真正做任务列表:【{task}】")

                if task in ["去领取"]:
                    try:
                        # source = self.driver.page_source
                        # logger.debug(f"做任务source:{source}")

                        progress_div = f'//*[@text="累计任务奖励"]/../android.view.View[3]/android.view.View/android.view.View'
                        progress_elm_lists = self.driver.find_elements(By.XPATH, progress_div)
                        logger.debug(f"找到[去领取]区域长度={len(progress_elm_lists)}")
                        for i, progress_elm in enumerate(progress_elm_lists, 0):
                            if i == 0:
                                continue
                            logger.debug(f"尝试点击第{i}个[去领取]")
                            progress_elm.click()
                            wait_time_bar(2)

                            # todo:关闭弹窗
                            # text="+500汪汪币"
                            close_tip_div = f'//android.view.View[contains(@text, "+")]'
                            close_tip_lists = self.driver.find_elements(By.XPATH, close_tip_div)
                            if len(close_tip_lists) > 0:
                                close_tip_elm = close_tip_lists[0]
                                tips = close_tip_elm.text
                                logger.debug(f"tips={tips}")
                                if '爆竹' in tips:
                                    logger.debug(f"关闭弹窗")
                                    # todo:不确定是否可以正常
                                    self.close_windows()

                            wait_time_bar(2)


                    except:
                        logger.warning(f"[去领取]异常={traceback.format_exc()}")
                    else:
                        wait_time_bar(8)
                    break
                elif task in ["关闭"]:
                    self.close_windows()

                    break
                elif '浏览' in task:
                    init_loop = 0
                    max_loop = 3
                    jump_loop_flag = 0

                    while init_loop < max_loop:
                        init_loop = init_loop + 1

                        if jump_loop_flag == 1:
                            logger.debug(f"超过循环次数，退出该类任务。")
                            break

                        try:
                            logger.debug(f"检查任务:【{task}】是否存在")
                            # task_div = f'//*[@text="{task}"]'
                            task_second_title_div = f'//*[contains(@text, "{task}")]'
                            task_second_title = self.driver.find_element(By.XPATH, task_second_title_div)
                            task_second_title_text = task_second_title.text
                            logger.debug(f"任务副标题={task_second_title_text}")
                        except:
                            logger.warning(f"该任务:【{task}】不执行")
                            # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                            break

                        if '成功入会并浏览可得' in task_second_title_text:
                            logger.warning(f"成功入会任务不做")
                            break
                        elif '浏览并加购' in task_second_title_text:
                            logger.warning(f"浏览并加购任务不做")
                            break
                        elif '去财富岛' in task_second_title_text:
                            logger.debug(f"财富岛任务不做")
                            break
                        elif '去小程序' in task_second_title_text:
                            logger.debug(f"去小程序任务不做")
                            break

                        try:
                            task_title_div = f'{task_second_title_div}//preceding-sibling::android.view.View[1]'
                            task_title_elm = self.driver.find_element(By.XPATH, task_title_div)
                            # 获取标题
                            task_title_elm_text = task_title_elm.text
                            logger.debug(f"任务标题={task_title_elm_text}")
                        except:
                            logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                            # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                            break

                        # 判断是否任务跳过
                        is_continue = self.continue_task(task_title_elm_text)

                        if not is_continue:
                            logger.warning(f"满足跳过任务关键字，退出2")
                            continue

                        # 开始点击
                        result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_elm_text}")
                        now_times = int(result['now_times'])
                        total_times = int(result['total_times'])
                        logger.debug(f"now_times={now_times},total_times={total_times}")
                        if now_times == total_times and total_times > 0:
                            continue
                        else:
                            while now_times < total_times:
                                # 当前节点是index=2，查找节点android.view.View index="3"
                                try:
                                    task_title_div = f'{task_second_title_div}//following-sibling::android.view.View[1]'
                                    task_button_elm = self.driver.find_element(By.XPATH, task_title_div)
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                    # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                    jump_loop_flag = 1
                                    break

                                # 开始任务点击
                                logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_elm_text}:开始执行")
                                task_button_elm.click()

                                if '直播间' in task_title_elm_text:
                                    # 直播时间更长
                                    wait_time_bar(5 + 20)
                                    logger.debug(f"关闭关注主播弹窗")
                                    self.driver.back()
                                else:
                                    wait_time_bar(5 + 10)

                                logger.debug(f"返回一下，然后稍微休息")
                                self.driver.back()
                                wait_time_bar(3)

                                now_times = now_times + 1

                                # 更新任务正标题
                                try:
                                    task_title_div = f'{task_second_title_div}//preceding-sibling::android.view.View[1]'
                                    task_title_elm = self.driver.find_element(By.XPATH, task_title_div)
                                    # 获取标题
                                    task_title_elm_text = task_title_elm.text
                                    logger.debug(f"任务标题={task_title_elm_text}")
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                    # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                    continue

                    break
                elif '城城' in task:

                    try:
                        logger.debug(f"检查任务:【{task}】是否存在")
                        # task_div = f'//*[@text="{task}"]'
                        task_second_title_div = f'//*[contains(@text, "{task}")]'
                        task_second_title = self.driver.find_element(By.XPATH, task_second_title_div)
                        task_second_title_text = task_second_title.text
                        logger.debug(f"任务副标题={task_second_title_text}")
                    except:
                        logger.warning(f"该任务:【{task}】不执行")
                        # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                        break

                    try:
                        task_title_div = f'{task_second_title_div}//preceding-sibling::android.view.View[1]'
                        task_title_elm = self.driver.find_element(By.XPATH, task_title_div)
                        # 获取标题
                        task_title_elm_text = task_title_elm.text
                        logger.debug(f"任务标题={task_title_elm_text}")
                    except:
                        logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                        # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                        break

                    # 判断是否任务跳过
                    is_continue = self.continue_task(task_title_elm_text)

                    if not is_continue:
                        logger.warning(f"满足跳过任务关键字，退出2")
                        break

                    # 开始点击
                    result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_elm_text}")
                    now_times = int(result['now_times'])
                    total_times = int(result['total_times'])
                    logger.debug(f"now_times={now_times},total_times={total_times}")
                    if now_times == total_times and total_times > 0:
                        break
                    else:
                        while now_times < total_times:
                            # 当前节点是index=2，查找节点android.view.View index="3"
                            try:
                                task_title_div = f'{task_second_title_div}//following-sibling::android.view.View[1]'
                                task_button_elm = self.driver.find_element(By.XPATH, task_title_div)
                            except:
                                logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                jump_loop_flag = 1
                                break

                            # 开始任务点击
                            logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_elm_text}:开始执行")
                            task_button_elm.click()

                            wait_time_bar(6)
                            self.process_city()

                            logger.debug(f"返回一下，然后稍微休息")
                            self.driver.back()
                            wait_time_bar(3)

                            now_times = now_times + 1

                            # 更新任务正标题
                            try:
                                task_title_div = f'{task_second_title_div}//preceding-sibling::android.view.View[1]'
                                task_title_elm = self.driver.find_element(By.XPATH, task_title_div)
                                # 获取标题
                                task_title_elm_text = task_title_elm.text
                                logger.debug(f"任务标题={task_title_elm_text}")
                            except:
                                logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                break
                    break

                elif '小程序' in task:

                    try:
                        logger.debug(f"检查任务:【{task}】是否存在")
                        # task_div = f'//*[@text="{task}"]'
                        task_second_title_div = f'//*[contains(@text, "{task}")]'
                        task_second_title = self.driver.find_element(By.XPATH, task_second_title_div)
                        task_second_title_text = task_second_title.text
                        logger.debug(f"任务副标题={task_second_title_text}")
                    except:
                        logger.warning(f"该任务:【{task}】不执行")
                        # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                        break

                    try:
                        task_title_div = f'{task_second_title_div}//preceding-sibling::android.view.View[1]'
                        task_title_elm = self.driver.find_element(By.XPATH, task_title_div)
                        # 获取标题
                        task_title_elm_text = task_title_elm.text
                        logger.debug(f"任务标题={task_title_elm_text}")
                    except:
                        logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                        # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                        break

                    # 判断是否任务跳过
                    is_continue = self.continue_task(task_title_elm_text)

                    if not is_continue:
                        logger.warning(f"满足跳过任务关键字，退出2")
                        break

                    # 开始点击
                    result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_elm_text}")
                    now_times = int(result['now_times'])
                    total_times = int(result['total_times'])
                    logger.debug(f"now_times={now_times},total_times={total_times}")
                    if now_times == total_times and total_times > 0:
                        break
                    else:
                        while now_times < total_times:
                            # 当前节点是index=2，查找节点android.view.View index="3"
                            program_flag = 0
                            try:
                                task_title_div = f'{task_second_title_div}//following-sibling::android.view.View[1]'
                                task_button_elm = self.driver.find_element(By.XPATH, task_title_div)
                            except NoSuchElementException:
                                logger.warning(f"没找到【去完成】按钮")
                                program_flag = 1
                            except:
                                logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行。异常={traceback.format_exc()}")
                                break

                            if program_flag == 1:
                                try:
                                    task_title_div = f'{task_second_title_div}//following-sibling::android.view.View[2]'
                                    task_button_elm = self.driver.find_element(By.XPATH, task_title_div)
                                except NoSuchElementException:
                                    logger.warning(f"再次没找到【去完成】按钮")
                                    break
                                except:
                                    logger.warning(f"该任务:【{task}】再次获取任务按钮异常,不执行。异常={traceback.format_exc()}")
                                    break

                            # 开始任务点击
                            logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_elm_text}:开始执行")
                            logger.debug(task_button_elm.get_attribute("bounds"))
                            task_button_elm.click()

                            # todo: 可能会有bug
                            wait_time_bar(5)
                            if self.driver.current_package != "com.jingdong.app.mall":
                                self.driver.back()

                            wait_time_bar(3)
                            if self.driver.current_package != "com.jingdong.app.mall":
                                self.driver.back()

                            logger.debug(f"返回一下，然后稍微休息")
                            if self.driver.current_package != "com.jingdong.app.mall":
                                self.driver.back()
                            wait_time_bar(5)

                            now_times = now_times + 1

                            # 更新任务正标题
                            try:
                                task_title_div = f'{task_second_title_div}//preceding-sibling::android.view.View[1]'
                                task_title_elm = self.driver.find_element(By.XPATH, task_title_div)
                                # 获取标题
                                task_title_elm_text = task_title_elm.text
                                logger.debug(f"任务标题={task_title_elm_text}")
                            except:
                                logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                break
                    break
                else:
                    logger.warning(f"其他任务不做:【{task}】")
                    break

        return

    # 处理"城城"
    def process_city(self):

        try:
            logger.debug(f"处理城城广告窗")
            city_close_title_div = '''//android.view.View[@resource-id="dialogs"]/android.view.View[2]/android.view.View/android.view.View/android.view.View[3]'''
            city_close_button_elm = self.driver.find_element(By.XPATH, city_close_title_div)
            city_close_button_elm.click()
        except NoSuchElementException:
            logger.warning(f"没找到关闭城城弹窗")
        except:
            logger.warning(f"关闭城城弹窗异常,不执行。{traceback.format_exc()}")
            return

        wait_time_bar(3)
        try:
            logger.debug(f"进入城城主页面，点击【邀3人立领现金】按钮")
            invite_div = '''//android.view.View[@resource-id="app"]/android.view.View/android.view.View/android.view.View[9]/android.view.View[2]'''
            invite_button_elm = self.driver.find_element(By.XPATH, invite_div)
            invite_button_elm.click()
            # todo:未测试，从微信返回
            self.driver.back()
        except:
            logger.warning(f"点击【邀3人立领现金】按钮异常,不执行")
            return

    #  gzh:testerzhang 点击生产出来的爆竹
    def collect_bomb(self):
        # source = self.driver.page_source
        # logger.debug(f"领取币source:{source}")

        try:
            logger.debug("开始点击【年兽】图标，收集爆竹")

            collect_bomb_div = '''//android.view.View[@resource-id="root"]/android.view.View[1]/android.view.View[3]'''
            collect_bomb_button = self.driver.find_element(By.XPATH, collect_bomb_div)
            # logger.debug(collect_bomb_button.get_attribute("bounds"))
            collect_bomb_button.click()
        except NoSuchElementException:
            pass
        except:
            logger.warning(f"【年兽】点击异常={traceback.format_exc()}")

        wait_time_bar(3)
        return

    def write_html(self, filename):
        source = self.driver.page_source
        # logger.debug(f"页面source:{source}")
        file_name = f"doc/{filename}"
        with open(file_name, 'w') as f:
            f.write(source)

    #  gzh:testerzhang 点击每日签到
    def do_sign(self):

        try:
            # 今日已签到
            logger.debug(f"查找是否含有【今日已签到】文字")
            query_sign_div_xpath = f'//android.view.View[@text="今日已签到"]'
            query_sign_div_elm = self.driver.find_element(By.XPATH, query_sign_div_xpath)
            # logger.debug(f"query_sign_div_elm={query_sign_div_elm}")
            if query_sign_div_elm is not None:
                logger.debug(f"【今日已签到】，不需要签到")
                return
        except NoSuchElementException as msg:
            pass
        except:
            logger.warning(f"查找【今日已签到】文字点击异常={traceback.format_exc()}")

        try:
            # 签到领红包签到领红包
            logger.debug(f"开始点击[签到领红包签到领红包]按钮")
            sign_div_xpath = f'//android.view.View[@text="签到领红包签到领红包"]'
            sign_div_lists = self.driver.find_element(By.XPATH, sign_div_xpath)
            sign_div_lists.click()
        except:
            logger.warning(f"点击[签到领红包签到领红包]按钮点击异常={traceback.format_exc()}")
        else:
            wait_time_bar(2)
            # 开始点击页面的"点我签到"按钮
            self.sign_page()

    # 签到页面处理
    def sign_page(self):
        try:
            # 明天再来明天再来
            logger.debug(f"查找是否含有【明天再来明天再来】文字")
            query_sign_div_xpath = f'//android.view.View[@text="明天再来明天再来"]'
            query_sign_div_elm = self.driver.find_element(By.XPATH, query_sign_div_xpath)
            # logger.debug(f"query_sign_div_elm={query_sign_div_elm}")
            if query_sign_div_elm is not None:
                logger.debug(f"【今日已签到】,准备退出弹窗")

                try:
                    logger.debug(f"尝试点击[关闭]按钮")
                    # 可能这个位置后续会变
                    close_div_xpath = f'{self.windows_xpath}/android.view.View[2]'

                    close_div_elm = self.driver.find_element(By.XPATH, close_div_xpath)
                    close_div_elm.click()
                except NoSuchElementException as msg:
                    pass
                except:
                    logger.warning(f"点击[关闭]动作异常={traceback.format_exc()}")

                return
        except NoSuchElementException as msg:
            pass
        except:
            logger.warning(f"查找【明天再来明天再来】文字处理异常={traceback.format_exc()}")

        try:
            logger.debug(f"查找是否含有【点我签到】按钮")
            sign_div_xpath = f'//android.view.View[@text="点我签到点我签到"]'
            sign_div_elm = self.driver.find_element(By.XPATH, sign_div_xpath)
            logger.debug(f"sign_div_elm={sign_div_elm}")
            if sign_div_elm is not None:
                logger.debug(f"点击【点我签到】按钮")
                sign_div_elm.click()

        except:
            logger.warning(f"点击[点我签到]按钮点击异常={traceback.format_exc()}")
        else:
            # todo: 处理弹窗，还没测试。

            wait_time_bar(3)

            try:
                logger.debug(f"开始点击[开心收下]按钮的关闭按钮")
                # 开心收下 弹窗
                sign_close_div_xpath = '//android.view.View[text="开心收下开心收下"]'
                sign_close_div_elm = self.driver.find_element(By.XPATH, sign_close_div_xpath)
                if sign_div_elm is not None:
                    sign_close_div_elm.click()
            except:
                logger.warning(f"点击[开心收下]按钮点击异常={traceback.format_exc()}")
            else:
                wait_time_bar(2)

    #  gzh:testerzhang 点击任务列表按钮，然后进入具体的任务列表
    def do_tasks(self, button_name):
        try:
            logger.debug(f"开始点击[{button_name}]按钮")
            button_div_xpath = '''//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[2]'''
            button_div_lists = self.driver.find_elements(By.XPATH, button_div_xpath)
            len_button_div_lists = len(button_div_lists)
            # logger.debug(f"button_div_lists={button_div_lists},len={len_button_div_lists}")

            if len_button_div_lists == 0:
                return

            button_div_lists[-1].click()
        except:
            logger.warning(f"【{button_name}】点击异常={traceback.format_exc()}")
        else:
            wait_time_bar(3)
            # 最新任务列表签到
            self.do_task()

    #  gzh:testerzhang 首页处理点爆竹
    def zha(self):
        # 加多一层最大次数，防止循环。
        max_times = config.DA_KA_LOOP

        logger.debug("开始集爆竹炸年兽")

        times = 1
        logger.debug(f"开始执行，最大执行次数={max_times}次")

        while True:
            logger.debug(f"开始执行第{times}次")
            if times > max_times:
                break

            try:
                wait_time_bar(2)
                # # 喂猫领红包,每次消耗89000个爆竹
                logger.debug("开始点击【集爆竹炸年兽】图标")
                # 每次消耗89000个爆竹
                feed_div = '//*[contains(@text, "每次消耗")]'
                self.driver.find_element(By.XPATH, feed_div).click()
            except NoSuchElementException:
                logger.warning(f"无法找到【集爆竹炸年兽】这个元素")
                # 可能是因为弹窗了，暂时没修复。
                # logger.debug(f"返回一下")
                break
            except:
                logger.warning(f"【集爆竹炸年兽】点击异常={traceback.format_exc()}")
                break
            else:
                wait_time_bar(5)
                # todo: 只处理了两种弹窗，其他弹窗，后续再搞。

                try:
                    logger.debug(f"尝试点击[开心收下]弹窗")
                    # 开心收下 弹窗
                    receive_div_xpath = '//android.view.View[text="开心收下开心收下"]'
                    receive_div_elm = self.driver.find_element(By.XPATH, receive_div_xpath)
                    if receive_div_elm is not None:
                        receive_div_elm.click()
                except NoSuchElementException:
                    pass
                except:
                    logger.warning(f"点击[开心收下]按钮点击异常={traceback.format_exc()}")

                close_flag = 0

                if close_flag == 0:
                    # 爆竹不够的时候，弹出任务列表
                    try:
                        logger.debug("尝试关闭[任务列表]")
                        task_list_xpath = '//*[contains(@text, "累计任务奖励")]'
                        self.driver.find_element(By.XPATH, task_list_xpath)
                        # 点击右上角关闭按钮
                        self.close_windows()
                        # 退出
                        logger.warning("爆竹不够了，不再执行循环。")
                        break
                    except NoSuchElementException as msg:
                        pass
                    except:
                        logger.warning(f"尝试关闭[任务列表]异常={traceback.format_exc()}")
                else:
                    # todo: 这里还可能有弹窗。
                    pass

            times = times + 1

        return

    # 第一次进入页面，弹窗处理
    def process_windows(self):
        # todo:判断弹框:继续抽奖

        try:
            windows_div = '//android.widget.ImageView[content-desc="返回"]'
            windows_button = self.driver.find_element(By.XPATH, windows_div)
            logger.debug(f"windows_button.text=[{windows_button.text}]")
            windows_button.click()
        except NoSuchElementException as msg:
            logger.warning(f"忽略")
        except:
            logger.warning(f"弹窗进行处理异常={traceback.format_exc()}")

        # plus会员弹窗,未测试。
        plus_flag = 0
        try:
            logger.debug(f"看是否有[Plus弹窗]")
            # plus_div = '//android.view.View[text="送您"]'
            plus_flag_div = '//android.view.View[text="Plus专享"]'
            plus_flag_button = self.driver.find_element(By.XPATH, plus_flag_div)
            logger.debug(f"plus_flag_button.text=[{plus_flag_button.text}]")

            plus_div = '//android.view.View[text="Plus专享"]/../../following-sibling::android.view.View[1]/android.view.View'
            plus_button = self.driver.find_element(By.XPATH, plus_div)
            logger.debug(f"plus_button.text=[{plus_button.text}]")

            plus_button.click()
            plus_flag = 1
        except NoSuchElementException as msg:
            # logger.warning(f"未找到plus弹窗，忽略")
            pass
        except:
            logger.warning(f"弹窗进行处理异常={traceback.format_exc()}")

        # 点击plus按钮之后，进入签到弹窗，未测试。
        if plus_flag == 1:
            try:
                sign_flag_div = '//android.view.View[text="每天来签到，得最高111.1元红包"]'
                sign_flag_button = self.driver.find_element(By.XPATH, sign_flag_div)
                logger.debug(f"sign_flag_button.text=[{sign_flag_button.text}]")

                sign_div_xpath = f'{self.windows_xpath2}/android.view.View[6]'
                self.sign_page(sign_div_xpath)

            except NoSuchElementException as msg:
                # logger.warning(f"未找到plus弹窗，忽略")
                pass
            except:
                logger.warning(f"弹窗进行处理异常={traceback.format_exc()}")

        else:
            try:
                logger.debug(f'尝试关掉[继续环游]弹窗')
                draw_div_xpath = f'{self.windows_xpath2}/android.view.View[3]'

                draw_close_div_elm = self.driver.find_element(By.XPATH, draw_div_xpath)
                draw_close_div_elm.click()
            except NoSuchElementException as msg:
                logger.warning(f"忽略")
            except:
                logger.warning(f"尝试关掉[继续环游]弹窗异常={traceback.format_exc()}")

            try:
                logger.debug(f'尝试关掉[立即抽奖]弹窗')
                draw_div_xpath = f'{self.windows_xpath2}/android.view.View[2]/android.view.View[2]'

                draw_close_div_elm = self.driver.find_element(By.XPATH, draw_div_xpath)
                draw_close_div_elm.click()
            except NoSuchElementException as msg:
                logger.warning(f"忽略")
            except:
                logger.warning(f"尝试关掉[立即抽奖]弹窗异常={traceback.format_exc()}")
        return plus_flag

    #  gzh:testerzhang 进入H5页面
    def do(self):

        # 获取入口
        search_result = self.active_page()
        if not search_result:
            logger.warning("找不到入口，退出")
            return

        logger.debug("3.准备切换H5页面")
        wait_time_bar(4)

        # todo: 尚未获取到相应弹窗信息，随缘修复。
        if config.FIRST_WINDOWS_FLAG:
            logger.debug("4.处理第一次进入页面的弹窗")
            plus_flag = self.process_windows()
        else:
            plus_flag = 0

        if config.DO_SIGN_FLAG and plus_flag == 0:
            # 打开每日签到
            self.do_sign()

        if config.DO_TASKS_FLAG:
            # 打开任务列表
            self.do_tasks('做任务，集爆竹')

        # # 点击收取爆竹
        if config.RECEIVE_BOMB_FLAG:
            self.collect_bomb()

        # 开始打卡
        if config.DO_DA_KA_FLAG:
            self.zha()


def main():
    jd = JD()
    jd.do()
    jd.close()
    exit("退出")


if __name__ == '__main__':
    main()
