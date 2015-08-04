# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for videowood.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import urlparse, urllib2, urllib, re
import os

from core import scrapertools
from core import logger
from core import config


def test_video_exists(page_url):
    logger.info("[videowood.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video doesn't exist." in data:
        return False, 'The requested video was not found.'

    pattern = "file\s*:\s*'[^']+/video/[^']+"
    match = re.search(pattern, data, re.DOTALL)
    if match:
        return True, ""

    return False, 'No video link found.'


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[videowood.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    # URL del vídeo
    pattern = "file\s*:\s*'([^']+/video/[^']+)"
    match = re.search(pattern, data, re.DOTALL)

    url = match.group(1)
    video_urls.append([".mp4" + " [Videowood]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = r"https?://(?:www.)?videowood.tv/(?:embed/|video/)[0-9a-z]+"
    logger.info("[videowood.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for url in matches:
        titulo = "[Videowood]"
        url = url.replace('/video/', '/embed/')
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'videowood'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
