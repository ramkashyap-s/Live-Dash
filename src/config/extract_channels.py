# from bs4 import BeautifulSoup as bs
from lxml import etree
import pickle
import os
import urllib

curr_path = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(curr_path, 'TopChannelsTwitch.html')


with open(my_file, "r") as f:
    page = f.read()
    data = etree.HTML(page)
    anchor = data.xpath('//a[@data-test-selector="preview-card-titles__primary-link"]')
    channels = [item.attrib["href"].replace("https://www.twitch.tv/", "") for item in anchor]
    file = 'channel_list.txt'
    with open(file, 'wb') as channel_list_file:
        pickle.dump(channels, channel_list_file)



