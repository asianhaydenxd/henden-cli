#!/usr/bin/env python3
import asyncio
import discord
import os
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from getch import Getch
from colorama import Fore

bot = commands.Bot(command_prefix = 'hb ')

getch = Getch()
menu = 'guilds'
guild = channel = None
scroll = 0
messages = []
cache_history = []

def load_guilds():
    global guild
    try:
        selection = bot.guilds.index(guild)
    except ValueError:
        selection = -1

    guild_scroll = 0

    while True:
        if selection < 0:
            selection = len(bot.guilds) - 1
        if selection >= len(bot.guilds):
            selection = 0
        
        if selection < guild_scroll:
            guild_scroll = selection
        if selection > guild_scroll + 10:
            guild_scroll = selection - 10
            
        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        print(f'{Fore.GREEN}? Select server {Fore.RESET}({selection+1}/{len(bot.guilds)})\n')
        for i, guild in enumerate(bot.guilds):
            if i < guild_scroll or i > guild_scroll + 10:
                continue
                
            if selection == i:
                print(Fore.BLUE + '> ' + guild.name + Fore.RESET)
            else:
                print('  ' + guild.name)

        input_char = getch.impl()

        if input_char == 'd':
            return bot.guilds[selection], 'channels'

        if input_char == 'w':
            selection -= 1
        if input_char == 's':
            selection += 1

def load_channels(guild):
    global channel
    try:
        selection = guild.text_channels.index(channel)
    except ValueError:
        selection = -1

    channel_scroll = 0

    while True:
        if selection < 0:
            selection = len(guild.text_channels) - 1
        if selection >= len(guild.text_channels):
            selection = 0
        
        if selection < channel_scroll:
            channel_scroll = selection
        if selection > channel_scroll + 10:
            channel_scroll = selection - 10

        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        print(f'{Fore.GREEN}? Select channel {Fore.RESET}({selection+1}/{len(guild.text_channels)})\n')
        for i, channel in enumerate(guild.text_channels):
            if i < channel_scroll or i > channel_scroll + 10:
                continue
            
            if selection == i:
                print(Fore.BLUE + '> ' + channel.name + Fore.RESET)
            else:
                print('  ' + channel.name)

        input_char = getch.impl()

        if input_char == 'd':
            return guild.text_channels[selection], 'messaging'
        if input_char == 'a':
            return guild.text_channels[selection], 'guilds'

        if input_char == 'w':
            selection -= 1
        if input_char == 's':
            selection += 1

def load_msgs(messages, channel, notif=None):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
    print(f'\r{Fore.YELLOW}Chatting in{Fore.RESET}: {channel.guild.name}{Fore.YELLOW}/{Fore.RESET}{channel.name}')

    if notif:
        print(f'\r{Fore.GREEN}! {notif.guild.name}{Fore.YELLOW}/{Fore.GREEN}{notif.channel.name} {notif.author.name}: {Fore.YELLOW}{notif.content}{Fore.RESET}')
    else:
        print('\r')

    for message in reversed(messages[scroll:scroll+10]):
        print(f'\r{Fore.LIGHTBLACK_EX}[{message.created_at}] {Fore.BLUE}{message.author.name}{Fore.RESET}: {message.content}')
    
    print('\r')

@bot.event
async def on_ready():
    print('Initiated HaydBot')

    global menu, guild, channel, scroll, cache_history
    while True:
        if menu == 'guilds':
            guild, menu = load_guilds()
        if menu == 'channels':
            channel, menu = load_channels(guild)
            scroll = 0
            cache_history = await channel.history().flatten()
        elif menu == 'messaging':
            load_msgs(cache_history, channel)
            input_char = await agetch()
            if input_char == 'q':
                await bot.close()
                break
            elif input_char == 'a':
                menu = 'channels'
            elif input_char == 'w':
                scroll += 1
            elif input_char == 's':
                scroll -= 1
                if scroll <= 0: scroll = 0
            elif input_char == 't':
                menu = 'typing'
                print(f'\r {Fore.BLUE}>{Fore.RESET} ', end='')
                input_text = await ainput()
                menu = 'messaging'
                if input_text: await channel.send(input_text)

@bot.event
async def on_message(message):
    global menu, guild, scroll, cache_history
    if menu == 'messaging':
        if message.channel == channel:
            if scroll > 0: scroll += 1
            cache_history = await channel.history().flatten()
            load_msgs(cache_history, channel)
        else:
            load_msgs(cache_history, channel, notif=message)

async def ainput() -> str:
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input)).rstrip()

async def agetch() -> str:
    with ThreadPoolExecutor(1, 'agetch') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, getch.impl)).rstrip()

def main():
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()