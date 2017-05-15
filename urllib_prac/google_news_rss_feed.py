from bs4 import BeautifulSoup as bs
import urllib.request as ur

req = ur.Request("https://news.google.com/?output=rss",headers=
                 {"User-Agent":""})

resp = ur.urlopen(req)

xml = bs(resp,"xml",exclude_encodings="utf-8")

for item in xml.findAll("link"):
    print (item.text)

print("end")
