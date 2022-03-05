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
    selection = 0
    while True:
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
        
        if selection < 0:
            selection = len(bot.guilds) - 1
        if selection >= len(bot.guilds):
            selection = 0

def load_channels(guild):
    selection = 0
    while True:
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
        
        if selection < 0:
            selection = len(guild.text_channels) - 1
        if selection >= len(guild.text_channels):
            selection = 0

def load_msgs(messages, guild, channel, depth):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
    display_messages = [message for message in messages if message['guild'] == guild.name and message['channel'] == channel.name][-depth:]
    
    print(f'{Fore.YELLOW}Chatting in{Fore.RESET}: {guild.name}{Fore.YELLOW}/{Fore.RESET}{channel.name}\n')
    for message in display_messages:
        print('%s: %s'%(Fore.BLUE+message['author']+Fore.RESET, message['text']))
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
            load_msgs(messages, guild, channel, 10)
            input_text = await ainput('')
            if input_text == '\\q':
                await bot.close()
                break
            await channel.send(input_text)

@bot.event
async def on_message(message):
    global menu, guild
    messages.append({'guild': message.guild.name, 'channel': message.channel.name, 'author': message.author.name, 'text': message.content})
    if menu == 'messaging':
        load_msgs(messages, guild, channel, 10)

async def ainput(prompt: str = '') -> str:
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()

def main():
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()