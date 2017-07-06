import re
import struct
import discord
import os
import sys
import json
import urllib.request as urllib2

if os.path.isfile('config.json') == False:
    file = open('config.json', 'w+')
    sys.exit('Created Config file')
else:
    print('Config Present')

with open('config.json', 'r', encoding='utf-8') as config_file:
    config = config_file.read()
    config = json.loads(config)
    print('Loaded Config file')

token = (config['Token'])
if token == '':
    sys.exit('No Token provided')
pfx = (config['Prefix'])

Vc = (config['VChannel'])
if Vc == '':
    sys.exit('No channel id provided')

Tc = (config['TChannel'])
if Tc == '':
    print("No text channel set, channel editing disabled")

streamurl = (config['Stream'])
if streamurl == '':
    sys.exit('No Stream provided')

class IceBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.player = None
        self.voice = None

    url = streamurl  # radio stream
    encoding = 'latin1' # default: iso-8859-1 for mp3 and utf-8 for ogg streams
    request = urllib2.Request(url, headers={'Icy-MetaData': 1})  # request metadata
    response = urllib2.urlopen(request)
    metaint = int(response.headers['icy-metaint'])
    for _ in range(10): # # title may be empty initially, try several times
        response.read(metaint)  # skip to metadata
        metadata_length = struct.unpack('B', response.read(1))[0] * 16  # length byte
        metadata = response.read(metadata_length).rstrip(b'\0')
        # extract title from the metadata
        m = re.search(br"StreamTitle='([^']*)';", metadata)
        if m:
            title = m.group(1)
            nowPlayingDecode = title.decode()
            nowPlaying = nowPlayingDecode.replace("b'", "'")
        if title:
            break
    else:
        nowPlaying = "No Title Found"

    async def on_ready(self):
        await self.change_presence(game=discord.Game(name=streamurl))
        print('===========================================')
        print('IceBot 0.3 By HDR')
        print('https://github.com/MrHDR/IceBot')
        print('Logged in as', self.user.name)
        print('===========================================')
        print("")
        Vchannel = self.get_channel(Vc)
        Tchannel = self.get_channel(Tc)
        await self.join_voice_channel(Vchannel)

    async def on_message(self, message):
        if message.content.startswith(pfx + 'count'):
            counter = 0
            tmp = await self.send_message(message.channel, 'Calculating messages...')
            async for log in self.logs_from(message.channel, limit=100):
                if log.author == message.author:
                    counter += 1
            await self.edit_message(tmp, 'You have {} messages.'.format(counter))

        elif message.content.startswith(pfx + 'stream'):
            await self.send_message(message.channel, 'Now Streaming ' + streamurl)
            self.voice = self.voice_client_in(message.server)
            self.player = self.voice.create_stream_player(streamurl)
            self.player.start()

        elif message.content.startswith(pfx + "rick"):
            await self.send_message(message.channel, 'No Strangers To Love')
            self.voice = self.voice_client_in(message.server)
            self.player = self.voice.create_ffmpeg_player("rick.mp3")
            self.player.run()

bot = IceBot()
bot.run(token)
