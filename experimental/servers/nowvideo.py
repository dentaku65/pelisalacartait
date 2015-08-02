# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para nowvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
# Credits:
# Unwise and main algorithm taken from Eldorado url resolver
# https://github.com/Eldorados/script.module.urlresolver/blob/master/lib/urlresolver/plugins/nowvideo.py

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import unwise

USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"

def test_video_exists( page_url ):
    logger.info("[nowvideo.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    
    if "The file is being converted" in data:
        return False,"El fichero está en proceso"

    if "no longer exists" in data:
        return False,"El fichero ha sido borrado"

    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[nowvideo.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []
    
    video_id = scrapertools.get_match(page_url,"http://www.nowvideo.../video/([a-z0-9]+)")

    if premium:
        # Lee la página de login
        login_url = "http://www.nowvideo.eu/login.php"
        data = scrapertools.cache_page( login_url )

        # Hace el login
        login_url = "http://www.nowvideo.eu/login.php?return="
        post = "user="+user+"&pass="+password+"&register=Login"
        headers=[]
        headers.append(["User-Agent",USER_AGENT])
        headers.append(["Referer","http://www.nowvideo.eu/login.php"])
        data = scrapertools.cache_page( login_url , post=post, headers=headers )

        # Descarga la página del vídeo 
        data = scrapertools.cache_page( page_url )
        logger.debug("data:" + data)
        
        # URL a invocar: http://www.nowvideo.eu/api/player.api.php?user=aaa&file=rxnwy9ku2nwx7&pass=bbb&cid=1&cid2=undefined&key=83%2E46%2E246%2E226%2Dc7e707c6e20a730c563e349d2333e788&cid3=undefined
        # En la página:
        '''
        flashvars.domain="http://www.nowvideo.eu";
        flashvars.file="rxnwy9ku2nwx7";
        flashvars.filekey="83.46.246.226-c7e707c6e20a730c563e349d2333e788";
        flashvars.advURL="0";
        flashvars.autoplay="false";
        flashvars.cid="1";
        flashvars.user="aaa";
        flashvars.key="bbb";
        flashvars.type="1";
        '''
        flashvar_file = scrapertools.get_match(data,'flashvars.file="([^"]+)"')
        flashvar_filekey = scrapertools.get_match(data,'flashvars.filekey=([^;]+);')
        flashvar_filekey = scrapertools.get_match(data,'var '+flashvar_filekey+'="([^"]+)"')
        flashvar_user = scrapertools.get_match(data,'flashvars.user="([^"]+)"')
        flashvar_key = scrapertools.get_match(data,'flashvars.key="([^"]+)"')
        flashvar_type = scrapertools.get_match(data,'flashvars.type="([^"]+)"')

        #http://www.nowvideo.eu/api/player.api.php?user=aaa&file=rxnwy9ku2nwx7&pass=bbb&cid=1&cid2=undefined&key=83%2E46%2E246%2E226%2Dc7e707c6e20a730c563e349d2333e788&cid3=undefined
        url = "http://www.nowvideo.eu/api/player.api.php?user="+flashvar_user+"&file="+flashvar_file+"&pass="+flashvar_key+"&cid=1&cid2=undefined&key="+flashvar_filekey.replace(".","%2E").replace("-","%2D")+"&cid3=undefined"
        data = scrapertools.cache_page( url )
        logger.info("data="+data)
        
        location = scrapertools.get_match(data,'url=([^\&]+)&')
        location = location + "?client=FLASH"

        video_urls.append( [ scrapertools.get_filename_from_url(location)[-4:] + " [premium][nowvideo]",location ] )

    else:

        data = scrapertools.cache_page( page_url )

        flashvar_filekey = scrapertools.get_match( data, 'flashvars.filekey=([^;]+);' )
        filekey = scrapertools.get_match( data,'var '+ flashvar_filekey + '="([^"]+)"' )

        #get stream url from api

        url = 'http://www.nowvideo.sx/api/player.api.php?key=%s&file=%s' % ( filekey.replace(".","%2E").replace("-","%2D"), video_id )
        data = scrapertools.cache_page( url )

        print "##### data 1 ## %s ##" % data

        data = scrapertools.get_match( data, 'url=([^\&]+)&' )
        res = scrapertools.get_header_from_response( url, header_to_get="content-type" )
        if res == "text/html":
            data = urllib.quote_plus( data )
            url = 'http://www.nowvideo.sx/api/player.api.php?cid3=undefined&numOfErrors=1&user=undefined&errorUrl=' + data.replace( ".", "%2E" ) + '&pass=undefined&errorCode=404&cid=1&cid2=undefined&file=' + video_id + '&key=' + filekey.replace( ".", "%2E" ).replace( "-", "%2D" )
            data = scrapertools.cache_page( url )
            try:
                data = scrapertools.get_match( data, 'url=([^\&]+)&' )
            except:
                url = 'http://www.nowvideo.sx/api/player.api.php?key=%s&file=%s' % ( filekey.replace(".","%2E").replace("-","%2D"), video_id )
                data = scrapertools.cache_page( url )
                data = scrapertools.get_match( data, 'url=([^\&]+)&' )

        media_url = data

        video_urls.append( [ scrapertools.get_filename_from_url( media_url )[-4:] + " [nowvideo]", media_url ] )
		


	return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []


    #http://www.nowvideo.eu/video/4fd0757fd4592
    #serie tv cineblog
    page = scrapertools.find_single_match(data,'canonical" href="http://www.cb01.tv/serietv/([^"]+)"')
    page2 = scrapertools.find_single_match(data,'title">Telef([^"]+)</span>')
    page3 = scrapertools.find_single_match(data,'content="http://www.piratestreaming.../serietv/([^"]+)"')
    patronvideos  = 'nowvideo.../video/([a-z0-9]+)'
    logger.info("[nowvideo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[nowvideo]"
        url = "http://www.nowvideo.sx/video/"+match
        d = scrapertools.cache_page(url)
        ma = scrapertools.find_single_match(d,'(?<=<h4>)([^<]+)(?=</h4>)')
        ma=titulo+" "+ma
        if url not in encontrados:
            logger.info("  url="+url)
            if page != "" or page2 != "" or page3 != "":
                devuelve.append( [ ma , url , 'nowvideo' ] )
            else:
                devuelve.append( [ titulo , url , 'nowvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

		

    #http://www.player3k.info/nowvideo/?id=t1hkrf1bnf2ek
    patronvideos  = 'player3k.info/nowvideo/\?id\=([a-z0-9]+)'
    logger.info("[nowvideo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[nowvideo]"
        url = "http://www.nowvideo.sx/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'nowvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://embed.nowvideo.eu/embed.php?v=obkqt27q712s9&amp;width=600&amp;height=480
    #http://embed.nowvideo.eu/embed.php?v=4grxvdgzh9fdw&width=568&height=340
    patronvideos  = 'nowvideo.../embed.php\?v\=([a-z0-9]+)'
    logger.info("[nowvideo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[nowvideo]"
        url = "http://www.nowvideo.sx/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'nowvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://embed.nowvideo.eu/embed.php?width=600&amp;height=480&amp;v=9fb588463b2c8
    patronvideos  = 'nowvideo.../embed.php\?.+?v\=([a-z0-9]+)'
    logger.info("[nowvideo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[nowvideo]"
        url = "http://www.nowvideo.sx/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'nowvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

#Cineblog by be4t5
    patronvideos  = '<a href="http://cineblog01.../HR/go.php\?id\=([0-9]+)'
    logger.info("[nowvideo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    page = scrapertools.find_single_match(data,'rel="canonical" href="([^"]+)"')
    from lib import mechanize
    br = mechanize.Browser()
    br.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0')]
    br.set_handle_robots(False)

    for match in matches:
        titulo = "[nowvideo]"
        url = "http://cineblog01.pw/HR/go.php?id="+match
        r = br.open(page)
        req = br.click_link(url=url)
        data = br.open(req)
        data= data.read()
        data = scrapertools.find_single_match(data,'www.nowvideo.../video/([^"]+)"?')
        url = "http://www.nowvideo.sx/video/"+data
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'nowvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

      

    return devuelve

def test():

    video_urls = get_video_url("http://www.nowvideo.eu/video/xuntu4pfq0qye")

    return len(video_urls)>0
