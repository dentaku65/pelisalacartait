# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import sys

from core import config
from core import logger
from core.item import Item
from core import scrapertools

CHANNELNAME = "buscador"

logger.info("[buscador.py] init")



DEBUG = True

def mainlist(params,url="",category=""):
    logger.info("[buscador.py] mainlist")

    listar_busquedas(params,url,category)

def searchresults(params,url="",category=""):
    import xbmc
    import xbmcgui
    import xbmcplugin
    from platformcode.xbmc import xbmctools

    logger.info("[buscador.py] searchresults")
    salvar_busquedas(params,url,category)
    if url == "" and category == "":
        tecleado = params.url
    else:
        tecleado = url
    tecleado = tecleado.replace(" ", "+")

    # Lanza las busquedas
    matches = []
    itemlist = do_search_results(tecleado)
    for item in itemlist:
        targetchannel = item.channel
        action = item.action
        category = category
        scrapedtitle = item.title+" ["+item.channel+"]"
        scrapedurl = item.url
        scrapedthumbnail = item.thumbnail
        scrapedplot = item.plot

        xbmctools.addnewfolder( targetchannel , action , category , scrapedtitle , scrapedurl , scrapedthumbnail, scrapedplot, show=item.show )

    # Cierra el directorio
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def do_search_results(tecleado):
    itemlist = []

    import os
    import glob
    import imp
    import xbmcgui
    
    progreso =xbmcgui.DialogProgressBG()

    tecleado2=tecleado.replace('+',' ').lower()
    progreso.create("Buscando "+ tecleado2.title())

    #Fichero de canales a excluir de la busqueda
    direxcludefile= os.path.join(config.get_runtime_path() ,'pelisalacarta', 'escludi.txt')
    path = os.path.join(config.get_runtime_path() ,'pelisalacarta', 'channels', '*.py')
    excluir=[]
    fileexclude = open(direxcludefile ,"r")
    excluir= fileexclude.read()
    fileexclude.close()
    #Para todos los canales que existan en el directorio canales y que no esten en el fichero de exclusion se llama al metodo search del canal
    channels = glob.glob(path)
    nchannels = len(channels)
    #try:
    for cn, infile in enumerate(channels):
        percentage=cn*100/nchannels
        basename = (os.path.basename(infile))[:-3]
        if basename not in excluir:
            logger.info("[buscador.py] do_search_results, Buscando en " +   basename + " de "+ tecleado)
            progreso.update (percentage, ' Sto cercando ' + tecleado2.title()+ ' su ' + basename.upper())
            try:
                obj = imp.load_source(basename, infile)
                itemlist.extend( obj.search( Item() , tecleado) )
                del obj
            except:
                for line in sys.exc_info():
                    logger.error( "%s" % line )
        else:
            logger.info("[buscador.py] do_search_results, Excluido server " + basename)
        #El valor solo se actualiza en debug , ¿como se recuperan los eventos pendientes de gui?
        #Cambio la busqueda a bakgroud 
        #if progreso.iscanceled(): break

    progreso.close()

    #Elimina elementos  sobrantes
    found = 0
    notfound = 0
    borrar = []
    for cn,it in enumerate(itemlist):
        encontrado= it.title.lower()
        if tecleado2 in encontrado:
            found +=1
        else:
            logger.info("[buscador.py]do_search_results %s no encontrado en %s - Ignorado proporcionado por %s" % (tecleado,encontrado, it.channel ))
            borrar.append(cn)
            notfound +=1

    borrar.sort(reverse=True)
    for i in borrar:
        del itemlist[i]

    logger.info("[[buscador.py]do_search_results Encontrados %s coincidencias para %s de %s elementos %s eliminados" % (found, tecleado2, cn +1, notfound))
    #Ordena y envía
    itemlist.sort(key=lambda item: item.channel.strip())


    return itemlist

def salvar_busquedas(params,url="",category=""):
    if url == "" and category == "":
        channel = params.channel
        url = params.url
    else:
        channel = params.get("channel")
    limite_busquedas = ( 10, 20, 30, 40, )[ int( config.get_setting( "limite_busquedas" ) ) ]
    matches = []
    try:
        presets = config.get_setting("presets_buscados")
        if "|" in presets:
            presets = matches = presets.split("|")
            for count, preset in enumerate( presets ):
                if url in preset:
                    del presets[ count ]
                    break

        if len( presets ) >= limite_busquedas:
            presets = presets[ : limite_busquedas - 1 ]
    except:
        presets = ""
    presets2 = ""
    if len(matches)>0:
        for preset in presets:
            presets2 = presets2 + "|" + preset
        presets = url + presets2
    elif presets != "":
        presets = url + "|" + presets
    else:
        presets = url
    config.set_setting("presets_buscados",presets)
    # refresh container so items is changed
    #xbmc.executebuiltin( "Container.Refresh" )

def listar_busquedas(params,url="",category=""):
    import xbmc
    import xbmcgui
    import xbmcplugin

    from platformcode.xbmc import xbmctools
    #print "category :" +category
    if url == "" and category == "":
        channel_preset = params.channel
        accion = params.action
        category = "Buscador_Generico"
    else:
        channel_preset = params.get("channel")
        accion = params.get("action")
        category = "Buscador_Normal"
    #print "listar_busquedas()"
    channel2 = ""
    itemlist=[]
    # Despliega las busquedas anteriormente guardadas
    try:
        presets = config.get_setting("presets_buscados")

        if channel_preset != CHANNELNAME:
            channel2 = channel_preset
        logger.info("channel_preset :%s" %channel_preset)

        matches = ""
        if "|" in presets:
            matches = presets.split("|")
            itemlist.append( Item(channel="buscador" , action="por_teclado"  , title=config.get_localized_string(30103)+"..."  , url=matches[0] ,thumbnail="" , plot=channel2, category = category , context = 1 ))
            #addfolder( "buscador"   , config.get_localized_string(30103)+"..." , matches[0] , "por_teclado", channel2 ) # Buscar
        else:
            itemlist.append( Item(channel="buscador" , action="por_teclado"  ,  title=config.get_localized_string(30103)+"..." ,   url="" ,thumbnail="" , plot=channel2 , category = category , context = 0 ))
            #addfolder( "buscador"   , config.get_localized_string(30103)+"..." , "" , "por_teclado", channel2 )
        if len(matches)>0:
            for match in matches:

                title=scrapedurl = match
                itemlist.append( Item(channel=channel_preset , action="searchresults"  , title=title ,  url=scrapedurl, thumbnail="" , plot="" , category = category ,  context=1 ))
                #addfolder( channel_preset , title , scrapedurl , "searchresults" )
        elif presets != "":

            title = scrapedurl = presets
            itemlist.append( Item(channel=channel_preset , action="searchresults"  , title=title ,  url=scrapedurl, thumbnail= "" , plot="" , category = category , context = 1 ))
            #addfolder( channel_preset , title , scrapedurl , "searchresults" )
    except:
        itemlist.append( Item(channel="buscador" , action="por_teclado"  , title=config.get_localized_string(30103)+"..." ,  url="", thumbnail="" , plot=channel2 , category = category ,  context = 0  ))
        #addfolder( "buscador"   , config.get_localized_string(30103)+"..." , "" , "por_teclado" , channel2 )

    if url=="" and category=="Buscador_Generico":

        return itemlist
    else:
        for item in itemlist:
            channel = item.channel
            action = item.action
            category = category
            scrapedtitle = item.title
            scrapedurl = item.url
            scrapedthumbnail = item.thumbnail
            scrapedplot = item.plot
            extra=item.extra
            context = item.context
            xbmctools.addnewfolderextra( channel , action , category , scrapedtitle , scrapedurl , scrapedthumbnail, scrapedplot , extradata = extra , context = context)

        # Cierra el directorio
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def borrar_busqueda(params,url="",category=""):
    import xbmc
    import xbmcgui
    import xbmcplugin

    from platformcode.xbmc import xbmctools
    if url == "" and category == "":
        channel = params.channel
        url = params.url
    else:
        channel = params.get("channel")

    matches = []
    try:
        presets = config.get_setting("presets_buscados")
        if "|" in presets:
            presets = matches = presets.split("|")
            for count, preset in enumerate( presets ):
                if url in preset:
                    del presets[ count ]
                    break
        elif presets == url:
            presets = ""

    except:
        presets = ""
    if len(matches)>1:
        presets2 = ""
        c = 0
        barra = ""
        for preset in presets:
            if c>0:
                barra = "|"
            presets2 =  presets2 + barra + preset
            c +=1
        presets = presets2
    elif len(matches) == 1:
        presets = presets[0]
    config.set_setting("presets_buscados",presets)
    # refresh container so item is removed
    xbmc.executebuiltin( "Container.Refresh" )

def teclado(default="", heading="", hidden=False):
    import xbmc
    import xbmcgui
    import xbmcplugin

    from platformcode.xbmc import xbmctools
    logger.info("[buscador.py] teclado")
    tecleado = ""
    keyboard = xbmc.Keyboard(default)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        tecleado = keyboard.getText()
        if len(tecleado)<=0:
            return

    return tecleado

def por_teclado(params,url="",category=""):
    logger.info("[buscador.py] por_teclado")
    logger.info("category :"+category+" url :"+url)
    if category == "" or category == "Buscador_Generico":

        channel  = params.channel
        tecleado = teclado(params.url)
        if len(tecleado)<=0:
            return
        if params.plot:
            channel = params.plot
            exec "import pelisalacarta.channels."+channel+" as plugin"
        else:
            exec "import pelisalacarta."+channel+" as plugin"


        params.url = tecleado
        itemlist = plugin.searchresults(params)
        return itemlist
    else:
        channel  = params.get("channel")
        tecleado = teclado(url)
        if len(tecleado)<=0:
            return
        if params.get("plot"):
            channel = params.get("plot")
            exec "import pelisalacarta.channels."+channel+" as plugin"
        else:
            exec "import pelisalacarta."+channel+" as plugin"

        url = tecleado
        plugin.searchresults(params, url, category)

def addfolder( canal , nombre , url , accion , channel2 = "" ):
    import xbmc
    import xbmcgui
    import xbmcplugin

    from platformcode.xbmc import xbmctools
    logger.info('[buscador.py] addfolder( "'+nombre+'" , "' + url + '" , "'+accion+'")"')
    listitem = xbmcgui.ListItem( nombre , iconImage="DefaultFolder.png")
    itemurl = '%s?channel=%s&action=%s&category=%s&url=%s&channel2=%s' % ( sys.argv[ 0 ] , canal , accion , urllib.quote_plus(nombre) , urllib.quote_plus(url),channel2 )


    if accion != "por_teclado":
        contextCommands = []
        DeleteCommand = "XBMC.RunPlugin(%s?channel=buscador&action=borrar_busqueda&title=%s&url=%s)" % ( sys.argv[ 0 ]  ,  urllib.quote_plus( nombre ) , urllib.quote_plus( url ) )
        contextCommands.append((config.get_localized_string( 30300 ),DeleteCommand))
        listitem.addContextMenuItems ( contextCommands, replaceItems=False)

    xbmcplugin.addDirectoryItem( handle = int( sys.argv[ 1 ] ), url = itemurl , listitem=listitem, isFolder=True)
