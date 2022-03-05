#!/usr/bin/env python3
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = 'hb ')

@bot.event
async def on_ready():
    print('Initiated HaydBot')

@bot.command()
async def exit(ctx):
    await ctx.bot.close()

with open('token.txt', 'r') as token:
    bot.run(token.read())