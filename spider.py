__author__ = ' Harold '

import urllib2
import urllib
import cookielib
from bs4 import BeautifulSoup
import re

def get_cookie():

    f = open('info.ini','r')
    url = f.readline()
    username = f.readline()
    pwd = f.readline()
    f.close()

    filename = 'cookie.txt'

    data={"username":username,"password":pwd, "rememberusername":"1"}
    post_data=urllib.urlencode(data)

    cookie = cookielib.MozillaCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    loginUrl = 'https://sdc-moodle.samf.aau.dk/login/index.php'
    result = opener.open(loginUrl,post_data)

    cookie.save(ignore_discard=True,ignore_expires=True)

    return opener

def open_url(opener,url):
    # This funciton is used to open and store content in specific URL

    result = opener.open(url)
    return result.read()

def download_url(opener,url,filename):

    result = opener.open(url)

    with open(filename,'wb') as output:
        output.write(result.read())

def analyse_download_page(content,opener):

    soup = BeautifulSoup(content,'lxml')
    result_temp = soup.find_all(href = re.compile('forcedownload=1'))
    for each in result_temp:

        url = each.attrs['href']
        filename = each.get_text()
        print ('Downloading ' + filename)
        download_url(opener,url,filename)

    print ('Current Folder download complete, moving on')

def analyse_folder_page(content,opener,url):

    key_string = 'https://sdc-moodle.samf.aau.dk/mod/folder/view.php?'

    soup = BeautifulSoup(content, 'lxml')
    result_temp = soup.find_all(href = re.compile(key_string))
    for each in result_temp:
        url = each.attrs['href']
        foldername = each.get_text()
        each_content = open_url(opener,url)
        print ('Downloading Folder : ' + foldername)
        analyse_download_page(each_content,opener)


if __name__ == '__main__':

    file = open('info.ini','r')
    url = file.readline()
    file.close()

    opener = get_cookie()
    content = open_url(opener,url)
    analyse_download_page(content,opener)