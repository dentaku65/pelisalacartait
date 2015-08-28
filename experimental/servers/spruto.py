# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for spruto.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re

from core import scrapertools
from core import logger


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[spruto.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    # URL del vídeo
    for url in re.findall(r'file: "(.*?\.mp4)"', data):
        video_urls.append([".mp4" + " [spruto]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = r'//(?:www.)?spruto.tv/iframe_embed.php\?video_id=(\d+)'
    logger.info("[spruto.py] find_videos #" + patronvideos + "#")
    
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[spruto]"
        url = 'http://www.spruto.tv/iframe_embed.php?video_id=%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'spruto'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    patronvideos = r'//(?:www.)?spruto.tv/videos/(\d+)'
    logger.info("[spruto.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[spruto]"
        url = 'http://www.spruto.tv/iframe_embed.php?video_id=%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'spruto'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
