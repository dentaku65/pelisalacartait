# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para backin.net
# by be4t5
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
# modify by Robalo, DrZ3r0

import urlparse, urllib2, urllib, re
import os

from core import scrapertools
from core import logger
from core import config


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[backin.py] url=" + page_url)
    video_urls = []

    # First access
    data = scrapertools.cache_page( page_url )
    logger.info("data=" + data)

    # URL 
    url = scrapertools.find_single_match( data, 'window.pddurl="([^"]+)"' )
    logger.info("url=" + url)

    # URL del vídeo
    video_urls.append([".mp4" + " [backin]", url])

    for video_url in video_urls:
        logger.info("[backin.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://backin.net/iwbe6genso37
    patronvideos = 'backin[^/]+/([A-Za-z0-9]+)'
    logger.info("[backin.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[backin]"
        url = "http://backin.net/0down/downloader2.php?f=" + match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'backin'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    # http://cineblog01.pw/HR/go.php?id=6475
    temp = text.split('<strong>Streaming')
    if len(temp) > 1:
        tem = temp[1].split('Download')
        patronvideos = '(?:HR)/go.php\?id\=([a-zA-Z0-9]+)'
        logger.info("[backin.py] find_videos #" + patronvideos + "#")
        matches = re.compile(patronvideos, re.DOTALL).findall(tem[0])
    else:
        matches = []
    page = scrapertools.find_single_match(text, 'rel="canonical" href="([^"]+)"')
    from lib import mechanize
    br = mechanize.Browser()
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_robots(False)

    for match in matches:
        titulo = "[backin]"
        url = "http://cineblog01.pw/HR/go.php?id=" + match
        r = br.open(page)
        req = br.click_link(url=url)
        data = br.open(req)
        data = data.read()
        vid = scrapertools.find_single_match(data, 'http://backin.net/([^"]+)"')
        url = "http://backin.net/0down/downloader2.php?f=" + vid
        if url not in encontrados and vid != "":
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'backin'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    # http://vcrypt.net/sb/0a8hqibleus5
    # Filmpertutti.eu
    tem = text.split('<p><strong>Download:<br />')
    patronvideos = 'http://vcrypt.net/sb/([^"]+)'
    matches = re.compile(patronvideos, re.DOTALL).findall(tem[0])
    page = scrapertools.find_single_match(text, 'rel="canonical" href="([^"]+)"')

    for match in matches:
        titulo = "[backin]"
        url = "http://vcrypt.net/sb/" + match
        r = br.open(url)
        data = r.read()
        vid = scrapertools.find_single_match(data, '/streams-([^"]+)-')
        url = "http://backin.net/0down/downloader2.php?f=" + vid
        if url not in encontrados and vid != "":
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'backin'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def test():
    video_urls = get_video_url("http://backin.net/6pggedui2euj")

    return len(video_urls) > 0
