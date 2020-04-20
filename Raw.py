import time
import mysql.connector
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import re
browser=webdriver.Chrome()
wait=WebDriverWait(browser,10)
global count#计数全局变量
count=1
def search():#爬虫搜索函数
   gameid=1
   k = 1#页码数初始为1
   while k<824:#共824页
    url = "https://store.steampowered.com/search/?filter=globaltopsellers&page=" + str(k) + "&os=win"#根据排行榜的页面规律来翻页
    browser.get(url)#get请求页面
    k=k+1#翻页加一
    i = 1#初始从第一页第一个开始爬
    STR="#search_resultsRows > a:nth-child("
    while(i<25):#每页25个游戏
       gameid=gameid+1#梅爬一个就向下加一
       try:
          element = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, STR+str(i)+")"))
          )#得到每个游戏的链接
          element.click()#进入游戏商店页面
          html=browser.page_source#获取当前页面的源代码
          soup = BeautifulSoup(html, "html.parser")#格式化
          if "app" in str(browser.current_url):#只爬榜单中的游戏而不爬游戏捆绑包
             getStatics(soup)#从页面中分离数据
          time.sleep(0)
          browser.back()#返回榜单
          i=i+1#下一个游戏
       except TimeoutException:
          search()#如果超时则重新请求

def getStatics(soup):
    global count
    conn = mysql.connector.connect(host='localhost', port='3306', user='root', password='123456',
                                   database='gameinfo')
    cursor = conn.cursor()#数据库初始化
    Name = soup.findAll(name="div", attrs={"class": "apphub_AppName"})
    Name = str(Name)[29:-7]  # 获取名称
    if len(Name)>0:#判断当前页面的游戏信息是否存在
        print('游戏名称：', Name)
        tag=""
        comment="无评价信息"
        percents=0.0
        developers="无开发商信息"#默认值
        for m in soup.find_all(class_="app_tag"):  # 获取游戏标签
            tag=tag+'|'+m.string
            print(m.string)
        for m in soup.find_all(class_="game_review_summary positive"):  # 获取评价
            print(m.string)
            comment=m.string
            break
        if len(soup.select('#game_highlights > div.rightcol > div > div.glance_ctn_responsive_left > div > div.user_reviews_summary_row > div.summary.column > span.nonresponsive_hidden.responsive_reviewdesc')) > 0:
            print(soup.select('#game_highlights > div.rightcol > div > div.glance_ctn_responsive_left > div > div.user_reviews_summary_row > div.summary.column > span.nonresponsive_hidden.responsive_reviewdesc')[0].text)  # 获取游戏厂商
            percents = soup.select('#game_highlights > div.rightcol > div > div.glance_ctn_responsive_left > div > div.user_reviews_summary_row > div.summary.column > span.nonresponsive_hidden.responsive_reviewdesc')[0].text
            temp=str(percents)
            percents="0."+re.sub("\D", "", temp)[-2:]
        if len(soup.select('#developers_list > a'))>0:#判断厂商信息是否存在
             tag=tag.replace("\t", "")
             tag=tag.replace("\n", "")
             tag = tag.replace("+", "")
             print(soup.select('#developers_list > a')[0].text)# 获取游戏厂商
             developers=soup.select('#developers_list > a')[0].text
             sql = "insert into game values (%s,%s,%s,%s,%s,%s)"
             if len(tag)<=0:
                tag="无标签"
             val = (count,str(Name), str(tag), str(comment),float(percents),str(developers))#插入数据库
             cursor.execute(sql,val)#执行语句
             count=count+1
             conn.commit()
             cursor.close()
             conn.close()#关闭数据库


def main():#主函数

    search()

if __name__=='__main__':
    main()#主函数运行
