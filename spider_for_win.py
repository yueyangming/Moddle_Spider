__author__ = ' Harold (Finch) '

import os
import urllib2
import urllib
import cookielib
from bs4 import BeautifulSoup
import re
import ssl
import lxml

def get_cookie(username,password):

    filename = 'cookie.txt'

    data={"username":username,"password":password, "rememberusername":"1"}
    post_data=urllib.urlencode(data)

    cookie = cookielib.MozillaCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    loginUrl = 'https://sdc-moodle.samf.aau.dk/login/index.php'
    result = opener.open(loginUrl,post_data)

    print ('Log in successfully, Begin downloading')
    return opener

def open_url(opener,url):
    # This funciton is used to open and store content in specific URL

    result = opener.open(url)
    return result.read()

def download_url(opener,url,filename):

    folder_flag = 0
    file_content = opener.open(url)

    url_split = url.split('/')
    if len(url_split) == 10:
        folder_flag = 1
        foldername = url_split[8]

    cwd = os.getcwd()

    if folder_flag:
        if not os.path.exists(foldername):
            os.mkdir(foldername)
        os.chdir(cwd + '/' + foldername)

    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        print ('Downloading ' + filename)
        with open(filename,'wb') as output:
            output.write(file_content.read())

    if folder_flag :
        os.chdir(cwd)

def analyse_download_page(opener,url):

    content = open_url(opener,url)
    soup = BeautifulSoup(content,'lxml')
    result_temp = soup.find_all(href = re.compile('forcedownload=1'))
    for each in result_temp:

        url = each.attrs['href']
        filename = each.get_text()
        download_url(opener,url,filename)

    print ('Current Folder download complete, moving to next one')

def analyse_folder_page(opener,url):

    key_string = 'https://sdc-moodle.samf.aau.dk/mod/folder/view.php?'
    cwd = os.getcwd()
    content = open_url(opener,url)
    soup = BeautifulSoup(content, 'lxml')
    result_temp = soup.find_all(href = re.compile(key_string))

    result_file = soup.find_all(href = re.compile('resource/view.php'))
    for each in result_file:
        url = each.attrs['href']
        filename = each.get_text()
        temp = filename.replace(' File','.pdf')
        filename = temp
        download_url(opener,url,filename)

    for each in result_temp:
        url = each.attrs['href']
        foldername = each.get_text()
        print ('Downloading Folder : ' + foldername)

        if not os.path.exists(foldername):
            os.mkdir(foldername)
        os.chdir(cwd + '/' + foldername)
        analyse_download_page(opener,url)
        os.chdir(cwd)

def analyse_course(opener,url):

    cwd = os.getcwd()
    content = open_url(opener,url)
    soup = BeautifulSoup(content,'lxml')
    result_temp = soup.find_all('h3')
    for each in result_temp:
        temp = each.find('a')
        url = temp.attrs['href']
        coursename = temp.get_text()
        print ('Downloading Course : ' + coursename)

        if not os.path.exists(coursename):
            os.mkdir(coursename)
        os.chdir(cwd + '/' + coursename)
        analyse_folder_page(opener,url)
        analyse_folder_page(opener,url)
        os.chdir(cwd)
    print ('Course ' + coursename + ' Download Complete, moving to next one')

def select_major(major):
    if major == 'NN':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=7'
    if major == 'IM':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=6'
    if major == 'PM':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=9'
    if major == 'Nano':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=32'
    if major == 'CBE':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=36'
    if major == 'Omics':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=31'
    if major == 'WE':
        url = 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=41'
    return url

def pure(str):
    if str[len(str) - 1 ] == '\n':
        str = str[0: len(str) - 1]
    return str

def init():

    file_info = open('info.ini', 'r')
    major = pure( file_info.readline())
    username = pure( file_info.readline())
    password = pure( file_info.readline())
    file_info.close()

    return (major,username,password)


(major,username,password) = init()
try:
    url = select_major(major)
except:
    print('Wrong input of major, Please check and try it again')
    exit()
print('Logging in, Please wait')
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    opener = get_cookie(username,password)
    analyse_course(opener,url)
    print('Everything download complete, enjoy')
except:
    print('Something wrong, Please contact author Harold at 447903563@qq.com')
    print ('Press enter to exit')
    content = raw_input()
    if (content!=''):
        exit
    
