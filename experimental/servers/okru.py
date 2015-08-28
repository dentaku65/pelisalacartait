# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for ok.ru
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re
import urllib

from core import scrapertools
from core import logger

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Connection', 'keep-alive']
]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[okru.py] url=" + page_url)
    video_urls = []

    headers.append(['Referer', page_url.split('|')[1]])

    data = scrapertools.cache_page(page_url.split('|')[0], headers=headers)

    headers.append(['X-Requested-With', 'ShockwaveFlash/99.999.999.999'])
    _headers = urllib.urlencode(dict(headers))

    # URL del vídeo
    for type, url in re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"', data, re.DOTALL):
        url = url.replace("%3B", ";").replace(r"\u0026", "&")
        url += '|' + _headers
        video_urls.append([type + " [okru]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '//(?:www.)?ok.../(?:videoembed|video)/(\d+)'
    logger.info("[okru.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[okru]"
        url = 'http://ok.ru/dk?cmd=videoPlayerMetadata&mid=%s|http://ok.ru/videoembed/%s' % (media_id, media_id)
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'okru'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
