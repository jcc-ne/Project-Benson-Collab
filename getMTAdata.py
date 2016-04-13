from bs4 import BeautifulSoup
import requests
import re


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
