"""
Created by: Wang MinWei
"""
from datetime import datetime

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from sqlalchemy import create_engine
from datetime import datetime


def run():
    s = requests.session()
    prog_dict = sso_main_list(s)
    prog_dict = sso_concert_page(prog_dict, s)

    df = pd.DataFrame.from_dict(prog_dict, orient='index')
    push_to_db(df)
    df = df.sort(['new', 'date-time'], ascending=[0, 1])
    df = df.drop('new', 1)
    df = df[sorted(df.columns.tolist())]
    df.to_excel('sso_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.xls', encoding='utf-8')



def push_to_db(sso):
    engine = create_engine('postgresql://wangminwei@localhost:5432/wangminwei')
    hist_sso = pd.read_sql('select id from sso', engine)
    hist_sso_hdr_ls = hist_sso['id'].tolist()
    new_sso = [i for i in sso.index.values.tolist() if i not in hist_sso_hdr_ls]
    new_sso_df = sso.loc[new_sso]
    new_sso_df['id'] = new_sso_df.index
    new_sso_df['id'].to_sql('sso', engine, if_exists='append', index = False)
    # sso['new'] = sso[sso.index.get_level_values(0) in new_sso]
    sso['new'] = 0
    sso.loc[new_sso, 'new'] = 1


def sso_concert_page(prog_dict, s):
    sso = 'https://www.sso.org.sg/orchestra-season/'

    for k, v in prog_dict.iteritems():
        print(k)
        response = s.get(urljoin(sso, k))
        # response.text
        soup_pg = BeautifulSoup(response.text, 'html.parser')
        # get programs

        prog_list = soup_pg.find(string='Programme')
        if prog_list:
            prog_list = prog_list.find_next()
            prog = ''.join(prog_list.findAll(text=True))
        else:
            prog = 'No info'
        # get price
        tickets = soup_pg.find(string=re.compile("Standard Tickets"))
        if tickets:
            tickets = tickets.find_next().findAll(text=True)[0].split(',')
        else:
            tickets = []
        cat_str = ['cat ' + str(i) for i in range(1, 10)]
        price_list = dict(zip(cat_str, tickets))
        v.update({'prog': prog,})
        v.update(price_list)
        # get date time
        dt = soup_pg.find(string=re.compile("Schedule"))
        d = None
        t = None
        if dt:
            dt = dt.find_next().text
            # string example: Thu / 22 Nov 2018 / 7:30PM
            day, date_str, time = dt.split('/')
            d = datetime.strptime(date_str.strip() + ' ' + time.strip(), '%d %b %Y %I:%M%p')

        # get venue
        vn = soup_pg.find(string=re.compile("^Venue"))
        if vn:
            vn = vn.find_next().text.strip()
            #         v.update({'venue': vn, 'date-time': dt, 'url': '=HYPERLINK("{}")'.format(urljoin(sso, k))})
        v.update({'venue': vn, 'date-time': d, 'url': urljoin(sso, k)})

    return prog_dict


def sso_main_list(s):
    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    res = s.get('https://www.sso.org.sg/orchestra-season', headers=agent, verify = False)
    soup = BeautifulSoup(res.text, 'html.parser')

    prog_dict = {}

    for d in soup.find_all(class_="events-list-details"):
        id = d.a['href'].split('/')[-1]
        tag = d.h2.text.strip()
        prog_dict[id] = {'tag': tag}

    return prog_dict

if __name__ == '__main__':
    run()