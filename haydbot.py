#!/usr/bin/env python3
import asyncio
import discord
import os
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from getch import Getch
from colorama import Fore

bot = commands.Bot(command_prefix = 'hb ')

menu = 'messaging'
messages = []

def load_channels():
    pass

def load_msgs(messages, guild, channel, depth):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
    display_messages = [message for message in messages if message['guild'] == guild and message['channel'] == channel][-depth:]
    
    print(f'{Fore.YELLOW}Chatting in{Fore.RESET}: {channel}\n')
    for message in display_messages:
        print('%s: %s'%(Fore.BLUE+message['author']+Fore.RESET, message['text']))
    print(f'\n {Fore.BLUE}>{Fore.RESET} ', end='')

@bot.event
async def on_ready():
    print('Initiated HaydBot')

    guild = input('Server: ')
    channel = input('Channel: ')
    while True:
        if menu == 'channels':
            load_channels()
        if menu == 'messaging':
            load_msgs(messages, guild, channel, 10)
            input_text = await ainput('')
            if input_text == '\\q':
                await bot.close()
                break
            general = discord.utils.get(bot.get_all_channels(), name=channel)
            await general.send(input_text)

@bot.event
async def on_message(message):
    messages.append({'guild': message.guild.name, 'channel': message.channel.name, 'author': message.author.name, 'text': message.content})
    if menu == 'messaging': load_msgs(messages, message.guild.name, message.channel.name, 10)

async def ainput(prompt: str = '') -> str:
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()

def main():
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()