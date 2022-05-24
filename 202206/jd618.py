#!/usr/bin/python
# coding=utf-8
# 公众号:testerzhang
__author__ = 'testerzhang'

import os
import time
import traceback

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
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

        try:
            self.driver = webdriver.Remote(url, desired_caps)
        except WebDriverException:
            raise Exception("请手机连接到电脑哦！")
        except:
            logger.error(f"异常={traceback.format_exc()}")
            raise Exception("连接手机出了问题，请检查下")

        self.wait = WebDriverWait(self.driver, config.TIME_OUT)

        self.game_over = False
        self.windows_xpath = config.WINDOWS_XPATH
        self.windows_xpath2 = config.WINDOWS_XPATH2

        self.except_html = "./except"

        if not os.path.exists(self.except_html):
            os.makedirs(self.except_html)

        self.finish_task_skip = []

        logger.debug("1.打开京东")
        wait_time_bar(4)

    # 点击中间区域位置
    def click_screen_middle(self):
        screen_size = self.driver.get_window_size()
        logger.debug(f"手机屏幕大小={screen_size}")
        # 屏幕的宽度 width
        x = screen_size['width']
        # 屏幕的高度 height
        y = screen_size['height']
        start_x = x / 2
        start_y = y / 2
        positions = [(start_x, start_y), (start_x, start_y)]
        logger.debug(f"点击屏幕位置={positions}")
        self.driver.tap(positions, 100)

    # 关闭
    def close(self):
        wait_time_bar(5)
        logger.debug("6.关闭app")
        self.driver.quit()

    # 检测是否在当前自动化的app
    def detect_app(self):
        if self.driver.current_package != "com.jingdong.app.mall":
            self.driver.back()

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

        logger.debug(f"2.查找活动入口")

        try:
            # 搜索框
            search_div = '//android.widget.TextView[contains(@content-desc,"搜索")]'
            search_elm = self.wait.until(EC.presence_of_element_located((By.XPATH, search_div)))
            search_elm.click()
            wait_time_bar(2)

            # 换个思路，拿到动态的resource-id
            my_regx = '''{temp}content-desc="搜索框,{temp2}resource-id="{search_id}"{temp3}'''
            regx_result = parse.parse(my_regx, self.driver.page_source)
            # logger.debug(f"regx_result={regx_result}")
            if regx_result is None:
                logger.warning("获取搜索框ID正则匹配失败，退出")
                raise Exception("获取搜索框ID正则匹配失败，退出")

            search_text_id = regx_result['search_id']

            box = self.wait.until(EC.presence_of_element_located((By.ID, search_text_id)))
            box.set_text("分19亿")

            # 点击搜索按钮
            logger.debug(f"点击搜索按钮")
            search_btn_xpath = '//android.widget.TextView[@content-desc="搜索，按钮"]'
            button = self.wait.until(EC.presence_of_element_located((By.XPATH, search_btn_xpath)))
            button.click()
            wait_time_bar(3)

            # 屏幕点击位置进入活动
            self.click_screen_middle()
            # 加载新页面时间
            wait_time_bar(5)
            logger.debug("进入活动入口")
        except NoSuchElementException:
            raise Exception("找不到活动入口")
            filename = f"{self.except_html}/search.html"
            self.write_html(filename)
        except:
            raise Exception("元素定位了，但是找不到活动入口")
            filename = f"{self.except_html}/search-except.html"
            self.write_html(filename)

        return True
    # 关闭任务列表窗口
    def close_windows(self):

        div_xpath = f'//*[@text="累计任务奖励"]/preceding-sibling::android.view.View[1]'
        div_desc = "关闭窗口"
        filename = "关闭窗口.html"
        enter_flag = self.single_div_click(div_xpath, div_desc, filename)
        if enter_flag:
            wait_time_bar(2)

    # task必须是副标题的内容
    def print_task_detail(self, task):
        continue_flag = True
        task_title_xpath = ""
        task_second_title_xpath = ""
        task_title_text = ""
        task_second_title_text = ""
        try:
            logger.debug(f"检查任务:【{task}】是否存在")
            task_second_title_xpath = f'//*[contains(@text, "{task}")]'
            task_second_title = self.driver.find_element(By.XPATH, task_second_title_xpath)
            task_second_title_text = task_second_title.text
            logger.debug(f"任务副标题={task_second_title_text}")
        except:
            logger.warning(f"该任务:【{task}】不执行")
            continue_flag = False
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

        try:
            task_title_xpath = f'{task_second_title_xpath}//preceding-sibling::android.view.View[1]'
            task_title_elm = self.driver.find_element(By.XPATH, task_title_xpath)
            # 获取标题
            task_title_text = task_title_elm.text
            logger.debug(f"任务标题={task_title_text}")
        except NoSuchElementException:
            continue_flag = False
            filename = f"{self.except_html}/获取任务主标题-不存在.html"
            self.write_html(filename)
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text
        except:
            logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
            continue_flag = False
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

        # 判断是否任务跳过
        is_continue = self.continue_task(task_title_text)

        if not is_continue:
            logger.warning(f"满足跳过任务关键字，退出2")
            continue_flag = False
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

        return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

    # task必须是主标题的内容
    def print_task_detail2(self, task):
        continue_flag = True
        task_title_xpath = ""
        task_second_title_xpath = ""
        task_title_text = ""
        task_second_title_text = ""
        try:
            logger.debug(f"检查任务:【{task}】是否存在")
            task_title_xpath = f'//*[contains(@text, "{task}")]'
            task_title = self.driver.find_element(By.XPATH, task_title_xpath)
            task_title_text = task_title.text
            logger.debug(f"任务主标题={task_title_text}")
        except NoSuchElementException:
            pass
        except:
            logger.warning(f"该任务:【{task}】不执行")
            continue_flag = False
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

        try:
            task_second_title_xpath = f'{task_title_xpath}//following-sibling::android.view.View[1]'
            task_second_title_elm = self.driver.find_element(By.XPATH, task_second_title_xpath)
            # 获取标题
            task_second_title_text = task_second_title_elm.text
            logger.debug(f"任务副标题={task_second_title_text}")
        except NoSuchElementException:
            continue_flag = False
            filename = f"{self.except_html}/获取任务副标题-不存在.html"
            self.write_html(filename)
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text
        except:
            logger.warning(f"该任务:【{task}】获取任务副标题异常,不执行")
            continue_flag = False
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

        # 判断是否任务跳过
        is_continue = self.continue_task(task_title_text)

        if not is_continue:
            logger.warning(f"满足跳过任务关键字，退出2")
            continue_flag = False
            return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

        return continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text

    def get_location(self, div_xpath):
        right_x, right_y = 0, 0
        try:
            logger.debug(f"开始获取元素边界")
            div_list = self.driver.find_element(By.XPATH, div_xpath)
            # 右下角x轴
            right_x = div_list.location['x'] + div_list.size['width']
            # 右下角y轴
            right_y = div_list.location['y'] + div_list.size['height']

        except NoSuchElementException:
            filename = f"{self.except_html}/get_location.html"
            self.write_html(filename)
        except:
            logger.warning(f"获取元素边界异常={traceback.format_exc()}")

        logger.debug(f"right_x=[{right_x}],right_y=[{right_y}]")
        return right_x, right_y

    # 种草城
    def grass_task(self, task):
        init_loop = 0
        max_loop = 1
        jump_loop_flag = 0

        while init_loop < max_loop:
            init_loop = init_loop + 1

            if jump_loop_flag == 1:
                logger.debug(f"超过循环次数，退出该类任务。")
                break

            continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail2(
                task)
            if not continue_flag:
                break

            # 开始点击
            result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
            now_times = int(result['now_times'])
            total_times = 3
            logger.debug(f"now_times={now_times},total_times={total_times}")
            if now_times == total_times and total_times > 0:
                continue
            else:
                while now_times < total_times:
                    logger.debug(f"开始【{task}】任务now_times={now_times}点击")

                    # todo:检测页面是否已经完成任务了
                    try:

                        task_button_do_xpath = f'{task_second_title_xpath}/following-sibling::android.view.View[1]'
                        task_button_do_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                        task_button_do_elm.click()

                    except NoSuchElementException:
                        filename = f"{self.except_html}/互动种草城-点击-{now_times}-no-found.html"
                        self.write_html(filename)
                        break
                    except:
                        logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                        break

                    wait_time_bar(3)

                    filename = f"{self.except_html}/互动种草城页面.html"
                    self.write_html(filename)

                    # 检测页面是否含有"当前页点击浏览4个商品领爆竹"文字
                    logger.debug(f"检测页面是否有关键字")
                    source = self.driver.page_source
                    find_flag = source.find("点击【喜欢】")
                    if find_flag == -1:
                        logger.warning(f"没找到【互动种草城】关键字，退出任务")
                        break

                    # 执行4次
                    shop_success = True
                    for i in range(1, 4):
                        try:
                            logger.debug(f"开始第{i}次访问店铺")

                            float_div = f'''//android.view.View[@resource-id="root"]/android.view.View/android.view.View[2]'''
                            right_x, right_y = self.get_location(float_div)
                            like_x = right_x - 240
                            like_y = right_y - 140

                            logger.debug(f"like_x=[{like_x}],like_y=[{like_y}]")

                            self.driver.tap([(like_x, like_y)], duration=100)

                        except NoSuchElementException:
                            shop_success = False
                            filename = f"{self.except_html}/互动种草城-店铺-{i}.html"
                            self.write_html(filename)
                            break
                        except:
                            shop_success = False
                            logger.warning(f"点击店铺异常={traceback.format_exc()}")
                            break

                        wait_time_bar(2)
                        logger.debug("从详情页返回")
                        self.driver.back()
                        wait_time_bar(2)

                    if shop_success:
                        logger.debug("返回任务列表")
                        self.driver.back()

                    now_times = now_times + 1

    #  gzh:testerzhang 做任务列表，还不能做全部，后续再看看。
    def do_task(self, detect=False):
        if detect:
            enter_success = self.detect_enter_task_lists()

            if not enter_success:
                logger.warning(f"没有进入任务列表，退出")
                return

        # 配置文件配置需要执行的任务清单
        task_list = config.TASK_LIST

        for task in task_list:

            if self.game_over:
                break

            while True:

                # 开始做任务
                logger.debug(f"开始真正做任务列表:【{task}】")

                if task in ["去领取"]:
                    try:
                        progress_div = f'//*[@text="累计任务奖励"]/following-sibling::android.view.View[2]/android.view.View'
                        progress_elm_lists = self.driver.find_elements(By.XPATH, progress_div)
                        logger.debug(f"找到[去领取]区域长度={len(progress_elm_lists)}")
                        for i, progress_elm in enumerate(progress_elm_lists, 0):
                            if i == 0:
                                continue
                            logger.debug(f"尝试点击第{i}个[去领取]")
                            progress_elm.click()
                            wait_time_bar(2)

                            # filename = f"{self.except_html}/领取后的弹窗.html"
                            # self.write_html(filename)

                            # todo:新节点未测试
                            div_xpath = '//*[contains(@text, "开心收下开心收下")]'
                            div_desc = "去领取后的开心收下"
                            filename = "去领取后的开心收下.html"
                            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
                            if enter_flag:
                                wait_time_bar(2)
                            else:
                                div_xpath = '//*[contains(@text, "去用券")]'
                                div_desc = "去领取后的去用券"
                                filename = "去领取后的去用券.html"
                                enter_flag = self.single_div_click(div_xpath, div_desc, filename)
                                if enter_flag:
                                    wait_time_bar(2)
                                    self.driver.back()
                                    return
                                else:
                                    wait_time_bar(2)

                    except NoSuchElementException:
                        filename = f"{self.except_html}/去领取元素异常.html"
                        self.write_html(filename)
                    except:
                        logger.warning(f"[去领取]异常={traceback.format_exc()}")
                    else:
                        wait_time_bar(5)
                    break
                elif task in ["关闭"]:
                    self.close_windows()

                    break
                elif task in ["去组队可得", "玩AR游戏"]:

                    continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail(
                        task)
                    if not continue_flag:
                        break

                    try:
                        logger.debug(f"开始【{task}】任务点击")
                        task_button_do_xpath = f'{task_title_xpath}/following-sibling::android.view.View[2]'
                        task_button_do_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                        task_button_do_elm.click()

                        if task in ["玩AR游戏"]:
                            wait_time_bar(4)
                            self.driver.back()
                        else:
                            wait_time_bar(2)

                    except NoSuchElementException:
                        filename = f"{self.except_html}/join_group_or_ar_no.html"
                        self.write_html(filename)
                    except:
                        logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                        break

                    break

                elif task in ["去种草城"]:
                    # todo: 只有一次种草城
                    self.grass_task(task)

                    break
                elif '底部跳转app' == task:
                    try:
                        logger.debug(f"开始点击任务列表底部的横幅")
                        task_button_do_xpath = f'''//android.view.View[@resource-id="taskPanelBanner"]'''
                        task_button_do_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                        task_button_do_elm.click()
                        self.do_other_app()
                    except NoSuchElementException:
                        filename = f"{self.except_html}/底部跳转app-no-found.html"
                        self.write_html(filename)
                    except:
                        logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")

                    logger.warning("做【其他任务】完成，直接退出吧")
                    self.game_over = True

                    ## 不管做啥，都退出
                    break
                elif '累计浏览' == task:
                    init_loop = 0
                    max_loop = 3
                    jump_loop_flag = 0

                    while init_loop < max_loop:
                        init_loop = init_loop + 1

                        if jump_loop_flag == 1:
                            logger.debug(f"超过循环次数，退出该类任务。")
                            break

                        continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail(
                            task)
                        if not continue_flag:
                            break

                        # 开始点击
                        result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
                        now_times = int(result['now_times'])
                        total_times = int(result['total_times'])
                        logger.debug(f"now_times={now_times},total_times={total_times}")
                        if now_times == total_times and total_times > 0:
                            continue
                        else:
                            while now_times < total_times:
                                try:
                                    logger.debug(f"开始【{task}】任务now_times={now_times}点击")
                                    task_button_do_xpath = f'{task_second_title_xpath}/following-sibling::android.view.View[1]'
                                    task_button_do_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                                    task_button_do_elm.click()

                                except NoSuchElementException:
                                    filename = f"{self.except_html}/累计浏览-点击浏览-{now_times}-no-found.html"
                                    self.write_html(filename)
                                    break
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                    break

                                wait_time_bar(3)
                                # 检测页面是否含有"当前页点击浏览4个商品领爆竹"文字
                                logger.debug(f"检测页面是否有关键字")
                                source = self.driver.page_source
                                keyword = config.BROWSE_FOUR_GOODS
                                find_flag = source.find(keyword)
                                if find_flag == -1:
                                    logger.warning(f"没找到【{keyword}】关键字，退出任务")
                                    break

                                # 执行4次
                                browse_success = True
                                for i in range(1, 5):
                                    try:
                                        logger.debug(f"开始第{i}次浏览商品")
                                        goods_views_xpath = f'//android.view.View[@resource-id="root"]/android.view.View[2]/android.view.View[{i}]'
                                        # logger.debug(f"goods_views_xpath={goods_views_xpath}")
                                        goods_views_elm = self.driver.find_element(By.XPATH, goods_views_xpath)
                                        goods_views_elm.click()
                                    except NoSuchElementException:
                                        browse_success = False
                                        filename = f"{self.except_html}/累计浏览-商品-{i}.html"
                                        self.write_html(filename)
                                        break
                                    except:
                                        browse_success = False
                                        logger.warning(f"点击商品异常={traceback.format_exc()}")
                                        break

                                    wait_time_bar(1)
                                    logger.debug("从商品详情页返回")
                                    self.driver.back()
                                    wait_time_bar(2)

                                if browse_success:
                                    logger.debug("返回任务列表")
                                    self.driver.back()

                                now_times = now_times + 1

                    break

                elif '浏览3个品牌墙' == task:
                    init_loop = 0
                    max_loop = 3
                    jump_loop_flag = 0

                    while init_loop < max_loop:
                        init_loop = init_loop + 1

                        if jump_loop_flag == 1:
                            logger.debug(f"超过循环次数，退出该类任务。")
                            break

                        continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail(
                            task)
                        if not continue_flag:
                            break

                        # 开始点击
                        result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
                        now_times = int(result['now_times'])
                        total_times = int(result['total_times'])
                        logger.debug(f"now_times={now_times},total_times={total_times}")
                        if now_times == total_times and total_times > 0:
                            continue
                        else:
                            while now_times < total_times:
                                try:
                                    logger.debug(f"开始【{task}】任务now_times={now_times}点击")
                                    task_button_do_xpath = f'{task_second_title_xpath}/following-sibling::android.view.View[1]'
                                    task_button_do_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                                    task_button_do_elm.click()

                                except NoSuchElementException:
                                    filename = f"{self.except_html}/浏览3个品牌墙-点击浏览-{now_times}-no-found.html"
                                    self.write_html(filename)
                                    break
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                    break

                                wait_time_bar(3)
                                # 检测页面是否含有"当前页点击浏览4个商品领爆竹"文字
                                logger.debug(f"检测页面是否有关键字")
                                source = self.driver.page_source
                                find_flag = source.find("feedBottom")
                                if find_flag == -1:
                                    logger.warning(f"没找到【feedBottom】关键字，退出任务")
                                    break

                                # 执行4次
                                browse_success = True
                                for i in range(1, 4):
                                    try:
                                        logger.debug(f"开始第{i}次浏览品牌墙")
                                        goods_views_xpath = f'//android.view.View[@resource-id="feedBottom"]/android.view.View/android.view.View[2]/android.view.View[{i}]'
                                        # logger.debug(f"goods_views_xpath={goods_views_xpath}")
                                        goods_views_elm = self.driver.find_element(By.XPATH, goods_views_xpath)
                                        goods_views_elm.click()
                                    except NoSuchElementException:
                                        browse_success = False
                                        filename = f"{self.except_html}/浏览3个品牌墙-品牌浏览-{i}.html"
                                        self.write_html(filename)
                                        break
                                    except:
                                        browse_success = False
                                        logger.warning(f"点击浏览品牌墙异常={traceback.format_exc()}")
                                        break

                                    wait_time_bar(1)
                                    logger.debug("从品牌墙详情页返回")
                                    self.driver.back()
                                    wait_time_bar(2)

                                if browse_success:
                                    logger.debug("返回任务列表")
                                    self.driver.back()
                                    # 屏幕点击位置进入活动
                                    self.click_screen_middle()
                                    # 加载新页面时间
                                    wait_time_bar(5)
                                    button_name = "重新进入:做任务，集金币"
                                    enter_success = self.find_task_list_entrance(button_name)
                                    if not enter_success:
                                        logger.error(f"重新进入活动，依然没找到任务列表入口")
                                    else:
                                        wait_time_bar(5)
                                        self.do_task(detect=True)

                                now_times = now_times + 1

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

                        continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail(
                            task)
                        if not continue_flag:
                            break

                        if '浏览并加购' in task_second_title_text:
                            logger.warning(f"浏览并加购任务不做")
                            break
                        elif '成功入会并浏览可得' in task_second_title_text:
                            if config.NOT_OPEN_CARD_FLAG:
                                logger.warning(f"成功入会任务不做")
                                break
                        elif '去财富岛' in task_second_title_text:
                            logger.debug(f"财富岛任务不做")
                            break
                        elif '去小程序' in task_second_title_text:
                            logger.debug(f"去小程序任务不做")
                            break

                        # 开始点击
                        result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
                        now_times = int(result['now_times'])
                        total_times = int(result['total_times'])
                        logger.debug(f"now_times={now_times},total_times={total_times}")
                        if now_times == total_times and total_times > 0:
                            continue
                        else:
                            while now_times < total_times:
                                # 当前节点是index=2，查找节点android.view.View index="3"
                                try:
                                    task_button_do_xpath = f'{task_second_title_xpath}//following-sibling::android.view.View[1]'
                                    task_button_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                    # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                    jump_loop_flag = 1
                                    break

                                # 开始任务点击
                                logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_text}:开始执行")
                                task_button_elm.click()

                                if '直播间' in task_title_text:
                                    # 直播时间更长
                                    wait_time_bar(5 + 20)
                                    logger.debug(f"关闭关注主播弹窗")
                                    self.driver.back()
                                elif '去逛东东超市' in task_title_text:
                                    wait_time_bar(5)
                                    logger.debug(f"多返回一次")
                                    self.driver.back()
                                elif '签到领188元红包' in task_title_text:
                                    # todo:待测试，会打开京喜
                                    wait_time_bar(10)
                                    self.driver.back()
                                    wait_time_bar(2)
                                    self.driver.back()
                                    wait_time_bar(2)
                                    self.driver.back()
                                elif '去京东金榜' in task_title_text:
                                    wait_time_bar(5)
                                elif '去种草城' in task_title_text:
                                    wait_time_bar(2)
                                    self.driver.back()
                                    self.grass_task('去种草城')
                                    jump_loop_flag = 1
                                    break
                                elif '浏览并关注可得' in task_second_title_text:
                                    wait_time_bar(5)
                                elif '去逛领券中心抢神券' in task_title_text:
                                    wait_time_bar(10)
                                    # 需要返回多一次
                                    self.driver.back()
                                elif '浏览可得10000爆竹' == task_second_title_text:
                                    if '去成为' in task_title_text:
                                        jump_loop_flag = 1
                                        self.driver.back()
                                        break
                                    wait_time_bar(2)
                                elif '成功入会并浏览' in task_second_title_text:
                                    wait_time_bar(10)
                                    # 确认授权并加入店铺会员 关键字，就退出循环
                                    page_source = self.driver.page_source

                                    if '确认授权并加入店铺会员' in page_source:
                                        logger.warning(f"发现【确认授权并加入店铺会员】，退出循环")
                                        jump_loop_flag = 1
                                        self.driver.back()
                                        break
                                    else:
                                        logger.debug("没有触犯规则，继续")

                                else:
                                    wait_time_bar(5 + 10)

                                if '去京东金榜' in task_title_text:
                                    logger.warning(f"尝试点击左上角返回按钮，如果无效，需要手工执行")

                                    div_xpath = '//*[@resource-id="com.jd.lib.RankingList.feature:id/q"]'
                                    self.only_click("去京东金榜", div_xpath, times=0)
                                else:
                                    logger.debug(f"返回一下，然后稍微休息")
                                    self.driver.back()

                                wait_time_bar(3)

                                now_times = now_times + 1

                                # 更新任务正标题
                                try:
                                    task_title_xpath = f'{task_second_title_xpath}//preceding-sibling::android.view.View[1]'
                                    task_title_elm = self.driver.find_element(By.XPATH, task_title_xpath)
                                    # 获取标题
                                    task_title_text = task_title_elm.text
                                    logger.debug(f"任务标题={task_title_text}")

                                except:
                                    logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                    continue

                    break
                elif '城城' in task:
                    continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail(
                        task)
                    if not continue_flag:
                        break

                    # 开始点击
                    result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
                    now_times = int(result['now_times'])
                    total_times = int(result['total_times'])
                    logger.debug(f"now_times={now_times},total_times={total_times}")
                    if now_times == total_times and total_times > 0:
                        break
                    else:
                        while now_times < total_times:
                            # 当前节点是index=2，查找节点android.view.View index="3"
                            try:
                                task_button_do_xpath = f'{task_second_title_xpath}//following-sibling::android.view.View[1]'
                                task_button_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                            except:
                                logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                break

                            # 开始任务点击
                            logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_text}:开始执行")
                            task_button_elm.click()

                            wait_time_bar(6)
                            self.process_city()

                            logger.debug(f"返回一下，然后稍微休息")
                            self.driver.back()
                            wait_time_bar(3)

                            now_times = now_times + 1

                            # 更新任务正标题
                            try:
                                task_title_xpath = f'{task_second_title_xpath}//preceding-sibling::android.view.View[1]'
                                task_title_elm = self.driver.find_element(By.XPATH, task_title_xpath)
                                # 获取标题
                                task_title_elm_text = task_title_elm.text
                                logger.debug(f"任务标题={task_title_elm_text}")
                            except:
                                logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                break
                    break

                elif '去参与小程序' in task:
                    continue_flag, task_title_xpath, \
                    task_second_title_xpath, task_title_text, \
                    task_second_title_text = self.print_task_detail(
                        task)
                    if not continue_flag:
                        break

                    # 开始点击
                    result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
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
                                task_button_do_xpath = f'{task_second_title_xpath}/../android.view.View[@index="3"]'
                                task_button_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)

                                if config.DEBUG_HTML:
                                    logger.debug(f'第1次查找:{task_button_elm.get_attribute("bounds")}')
                                    filename = f"{self.except_html}/program_to_do-1.html"
                                    self.write_html(filename)
                            except NoSuchElementException:
                                logger.warning(f"没找到【去完成】按钮")
                                program_flag = 1
                            except:
                                logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行。异常={traceback.format_exc()}")
                                break

                            # todo:修正了上一个定位，可能这个不需要了。
                            if program_flag == 1:
                                try:
                                    task_button_do_xpath = f'{task_second_title_xpath}//following-sibling::android.view.View[2]'
                                    task_button_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                                    if config.DEBUG_HTML:
                                        logger.debug(f'第2次查找:{task_button_elm.get_attribute("bounds")}')
                                        filename = f"{self.except_html}/program_to_do-2.html"
                                        self.write_html(filename)
                                except NoSuchElementException:
                                    logger.warning(f"再次没找到【去完成】按钮")
                                    filename = f"{self.except_html}/program_to_do_not_found.html"
                                    self.write_html(filename)
                                    break
                                except:
                                    logger.warning(f"该任务:【{task}】再次获取任务按钮异常,不执行。异常={traceback.format_exc()}")
                                    break

                            # 开始任务点击
                            logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_text}:开始执行")
                            task_button_elm.click()

                            # todo: 可能会有bug
                            wait_time_bar(3)
                            self.detect_app()

                            wait_time_bar(3)
                            self.detect_app()

                            logger.debug(f"返回一下，然后稍微休息")
                            self.detect_app()
                            wait_time_bar(6)

                            now_times = now_times + 1

                            # 更新任务正标题
                            try:
                                wait_time_bar(2)
                                task_title_xpath = f'{task_second_title_xpath}//preceding-sibling::android.view.View[1]'
                                task_title_elm = self.driver.find_element(By.XPATH, task_title_xpath)
                                # 获取标题
                                task_title_elm_text = task_title_elm.text
                                logger.debug(f"任务标题={task_title_elm_text}")
                            except NoSuchElementException:
                                try:
                                    # 年货特卖
                                    logger.debug(f"查找是否含有【好货特卖】文字")
                                    nian_div_xpath = f'//android.widget.TextView[@text="好货特卖"]'
                                    nian_sign_div_elm = self.driver.find_element(By.XPATH, nian_div_xpath)
                                    if nian_sign_div_elm is not None:
                                        logger.debug(f"从小程序跳转回来，还需要再返回一次")
                                        self.driver.back()

                                except NoSuchElementException:
                                    logger.warning(f"没找到任务标题信息")
                                    filename = f"{self.except_html}/program_jump_back_title.html"
                                    self.write_html(filename)

                            except:
                                logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                break
                    break
                else:
                    logger.warning(f"其他任务不做:【{task}】")
                    break

        return

    #  gzh:testerzhang 做任务列表，只做 浏览 任务。
    def do_jr_task_details(self):
        try:
            logger.debug(f"检测是否进入金融app[任务列表]")
            flag_div = f'//*[@text="累计任务奖励"]'
            self.driver.find_elements(By.XPATH, flag_div)

            if config.DEBUG_HTML:
                filename = f"{self.except_html}/jr_task-temp.html"
                self.write_html(filename)
        except NoSuchElementException:
            raise Exception("没成功进入金融app【任务列表】，退出")
            return
        except:
            logger.warning(f"检测是否进入金融app[任务列表]异常={traceback.format_exc()}")
            return

        # 配置文件配置需要执行的任务清单
        task_list = config.JR_TASK_LIST

        for task in task_list:

            while True:
                # 开始做任务
                logger.debug(f"开始真正做JR任务列表:【{task}】")

                if task in ["去领取"]:
                    try:
                        progress_div = f'//*[@text="累计任务奖励"]/../android.view.View[3]/android.view.View/android.view.View'
                        progress_elm_lists = self.driver.find_elements(By.XPATH, progress_div)
                        logger.debug(f"找到[去领取]区域长度={len(progress_elm_lists)}")
                        for i, progress_elm in enumerate(progress_elm_lists, 0):
                            if i == 0:
                                continue
                            logger.debug(f"尝试点击第{i}个[去领取]")
                            progress_elm.click()
                            wait_time_bar(2)

                            ## todo:新的节点，未测试
                            close_tip_div = f'//android.view.View[contains(@text, "+")]'
                            close_tip_lists = self.driver.find_elements(By.XPATH, close_tip_div)
                            if len(close_tip_lists) > 0:
                                close_tip_elm = close_tip_lists[0]
                                tips = close_tip_elm.text
                                logger.debug(f"tips={tips}")
                                if '金币' in tips:
                                    logger.debug(f"关闭弹窗")
                                    self.close_windows()

                            wait_time_bar(2)

                    except NoSuchElementException:
                        filename = f"{self.except_html}/lingqu.html"
                        self.write_html(filename)
                    except:
                        logger.warning(f"[去领取]异常={traceback.format_exc()}")
                    else:
                        wait_time_bar(5)
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

                        continue_flag, task_title_xpath, task_second_title_xpath, task_title_text, task_second_title_text = self.print_task_detail(
                            task)
                        if not continue_flag:
                            break

                        if '浏览并加购' in task_second_title_text:
                            logger.warning(f"浏览并加购任务不做")
                            break
                        # elif '成功入会并浏览可得' in task_second_title_text:
                        #     logger.warning(f"成功入会任务不做")
                        #     break
                        elif '去财富岛' in task_second_title_text:
                            logger.debug(f"财富岛任务不做")
                            break
                        elif '去小程序' in task_second_title_text:
                            logger.debug(f"去小程序任务不做")
                            break

                        # 开始点击
                        result = parse.parse("{temp}({now_times}/{total_times})", f"{task_title_text}")
                        now_times = int(result['now_times'])
                        total_times = int(result['total_times'])
                        logger.debug(f"now_times={now_times},total_times={total_times}")
                        if now_times == total_times and total_times > 0:
                            continue
                        else:
                            while now_times < total_times:
                                # 当前节点是index=2，查找节点android.view.View index="3"
                                try:
                                    task_button_do_xpath = f'{task_second_title_xpath}//following-sibling::android.view.View[1]'
                                    task_button_elm = self.driver.find_element(By.XPATH, task_button_do_xpath)
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务按钮异常,不执行")
                                    # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                    jump_loop_flag = 1
                                    break

                                # 开始任务点击
                                logger.debug(f"任务副标题={task_second_title_text},任务标题={task_title_text}:开始执行")
                                task_button_elm.click()

                                if '去合成压岁钱' in task_title_text:
                                    logger.debug(f"去合成压岁钱要去财富岛，尝试直接返回")
                                elif '去瓜分3亿红包' in task_title_text:
                                    wait_time_bar(5 + 10)
                                    return_flag = self.detect_enter_task_lists()
                                    if not return_flag:
                                        logger.debug(f"不在任务列表页面，再次尝试返回一下")
                                        self.driver.back()
                                elif '去京东金融app签到' in task_title_text:
                                    wait_time_bar(15)
                                    self.driver.back()
                                elif '浏览你的家庭保障缺口' in task_title_text:
                                    wait_time_bar(15)
                                    self.driver.back()
                                elif '浏览并关注可得' in task_second_title_text:
                                    wait_time_bar(5)
                                else:
                                    wait_time_bar(5 + 10)

                                logger.debug(f"返回一下，然后稍微休息")
                                self.driver.back()

                                wait_time_bar(5)

                                now_times = now_times + 1

                                # 更新任务正标题
                                try:
                                    task_title_xpath = f'{task_second_title_xpath}//preceding-sibling::android.view.View[1]'
                                    task_title_elm = self.driver.find_element(By.XPATH, task_title_xpath)
                                    # 获取标题
                                    task_title_text = task_title_elm.text
                                    logger.debug(f"任务标题={task_title_text}")
                                except NoSuchElementException:
                                    logger.warning(f"该任务:【{task}】获取金融任务标题异常,不执行")
                                    filename = f"{self.except_html}/jr_task_title_no_found.html"
                                    self.write_html(filename)
                                except:
                                    logger.warning(f"该任务:【{task}】获取金融任务标题异常,不执行")
                                    continue

                    break

                else:
                    logger.warning(f"其他任务不做:【{task}】")
                    break

        return

    # 做jr app
    def do_jr_app_task(self):
        if config.DEBUG_HTML:
            filename = f"{self.except_html}/金融app.html"
            self.write_html(filename)

        try:
            logger.debug(f"开始点击金融app【任务列表】按钮")
            button_div_xpath = config.JR_TASK_LISTS_BUTTON_XPATH
            button_div_lists = self.driver.find_elements(By.XPATH, button_div_xpath)
            len_button_div_lists = len(button_div_lists)
            # logger.debug(f"button_div_lists={button_div_lists},len={len_button_div_lists}")

            if len_button_div_lists == 0:
                logger.warning("没有定位到金融app任务列表按钮元素，可能得手动杀掉进程，返回")
                return

            filename = f"{self.except_html}/金融首页.html"
            self.write_html(filename)

            button_div_lists[-1].click()

            if config.DEBUG_HTML:
                filename = f"{self.except_html}/jr_home.html"
                self.write_html(filename)
        except NoSuchElementException:
            logger.warning(f"找不到金融app【任务列表】按钮")
            filename = f"{self.except_html}/jr_home_no_found.html"
            self.write_html(filename)
        except:
            logger.warning(f"【金融app【任务列表】按钮点击异常={traceback.format_exc()}")
            filename = f"{self.except_html}/jr_home_exception.html"
            self.write_html(filename)
        else:
            wait_time_bar(3)
            logger.debug(f"继续做金融的其他任务")
            self.do_jr_task_details()

    # 做wx app,涉及小程序，不做。
    def do_wx_app_task(self):
        pass

    # 做其他任务
    def do_other_app(self):
        wait_time_bar(5)

        now_app = self.driver.current_package
        now_app_activity = self.driver.current_activity
        logger.debug(f"now_app={now_app},now_app_activity={now_app_activity}")

        if now_app == "com.jd.jrapp":
            wait_time_bar(8 + 10)
            logger.debug(f"做京东金融任务")
            self.do_jr_app_task()
        elif now_app == "com.tencent.mm":
            wait_time_bar(1)
            logger.debug(f"做微信任务")
            self.do_wx_app_task()
        else:
            logger.warning("做【其他任务】异常，直接退出吧")

    # 处理"城城"
    def process_city(self):

        if config.CITY_GAME_OVER_FLAG:
            logger.debug(f"城城【活动已结束】，不会有弹窗")
            try:
                logger.debug(f"进入城城主页面，点击【查看我的现金】按钮")
                invite_div = '''//android.view.View[@resource-id="app"]/android.view.View/android.view.View/android.view.View[5]/android.view.View'''
                invite_button_elm = self.driver.find_element(By.XPATH, invite_div)
                invite_button_elm.click()

                wait_time_bar(5)
                self.detect_app()
            except:
                logger.warning(f"点击【邀3人立领现金】按钮异常,不执行")
                return

        else:
            # todo: 还有收下现金弹窗
            invite_windows_flag = 0
            try:
                logger.debug(f"处理城城【邀请活动新朋友，金额更高噢】弹窗")
                city_invite_text_div = f'//android.view.View[@text="邀请活动新朋友，金额更高噢"]'
                self.driver.find_element(By.XPATH, city_invite_text_div)

                close_city_invite_text_div = '''//android.view.View[@resource-id="dialogs"]/android.view.View[2]/android.view.View/android.view.View/android.view.View[1]'''
                close_city_invite_button_elm = self.driver.find_element(By.XPATH, close_city_invite_text_div)
                close_city_invite_button_elm.click()

                invite_windows_flag = 1
            except NoSuchElementException:
                pass
            except:
                logger.warning(f"关闭城城【邀请活动新朋友，金额更高噢】弹窗异常,不执行。{traceback.format_exc()}")
                return

            if invite_windows_flag == 0:
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

                wait_time_bar(5)
                self.detect_app()
            except:
                logger.warning(f"点击【邀3人立领现金】按钮异常,不执行")
                return

            # todo:京口令复制弹窗

    #  gzh:testerzhang 点击生产出来的爆竹/金币
    def collect_reward(self):
        div_xpath = f'''//*[contains(@text, '后满')]'''
        div_desc = "未满先收取金币"
        filename = "未满先收取金币.html"
        enter_flag = self.single_div_click(div_xpath, div_desc, filename)
        if enter_flag:
            logger.debug(f"收取成功")
            filename = f"{self.except_html}/未满先收取金币.html"
            self.write_html(filename)

            wait_time_bar(3)
            return

        div_xpath = f'''//*[contains(@text, '5000 5000 领取金币')]'''
        div_desc = "收取金币"
        filename = "收取金币.html"
        enter_flag = self.single_div_click(div_xpath, div_desc, filename)
        if enter_flag:
            logger.debug(f"收取成功")
            filename = f"{self.except_html}/收取金币后的弹窗.html"
            self.write_html(filename)

            wait_time_bar(3)
            ## todo: 如果已经装满了，点击会弹窗，需要关闭弹窗

        return

    def write_html(self, filename):
        source = self.driver.page_source
        # logger.debug(f"页面source:{source}")
        # file_name = f"doc/{filename}"
        with open(filename, 'w') as f:
            f.write(source)

    # 单个元素点击
    def single_div_click(self, div_xpath, div_desc, filename):
        click_success = False
        try:
            logger.debug(f"开始点击[{div_desc}]按钮")
            # div_xpath = f'//android.view.View[@text="签到领红包签到领红包"]'
            div_lists = self.driver.find_element(By.XPATH, div_xpath)
            div_lists.click()
            click_success = True
        except NoSuchElementException:
            filename = f"{self.except_html}/{filename}"
            self.write_html(filename)
        except:
            logger.warning(f"点击[{div_desc}]按钮点击异常={traceback.format_exc()}")

        return click_success

    # 单个元素点击发现已完成，关闭窗口
    def single_div_click_close(self, div_xpath, div_desc, filename, close_div_xpath):
        click_success = False
        try:
            logger.debug(f"开始查找[{div_desc}]按钮")
            # div_xpath = f'//android.view.View[@text="明天再来明天再来"]'
            div_lists = self.driver.find_element(By.XPATH, div_xpath)
            if div_lists is not None:
                logger.debug(f"发现【{div_desc}】,准备退出弹窗")
                try:
                    logger.debug(f"尝试点击[关闭]按钮")
                    close_div_elm = self.driver.find_element(By.XPATH, close_div_xpath)
                    close_div_elm.click()
                    click_success = True
                except NoSuchElementException:
                    filename = f"{self.except_html}/close_{filename}"
                    self.write_html(filename)
                except:
                    logger.warning(f"点击[关闭]动作异常={traceback.format_exc()}")

        except NoSuchElementException:
            filename = f"{self.except_html}/{filename}"
            self.write_html(filename)
        except:
            logger.warning(f"点击[{div_desc}]按钮点击异常={traceback.format_exc()}")

        return click_success

    #  gzh:testerzhang 点击每日签到
    def do_sign(self):
        div_xpath = '//*[contains(@text, "分红：")]/../preceding-sibling::android.view.View[1]'
        div_desc = "每天签到"
        filename = "sign_enter.html"
        enter_flag = self.single_div_click(div_xpath, div_desc, filename)
        if enter_flag:
            wait_time_bar(2)
            # 开始点击页面的"点我签到"按钮
            self.do_sign_window()

    # 签到页面处理
    def do_sign_window(self):

        if '明天再来明天再来' in self.driver.page_source:
            div_xpath = f'//android.view.View[@text="明天再来明天再来"]'
            div_desc = "明天再来明天再来"
            filename = "sign_home_text.html"
            close_div_xpath = f'//android.view.View[@text="每天签到领大额红包"]/preceding-sibling::android.view.View[1]     '
            enter_flag = self.single_div_click_close(div_xpath, div_desc, filename, close_div_xpath)
            if enter_flag:
                logger.debug(f"点击[{div_desc}]成功")
                return
        else:
            div_xpath = f'//android.view.View[@text="点我签到点我签到"]'
            div_desc = "点我签到"
            filename = "sign_home_text.html"
            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
            if enter_flag:
                logger.debug(f"点击[{div_desc}]成功")
                filename = f"{self.except_html}/签到后弹窗页面.html"
                self.write_html(filename)

                wait_time_bar(3)

                div_xpath = '//*[contains(@text, "开心收下开心收下")]'
                div_desc = "签到后开心收下"
                filename = "签到后开心收下.html"
                enter_flag = self.single_div_click(div_xpath, div_desc, filename)
                if enter_flag:
                    logger.debug(f"签到后开心收下成功")
                    wait_time_bar(2)
                    if '明天再来明天再来' in self.driver.page_source:
                        div_xpath = f'//android.view.View[@text="明天再来明天再来"]'
                        div_desc = "明天再来明天再来"
                        filename = "sign_home_text.html"
                        close_div_xpath = f'//android.view.View[@text="每天签到领大额红包"]/preceding-sibling::android.view.View[1]     '
                        enter_flag = self.single_div_click_close(div_xpath, div_desc, filename, close_div_xpath)
                        if enter_flag:
                            logger.debug(f"点击[{div_desc}]成功")
                            return

        return

    # 检测是否进入任务列表
    def detect_enter_task_lists(self):
        enter_success = False
        try:
            logger.debug(f"检测是否进入[任务列表]")
            flag_div = f'//*[@text="累计任务奖励"]'
            self.driver.find_element(By.XPATH, flag_div)
            enter_success = True
            if config.DEBUG_HTML:
                filename = f"{self.except_html}/检测是否进入任务列表debug.html"
                self.write_html(filename)
        except NoSuchElementException:
            logger.warning("没成功进入【任务列表】，有可能是有两个手导致图层不对，退出")
            filename = f"{self.except_html}/没成功接入任务列表.html"
            self.write_html(filename)
        except:
            logger.error(f"检测是否进入[任务列表]异常={traceback.format_exc()}")

        return enter_success

    # 查找任务列表入口
    def find_task_list_entrance(self, button_name):
        div_xpath = '//*[contains(@text, "分红")]/../following-sibling::android.view.View[5]/android.view.View'
        div_desc = "做任务得金币"
        filename = "点击做任务得金币按钮.html"
        enter_flag = self.single_div_click(div_xpath, div_desc, filename)
        return enter_flag

    #  gzh:testerzhang 点击任务列表按钮，然后进入具体的任务列表
    def do_tasks(self, button_name):
        enter_success = self.find_task_list_entrance(button_name)
        if not enter_success:
            logger.error(f"没找到任务列表入口")
        else:
            wait_time_bar(5)

            enter_success = self.detect_enter_task_lists()

            if enter_success:
                # 最新任务列表签到
                self.do_task()
            else:
                # todo:先关闭弹窗
                wait_time_bar(3)
                logger.warning(f"未处理弹窗")

        return

    # 只负责点击，后续没其他动作
    def only_click(self, text, div_xpath, times=0):
        error_flag = True
        try:
            logger.debug(f"尝试点击[{text}]弹窗")
            # 弹窗
            # div_xpath = '//android.view.View[text="开心收下开心收下"]'
            div_elm = self.driver.find_element(By.XPATH, div_xpath)
            div_elm_click_enable = div_elm.get_attribute('clickable')
            # logger.debug(f"元素是否可以点击={div_elm_click_enable}")
            # logger.debug(f"元素的坐标={div_elm.get_attribute('bounds')}")
            if text == "去京东金榜":
                logger.debug(f"尝试返回")
                self.driver.back()
                logger.debug(f"再次尝试返回")
                self.driver.back()
                logger.debug(f"尝试点击之后...")
            else:
                if div_elm_click_enable:
                    logger.debug(f"元素状态是可以点击")

                # logger.debug(f"元素的坐标={div_elm.get_attribute('bounds')}")
                div_elm.click()
            error_flag = False

            if config.DEBUG_HTML and text == "去京东金榜":
                filename = f"{self.except_html}/public_click-{text}.html"
                self.write_html(filename)
        except NoSuchElementException:
            if times == 0:
                filename = f"{self.except_html}/public_click-{text}.html"
            else:
                filename = f"{self.except_html}/public_click-{text}-{times}.html"
            self.write_html(filename)
        except:
            logger.warning(f"点击[{text}]按钮点击异常={traceback.format_exc()}")

        return error_flag

    # 寻找弹窗关闭窗口
    def search_close(self, text, div_xpath, times=0):
        error_flag = True
        try:
            logger.debug(f"尝试点击[{text}]弹窗关闭按钮")
            # 弹窗
            div_elm = self.driver.find_element(By.XPATH, div_xpath)
            logger.debug(f"元素是否可以点击={div_elm.get_attribute('clickable')}")
            logger.debug(f"元素的坐标={div_elm.get_attribute('bounds')}")
            div_elm.click()
            error_flag = False

        except NoSuchElementException:
            if times == 0:
                filename = f"{self.except_html}/public_click-{text}.html"
            else:
                filename = f"{self.except_html}/public_click-{text}-{times}.html"
            self.write_html(filename)
            if text == "开心收下x按钮" and config.DEBUG_HTML:
                logger.debug(f"self.driver.page_source={self.driver.page_source}")
        except:
            logger.warning(f"点击[{text}]按钮点击异常={traceback.format_exc()}")

        return error_flag

    #  gzh:testerzhang 首页处理点爆竹/抽奖
    def da_ka(self):
        # 加多一层最大次数，防止循环。
        max_times = config.DA_KA_LOOP

        # 检测当前app
        self.detect_app()

        times = 1
        logger.debug(f"开始执行，最大执行次数={max_times}次")

        while True:
            logger.debug(f"开始执行第{times}次")
            if times > max_times:
                break
            wait_time_bar(2)

            div_xpath = '//*[contains(@text, "还差")]'
            div_desc = "抽奖"
            filename = "抽奖.html"
            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
            if enter_flag:
                wait_time_bar(8)
                # todo: 只处理了两种弹窗，其他弹窗，后续再搞。

                if config.DEBUG_HTML:
                    filename = f"{self.except_html}/抽奖后其他弹窗-{times}.html"
                    self.write_html(filename)

                div_xpath = '//*[contains(@text, "立即完成立即完成")]'
                div_desc = "抽奖后立即完成"
                filename = "抽奖后立即完成.html"
                enter_flag = self.single_div_click(div_xpath, div_desc, filename)
                if enter_flag:
                    wait_time_bar(15)
                    self.driver.back()
                else:
                    div_xpath = '//*[contains(@text, "开心收下开心收下")]'
                    div_desc = "抽奖后开心收下"
                    filename = "抽奖后开心收下.html"
                    enter_flag = self.single_div_click(div_xpath, div_desc, filename)
                    if enter_flag:
                        wait_time_bar(2)

                close_flag = 0

                if close_flag == 0:
                    # 不够的时候，弹出任务列表
                    try:
                        logger.debug("尝试关闭[任务列表]")
                        task_list_xpath = '//*[contains(@text, "累计任务奖励")]'
                        self.driver.find_element(By.XPATH, task_list_xpath)
                        # 点击右上角关闭按钮
                        self.close_windows()
                        # 退出
                        logger.warning("不够了，不再执行循环。")
                        break
                    except NoSuchElementException:
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
        # todo:判断弹框
        try:
            windows_div = '//android.widget.ImageView[content-desc="返回"]'
            windows_button = self.driver.find_element(By.XPATH, windows_div)
            logger.debug(f"windows_button.text=[{windows_button.text}]")
            windows_button.click()
        except NoSuchElementException:
            logger.warning(f"忽略")
        except:
            logger.warning(f"弹窗进行处理异常={traceback.format_exc()}")

        # plus会员弹窗,未测试。
        plus_flag = 0
        # try:
        #     logger.debug(f"看是否有[Plus弹窗]")
        #     # plus_div = '//android.view.View[text="送您"]'
        #     plus_flag_div = '//android.view.View[text="Plus专享"]'
        #     plus_flag_button = self.driver.find_element(By.XPATH, plus_flag_div)
        #     logger.debug(f"plus_flag_button.text=[{plus_flag_button.text}]")
        #
        #     plus_div = '//android.view.View[text="Plus专享"]/../../following-sibling::android.view.View[1]/android.view.View'
        #     plus_button = self.driver.find_element(By.XPATH, plus_div)
        #     logger.debug(f"plus_button.text=[{plus_button.text}]")
        #
        #     plus_button.click()
        #     plus_flag = 1
        # except NoSuchElementException:
        #     # logger.warning(f"未找到plus弹窗，忽略")
        #     pass
        # except:
        #     logger.warning(f"弹窗进行处理异常={traceback.format_exc()}")

        # 点击plus按钮之后，进入签到弹窗，未测试。
        if plus_flag == 1:
            try:
                sign_flag_div = '//android.view.View[text="每天来签到，得最高111.1元红包"]'
                sign_flag_button = self.driver.find_element(By.XPATH, sign_flag_div)
                logger.debug(f"sign_flag_button.text=[{sign_flag_button.text}]")

                sign_div_xpath = f'{self.windows_xpath2}/android.view.View[6]'
                self.sign_page(sign_div_xpath)

            except NoSuchElementException:
                # logger.warning(f"未找到plus弹窗，忽略")
                pass
            except:
                logger.warning(f"弹窗进行处理异常={traceback.format_exc()}")

        else:
            logger.debug(f'尝试关掉[继续环游]弹窗')
            div_xpath = '//*[contains(@text, "继续环游继续环游")]/../preceding-sibling::android.view.View[3]'
            div_desc = "首页开启继续环游"
            filename = "首页开启继续环游.html"
            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
            if enter_flag:
                wait_time_bar(2)
                return plus_flag

            logger.debug(f'尝试关掉[开心收下]弹窗')
            div_xpath = '//*[contains(@text, "开心收下开心收下")]/../preceding-sibling::android.view.View[3]'
            div_desc = "首页开启开心收下"
            filename = "首页开启开心收下.html"
            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
            if enter_flag:
                wait_time_bar(2)
                return plus_flag

            logger.debug(f'尝试关掉[开启今日抽奖]弹窗')
            div_xpath = '//*[contains(@text, "开启今日抽奖开启今日抽奖")]/../preceding-sibling::android.view.View[3]'
            div_desc = "首页开启今日抽奖"
            filename = "首页开启今日抽奖.html"
            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
            if enter_flag:
                wait_time_bar(2)
                return plus_flag

            logger.debug(f'尝试关掉[立即抽奖]弹窗')
            div_xpath = '//*[contains(@text, "立即抽奖立即抽奖")]/../preceding-sibling::android.view.View[3]'
            div_desc = "立即抽奖立即抽奖"
            filename = "立即抽奖立即抽奖.html"
            enter_flag = self.single_div_click(div_xpath, div_desc, filename)
            if enter_flag:
                wait_time_bar(2)
                return plus_flag

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
            self.do_tasks('做任务，集金币')

        # # 点击收取爆竹/金币
        if config.RECEIVE_REWARD_FLAG and not self.game_over:
            self.collect_reward()

        # 开始打卡/抽奖
        if config.DO_DA_KA_FLAG and not self.game_over:
            self.da_ka()


def main():
    jd = JD()
    jd.do()
    jd.close()
    exit("退出")


if __name__ == '__main__':
    main()
