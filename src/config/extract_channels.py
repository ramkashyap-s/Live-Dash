# from bs4 import BeautifulSoup as bs
from lxml import etree
import pickle


url='TopChannelsTwitch.html'

with open(url, "r") as f:
    page = f.read()
    data = etree.HTML(page)
    anchor = data.xpath('//a[@data-test-selector="preview-card-titles__primary-link"]')
    channels = [item.attrib["href"].replace("https://www.twitch.tv/", "") for item in anchor]
    file = 'channel_list.txt'
    with open(file, 'wb') as channel_list_file:
        pickle.dump(channels, channel_list_file)



