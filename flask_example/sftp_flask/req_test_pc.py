import requests
import urllib
url = "http://localhost:5000/"
data = {"username":"user_name","password":"user_password"}
response = requests.get(url,headers={'User-Agent':'Windows'})


