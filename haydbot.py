#!/usr/bin/env python3
import asyncio
import discord
import os
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor

bot = commands.Bot(command_prefix = 'hb ')

messages = []

def load_msgs(messages, channel, depth):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
    display_messages = [message for message in messages if message['channel'] == channel][-depth:]
    for message in display_messages:
        print('#%s @%s: %s'%(message['channel'], message['author'], message['text']))
    print('\n > ', end='')

@bot.event
async def on_ready():
    print('Initiated HaydBot')

    channel = input('Channel: ')
    while True:
        load_msgs(messages, channel, 10)
        input_text = await ainput('')
        general = discord.utils.get(bot.get_all_channels(), name=channel)
        await general.send(input_text)

@bot.event
async def on_message(message):
    messages.append({'channel': message.channel.name, 'author': message.author.name, 'text': message.content})
    load_msgs(messages, message.channel.name, 10)

async def ainput(prompt: str = '') -> str:
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()

def main():
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()