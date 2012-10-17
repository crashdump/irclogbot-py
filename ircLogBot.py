#!/usr/bin/env python
# -*- coding: utf-8 -*-

VERSION = "0.3c"

#    Adrien Pujol - crashdump.fr
#
# Un bot IRC en python qui loggue tout ce qui se passe sur un chan.
#
#    Version 0.3c (17 Oct 2012)
#      * Correction de bugs
#
#    Version 0.3 (1 Mai 2009)
#      * Enregistrement des logs au format XML
#
#    Version 0.2 (20 Avril 2009)
#      * Optimisation/Nettoyage du code
#      * Fonction twitter
#      * Rotation des logs par jours
#
#    Version 0.1 (02 Avril 2009)
#      * Ecriture du core (IRC, LOG)
#
#    TODO:
#      * Implementer des commandes basiques de controle.
#
#
# Un argument a y passer: (ce qui creera un log du nom du chan + date .log)
#   $ python ircLogBot.py leChannel
#
# 1) Réponse con:
# *Si quelqu'un dit son nom suivit d'un ":" :
#         <fo0> logbot: salut !
# *Il répond tout conement (oui, c'est un bot..) :
#         <logbot> foo: Je suis un bot, notre conversation risque d'être très limitée..
#
# 2) Log bot:
# *Il log tout le chan dans le fichier log décrit plus haut
#
# 2) Twitter post:
# *De plus il intègre une fonction twitter, si l'owner lui dit:
#        "twitter: Bla Bla Bla" -> Envois de Bla Bla Bla sur le compte twitter configuré.
#
# Les librairies suivantes sont Necessaires:
#
#   python-twistted - Moteur IRC ()
#   python-twitter  - Connexion a twitter ()
#   python-celementtree - XML (rapide et legere, une merveille: http://effbot.org/zone/celementtree.htm)
#
# Format XML en sortie:
#
#   <?xml version="1.0" encoding="utf-8" standalone="no"?>
#   <channel id="informatique">
#	   <message>
#          <timestamp>13:40:11</timestamp>
#          <type>global/messages/action</type>
#          <username>crashdump</username>
#          <text>coucou, comment ça va ?</text>
#      </message>
#   </channel>
#

""" ------------------------- VARIABLES A CONFIGURER -------------------------------- """

# Serveur:
IRCSERVER = "irc.europnet.org"
IRCSERVERPORT = 6667

# Nicks:
BOTNICKNAME = "crashdump_"
BOTOWNERNICKNAME = "crashdump"

# Phrases types:
MSGDIRECTSEND = "Je ne suis qu un bot la conversation risque d'etre tres limitee... rejoins nous sur #informatique"
TWITMSGSENT = "Cuicui envoye avec succes"

# Identifants compte twitter:
TWITUSERNAME = "crashdumpfr"
TWITPASSWORD = "MDP"

""" ------------------------- CORE ----- NE PAS TOUCHER ----------------------------- """

# system imports
import time, sys, re, os
# charset tools
import unicodedata
# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log, logfile
# twitter imports
import twitter
# XML processor imports
import xml.etree.cElementTree as ET
# Charset treatment
import unicode2ascii as _

#-------------------------------------- LOGGING ----------------------------------------#
class MessageLogger:
    # Classe Logger:
    def __init__(self, file):
        self.file = file

    def constructXMLOutput(self, channel, logArray):
            logfile = "logs/%s.xml" % channel
        #try:
            xmlOutput = ET.parse(logfile)
            XMLLogElem = xmlOutput.getroot()
            XMLchannel = ET.Element("channel",{'id':channel})
            XMLmessage = ET.Element("message")
            XMLmessageTimestamp = ET.Element("timestamp")
            XMLmessageType = ET.Element("type")
            XMLmessageUsername = ET.Element("username")
            XMLmessageText = ET.Element("text")
            XMLmessageTimestamp.text = logArray[0].strip(' "^') # timestamp  # strip -> on s'assure qu'il
            XMLmessageType.text = logArray[1].strip(' "^')      # action             -> qu'il n'y ai pas d'espaces 
            XMLmessageUsername.text = logArray[2].strip(' "^')  # username           -> ou de char speciaux avant
            XMLmessageText.text = logArray[3].strip(' "^')      # message            -> ou après.. ça chie le XML
            XMLmessage.append(XMLmessageTimestamp)
            XMLmessage.append(XMLmessageType)
            XMLmessage.append(XMLmessageUsername)
            XMLmessage.append(XMLmessageText)
            XMLchannel.append(XMLmessage)
            XMLLogElem.append(XMLmessage)
            self.XMLIndent(XMLLogElem)                     # on met au propre l'indentation
            ET.ElementTree(XMLLogElem).write(logfile, "utf-8")
        #except:
        #    print "Erreur d'acces: %s" % sys.exc_info()[0]
    
    # gestion de l'indentation du XML
    def XMLIndent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                self.XMLIndent(e, level+1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "  "
            if not e.tail or not e.tail.strip():
                e.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
    
    # creation du log
    def log(self, user, channel, message):
        timestamp = time.strftime("%H:%M:%S", time.localtime(time.time()))
        toXMLOutput = (timestamp, "message", user.strip(), message.strip())
        print "[LOG] timestamp: %s - action: message - user: %s - message: %s" % (timestamp, user.strip(), message.strip())
        self.constructXMLOutput(channel.replace('#',''), toXMLOutput)

#-------------------------------------- THE BOT ----------------------------------------#
class LogBot(irc.IRCClient):
    # Le bot quoi..
    nickname = BOTNICKNAME
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(self.factory.channel)
        self.logger.log(self.nickname, self.factory.channel, "[Connecte a %s]" % time.asctime(time.localtime(time.time())))
    
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log(self.nickname, self.factory.channel, "[Deconnecte a %s]" % time.asctime(time.localtime(time.time())))
    
    # callbacks for events
    def signedOn(self):
        # Quand il s'est correctement connecté
        self.join(self.factory.channel)
    
    def joined(self, channel):
        # Quand le bot rejoins un chan
        self.logger.log(self.nickname, channel, "[J'ai rejoin: %s]" % channel)
    
    def privmsg(self, user, channel, msg):
        # Quand le bot reçoit un message
        user = user.split('!', 1)[0]
        if channel == BOTNICKNAME: # si msg global
            return
        self.logger.log(user, channel, _.unicode2ascii(unicode(msg, "UTF-8"))) # sinon log
        
        # Verification si on m'envois un send
        if channel == self.nickname:
            if channel == BOTNICKNAME or channel == "AUTH": # si msg global
                return
            msg = MSGDIRECTSEND
            self.msg(user, _.unicode2ascii(unicode(msg, "UTF-8")))
            return
        
        # Vérification si quelqu'un m'ecris sur le chan - reponse con
        if msg.startswith(self.nickname + ":"):
            msg = "%s: Je suis un bot tres limite intellectuellement.. " % user
            self.msg(channel, _.unicode2ascii(unicode(msg, "UTF-8")))
            self.logger.log(self.nickname, channel, _.unicode2ascii(unicode(msg, "UTF-8")))
        
        # Commandes a executer
        if user == BOTOWNERNICKNAME:
            # COMMANDE: QUITTER
            if msg.startswith("~quit"):
                msg = "Bisous, Bye !"
                self.msg(channel, msg)
                self.logger.log(self.nickname, channel, _.unicode2ascii(unicode(msg, "UTF-8")))
                # on stopper le reacteur et on quitte
                time.sleep(1)
                reactor.stop()
                sys.exit(0)
            # COMMANDE: TWITTER
            if msg.startswith("~tweet"):
                tweet = re.findall(r'"(.*?)"', _.unicode2ascii(unicode(msg, "UTF-8")))
                # Si la REGEX retourne un array tweet de 0 on note une erreur et on lui balance la syntaxe
                # en pleine gueule, sinon on envois le tout a l'API twit.
                if len(tweet) == 1:
                    api = twitter.Api(username = TWITUSERNAME, password = TWITPASSWORD)
                    status = api.PostUpdate(tweet[0])
                    self.msg(channel, "%s : %s" % (TWITMSGSENT, tweet[0]))
                    self.logger.log(self.nickname, channel, "%s : %s" % (TWITMSGSENT, tweet[0]))
                else:
                    msg = "%s: Je n'ai pas compris, la syntaxe: ~tweet \"mon texte\"" % user
                    self.msg(channel, _.unicode2ascii(unicode(msg, "UTF-8")))
                    self.logger.log(self.nickname, channel, _.unicode2ascii(unicode(msg, "UTF-8")))
            # COMMANDE: ABOIS
            if msg.startswith("~abois"):
                msg = "Wof, wof !"
                self.msg(channel, _.unicode2ascii(unicode(msg, "UTF-8")))
                self.logger.log(self.nickname, channel, _.unicode2ascii(unicode(msg, "UTF-8")))
    
    
    def action(self, user, channel, msg):
        # Quand quelqu'un affectue une action on rajoute une * en tete du msg dans le log
        user = user.split("!", 1)[0]
        self.logger.log(user, channel, _.unicode2ascii(unicode(msg, "UTF-8")))
    
    # irc callbacks
    def irc_NICK(self, prefix, params):
        # Quand quelqu'un change son pseudo
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log(self.nickname, self.factory.channel, _.unicode2ascii("%s est maintenant connu comme %s" % (old_nick, new_nick)))

#-------------------------------------- CONNEXIONS --------------------------------------#
class LogBotFct(protocol.ClientFactory):
    # Les logs.. -> nouvelle instance a construire a chaque nouvelles connexions
    protocol = LogBot
    
    def __init__(self, channel):
        self.channel = channel
        self.filename = channel
    
    def clientConnectionLost(self, connector, reason):
        # Quand on est deco, on retry
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        # Si erreur on affiche les raisons
        print "Erreur de connexion:", reason
        reactor.stop()

#-------------------------------------- MAIN --------------------------------------------#
if __name__ == "__main__":
    # arguments, aide.
    for arg in sys.argv:
        if arg in ("-h", "--help") or len(sys.argv) < 2:
            print " logBot.py version %s par Adrien Pujol - crashdump.fr" % VERSION
            print "    Syntaxe: logBot [channel]"
            print ""
            print " Options:"
            print "    -h, --help                     affiche cette aide"
            print "    -q, --quiet                    mode silencieux"
            print ""
            sys.exit()
        elif arg in ("-q", "--quiet"):
            print " Pas encore implemente, je reprend le cours des choses.."

    # on teste l'existance du fichier de log, sinon on en cree un avec la structure.
    if not os.path.isfile("logs/%s.xml" % sys.argv[1]):
        structureXML = '<channel id="informatique"> \
                            <message>\
                                <timestamp>00:00:01</timestamp>\
                                <type>global or messages or action</type> \
                                <username>User</username>\
                                <text>Message</text>\
                            </message>\
                        </channel>'
        print "Creation du fichier de log.. "
        testFileExist = open("logs/%s.xml" % sys.argv[1], "w", 0)
        testFileExist.writelines(structureXML)
        testFileExist.close()

    
    # initialisation de la classe loging
    log.startLogging(sys.stdout)
    
    # creation de la classe de connexion
    f = LogBotFct(sys.argv[1])
    
    # connection au serveur irc
    reactor.connectTCP(IRCSERVER, IRCSERVERPORT, f)
    print "Connexion a %s" % IRCSERVER
    
    # run bot
    reactor.run()
