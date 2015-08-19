# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para flashx
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
# Credits: DrZ3r0

import re

from core import scrapertools
from core import logger
from lib.jsbeautifier.unpackers import packer


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[flashx.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    headers = [
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
        ['Referer', page_url]]
    media_url = get_link(page_url, headers)

    if media_url is None:
        headers = [
            ['User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'],
            ['Referer', page_url]]
        media_url = get_link(page_url, headers)

    if media_url is None:
        video_urls.append([".mp4" + " [flashx]", media_url])

    for video_url in video_urls:
        logger.info("[flashx.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = '//(?:www.|play.)?flashx.tv/(?:embed-|dl\?)?([0-9a-zA-Z/-]+)'
    logger.info("[flashx.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for media_id in matches:
        titulo = "[flashx]"
        url = 'http://flashx.tv/embed-%s.html' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'flashx'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def get_link(page_url, headers):
    data = scrapertools.cache_page(page_url, headers=headers)
    for match in re.finditer('(eval\(function\(p,a,c,k,e,d\).*?)</script>', data, re.DOTALL):
        js = packer.unpack(match.group(1))
        match2 = re.search('file\s*:\s*"([^"]+(?:video|mobile)[^"]+)', js)
        if match2:
            return match2.group(1)
