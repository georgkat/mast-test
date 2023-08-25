import os, re, json, unicodedata, urllib.request, time, subprocess
import smtplib as smtp
import socket
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# объявляем переменные
# для замены ударений
# https://habr.com/ru/articles/725406/
char_preserve = ["й", "ё", "Ё"]
placeholders = ["@", "#", "%"]

# для отправки почты
# изменить на нужные

smtp_server = 'smtp.yandex.ru'
smtp_port = '465'
login = 'login'
password = 'password'
mail_from = f'from@yandex.ru'
mail_to = f'to@yandex.ru'

# заголовки для обхода защиты википедии

HEADER_1 = ['User-Agent', 'Mozilla/5.0']
HEADER_2 = ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7']

# проверка того, первый ли это запуск
# если да, создаём переменные

old_links = [] # ссылки
new_links = []
last_modified = None

# для проверки одного инстанса программы

SOCKET = None

files = os.listdir()
if 'links.json' in files:
    with open('links.json') as json_file:
        old_data = json.load(json_file)
        old_links = old_data['links']
        last_modified = old_data['last_modified']

# функции
def send_mail(subject, body):
    try:
        email = MIMEMultipart()
        email['Subject'] = subject
        email['From'] = mail_from
        email['To'] = mail_to
        text = MIMEText(body)
        email.attach(text)
        server = smtp.SMTP_SSL(f'{smtp_server}:{smtp_port}')
        server.ehlo(f'{login}')
        server.login(f'{login}', f'{password}')
        server.auth_plain()
        server.sendmail(mail_from, mail_to, email.as_string())
        server.quit()
    except Exception as e:
        return False

def clean_links_list(links_list):
    new_list = []
    for row in links_list:
        if '/wiki/' in row and 'redlink=1' not in row:  # проверям наличие "живых" ссылок и отсутствие флага отсутствия статьи
            new_row = re.findall(r'a href="(.+?)"', row)[0] # берем все ссылки, и берем из них первую
            new_list.append(new_row)
    return new_list

def remove_accents(input_str):
    # https://habr.com/ru/articles/725406/
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def replace_characters(original, new, st):
    # https://habr.com/ru/articles/725406/
    for i in range(len(original) - 1):
        st = st.replace(original[i], new[i])
    return st

def get_brief_bio(r: str):
    # очистка страницы для получения первого абзаца
    title = re.findall(r'<span class="mw-page-title-main">(.+?)</span>', r)[0] # безу заголовок страницы
    brief_bio = re.findall(r'<p>(.+?)</p>', r, flags=re.S)[0] # и первый абзац текста
    brief_bio = re.sub('<[^>]*>', '', brief_bio) # удаляю html-тэги
    brief_bio = re.sub(r'&#91;(.+?)&#93;|&#160;', '', brief_bio) # удаляю курсив и символы цитирования
    brief_bio = brief_bio.replace('\n', '') # удаляю переносы
    temp = replace_characters(char_preserve, placeholders, brief_bio) # удаляю ударения
    temp = remove_accents(temp)
    brief_bio = replace_characters(placeholders, char_preserve, temp)
    return title, brief_bio

def get_page_data(url, modified_info=False):
    req = urllib.request.Request(url)
    req.add_header(*HEADER_1) # заменяю заголовки запросов
    req.add_header(*HEADER_2) # заменяю заголовки запросов
    resp = urllib.request.urlopen(req)
    text = resp.read().decode("utf-8")
    last_modified = resp.headers['last-modified']
    if not modified_info:
        return text
    else:
        return text, last_modified

def run_single_instance(uniq_name):
    try:
        global SOCKET
        SOCKET = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        SOCKET.bind('\0' + uniq_name)
        return True
    except socket.error as e:
        return False

def parse_wiki():
    first_page, modified = get_page_data(f'https://en.wikipedia.org/wiki/Deaths_in_2023#August', True) # получаем страницу со смертями
    time.sleep(3) # делаю паузу между запросами
    if modified != last_modified: # проверяем изменилась ли страница с прошлого захода
        links_raw = re.findall(r'<span class="mw-headline" id="August">(.+?)<h2', first_page, flags=re.S) # берем абзац августа
        links_list_raw = links_raw[0].split('<li>') # разделяем по строкам (там тэг <li>)
        new_links = clean_links_list(links_list_raw) # очищаем ссылки
        links = set(new_links).difference(set(old_links)) # сравниваем новые и старые ссылки,
        lines = [] # словарь для биографий
        for link in links: # итерируем по кажой ссылке
            full_link = 'https://en.wikipedia.org' + link
            try:
                linked_text = get_page_data(full_link)
                ru_link_raw = re.findall(r'interwiki-ru(.+?)</a>', linked_text) # проверяем наличие русской версии статьи
                if ru_link_raw:
                    ru_link = re.findall(r'a href="(.+?)"', ru_link_raw[0])[0] # если есть - получаем ссылку
                    rus_linked_text =  get_page_data(ru_link)
                    title, brief_bio = get_brief_bio(rus_linked_text)
                    lines.append(f'{title}: {brief_bio}')
                else: # если нет - берем английскую версию
                    title, brief_bio = get_brief_bio(linked_text)
                    lines.append(f'{title}: {brief_bio}')
            except:
                # требуется на тот случай если страница с умершим существует, но там действует редирект, например на страницу его самого известного фильма
                new_links.remove(link)

        if lines:
            send_mail('subj', '\r\n\r\n'.join(lines))

    if not new_links:
        new_links = old_links

    # сохраняем проверенные ссылки

    dump_data = {'links': new_links,
                 'last_modified': modified}

    with open('links.json', 'w') as f:
        json.dump(dump_data, f)

    time.sleep(60 * 60 * 3) # отключается на 3 часа

if __name__ == '__main__':
    if sys.argv[1] == 'start':
        if not run_single_instance('parser'):
            print('Script already started')
        parse_wiki()
    elif sys.argv[1] == 'stop':
        processes = subprocess.check_output("ps -ef | grep wikipedia_parser.py", shell=True).decode()
        processes = processes.split('\n')
        for process in processes:
            if 'wikipedia_parser' in process:
                for row in process.split(' ')[1:]:
                    if row != '':
                        subprocess.run(["kill", row])
                        break