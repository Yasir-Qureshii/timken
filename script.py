import requests
import re
import os
import concurrent.futures
from bs4 import BeautifulSoup
from datetime import datetime
from openpyxl import Workbook


print("scraping the data")
def generate_filename():
    now = datetime.now()
    xx = 'Output_' + str(now)[:-7] + '.xlsx'
    xx = xx.replace(' ', '_').replace(':', '-')
    return xx

filename = "Output.xlsx"
if os.path.exists(filename):
    filename = generate_filename()
    
wb = Workbook()
ws = wb.active


def get_data(url, count):
    global ws, wb
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    groups = soup.find_all('div', 'group')
    specs = groups[2]
    dimensions = groups[3]

    header = []
    row = []

    # plp-table-value 
    for tr in specs.find_all('tr', {'itemprop': 'additionalProperty'}):
        head = tr.find('td', 'plp-table-name').text.strip()
    #     value = tr.find('span', {'itemprop': 'value'}).text.strip()
        value = tr.find('span', 'plp-spec-value').find_all('span', recursive=False)[-1].text.strip()
        header.append(head)
        row.append(value)

    for tr in dimensions.find_all('tr', {'itemprop': 'additionalProperty'}):
        head = tr.find('td', 'plp-table-name').text.strip()
        value = tr.find('span', 'plp-spec-value').find_all('span', recursive=False)[-1].text.strip()
        header.append(head)
        row.append(value)
       
    ws.append(header)
    ws.append(row)
    
    if count % 20 == 0:
        wb.save(filename)

base_url = 'https://cad.timken.com'
url = 'https://cad.timken.com/viewitems/engineered-bearings/automotive-aftermarket-hub-assemblies?pagesize=200&pagenum=1&selecteduom=1'
res = requests.get(url)

soup = BeautifulSoup(res.text, 'html.parser')
links = soup.find('table', {'id': 'plp-table-filter'}).find_all('a', 'plp-itemlink')
urls = []
counter = []
for link in links:
    link = base_url + link['href']
    urls.append(link)
    
for i in range(1,len(urls)):
    counter.append(i)

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(get_data, urls, counter)
    
wb.save(filename)
