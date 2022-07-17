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
basic_url = 'https://api.lolicon.app/setu/v2?r18={}&keyword={}'
# 主窗口中会用到的全局变量
var = tk.StringVar
info = tk.Listbox
r18 = tk.StringVar
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


def get_info(r18=0, keyword=''):  # update log: debug and update error expression
    url = basic_url.format(r18, keyword)
    r = requests.get(url=url, headers=headers)
    js = r.json()
    try:  # 再次定位到问题，，应该是这个try
        img_url = js['data'][0]['urls']['original']
        webbrowser.open(img_url)
        error = js['error']
        if error:
            tk.messagebox.showerror('error', error)
        return js['data'][0], error
    except Exception as e:
        tk.messagebox.showerror('error', str(e))
        with open('log/' + change(str(datetime.datetime.now())) + '.txt', 'a+') as f:
            f.write(str(e))
            f.write(r.text)
        return None


def get_r18():
    return r18.get()


def get_keyword():
    return keyword.get()


def save_json(data):
    pid = data['pid']
    uid = data['uid']
    title = data['title']
    author = data['author']
    picture_url = data['urls']
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
    data = json.dumps(js_data, ensure_ascii=False)
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
    # for key, value in log.items():  # 更新后log就是一个字符串了
    info.insert(tk.END, log)


def save_img(data):
    img_url = data['urls']['original']
    img_title = change(data['title']) + '.' + img_url.split('.')[-1]
    img = requests.get(img_url, headers, timeout=5)
    with open('imgs/' + change(img_title), 'wb') as p:
        p.write(img.content)


def opendir():
    dir = os.path.abspath('.')
    try:
        os.startfile(dir + '/imgs')
    except:
        tk.messagebox.showerror('Error','请先获取图片')


def run(r18, keyword):
    try:
        data, log = get_info(r18, keyword)  # ------定位问题函数
        try:
            data_list = save_json(data)
            showinfo(data_list, log)  # ---------更新后图片显示信息问题定位
            try:
                var.set('稍等，色图保存中')
                save_img(data)
                var.set('色图已保存')
            except:
                tk.messagebox.showerror('Error', f'{data["title"]}图片保存失败，请手动下载')
                var.set('色图保存失败，请手动下载')
        except:
            tk.messagebox.showerror('Error', '加载图片信息时出错，请检查是否配置错误后再试一次')
            var.set('error')
    except:
        tk.messagebox.showerror('get_info function error')


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


    # 设置keyword
    global keyword
    tk.Label(win, text='*关键词:').grid(row=4, column=1)
    keyword = tk.Entry(win, width=25)
    keyword.grid(row=4, column=2, columnspan=5)

    # 展示图片信息的标头
    info_headers = ['pid:', 'uid:', 'title:', 'author:', 'url:', 'r18:', 'width:', 'height:', 'tags:', 'error:']
    info_headers_list = tk.Listbox(win, width=6)
    for info_header in info_headers:
        info_headers_list.insert('end', str(info_header))
    info_headers_list.grid(row=5, column=1)

    # 用于展示api图片信息
    global info
    sb = tk.Scrollbar(win, orient=tk.HORIZONTAL)
    sb.grid(row=6, column=1, columnspan=5, sticky=tk.N + tk.E + tk.S + tk.W)
    info = tk.Listbox(win, width=42, xscrollcommand=sb.set)
    info.grid(row=5, column=2, columnspan=4)
    sb.config(command=info.xview)

    # 运行按钮
    run_button = tk.Button(win, text='来张色图', font=('软体雅黑', 12, 'bold'), height=3, width=10, command=run_thread)
    run_button.grid(row=7, column=3, columnspan=2)

    # 打开路径
    run_button = tk.Button(win, text='打开图片文件夹', font=('软体雅黑', 10, 'bold'), height=3, width=13, command=opendir)
    run_button.grid(row=7, column=5)

    # 下载图片信息显示
    global var
    var = tk.StringVar()
    saving = tk.Label(win, textvariable=var)
    saving.grid(row=8, column=2, columnspan=5)

    win.mainloop()


def run_thread():
    mkdir()
    var.set('稍等，正在请求中')
    r18 = get_r18()
    keyword = get_keyword()
    t = threading.Thread(target=run, args=(r18, keyword))
    t.start()


if __name__ == '__main__':
    main()
