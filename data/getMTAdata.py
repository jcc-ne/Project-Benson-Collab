from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from StringIO import StringIO


link = 'http://web.mta.info/developers/turnstile.html'
mtaweb = 'http://web.mta.info/developers/'
r = requests.get(link)
if r.status_code != 200:
    raise Exception('webpage not working')

soup = BeautifulSoup(r.content)

# try to understand the structure of the html page by iter thru the ancestors
# in this case, just finding the parent might be enough
ptrn = re.compile('Saturday, July 17.*')
turnstile_page = soup.find(string=ptrn)


def iterAncestor(child_string):
    lname = []
    lclass = []
    parent = child_string.findParent()
    while parent:
        lname.append(parent.name)
        lclass.append(parent.get('class'))
        parent = parent.findParent()
    cnt = 0
    for n, c in zip(lname[-1:0:-1], lclass[-1:0:-1]):
        print cnt*'  ', n, 'class:', c
        cnt += 1


def getAllLinks(link=link):
    """ return all turnstile data links from {}""".format(link)
    alllinkspage = turnstile_page.parent.parent
    links = alllinkspage.findAll('a')
    abslinks = [mtaweb + l.attrs['href'] for l in links]
    return abslinks


def getAllDf(n_start=None, n_end=None):
    """ get dataframe from the MTA website, if n_start and n_end not given
    all data on that page will be downloaded
    """
    print "getting data from the MTA website..."
    links = getAllLinks()[n_start: n_end]
    df_all = pd.DataFrame()
    for l in links:
        print "working on {}...".format(l)
        df = get_df_from_MTAlink(l)
        df_all = df_all.append(df)
    print 'ok'
    return df_all, links


def get_df_from_MTAlink(link):
    r = requests.get(link)
    if r.status_code != 200:
        raise Exception('{} webpage not working'.format(link))
    f = StringIO(r.content)
    df = pd.read_csv(f)
    df.columns = [c.strip() for c in df.columns]
    return df
