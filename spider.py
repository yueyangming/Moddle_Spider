__author__ = ' Harold (Finch) '

import os
import urllib.request
import urllib.parse
import http.cookiejar
from bs4 import BeautifulSoup
import re
import ssl
import sys


global dict_number_to_major
global dict_major_to_site
dict_number_to_major = {'1' : 'NN', '2':'IM', '3':'PM','4':'Nano', '5' : 'CBE', '6' : 'Omics', '7' : 'WE'}
dict_major_to_site = {'NN' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=15', 'IM' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=11',
                      'PM' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=18', 'Nano' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=33',
                      'CBE' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=37', 'Omics' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=30',
                      'WE' : 'https://sdc-moodle.samf.aau.dk/course/index.php?categoryid=42'}

def get_cookie(username,password):

    try:

        filename = 'cookie.txt'

        data={"username":username, "password":password, "rememberusername":"1"}
        post_data=urllib.parse.urlencode(data).encode(encoding='UTF8')

        cookie = http.cookiejar.MozillaCookieJar(filename)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        loginUrl = 'https://sdc-moodle.samf.aau.dk/login/index.php'
        result = opener.open(loginUrl, post_data)

        return opener

    except:

        print('Something wrong with get_cookie part')

def open_url(opener,url):
    # This funciton is used to open and store content in specific URL
    try:

        result = opener.open(url)
        return result.read()

    except:

        print('Something wrong with open_url part')

def download_url(opener,url,filename):

    try:

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
    except:

        print('Something wrong with download_url part')

def analyse_download_page(opener,url):

    try:

        content = open_url(opener,url)
        soup = BeautifulSoup(content,'lxml')
        result_temp = soup.find_all(href = re.compile('forcedownload=1'))
        for each in result_temp:

            url = each.attrs['href']
            filename = each.get_text()
            download_url(opener,url,filename)

        print ('Current Folder download complete, moving to next one')

    except:
        print('Something wrong with analyse_download_page part')

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
        foldername = pure(foldername)        # For windows
        print ('Downloading Folder : ' + foldername)

        if not os.path.exists(foldername):
            os.mkdir(foldername)
        os.chdir(cwd + '/' + foldername)
        analyse_download_page(opener,url)
        os.chdir(cwd)

def analyse_course(opener,url):

    try:

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
            os.chdir(cwd)
        print ('Course ' + coursename + ' Download Complete, moving to next one')

    except:

        print('Something wrong with analyse_course part')

def pure(str):
    if str[len(str) - 1 ] == '\n':
        str = str[0: len(str) - 1]

    if str.find(':') > -1:     # For windows
        str = str.replace(':',' ')
    return str

def init():

    # First three lines is for mac, don't know if it will cause some problems.
    path_temp = sys.argv[0]
    parent_path = os.path.dirname(path_temp)
    os.chdir(parent_path)

    if os.path.exists('info.ini'):
        with open('info.ini','r') as file_info:
            major = pure( file_info.readline())
            username = pure( file_info.readline())
            password = pure( file_info.readline())


        return (major,username,password)
    else:
        return generation()

def generation():
    global dict_number_to_major
    print ('Not found ini file, create a new one')
    print ('First, Select your major,  \n 1 for NN \n 2 for IM \n 3 for PM \n 4 for Nano \n 5 for CBE \n 6 for Omics \n 7 for WE \n ')
    major_number = input('Select your major number \n')
    major_name = dict_number_to_major[major_number]
    username = input('Please input your username to log in Moodle \n')
    password = input('Please input your password to log in Moodle \n')

    with open('info.ini','w') as file_ini:
        file_ini.write(major_name + '\n' + username + '\n' + password + '\n')

    return (major_name,username,password)

if __name__ == '__main__':

    (major,username,password) = init()
    try:
        url = dict_major_to_site[major]
    except:
        print('Wrong input of major, Please check and try it again')
        exit()
    print('Logging in, Please wait')
    try:
        # ssl._create_default_https_context = ssl._create_unverified_context       # For windows
        opener = get_cookie(username,password)
        log_in_url = 'https://sdc-moodle.samf.aau.dk/login/index.php'
        content_temp = open_url(opener,log_in_url).decode('utf-8')
        if 'You are logged in as ' in content_temp :
            print ('Log in successfully, Begin downloading')
            analyse_course(opener,url)
            print('Everything download complete, enjoy')
        else:
            print ('Log in failed')
            print ('Maybe something wrong with info.ini or Internet, Please check, if need help, please contact Harold at 447903563@qq.com ')

    except:
        print('Something wrong, Please contact author Harold at 447903563@qq.com')