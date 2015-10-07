import requests as req
from bs4 import BeautifulSoup as bs
import json
import re
import rd2wgs84 as rd_convert
# import rd2wgs84 as jesus

base_url = 'http://monumentenregister.cultureelerfgoed.nl/php/main.php?cAction=search&cOffset=1&cLimit=%s&oOrder=ASC&cSubmit=1&sProvincie=Noord-Holland&sGemeente=Amsterdam&sPlaats=&sStraat=&sHuisnummer=&sPostcode=&sOmschrijving=&sCompMonNr=&sCompMonName=&sStatus=&sHoofdcategorie=&sSubcategorie=&sFunctie='
monument_url = 'http://monumentenregister.cultureelerfgoed.nl/php/main.php?cAction=show&cOffset=2&cLimit=25&cOBJnr=%s&oOrder=ASC&cLast=7511&oField=OBJ_RIJKSNUMMER&sCompMonNr=&sCompMonName=&sStatus=&sProvincie=Noord-Holland&sGemeente=Amsterdam&sPlaats=&sStraat=&sHuisnummer=&sPostcode=&sFunctie=&sHoofdcategorie=&sSubcategorie=&sOmschrijving=&ID=0&oField=OBJ_RIJKSNUMMER'
results = []


def get_text(select, sub=''):
    raw = [sel.text for sel in select]
    if sub:
        raw = [text.replace(sub, '') for text in raw]
    if len(raw) == 1:
        return raw[0]
    return raw


def parse_table(selector):
    keys = [sel.text for sel in selector[0::3]]
    values = [sel.text for sel in selector[2::3]]
    return dict(zip(keys, values))


def parse_href(selector):
    return [select.attrs['href'] for select in selector]


def parse_regex(selector, regex):
    text = get_text(selector)
    if text:
        if type(text) == list:
            text = ';'.join(text)
        match = re.search(regex, text)
        if match:
            if match.groups():
                return match.groups()[0]
            return match.group()


def parse_attr(selector, attr):
    return [sel.attrs.get(attr) for sel in selector]


chunks = ['5000', '2511']
for chunk in chunks:
    monument_list = bs(req.get(base_url % (chunk)).text)
    urls = parse_href(monument_list.select('td a')[1:-1])
    urls = [url.split("'")[1] for url in urls]
    for url in urls:
        print(monument_url % (url))
        monument = bs(req.get(monument_url % (url)).text)
        attrs = monument.select('.tabeltype1 td')
        attrs.pop(0)
        attrs.pop(24)
        attrs.pop(42)
        p_attrs = parse_table(attrs)
        p_attrs['url'] = monument_url
        x, y = p_attrs['X-Y coörd'].split('-')
        if x and y:
            x, y = int(x), int(y)
            p_attrs['lat'], p_attrs['lon'] = rd_convert.convert(x, y)
        results.append(p_attrs)

with open('results.json', 'w') as dump:
    json.dump(results, dump)
