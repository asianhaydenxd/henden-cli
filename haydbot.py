#!/usr/bin/env python3
import asyncio
import discord
import os
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from getch import Getch
from colorama import Fore

bot = commands.Bot(command_prefix = 'hb ')

class Client(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.getch = Getch()
        self.menu = 'guilds'

        self.guild = None
        self.channel = None

        self.scroll = 0
        self.results = 35

        self.messages = []
        self.cache_history = []
        self.unread_messages = []
    
    async def ainput(self) -> str:
        with ThreadPoolExecutor(1, 'ainput') as executor:
            return (await asyncio.get_event_loop().run_in_executor(executor, input)).rstrip()

    async def agetch(self) -> str:
        with ThreadPoolExecutor(1, 'agetch') as executor:
            return (await asyncio.get_event_loop().run_in_executor(executor, self.getch.impl)).rstrip()

    def load_msgs(self, messages, channel):
        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        print(f'\r{Fore.YELLOW}Chatting in{Fore.RESET}: {channel.guild.name}{Fore.YELLOW}/{Fore.RESET}{channel.name}')

        if [message for message in self.unread_messages if message.channel != channel]:
            last_foreign_message = [message for message in self.unread_messages if message.channel != channel][-1]
            print(f'\r{Fore.GREEN}! {last_foreign_message.guild.name}{Fore.YELLOW}/{Fore.GREEN}{last_foreign_message.channel.name} {last_foreign_message.author.name}: {Fore.YELLOW}{last_foreign_message.content}{Fore.RESET}')
        else:
            print('\r')

        for message in reversed(messages[self.scroll:self.scroll+self.results]):
            print(f'\r{Fore.BLUE}{message.author.display_name}{Fore.RESET}: {Fore.RED if message in self.unread_messages else Fore.RESET}{message.content}{Fore.RESET}')
        
        print('\r')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Initiated HaydBot')

        while True:
            if self.menu == 'guilds':
                try:
                    selection = bot.guilds.index(self.guild)
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
                    if selection > guild_scroll + self.results:
                        guild_scroll = selection - self.results
                        
                    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
                    print(f'{Fore.GREEN}? Select server {Fore.RESET}({selection+1}/{len(bot.guilds)})\n')
                    for i, guild in enumerate(bot.guilds):
                        if i < guild_scroll or i > guild_scroll + self.results:
                            continue
                            
                        if selection == i:
                            if guild in [message.guild for message in self.unread_messages]:
                                print(Fore.BLUE + '> ' + Fore.GREEN + guild.name + ' !' + Fore.RESET)
                            else:
                                print(Fore.BLUE + '> ' + guild.name + Fore.RESET)
                        elif guild in [message.guild for message in self.unread_messages]:
                            print(Fore.GREEN + '  ' + guild.name + ' !' + Fore.RESET)
                        else:
                            print('  ' + guild.name)

                    input_char = await self.agetch()

                    if input_char == 'd' or input_char == 'C':
                        self.guild = bot.guilds[selection]
                        self.menu = 'channels'
                        break

                    if input_char == 'w' or input_char == 'A':
                        selection -= 1
                    if input_char == 's' or input_char == 'B':
                        selection += 1
                    
                    if input_char == 'q':
                        await bot.close()
                        return

            if self.menu == 'channels':
                try:
                    selection = self.guild.text_channels.index(self.channel)
                except ValueError:
                    selection = -1

                channel_scroll = 0

                while True:
                    if selection < 0:
                        selection = len(self.guild.text_channels) - 1
                    if selection >= len(self.guild.text_channels):
                        selection = 0
                    
                    if selection < channel_scroll:
                        channel_scroll = selection
                    if selection > channel_scroll + self.results:
                        channel_scroll = selection - self.results

                    os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
                    print(f'{Fore.GREEN}? Select channel {Fore.RESET}({selection+1}/{len(self.guild.text_channels)})\n')
                    for i, channel in enumerate(self.guild.text_channels):
                        if i < channel_scroll or i > channel_scroll + self.results:
                            continue
                        
                        if selection == i:
                            if channel in [message.channel for message in self.unread_messages]:
                                print(Fore.BLUE + '> ' + Fore.GREEN + channel.name + ' !' + Fore.RESET)
                            else:
                                print(Fore.BLUE + '> ' + channel.name + Fore.RESET)
                        elif channel in [message.channel for message in self.unread_messages]:
                            print(Fore.GREEN + '  ' + channel.name + ' !' + Fore.RESET)
                        else:
                            print('  ' + channel.name)

                    input_char = await self.agetch()

                    if input_char == 'd' or input_char == 'C':
                        self.channel = self.guild.text_channels[selection]
                        self.menu = 'messaging'
                        break
                    if input_char == 'a' or input_char == 'D':
                        self.channel = self.guild.text_channels[selection]
                        self.menu = 'guilds'
                        break

                    if input_char == 'w' or input_char == 'A':
                        selection -= 1
                    if input_char == 's' or input_char == 'B':
                        selection += 1
                    
                    if input_char == 'q':
                        await bot.close()
                        return

                if self.menu == 'messaging':
                    self.scroll = 0
                    self.cache_history = await self.channel.history().flatten()

            elif self.menu == 'messaging':
                self.load_msgs(self.cache_history, self.channel)
                input_char = await self.agetch()
                if input_char == 'q':
                    await bot.close()
                    return
                    
                elif input_char == 'a' or input_char == 'D':
                    self.menu = 'channels'
                    for message in [message for message in self.unread_messages if message.channel == self.channel]:
                        self.unread_messages.remove(message)

                elif input_char == 'w' or input_char == 'A':
                    self.scroll += 1
                    if self.scroll >= len(self.cache_history) - self.results: self.scroll = len(self.cache_history) - self.results
                elif input_char == 's' or input_char == 'B':
                    self.scroll -= 1
                    if self.scroll <= 0: self.scroll = 0

                elif ord(input_char) == 27:
                    for message in [message for message in self.unread_messages if message.channel == self.channel]:
                        self.unread_messages.remove(message)

                elif input_char == 't':
                    self.menu = 'typing'
                    print(f'\r {Fore.BLUE}>{Fore.RESET} ', end='')
                    input_text = await self.ainput()
                    self.menu = 'messaging'
                    if input_text: await self.channel.send(input_text)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel != self.channel and message not in self.unread_messages:
            self.unread_messages.append(message)

        if self.menu == 'messaging':
            if message.channel == self.channel:
                if self.scroll > 0: self.scroll += 1
                self.cache_history = await self.channel.history().flatten()

            self.load_msgs(self.cache_history, self.channel)

def main():
    bot.add_cog(Client(bot))
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()