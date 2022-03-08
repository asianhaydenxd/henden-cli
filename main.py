#!/usr/bin/env python3
import asyncio
import discord
import os # plan to remove
import curses
from discord.ext import commands
from enum import Enum, auto
from concurrent.futures import ThreadPoolExecutor
from getch import Getch # plan to remove
from colorama import Fore # plan to remove

bot = commands.Bot(command_prefix = 'hb ', intents=discord.Intents.all())

RESULTS = 8

class Menu(Enum):
    GUILD = auto()
    CHANNEL = auto()
    CHAT = auto()

class Client(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.getch = Getch()
        self.menu = Menu.GUILD

        self.guild = None
        self.channel = None

        self.scroll = 0
        self.results = RESULTS

        self.messages = []
        self.unread_messages = []

        self.screen = curses.initscr()
        self.screen.keypad(True)
        curses.start_color()
        curses.cbreak()
        curses.noecho()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Initiated HaydBot')

        self.guild = bot.guilds[0]
        self.channel = self.guild.text_channels[0]

        while True:
            if self.menu == Menu.GUILD:
                self.load_guilds()

                input_char = await self.agetch()

                if input_char == 'd' or input_char == 'C':
                    self.menu = Menu.CHANNEL
                    self.channel = self.guild.text_channels[0]

                if input_char == 'w' or input_char == 'A':
                    try: self.guild = bot.guilds[bot.guilds.index(self.guild) - 1]
                    except IndexError: self.guild = bot.guilds[-1]
                if input_char == 's' or input_char == 'B':
                    try: self.guild = bot.guilds[bot.guilds.index(self.guild) + 1]
                    except IndexError: self.guild = bot.guilds[0]
                
                if input_char == 'q':
                    await bot.close()
                    return

            if self.menu == Menu.CHANNEL:
                self.load_channels()

                input_char = await self.agetch()

                if input_char == 'd' or input_char == 'C':
                    self.menu = Menu.CHAT
                if input_char == 'a' or input_char == 'D':
                    self.menu = Menu.GUILD

                if input_char == 'w' or input_char == 'A':
                    try: self.channel = self.guild.text_channels[self.guild.text_channels.index(self.channel) - 1]
                    except IndexError: self.channel = self.guild.text_channels[-1]
                if input_char == 's' or input_char == 'B':
                    try: self.channel = self.guild.text_channels[self.guild.text_channels.index(self.channel) + 1]
                    except IndexError: self.channel = self.guild.text_channels[0]
                
                if input_char == 'q':
                    await bot.close()
                    return

                if self.menu == Menu.CHAT:
                    self.scroll = 0
                    self.messages = await self.channel.history().flatten()

            if self.menu == Menu.CHAT:
                self.load_msgs()
                input_char = await self.agetch()
                if input_char == 'q':
                    await bot.close()
                    return
                    
                elif input_char == 'a' or input_char == 'D':
                    self.menu = Menu.CHANNEL
                    for message in [message for message in self.unread_messages if message.channel == self.channel]:
                        self.unread_messages.remove(message)

                elif input_char == 'w' or input_char == 'A':
                    self.scroll += 1
                    if self.scroll >= len(self.messages) - self.results: self.scroll = len(self.messages) - self.results
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
                    self.menu = Menu.CHAT
                    if input_text: await self.channel.send(input_text)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel != self.channel and message not in self.unread_messages:
            self.unread_messages.append(message)

        if self.menu == Menu.CHAT:
            if message.channel == self.channel:
                if self.scroll > 0: self.scroll += 1
                self.messages = await self.channel.history().flatten()

            self.load_msgs()

    def load_guilds(self):
        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        print(f'{Fore.GREEN}? Select server {Fore.RESET}({bot.guilds.index(self.guild)+1}/{len(bot.guilds)})\n')
        for i, guild in enumerate(bot.guilds):
            if i < bot.guilds.index(self.guild) - self.results/2 or i > bot.guilds.index(self.guild) + self.results/2:
                continue
                
            if self.guild == guild:
                if guild in [message.guild for message in self.unread_messages]:
                    print(Fore.BLUE + '> ' + Fore.GREEN + guild.name + ' !' + Fore.RESET)
                else:
                    print(Fore.BLUE + '> ' + guild.name + Fore.RESET)
            elif guild in [message.guild for message in self.unread_messages]:
                print(Fore.GREEN + '  ' + guild.name + ' !' + Fore.RESET)
            else:
                print('  ' + guild.name)

    def load_channels(self):
        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        print(f'{Fore.GREEN}? Select channel {Fore.RESET}({self.guild.text_channels.index(self.channel)+1}/{len(self.guild.text_channels)})\n')
        for i, channel in enumerate(self.guild.text_channels):
            if i < self.guild.text_channels.index(self.channel) - self.results/2 or i > self.guild.text_channels.index(self.channel) + self.results/2:
                continue
            
            if self.channel == channel:
                if channel in [message.channel for message in self.unread_messages]:
                    print(Fore.BLUE + '> ' + Fore.GREEN + channel.name + ' !' + Fore.RESET)
                else:
                    print(Fore.BLUE + '> ' + channel.name + Fore.RESET)
            elif channel in [message.channel for message in self.unread_messages]:
                print(Fore.GREEN + '  ' + channel.name + ' !' + Fore.RESET)
            else:
                print('  ' + channel.name)
    
    def load_msgs(self):
        os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal for both Windows and Unix
        print(f'\r{Fore.YELLOW}Chatting in{Fore.RESET}: {self.channel.guild.name}{Fore.YELLOW}/{Fore.RESET}{self.channel.name}')

        if [message for message in self.unread_messages if message.channel != self.channel]:
            last_foreign_message = [message for message in self.unread_messages if message.channel != self.channel][-1]
            print(f'\r{Fore.GREEN}! {last_foreign_message.guild.name}{Fore.YELLOW}/{Fore.GREEN}{last_foreign_message.channel.name} {last_foreign_message.author.name}: {Fore.YELLOW}{last_foreign_message.content}{Fore.RESET}')
        else:
            print('\r')

        lines = []
        message_index = 0
        while len(lines) < self.results:
            if self.messages[message_index] not in self.messages[self.scroll : self.scroll + self.results]:
                message_index += 1
                continue
                
            message = self.messages[message_index]
            message_index += 1
            
            color = discord.Color.greyple()
            try:
                for role in reversed(message.author.roles):
                    if role.color.value != 0:
                        color = role.color
                        break
            except AttributeError as e:
                if e.name != 'roles': raise
            finally:
                message_lines = [f'\r\033[38;2;{color.r};{color.g};{color.b}m{message.author.display_name}{Fore.RESET}: {Fore.RED if message in self.unread_messages else Fore.RESET}' + message.content.split('\n')[0]] + message.content.replace('\n', '\n' + ' ' * (len(message.author.display_name) + 2)).split('\n')[1:]
                message_lines.reverse()
                lines += message_lines

        print('\n'.join(list(reversed(lines[:self.results]))))
                
        
        print('\r')

    def end_curses(self):
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()

        curses.endwin()
    
    async def ainput(self) -> str:
        with ThreadPoolExecutor(1, 'ainput') as executor:
            return (await asyncio.get_event_loop().run_in_executor(executor, input)).rstrip()

    async def agetch(self) -> str:
        with ThreadPoolExecutor(1, 'agetch') as executor:
            return (await asyncio.get_event_loop().run_in_executor(executor, self.getch.impl)).rstrip()

def main():
    bot.add_cog(Client(bot))
    with open('token.txt', 'r') as token:
        bot.run(token.read())
    
if __name__ == '__main__': main()