# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for abysstream.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by be4t5
# ------------------------------------------------------------

import urlparse, urllib2, urllib, re
import os

from core import scrapertools
from core import logger
from core import config
from lib import mechanize


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[abysstream.py] url=" + page_url)
    video_urls = []

    br = mechanize.Browser()
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_robots(False)

    r = br.open(page_url)

    url = "../viewvideo.php"
    req = br.click_link(url=url)
    data = br.open(req)
    data = data.read()

    # URL 
    url = scrapertools.find_single_match(data, '<source src="([^"]+)" type="video/mp4"')
    logger.info("url=" + url)

    # URL del vídeo
    video_urls.append([".mp4" + " [Abysstream]", url])

    for video_url in video_urls:
        logger.info("[abysstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://abysstream.net/v/iwbe6genso37
    patronvideos = 'http://abysstream.com/videos/([A-Za-z0-9]+)'
    logger.info("[abysstream.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[Abysstream]"
        url = "http://abysstream.com/videos/" + match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'abysstream'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    # http://cineblog01.pw/HR/go.php?id=6475
    temp = text.split('<strong>Streaming')
    if len(temp) > 1:
        tem = temp[1].split('Download')
        patronvideos = '(?:HR)/go.php\?id\=([a-zA-Z0-9]+)'
        matches = re.compile(patronvideos, re.DOTALL).findall(tem[0])
    else:
        matches = []

    br = mechanize.Browser()
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_robots(False)
    page = scrapertools.find_single_match(text, 'rel="canonical" href="([^"]+)"')

    for match in matches:
        titulo = "[Abysstream]"
        url = "http://cineblog01.pw/HR/go.php?id=%s" % match
        r = br.open(page)
        req = br.click_link(url=url)
        data = br.open(req)
        data = data.read()
        vid = scrapertools.find_single_match(data, 'http://abysstream.com/videos/([^"]+)"?')
        url = "http://abysstream.com/videos/%s" % vid
        if url not in encontrados and vid != "":
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'abysstream'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def test():
    video_urls = get_video_url("http://abysstream.com/videos/ub4ztmqe57l8")

    return len(video_urls) > 0
