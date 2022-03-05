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
messages = []

def load_guilds():
    global guild
    try:
        selection = bot.guilds.index(guild)
    except ValueError:
        selection = -1

    while True:
        if selection < 0:
            selection = len(bot.guilds) - 1
        if selection >= len(bot.guilds):
            selection = 0
            
        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        for i, guild in enumerate(bot.guilds):
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

    while True:
        if selection < 0:
            selection = len(guild.text_channels) - 1
        if selection >= len(guild.text_channels):
            selection = 0

        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        for i, channel in enumerate(guild.text_channels):
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

def load_msgs(messages, guild, channel):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
    print(f'{Fore.YELLOW}Chatting in{Fore.RESET}: {guild.name}{Fore.YELLOW}/{Fore.RESET}{channel.name}\n')
    for message in reversed(messages):
        print(f'{Fore.BLUE}{message.author.name}{Fore.RESET}: {message.content}')
    print(f'\n {Fore.BLUE}>{Fore.RESET} ', end='')

@bot.event
async def on_ready():
    print('Initiated HaydBot')

    global menu, guild, channel
    while True:
        if menu == 'guilds':
            guild, menu = load_guilds()
        if menu == 'channels':
            channel, menu = load_channels(guild)
        elif menu == 'messaging':
            load_msgs(await channel.history(limit=10).flatten(), guild, channel)
            input_text = await ainput('')
            if input_text[0] == '\\':
                args = input_text[1:].split()
                if args[0] == 'q':
                    await bot.close()
                    break
                if args[0] == 'l':
                    menu = 'channels'
                    continue
            await channel.send(input_text)

@bot.event
async def on_message(message):
    global menu, guild
    if menu == 'messaging':
        load_msgs(await channel.history(limit=10).flatten(), guild, channel)

async def ainput(prompt: str = '') -> str:
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()

def main():
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()