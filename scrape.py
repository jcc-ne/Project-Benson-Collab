import urllib as ul
import re

exp = 'http://web\.mta\.info/developers/data/nyct/turnstile/turnstile_\d\d\d\d\d\d\.txt'

with ul.urlopen('http://web.mta.info/developers/turnstile.html') as page:
    urls = re.findall()
    print (urls)



