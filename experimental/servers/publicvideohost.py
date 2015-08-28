# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for publicvideohost.org
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re

from core import scrapertools
from core import logger


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[publicvideohost.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    # URL del vídeo
    for url in re.findall(r'playlist: \[\{\s*file: "([^"]+)",', data, re.DOTALL):
        video_urls.append([".flv" + " [publicvideohost]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = r'//(?:www.|embed.)?publicvideohost.org/v.php\?.*?v=(\d+)'
    logger.info("[publicvideohost.py] find_videos #" + patronvideos + "#")
    
    matches = re.compile(patronvideos).findall(text)

    for media_id in matches:
        titulo = "[publicvideohost]"
        url = 'http://publicvideohost.org/v.php?v=%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'publicvideohost'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
