# from bs4 import BeautifulSoup as bs
from lxml import etree


url='TopChannelsTwitch.html'

with open(url, "r") as f:
    page = f.read()
    data = etree.HTML(page)
    anchor = data.xpath('//a[@data-test-selector="preview-card-titles__primary-link"]')
    campaigns = [item.attrib["href"].replace("https://www.twitch.tv/", "") for item in anchor]
    print(str(campaigns))


