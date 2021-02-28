# coding=utf8
from bs4 import BeautifulSoup
import lxml
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import socks
import socket


def Retrieve_from_nga(session):

    read = session.get('https://bbs.nga.cn/thread.php?fid=498', headers=send_headers)
    read.encoding = ('gbk')
    #print(read.text)

    html_doc = read.text

    #print(read.cookies)
    # print(read.encoding)
    # print(read.apparent_encoding)

    new_cookie = read.cookies.get_dict()
    old_cookie = session.cookies.get_dict()

    for key in new_cookie.keys():
        if key in old_cookie.keys():
            session.cookies.set(key, None)

    try:
        if 'guestJs' in old_cookie.keys():
            session.cookies.set('guestJs', old_cookie['lastvisit'])
    except:
        print('网站cookie格式发生变化')

    #print(session.cookies)
    session.cookies.update(read.cookies)
    #print(session.cookies)

    cookie_dict = session.cookies.get_dict()
    keys = cookie_dict.keys()

#保存访问后已经更新的cookie以备随时重新启动程序时载入
    with open('cookie.txt','w',encoding = 'gbk') as fp:
        for key in keys:
            fp.write(key + '=' + cookie_dict[key])
            if key != list(keys)[-1]:
                fp.write('; ')


    return html_doc

def analyse_content(html_doc, history):


    #with open('nga.txt','r',encoding = 'gbk') as f:
        #html_doc = f.read()
        #print(html_doc)

    soup = BeautifulSoup(html_doc, 'lxml')
    find = soup.find_all('td', class_ = 'c2')

    #print(find)



##    key_1  = '不按格式会被删除'
##    key_2  = '电脑硬件'
##    key_3  = '电脑整机'
##    key_4  = '福利'
##    key_5  = '垃圾'
##    key_6  = '打包'
##    key_7  = '电脑配件'
##    key_8  = '送'
    
    #those are the key words to be ignored
    key_9  = '收'
    key_10 = '求购'
    key_11 = '出'

#those are the key word to be included, you may add your own
    key = []
    key.append('电脑硬件')
    key.append('电脑整机')
    key.append('福利')
    key.append('垃圾')
    key.append('打包')
    key.append('电脑配件')
    key.append('送')
    key.append('手机')
    #key.append('小米')
    #key.append('华为')
    key.append('华硕')
    key.append('微星')
    key.append('技嘉')
    key.append('b75')
    key.append('B75')
    key.append('破烂')
    #key.append('iphone')
    #key.append('Iphone')
    key.append('B85')
    key.append('b85')
    key.append('铭瑄')
    key.append('丐帮')
    #key.append('mate')
    key.append('电源')
    key.append('主板')
    key.append('古董')
    key.append('硬盘')
    key.append('显卡')
    key.append('亮机')
    key.append('cpu')
    key.append('闲置')

  
    boolean = []

    find_kept = []

    for each in find:

        flag = 0
        for string in each.strings: # an alternative is to use each.stripped_strings, which will remove all the blankspace, '\n', and '\t'
            #print(string)
    # the reason to use flag and three if, is that there are at least 4 strings in each iteration, '\n' is considered a string. An alternative is stated above.
            # if key_1 not in string:
            #     #flag = 0
            #     #continue

            #     if all([key_2 not in string, key_3 not in string, key_4 not in string, key_5 not in string, key_6 not in string,key_7 not in string, key_8 not in string]):
            #         continue

            #     if any([key_2 in string, key_3 in string, key_4 in string, key_5 in string, key_6 in string, key_7 in string, key_8 in string]):
            #         flag = 1
                    
            #         if key_9 in string or key_10 in string and key_11 not in string:
            #             flag = 0     

            boolean.clear()

            for name in key:
                boolean.append(name not in string)
            if all(boolean):
                continue

            for name in key:
                boolean.append(name in string)
            if any(boolean):
                flag = 1

                if key_9 in string or key_10 in string and key_11 not in string:
                    flag = 0   


        if flag:
            find_kept.append(each)

    key = ''
    value = ''

    item_to_send = {}
    process_time = time.localtime(time.time())

    #history 字典由如下元素组成. key是帖子地址, value是一个list，有4个元素：帖子标题，发现年、月、日

    for each in find_kept:
        key = each.contents[1]['href']                 #the second child node is what we want: each.contents[1]
        if key not in history.keys():
            value = each.contents[1].string + '          '      #标题
            value += str(process_time[0]) + '          '  #加入历史记录时间 year
            value += str(process_time[1]) + '          '  # month
            value += str(process_time[2]) # day
            history[key] = value

            web_url = 'bbs.nga.cn' + key
            subject = value
            item_to_send[web_url] = subject

    keys = history.keys()

    with open('history.txt','w',encoding = 'gbk') as fp:
        for key in keys:
            fp.write(key + ':' + history[key])
            if key != list(keys)[-1]:
                fp.write('\n')

    return item_to_send


    #print(history)


def send_email(content, subject,account,password,receiver):

    #socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5,'127.0.0.1',1080)
    #socket.socket = socks.socksocket
    
    mailhost = 'smtp.qq.com'
    mail = smtplib.SMTP_SSL(mailhost,465)
    #mail.connect(mailhost,25)
    mail.login(account,password)
    #content = 'history'
    message = MIMEText(content,'plain','utf-8')
    #subject = '二手硬件'
    message['Subject'] = Header(subject,'utf-8')

    try:
        mail.sendmail(account,receiver,message.as_string())
        print('mail sent success')
    except:
        print('mail sent failure')
    mail.quit()

if __name__ == "__main__":


    # history is to store all the information downloaded, for the purpose of storing and comparing to see if the newly downloaded ones are exsited already

    with open('history.txt', 'r', encoding = 'gbk') as fp:
        history = {}
        for line in fp.read().split('\n'):
            name, value = line.strip().split(':', 1)
            history[name] = value

    #history = {}

    #set your own email account        
    account = 
    password = 
    receiver = 



    send_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Host": "bbs.nga.cn",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive"
    }
    session = requests.Session()

    with open('cookie.txt', 'r', encoding = 'gbk') as fp:
        nga_cookie = {}
        for line in fp.read().split(';'):
            name, value = line.strip().split('=', 1)
            nga_cookie[name] = value

    nga_cookie = requests.utils.cookiejar_from_dict(nga_cookie)

    session.cookies = nga_cookie

    iter = 1

    while True:

        html_doc = Retrieve_from_nga(session)
        item_to_send = analyse_content(html_doc,history)

        for key in item_to_send.keys():
            content = key
            subject = item_to_send[key]
            send_email(content, subject,account,password,receiver)
            time.sleep(5)

        time.sleep(30)

        print('downloading times %s'% iter)
        iter +=1




