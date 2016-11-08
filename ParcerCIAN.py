
# coding: utf-8

# In[1]:

import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np


# In[2]:

def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))


# ## Цена квартиры

# In[9]:

def getPrice(flat_page):
    price = flat_page.find('div', attrs={'class':'object_descr_price'})
    price = re.split('<div>|руб|\W', str(price))
    price = "".join([i for i in price if i.isdigit()][-3:])
    return int(price)


# ## Координаты квартиры

# In[10]:

def getCoords(flat_page):
    coords = flat_page.find('div', attrs={'class':'map_info_button_extend'}).contents[1]
    coords = re.split('&amp|center=|%2C', str(coords))
    coords_list = []
    for item in coords:
        if item[0].isdigit():
            coords_list.append(item)
    lat = float(coords_list[0])
    lon = float(coords_list[1])
    return lat, lon


# ## Количество комнат

# In[11]:

def getRoom(flat_page):
    rooms = flat_page.find('div', attrs={'class':'object_descr_title'})
    rooms = html_stripper(rooms)
    room_number = ''
    for i in re.split('-|\n', rooms):
        if 'комн' in i:
            break
        else:
            room_number += i
    room_number = "".join(room_number.split())
    return room_number


# ## Этаж

# In[12]:

def getFloor(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    floor_number = ''
    for i in re.split('\xa0|-|\n', re.split('Этаж:|Тип дома', table)[1]):
        if '/' in i:
            break
        else:
            floor_number += i
    floor_number = "".join(floor_number.split())
    return floor_number


# ## Количество этажей в доме

# In[13]:

def getNFloor(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if '/' in re.split('\xa0|:|-|\n', re.split('Этаж:|Тип дома', table)[1]):
        Nfloor_number = "".join([i for i in re.split('\xa0|:|-|\n', re.split('Этаж:|Тип дома', table)[1]) if i.isdigit()][-1])
    else: Nfloor_number = np.NaN
    return Nfloor_number


# ## Общая площадь квартиры

# In[14]:

def getTotsp(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    Totsp  = re.split('\n|\xa0', re.split('Общая площадь:|м2', table)[1])[-2]
    return float(Totsp.replace(',','.'))


# ## Жилая площадь квартиры

# In[15]:

def getLivesp(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if '–' in re.split('Жилая площадь:|Площадь кухни', table)[1]:
        Livesp = np.NaN
    else:
        Livesp  = re.split('\n|\xa0', re.split('Жилая площадь:|Площадь кухни', table)[1])[-6].replace(',','.')
    return Livesp


# ## Площадь кухни

# In[16]:

def getKitsp (flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if '–' in re.split('Площадь кухни:|санузлов|Санузел', table)[1]:
        Kitsp = np.NaN
    else:
        Kitsp  = re.split('\n|\xa0', re.split('Площадь кухни:|Совмещенных санузлов', table)[1])[2].replace(',','.')
    return Kitsp


# ## Расстояние до метро в минутах

# In[17]:

def getMetrdist(flat_page):
    Metrdist = ''
    if 'None' in re.split('\n',html_stripper(flat_page.find('span', attrs = {'class':'object_item_metro_comment'}))):
        Metrdist = np.NaN
    else:
        for i in re.split('\n',html_stripper(flat_page.find('span', attrs = {'class':'object_item_metro_comment'}))):
            if 'мин' in i:
                break
            else:
                Metrdist += i
        Metrdist = "".join(Metrdist.split())
    return Metrdist


# ## Пешком или на транспорте

# In[18]:

def getWalk(flat_page):
    Walk  = ''
    if 'None' in re.split('\n',html_stripper(flat_page.find('span', attrs = {'class':'object_item_metro_comment'}))):
        Walk = np.NaN
    else:
        for i in re.split('\n',html_stripper(flat_page.find('span', attrs = {'class':'object_item_metro_comment'}))):
            if 'пешком' in i: 
                Walk = 1
                break
            else:
                Walk = 0
    return Walk


# ## Наличие телефона

# In[19]:

def getTel (flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if 'Телефон' in table:
        Tel  = ''
        for i in re.split('\n|\xa0',re.split('Телефон:|Вид из окна', table)[1]):
            if 'да' in i: 
                Tel = 1
                break
            else:
                Tel = 0
    else:
        Tel = 0
    return Tel


# ## Новостройка или вторичка

# In[20]:

def getNew (flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if 'вторичка' in table:
        New  = 0
    else:
        New = 1
    return New


# ## Кирпичный/монолит/жб

# In[21]:

def getBrick (flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    Brick  = 0
    if 'кирпич' in table: Brick = 1
    if 'монолит' in table: Brick = 1
    if 'жб' in table: Brick = 1
    return Brick 


# ## Наличие балкона/лоджии

# In[22]:

def getBal (flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    Bal  = 0
    if 'балк' in table: Bal = 1
    if 'лодж' in table: Bal = 1
    return Bal 


# ## Расстояние до цента Москвы

# In[23]:

def getDist (flat_page):
    coorsh = 55.755826
    coordol = 37.6173
    Dist = (((getCoords(flat_page)[1] - coordol)*111.3*np.cos(getCoords(flat_page)[0]))**2 +
            ((getCoords(flat_page)[0] - coorsh)*111*np.cos(coordol))**2)**(1/2)
    return Dist


# # Итоговая таблица по районам

# In[36]:

FlatsStats = pd.DataFrame(columns=['District', 'N', 'Rooms', 'Price','Totsp','Livesp','Kitsp','Dist','Metrdist','Walk','Brick','Tel',
                                       'Bal','Floor','Nfloors','New'])


# In[37]:

def Stats(district,k,FlatsStats):
    links = []
    for page in range(1, 30):
        page_url =  district.format(page)

        search_page = requests.get(page_url)
        search_page = search_page.content
        search_page = BeautifulSoup(search_page, 'lxml')

        flat_urls = search_page.findAll('div', attrs = {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
        flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))

        for link in flat_urls:
            if link.isdigit():
                links.append(link)
    for i in range(len(links)):
        flat_url = 'http://www.cian.ru/sale/flat/' + str(links[i]) + '/' 
        flat_page = requests.get(flat_url)
        flat_page = flat_page.content
        flat_page = BeautifulSoup(flat_page, 'lxml')    

        to_append = {'District':k,'N':i, 'Rooms':getRoom(flat_page), 'Price':getPrice(flat_page), 'Totsp':getTotsp(flat_page), 
                     'Livesp':getLivesp(flat_page),'Kitsp':getKitsp(flat_page), 'Dist':getDist(flat_page),
                     'Metrdist':getMetrdist(flat_page), 'Walk':getWalk(flat_page),'Brick':getBrick(flat_page), 
                     'Tel':getTel(flat_page), 'Bal':getBal(flat_page),'Floor':getFloor(flat_page),
                     'Nfloors':getNFloor(flat_page), 'New':getNew(flat_page)}
        FlatsStats = FlatsStats.append(to_append, ignore_index=True)
        if i%100==0: print('I`m not dead, I`m working! The page is {}'.format(i+1))
    return FlatsStats


# In[38]:

#ЦАО
district0 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=13&district%5B1%5D=14&district%5B2%5D=15&district%5B3%5D=16&district%5B4%5D=17&district%5B5%5D=18&district%5B6%5D=19&district%5B7%5D=20&district%5B8%5D=21&district%5B9%5D=22&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district0,0,FlatsStats)
#САО
district1 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=23&district%5B1%5D=24&district%5B10%5D=33&district%5B11%5D=34&district%5B12%5D=35&district%5B13%5D=36&district%5B14%5D=37&district%5B15%5D=38&district%5B2%5D=25&district%5B3%5D=26&district%5B4%5D=27&district%5B5%5D=28&district%5B6%5D=29&district%5B7%5D=30&district%5B8%5D=31&district%5B9%5D=32&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district1,1,FlatsStats)
#СВАО
district2 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=39&district%5B1%5D=40&district%5B10%5D=49&district%5B11%5D=50&district%5B12%5D=51&district%5B13%5D=52&district%5B14%5D=53&district%5B15%5D=54&district%5B16%5D=55&district%5B2%5D=41&district%5B3%5D=42&district%5B4%5D=43&district%5B5%5D=44&district%5B6%5D=45&district%5B7%5D=46&district%5B8%5D=47&district%5B9%5D=48&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district2,2,FlatsStats)
#ВАО
district3 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=56&district%5B1%5D=57&district%5B10%5D=66&district%5B11%5D=67&district%5B12%5D=68&district%5B13%5D=69&district%5B14%5D=70&district%5B15%5D=71&district%5B2%5D=58&district%5B3%5D=59&district%5B4%5D=60&district%5B5%5D=61&district%5B6%5D=62&district%5B7%5D=63&district%5B8%5D=64&district%5B9%5D=65&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district3,3,FlatsStats)
#ЮВАО
district4 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=72&district%5B1%5D=73&district%5B10%5D=82&district%5B11%5D=83&district%5B2%5D=74&district%5B3%5D=75&district%5B4%5D=76&district%5B5%5D=77&district%5B6%5D=78&district%5B7%5D=79&district%5B8%5D=80&district%5B9%5D=81&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district4,4,FlatsStats)
#ЮАО
district5 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=84&district%5B1%5D=85&district%5B10%5D=94&district%5B11%5D=95&district%5B12%5D=96&district%5B13%5D=97&district%5B14%5D=98&district%5B15%5D=99&district%5B2%5D=86&district%5B3%5D=87&district%5B4%5D=88&district%5B5%5D=89&district%5B6%5D=90&district%5B7%5D=91&district%5B8%5D=92&district%5B9%5D=93&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district5,5,FlatsStats)
#ЮЗАО
district6 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=100&district%5B1%5D=101&district%5B10%5D=110&district%5B11%5D=111&district%5B2%5D=102&district%5B3%5D=103&district%5B4%5D=104&district%5B5%5D=105&district%5B6%5D=106&district%5B7%5D=107&district%5B8%5D=108&district%5B9%5D=109&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district6,6,FlatsStats)
#ЗАО
district7 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=112&district%5B1%5D=113&district%5B10%5D=122&district%5B11%5D=123&district%5B12%5D=124&district%5B13%5D=348&district%5B14%5D=349&district%5B15%5D=350&district%5B2%5D=114&district%5B3%5D=115&district%5B4%5D=116&district%5B5%5D=117&district%5B6%5D=118&district%5B7%5D=119&district%5B8%5D=120&district%5B9%5D=121&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district7,7,FlatsStats)
#СЗАО
district8 = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=125&district%5B1%5D=126&district%5B2%5D=127&district%5B3%5D=128&district%5B4%5D=129&district%5B5%5D=130&district%5B6%5D=131&district%5B7%5D=132&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
FlatsStats=Stats(district8,8,FlatsStats)


# In[53]:

del FlatsStats['N']
FlatsStats.insert(1,'N',np.arange(0,FlatsStats.shape[0],1))


# In[55]:

import csv
with open('FlatsStats.csv', 'w',newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['District','N','Rooms','Price','Totsp','Livesp','Kitsp','Dist',
                                                 'Metrdist','Walk','Brick','Tel','Bal','Floor','Nfloors','New'])
    n=FlatsStats.shape[0]
    writer.writeheader()
    for i in range(n):
        writer.writerow({'District':FlatsStats['District'][i],
                         'N':FlatsStats['N'][i],
                         'Rooms':FlatsStats['Rooms'][i],
                         'Price':FlatsStats['Price'][i],
                         'Totsp':FlatsStats['Totsp'][i],
                         'Livesp':FlatsStats['Livesp'][i],
                         'Kitsp':FlatsStats['Kitsp'][i],
                         'Dist':FlatsStats['Dist'][i],
                         'Metrdist':FlatsStats['Metrdist'][i],
                         'Walk':FlatsStats['Walk'][i],
                         'Brick':FlatsStats['Brick'][i],
                         'Tel':FlatsStats['Tel'][i],
                         'Bal':FlatsStats['Bal'][i],
                         'Floor':FlatsStats['Floor'][i],
                         'Nfloors':FlatsStats['Nfloors'][i],
                         'New':FlatsStats['New'][i],
                         })

