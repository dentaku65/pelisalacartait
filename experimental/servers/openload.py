# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.io
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import urlparse, urllib2, urllib, re
import os

from core import scrapertools
from core import logger
from core import config


def test_video_exists(page_url):
    logger.info("[openload.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if 'We are sorry!' in data:
        return False, 'File Not Found or Removed.'

    match = re.search(r"""<source\s+type=(?:"|')video/mp4(?:"|')\s+src=(?:"|')(?:[^"']+)""", data, re.DOTALL)
    if match:
        return True, ""

    match = re.search('attr\s*\(\s*"src"\s*,\s*"([^"]+)', data, re.DOTALL)
    if match:
        return True, ""

    return False, 'Unable to resolve openload.io link. Filelink not found.'


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[openload.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    # URL del vídeo
    match = re.search(r"""<source\s+type=(?:"|')video/mp4(?:"|')\s+src=(?:"|')([^"']+)""", data, re.DOTALL)
    if not match:
        match = re.search('attr\s*\(\s*"src"\s*,\s*"([^"]+)', data, re.DOTALL)

    url = match.group(1).replace(r"\/", "/")
    video_urls.append([".mp4" + " [Openload]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '//(?:www.)?openload\.io/(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("[openload.py] find_videos #" + patronvideos + "#")
    
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[Openload]"
        url = 'http://openload.io/embed/%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'openload'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
