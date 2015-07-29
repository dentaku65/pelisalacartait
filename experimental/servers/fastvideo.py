# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para fastvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urllib,re

from core import scrapertools
from core import logger

from lib.jsbeautifier.unpackers  import packer

def test_video_exists( page_url ):
    logger.info( "[fastvideo.py] test_video_exists(page_url='%s')" % page_url )

    video_id = scrapertools.get_match( page_url, 'me/([A-Za-z0-9]+)' )
    url = 'http://www.fastvideo.me/embed-%s-607x360.html' % video_id

    data = scrapertools.cache_page( url )

    if "File was deleted from FastVideo" in data:
        return False, "The file not exists or was removed from FastVideo."

    return True, ""

def get_video_url( page_url, premium = False, user="", password="", video_password="" ):
    logger.info( "[fastvideo.py] url=" + page_url )

    video_id = scrapertools.get_match( page_url, 'me/([A-Za-z0-9]+)' )
    url = 'http://www.fastvideo.me/embed-%s-607x360.html' % video_id

    data = scrapertools.cache_page( url )

    packed = scrapertools.get_match( data, "<script type='text/javascript'>eval.function.p,a,c,k,e,.*?</script>" )
    unpacked = packer.unpack( packed )
    media_url = scrapertools.get_match( unpacked, 'file:"([^"]+)"' )

    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url( media_url )[-4:] + " [fastvideo.me]", media_url ] )

    for video_url in video_urls:
        logger.info( "[fastvideo.py] %s - %s" % ( video_url[0], video_url[1] ) )

    return video_urls

# Encuentra vídeos de este servidor en el texto pasado
def find_videos( data ):
    encontrados = set()
    devuelve = []
            
    #http://www.fastvideo.me/8fw55lppkeps
    patronvideos  = 'fastvideo.me/([A-Za-z0-9]+)'
    logger.info( "[fastvideo.py] find_videos #" + patronvideos + "#" )
    matches = re.compile( patronvideos, re.DOTALL ).findall( data )

    for match in matches:
        titulo = "[fastvideo]"
        url = "http://www.fastvideo.me/" + match
        if url not in encontrados:
            logger.info( "  url=" + url )
            devuelve.append( [ titulo ,url ,'fastvideo' ] )
            encontrados.add( url )
        else:
            logger.info( " url duplicada=" + url )

    return devuelve

def test():

    video_urls = get_video_url( "http://www.fastvideo.me/8fw55lppkeps" )

    return len( video_urls ) > 0
