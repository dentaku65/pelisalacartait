# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para flashx
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
# Credits: DrZ3r0

import re
import time

from core import scrapertools
from core import logger
from lib.jsbeautifier.unpackers import packer


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[flashx.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    headers = [
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
        ['Accept-Encoding', 'gzip, deflate, lzma'],
        ['Connection', 'keep-alive'],
        ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8']]

    data = scrapertools.cache_page(page_url, headers=headers)

    time.sleep(5)

    post_url = re.findall('Form method="POST" action=\'(.*)\'', data)[0]
    post_selected = re.findall('Form method="POST" action=(.*)</Form>', data, re.DOTALL)[0]

    post_data = 'op=%s&usr_login=%s&id=%s&fname=%s&referer=%s&hash=%s&imhuman=Proceed+to+video' % (
        re.findall('input type="hidden" name="op" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="usr_login" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="id" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="fname" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="referer" value="(.*)"', post_selected)[0],
        re.findall('input type="hidden" name="hash" value="(.*)"', post_selected)[0])

    headers.append(['Referer', page_url])
    data = scrapertools.cache_page('http://www.flashx.tv' + post_url, post=post_data, headers=headers)

    for media_url in get_link(data):
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
        url = 'http://flashx.tv/%s.html' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'flashx'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def get_link(data):
    for match in re.finditer('(eval\(function\(p,a,c,k,e,d\).*?)</script>', data, re.DOTALL):
        js = packer.unpack(match.group(1))
        return re.findall('file\s*:\s*"([^"]+\.mp4)"', js)
