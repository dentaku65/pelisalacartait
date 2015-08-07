# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para Google Video
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
# modify by DrZ3r0

import os
import urlparse, urllib2, urllib, re

from core import scrapertools
from core import logger
from core import config


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[googlevideo.py] get_video_url(page_url='%s')" % page_url)

    print page_url

    video_urls = [["[googlevideo]", page_url]]

    for video_url in video_urls:
        logger.info("[googlevideo.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra v�deos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"""(https?://(?:redirector\.)?googlevideo.com/[^"']+)(?:",\s*"label":\s*([0-9]+),)?"""
    logger.info("[googlevideo.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        titulo = "[googlevideo]" if match.group(2) is None else "[googlevideo %s]" % match.group(2)
        url = match.group(1)

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'googlevideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
