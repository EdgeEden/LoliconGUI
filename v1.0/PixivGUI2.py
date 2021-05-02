# url = 'https://api.lolicon.app/setu/?apikey=72915888608c184b383c56&r18=0'

import os
import requests
import json
import webbrowser
import datetime
import re
import tkinter as tk
import tkinter.messagebox
import threading

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; '
    'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.49'
}
basic_url = 'https://api.lolicon.app/setu/?apikey={}&r18={}&keyword={}'
# 主窗口中会用到的全局变量
var = tk.StringVar
info = tk.Listbox
r18 = tk.StringVar
apikey = tk.Entry
keyword = tk.Entry

def mkdir():
    try:
        os.mkdir('imgs')
    except:
        pass
    try:
        os.mkdir('json')
    except:
        pass
    try:
        os.mkdir('log')
    except:
        pass


def change(name):
    mode = re.compile(r'[\\/:*?"<>|]')
    new_name = re.sub(mode, '_', name)
    return new_name


def get_info(apikey='', r18=0, keyword=''):
    url = basic_url.format(apikey, r18, keyword)
    r = requests.get(url=url, headers=headers)
    js = json.loads(r.text)
    try:
        img_url = js['data'][0]['url']
        webbrowser.open(img_url)
        log = {
            'code': str(js['code']),
            '剩余次数': str(js['quota']),
            '次数恢复剩余秒数': str(js['quota_min_ttl'])
        }
        return js['data'][0], log
    except Exception as e:
        if js['code'] == -1:
            tk.messagebox.showerror('-11', '内部错误，请再试一次，且可以向 i@loli.best 反馈')
        elif js['code'] == 401:
            tk.messagebox.showerror('401', 'APIKEY 不存在或被封禁')
        elif js['code'] == 429:
            tk.messagebox.showerror('429', '已超过当日使用次数，还有 '+str(js['quota_min_ttl'])+' 秒增加一次次数')
        else:
            tk.messagebox.showerror('内部错误', '内部错误，请再试一次')
        with open('log/' + change(str(datetime.datetime.now())) + '.txt', 'a+') as f:
            f.write(str(e))
            f.write(r.text)
        return None


def get_r18():
    return r18.get()


def get_apikey():
    return apikey.get()

def get_keyword():
    return keyword.get()

def save_json(data):
    pid = data['pid']
    uid = data['uid']
    title = data['title']
    author = data['author']
    picture_url = data['url']
    r18 = data['r18']
    width = data['width']
    height = data['height']
    tags = data['tags']

    js_data = {
        'pid': pid,
        'uid': uid,
        'title': title,
        'author': author,
        'picture_url': picture_url,
        'r18': r18,
        'width': width,
        'height': height,
        'tags': tags
    }
    data = json.dumps(js_data)
    with open('json/' + change(title) + '.json', 'a+') as f:
        f.write(data)
    return js_data


def showinfo(data, log):  # 这里更新了，加一个删除列表内容
    try:  # 防止第一遍的时候报错
        info.delete(0, tk.END)  # 从开始到末尾删除所有
    except:
        pass
    
    for value in data.values():
        info.insert(tk.END, str(value))
    log_list = []
    for key, value in log.items():
        log_list.append(key+' : '+value)
    info.insert(tk.END, log_list)


def save_img(data):
    img_url = data['url']
    img_title = change(data['title']) + '.' + img_url.split('.')[-1]
    img = requests.get(img_url, headers, timeout=5)
    with open('imgs/' + change(img_title), 'wb') as p:
        p.write(img.content)


def run(apikey, r18, keyword):
    try:
        data, log = get_info(apikey, r18, keyword)
        try:
            data_list = save_json(data)
            showinfo(data_list, log)
            try:
                var.set('稍等，色图保存中')
                save_img(data)
                var.set('色图已保存')
            except:
                tk.messagebox.showerror('Error', '图片保存失败，请手动下载')
        except:
            tk.messagebox.showerror('Error', '加载图片信息时出错，请检查是否配置错误后再试一次')
    except:
        pass


def main():
    # 主窗口
    win = tk.Tk()
    win.title('随机色图')
    win.geometry('376x400')

    # 标明来源
    tk.Label(win, text='源自：').grid(row=1, column=1)
    text = tk.Listbox(win, height=1, width=30)
    text.insert('end', 'https://api.lolicon.app/')
    text.grid(row=1, column=2, columnspan=5)

    # 设置r18选项，默认为非r18
    global r18
    r18 = tk.StringVar()
    tk.Label(win, text='R18选项：').grid(row=2, column=1)
    r1 = tk.Radiobutton(win, text='非R18', value='0', variable=r18)
    r2 = tk.Radiobutton(win, text='R18', value='1', variable=r18)
    r3 = tk.Radiobutton(win, text='混合', value='2', variable=r18)
    r18.set('0')
    r1.grid(row=2, column=2)
    r2.grid(row=2, column=3)
    r3.grid(row=2, column=4)

    # 设置APIKEY
    global apikey
    default = tk.StringVar()
    tk.Label(win, text='*apikey：').grid(row=3, column=1)
    apikey = tk.Entry(win, width=25, textvariable=default)
    default.set('72915888608c184b383c56')
    apikey.grid(row=3, column=2, columnspan=5)

    # 设置keyword
    global keyword
    tk.Label(win, text='*关键词:').grid(row=4, column=1)
    keyword = tk.Entry(win, width=25)
    keyword.grid(row=4, column=2, columnspan=5)

    # 展示图片信息的标头
    info_headers = ['pid:', 'uid:', 'title:', 'author:', 'url:', 'r18:', 'width:', 'height:', 'tags:', 'code:']
    info_headers_list = tk.Listbox(win, width=6)
    for info_header in info_headers:
        info_headers_list.insert('end', str(info_header))
    info_headers_list.grid(row=5, column=1)

    # 用于展示api图片信息
    global info
    sb = tk.Scrollbar(win, orient=tk.HORIZONTAL)
    sb.grid(row=6, column=1, columnspan=5, sticky=tk.N+tk.E+tk.S+tk.W)
    info = tk.Listbox(win, width=42, xscrollcommand=sb.set)
    info.grid(row=5, column=2, columnspan=4)
    sb.config(command=info.xview)

    # 运行按钮
    run_button = tk.Button(win, text='来张色图', font=('软体雅黑', 12, 'bold'), height=3, width=10, command=run_thread)
    run_button.grid(row=7, column=1, columnspan=10)

    # 下载图片信息显示
    global var
    var = tk.StringVar()
    saving = tk.Label(win, textvariable=var)
    saving.grid(row=8, column=2, columnspan=5)

    win.mainloop()


def run_thread():
    var.set('稍等，正在请求中')
    apikey = get_apikey()
    r18 = get_r18()
    keyword = get_keyword()
    t = threading.Thread(target=run, args=(apikey, r18, keyword))
    t.start()


if __name__ == '__main__':
    mkdir()
    main()
