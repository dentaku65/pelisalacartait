# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para MegaHD.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import os
import urlparse, urllib2, urllib, re

from core import scrapertools
from core import logger
from core import config


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[megahd.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    data = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if data != "":
        from lib.jsbeautifier.unpackers import packer
        data = packer.unpack(data)
        video_url = scrapertools.find_single_match(data, 'file"?\s*:\s*"([^"]+)",')
        video_urls.append(["[megahd]", video_url])

    for video_url in video_urls:
        logger.info("[megahd.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra v�deos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"""http://www.megahd.tv/(?:embed-)?([a-z0-9A-Z]+)"""
    logger.info("[megahd.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[megahd]"
        url = 'http://www.megahd.tv/embed-%s.html' % match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'megahd'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
