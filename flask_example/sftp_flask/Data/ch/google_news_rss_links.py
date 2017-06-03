from bs4 import BeautifulSoup as bs
import urllib.request as ur

req = ur.urlopen(ur.Request("https://www.google.com/alerts/feeds/07758061642072000886/7296220825509711713",
                 headers={"User-Agent":""}))

xml = bs(req,"xml")
flag = True
for item in xml.findAll("link"):
    while flag:
        print (dir(item))
        flag = False
        print ()
    print ("".join(item.get_attribute_list("href")))

print ("end")
