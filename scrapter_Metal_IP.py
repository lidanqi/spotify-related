# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 18:23:23 2018

@author: luke&jessica
"""

from datetime import datetime

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from sqlalchemy import create_engine
from datetime import datetime


import logging
import sys

BASE_URL = "https://www.metal-archives.com/"

def get_soup(url):
    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
    res = requests.get(url, headers=agent) #, verify = False)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

# scrape a band page
def get_band(url):
    url = 'https://www.metal-archives.com/bands/Z%C4%81_L%C3%A4_Th%C3%BC/3540369238'
    band_id_str = url[url.rindex('/')+1:]
    band_id = int(band_id_str)
    
    soup = get_soup(url)
    
    band_info = soup.find("div", {"id": "band_info"})
    
    dict_info = {}
    try:
        dict_info["band_id"] = band_id
        dict_info['band_name'] = band_info.find(class_ = "band_name").a.text
        dict_info['birth_year'] = int(band_info.find("dt", text = "Formed in:").next_sibling.next_sibling.text)
        
        dict_info['status'] = band_info.find("dt", text = "Status:").next_sibling.next_sibling.text
        dict_info['is_active'] = dict_info['status'] == 'Active'
        
        temp = band_info.find("dt", text = "Genre:").next_sibling.next_sibling.text.split('/')
        dict_info['genres'] = [w.upper().replace(' ', '_') for w in temp]
        
        temp = band_info.find("dt", text = "Lyrical themes:").next_sibling.next_sibling.text.split(', ')
        dict_info['lyric_themes'] = [w.upper().replace(' ', '_') for w in temp]
        
        dict_info['country_name'] = band_info.find("dt", text = "Country of origin:").next_sibling.next_sibling.text
        dict_info['country_url'] = band_info.find("dt", text = "Country of origin:").next_sibling.next_sibling.a['href']
        dict_info['location'] = band_info.find("dt", text = "Location:").next_sibling.next_sibling.text
        
        description = ''
        try:
            url_readmore = BASE_URL + 'band/read-more/id/' + band_id_str
            soup_readmore = get_soup(url_readmore)
            description = soup_readmore.text
        except:
            # readmore failed, fall back to main page's description
            description = band_info.find(class_ = "band_comment clear").text
            
        dict_info['description'] = description.replace('\r\n','\n').replace('\n','  ')
        
        # TODO: add YEARS_ACTIVE and its previous names        
        # TODO: add MEMBERS
        # TODO: add Album
        

        
        # TODO: add related bands(exclude itself)
        
    except:
        print("Error for band with id {}".format(band_id_str))
    return None
    
        
def get_artist():
    return None

def get_lyrics():
    # https://www.metal-archives.com/release/ajax-view-lyrics/id/2674901        
    return None

def get_album():
    # https://www.metal-archives.com/albums/Z%C4%81_L%C3%A4_Th%C3%BC/77%2B_%287%2B7%29-7_%2B77%3D156/394842
    return None    
        

# scrape a artist page




# start from a alpha page

logger = logging.getLogger()
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message) - s')
file_handler = logging.FileHandler('metal.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S")))
file_handler.setFormatter(logFormatter)
logger.addHandler(file_handler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)



s = requests.session()
