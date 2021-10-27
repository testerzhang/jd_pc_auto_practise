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

logger.add(config.MIAO_LOG)


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

                # 输入搜索文本，这里目前只能是用ID，xpath解析异常
                # search_text_id = 'com.jd.lib.search.feature:id/a3v'
                search_text_id = 'com.jd.lib.search.feature:id/a47'
                box = self.wait.until(EC.presence_of_element_located((By.ID, search_text_id)))

                # search_text_xpath = '//android.view.View[contains(@content-desc, "搜索框")]'
                # search_text_xpath = '//android.widget.ImageView[@content-desc="拍照购"]/../android.view.View'
                # box = self.wait.until(EC.presence_of_element_located((By.XPATH, search_text_xpath)))

                box.set_text("热爱环游记")

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
            count_elm = self.driver.find_element_by_xpath(count_div)
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

                        progress_div = f'//*[@text="累计任务奖励"]/../android.view.View[3]/android.view.View'
                        progress_elm_lists = self.driver.find_elements_by_xpath(progress_div)
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
                            close_tip_lists = self.driver.find_elements_by_xpath(close_tip_div)
                            if len(close_tip_lists) > 0:
                                close_tip_elm = close_tip_lists[0]
                                tips = close_tip_elm.text
                                logger.debug(f"tips={tips}")
                                if '汪汪币' in tips:
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
                            task_second_title = self.driver.find_element_by_xpath(task_second_title_div)
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
                            task_title_elm = self.driver.find_element_by_xpath(task_title_div)
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
                                    task_button_elm = self.driver.find_element_by_xpath(task_title_div)
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
                                    task_title_elm = self.driver.find_element_by_xpath(task_title_div)
                                    # 获取标题
                                    task_title_elm_text = task_title_elm.text
                                    logger.debug(f"任务标题={task_title_elm_text}")
                                except:
                                    logger.warning(f"该任务:【{task}】获取任务标题异常,不执行")
                                    # logger.debug(f"【{task}】点击异常={traceback.format_exc()}")
                                    continue

                    break

                else:
                    logger.warning(f"其他任务不做:【{task}】")
                    break

        return

    #  gzh:testerzhang 点击生产出来的汪汪币
    def click_coin(self):
        # source = self.driver.page_source
        # logger.debug(f"领取币source:{source}")

        try:
            logger.debug("开始点击【领取汪汪币】图标")
            feed_div = '//*[contains(@text, "领取汪汪币")]'
            feed_button = self.driver.find_element_by_xpath(feed_div)
            logger.debug(f"feed_button.text=[{feed_button.text}]")
            feed_button.click()
        except NoSuchElementException:
            pass
        except:
            logger.warning(f"【领取汪汪币】点击异常={traceback.format_exc()}")

        try:
            logger.debug("开始点击【存满】图标")
            feed_div = '//*[contains(@text, "后存满")]'
            feed_button = self.driver.find_element_by_xpath(feed_div)
            logger.debug(f"feed_button.text=[{feed_button.text}]")
            feed_button.click()
        except NoSuchElementException:
            pass
        except:
            logger.warning(f"【领取汪汪币】点击异常={traceback.format_exc()}")

        return

    # 签到页面处理
    def sign_page(self, sign_div_xpath):
        try:
            logger.debug(f"开始点击[点我签到]按钮")
            # 可能这个位置后续会变
            # sign_div_xpath = '//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[7]/android.view.View[2]/android.view.View/android.view.View[6]'

            sign_div_lists = self.driver.find_element_by_xpath(sign_div_xpath)
            sign_div_lists.click()
        except:
            logger.warning(f"点击[点我签到]按钮点击异常={traceback.format_exc()}")
        else:
            # todo: 签到成功后，还要处理一个弹窗，还没测试。

            wait_time_bar(3)

            try:
                logger.debug(f"开始点击[开心收下]按钮的关闭按钮")
                # 提醒我明天签到领红包
                sign_close_flag_xpath = '//android.view.View[text="提醒我明天签到领红包"]'
                self.driver.find_element_by_xpath(sign_close_flag_xpath)

                sign_close_div_xpath = '//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[7]/android.view.View[2]/android.view.View/android.view.View[2]'

                sign_close_div_lists = self.driver.find_element_by_xpath(sign_close_div_xpath)
                if len(sign_div_lists) > 0:
                    sign_close_div_lists[0].click()
            except:
                logger.warning(f"点击[开心收下]按钮点击异常={traceback.format_exc()}")
            else:
                wait_time_bar(2)

    #  gzh:testerzhang 点击每日签到
    def do_sign(self):

        try:
            logger.debug(f"开始点击[每日签到]按钮")
            sign_div_xpath = '//android.view.View[@resource-id="homeBtnTeam"]/preceding-sibling::android.view.View[1]'
            sign_div_lists = self.driver.find_element_by_xpath(sign_div_xpath)
            sign_div_lists.click()
        except:
            logger.warning(f"点击[每日签到]按钮点击异常={traceback.format_exc()}")
        else:
            wait_time_bar(2)
            # 开始点击页面的"点我签到"按钮
            sign_div_xpath = '//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[7]/android.view.View[2]/android.view.View/android.view.View[6]'
            self.sign_page(sign_div_xpath)

    #  gzh:testerzhang 点击任务列表按钮，然后进入具体的任务列表
    def do_coins(self, button_name):
        # source = self.driver.page_source
        # logger.debug(f"do_coins任务source:{source}")

        try:
            logger.debug(f"开始点击[{button_name}]按钮")
            # todo: 这个index可能需要手动修改正确位置。
            # button_div_xpath = '//android.view.View[contains(@index,9)]'
            button_div_xpath = '//android.view.View[contains(@index,10)]'
            button_div_lists = self.driver.find_elements_by_xpath(button_div_xpath)
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

    #  gzh:testerzhang 首页处理打卡领红包
    def feed_dog(self):
        # 加多一层最大喂养次数，防止循环。
        max_times = 10

        logger.debug("欢迎进入【打卡领红包】")

        times = 1
        logger.debug(f"开始执行，最大执行次数={max_times}次")

        while True:
            logger.debug(f"开始执行第{times}次")
            if times > max_times:
                break

            try:
                wait_time_bar(2)
                logger.debug("开始点击【打卡领红包】入口")
                # 喂猫领红包,每次消耗98000汪汪币
                feed_div = '//*[contains(@text, "打卡领红包打卡领红包")]'
                self.driver.find_element_by_xpath(feed_div).click()
            except NoSuchElementException:
                logger.warning(f"无法找到【打卡领红包】这个元素")
                # 可能是因为弹窗了，暂时没修复。
                # logger.debug(f"返回一下")
                break
            except:
                logger.warning(f"【打卡领红包】点击异常={traceback.format_exc()}")
                break
            else:
                wait_time_bar(5)
                # source = self.driver.page_source
                # logger.debug(f"打卡后source:{source}")

                try:
                    logger.debug(f"尝试关闭打卡之后的弹窗")
                    # 可能这个位置后续会变
                    close_div_xpath = '//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[6]/android.view.View[2]/android.view.View/android.view.View[2]'

                    close_div_elm = self.driver.find_element_by_xpath(close_div_xpath)
                    close_div_elm.click()
                except NoSuchElementException as msg:
                    pass
                except:
                    logger.warning(f"尝试关闭打卡之后的弹窗动作异常={traceback.format_exc()}")

                # 弹出【去完成】弹窗
                try:
                    logger.debug("尝试[开心收下]确认之后的弹窗")
                    to_finish_xpath = '//*[contains(@text, "完成以下任务获得大量汪汪币")]'
                    to_finish_close_xpath = f'{to_finish_xpath}//preceding-sibling::android.view.View[1]'
                    to_finish_close_elm = self.driver.find_element_by_xpath(to_finish_close_xpath)
                    # 点击右上角关闭按钮
                    to_finish_close_elm.click()
                except NoSuchElementException as msg:
                    pass
                except:
                    logger.warning(f"尝试[开心收下]确认之后的弹窗异常={traceback.format_exc()}")

                # 汪汪币不够的时候，弹出任务列表
                try:
                    logger.debug("尝试关闭[任务列表]")
                    task_list_xpath = '//*[contains(@text, "累计任务奖励")]'
                    task_list_elm = self.driver.find_element_by_xpath(task_list_xpath)
                    # 点击右上角关闭按钮
                    self.close_windows()
                    # 退出
                    return
                except NoSuchElementException as msg:
                    pass
                except:
                    logger.warning(f"尝试关闭[任务列表]异常={traceback.format_exc()}")

            times = times + 1

        return

    # 第一次进入页面，弹窗处理
    def process_windows(self):
        # todo:判断弹框:继续抽奖

        try:
            windows_div = '//android.widget.ImageView[content-desc="返回"]'
            windows_button = self.driver.find_element_by_xpath(windows_div)
            logger.debug(f"windows_button.text=[{windows_button.text}]")
            windows_button.click()
        except NoSuchElementException as msg:
            logger.warning(f"忽略")
        except:
            logger.warning(f"弹窗进行处,异常={traceback.format_exc()}")

        # plus会员弹窗,未测试。
        plus_flag = 0
        try:
            # plus_div = '//android.view.View[text="送您"]'
            plus_flag_div = '//android.view.View[text="Plus专享"]'
            plus_flag_button = self.driver.find_element_by_xpath(plus_flag_div)
            logger.debug(f"plus_flag_button.text=[{plus_flag_button.text}]")

            plus_div = '//android.view.View[text="Plus专享"]/../../following-sibling::android.view.View[1]/android.view.View'
            plus_button = self.driver.find_element_by_xpath(plus_div)
            logger.debug(f"plus_button.text=[{plus_button.text}]")

            plus_button.click()
            plus_flag = 1
        except NoSuchElementException as msg:
            # logger.warning(f"未找到plus弹窗，忽略")
            pass
        except:
            logger.warning(f"弹窗进行处,异常={traceback.format_exc()}")

        # 点击plus按钮之后，进入签到弹窗，未测试。
        if plus_flag == 1:
            try:
                sign_flag_div = '//android.view.View[text="每天来签到，得最高111.1元红包"]'
                sign_flag_button = self.driver.find_element_by_xpath(sign_flag_div)
                logger.debug(f"sign_flag_button.text=[{sign_flag_button.text}]")

                sign_div_xpath = '//android.view.View[@resource-id="homeBtnTeam"]/following-sibling::android.view.View[7]/android.view.View[2]/android.view.View/android.view.View[6]'
                self.sign_page(sign_div_xpath)

            except NoSuchElementException as msg:
                # logger.warning(f"未找到plus弹窗，忽略")
                pass
            except:
                logger.warning(f"弹窗进行处,异常={traceback.format_exc()}")

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

        logger.debug("4.处理第一次进入页面的弹窗")
        plus_flag = self.process_windows()

        if config.DO_SIGN_FLAG and plus_flag == 0:
            # 打开每日签到
            self.do_sign()

        if config.DO_COINS_FLAG:
            # 打开任务列表
            self.do_coins('做任务，赚汪汪币')

        # 点击收取生产的汪汪币
        if config.RECEIVE_COINS_FLAG:
            self.click_coin()

        # 开始打卡
        if config.DO_DA_KA_FLAG:
            self.feed_dog()


def main():
    jd = JD()
    jd.do()
    jd.close()
    exit("退出")


if __name__ == '__main__':
    main()
