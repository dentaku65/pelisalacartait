# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for exashare.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re
import time

from core import scrapertools
from core import logger

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate, lzma'],
    ['Connection', 'keep-alive'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8']]


def test_video_exists(page_url):
    logger.info("[exashare.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url, headers=headers)

    if re.search("""File Not Found""", data):
        return False, 'File Not Found or Removed.'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[exashare.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url, headers=headers)

    time.sleep(10)

    post_url = re.findall('form method="POST" action=\'(.*)\'', data)[0]
    post_selected = re.findall('form method="POST" action=(.*)</Form>', data, re.DOTALL)[0]

    post_data = 'op=%s&usr_login=%s&id=%s&fname=%s&referer=%s&hash=%s&imhuman=Proceed+to+video' % (
        re.findall('input type="hidden" name="op" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="usr_login" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="id" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="fname" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="referer" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="hash" value="(.*)"', post_selected)[0])

    headers.append(['Referer', page_url])
    data = scrapertools.cache_page(post_url, post=post_data, headers=headers)

    # URL del vídeo
    url = re.findall('file:\s*"([^"]+)"', data)[0]

    video_urls.append([".mp4" + " [exashare]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = 'http://(?:www.)?exashare.com/(?:embed\-)?([0-9A-Za-z]+)(?:\-[0-9]+x[0-9]+.html)?'
    logger.info("[exashare.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[exashare]"
        url = 'http://www.exashare.com/%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'exashare'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
