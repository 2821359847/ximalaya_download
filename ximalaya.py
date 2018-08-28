
# coding: utf-8

# In[1]:


import os
import sys
import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool, Lock, freeze_support


# In[2]:


page_url = ''
headers = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'Chrome/57.0.2987.133')
}


# In[3]:


def input_page_url_with_change_dir():
    '''
    转移到要存储的文件夹位置并获取专辑页面地址
    '''
    print('请输入存储文件夹(回车确认):')
    while True:
        dir_ = input()
        if os.path.exists(dir_):
            os.chdir(dir_)
            break
        else:
            try:
                os.mkdir(dir_)
                os.chdir(dir_)
                break
            except Exception as e:
                print('请输入有效的文件夹地址:')

    print('请输入想下载FM页面的网址(回车确认) -\n'
          '如 https://www.ximalaya.com/youshengshu/10996284/')
    page_url = input()
    return page_url


# In[4]:


def get_json_urls_from_page_url(page_url, page_num):
    urls = []
    for i in range(page_num - 1):
        tmp_url = page_url + 'p' + str(i + 1)
        print(tmp_url)
        res = requests.get(tmp_url, headers=headers)
        soup = BeautifulSoup(res.content, "html5lib")
        mp3_ids = soup.find('div',class_='dOi2 sound-list').findAll('li')
        for i in range(30):
            tmp_int = mp3_ids[i].find_all('div')[4].find_all('a')[0].attrs['href'].split('/')[-1]
            urls.append('http://www.ximalaya.com/tracks/' + str(tmp_int) + '.json')
    tmp_url = page_url + 'p' + str(page_num)
    print(tmp_url)
    res = requests.get(tmp_url, headers=headers)
    soup = BeautifulSoup(res.content, "html5lib")
    mp3_ids = soup.find('div',class_='dOi2 sound-list').findAll('li')
    for i in range(30):
        try:
            tmp_int = mp3_ids[i].find_all('div')[4].find_all('a')[0].attrs['href'].split('/')[-1]
            urls.append('http://www.ximalaya.com/tracks/' + str(tmp_int) + '.json')
        except:
            print("nothing happen")
    return urls


# In[5]:


def get_mp3_from_json_url(json_url):
    '''
    访问json链接获取音频名称与下载地址并开始下载
    '''
    mp3_info = requests.get(json_url, headers=headers).json()
    title = mp3_info['album_title'] + '+ ' + mp3_info['title'] + '.m4a'
    path = mp3_info['play_path']
    title = title.replace('|', '-')  # 避免特殊字符文件名异常

    if os.path.exists(title):
        return 'Already exists!'

    # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
    while True:
        try:
            with open(title, 'wb') as f:
                response = requests.get(path, headers=headers, stream=True)

                if not response.ok:
                    # shared_dict.pop(title)
                    print('response error with', title)
                    continue

                total_length = int(response.headers.get('content-length'))
                chunk_size = 4096
                dl = 0
                shared_dict[title] = 0

                for block in response.iter_content(chunk_size):
                    dl += len(block)
                    f.write(block)
                    done = int(50 * dl / total_length)
                    shared_dict[title] = done
                
                global n_tasks
                with lock:
                    n_tasks -= 1
                shared_dict.pop(title)
                return 'Done!'

        except Exception as e:
            print('other error with', title)
            os.remove(title)


# In[6]:


def report_status():
    '''
    根据共享字典汇报下载进度
    '''
    import time
    n = len(mp3_json_urls)

    print(u'准备下载...')
    while len(shared_dict) == 0:
        time.sleep(0.2)

    while len(shared_dict) != 0:
        line = ''  # "\r"
        for title, done in shared_dict.items():
            line += "%s\n - [%s%s]\n" % (
                title, '=' * done, ' ' * (50 - done)
            )
        line += '\n**** 剩余/总任务 = %s/%s ****' % (n_tasks, n)
        os.system('cls')
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(1)


# In[7]:


page_url = input_page_url_with_change_dir()


# In[8]:


mp3_json_urls = get_json_urls_from_page_url(page_url, 2)


# In[9]:


n_tasks = len(mp3_json_urls)
lock = Lock()
shared_dict = {}


# In[11]:


freeze_support()
with Pool(6) as pool:
    # http://stackoverflow.com/questions/35908987/python-multiprocessing-map-vs-map-async
    r = pool.map_async(get_mp3_from_json_url, mp3_json_urls)
    report_status()
    r.wait()
    os.system('cls')
    print('下载完成！')


# In[10]:


i = 174
while i < 180:
    get_mp3_from_json_url(mp3_json_urls[i])
    i = i + 1


# In[12]:


get_mp3_from_json_url(mp3_json_urls[11])

