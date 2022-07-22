#!/usr/bin/env python3

import asyncio
import os
import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

# Load Environment
load_dotenv()

# Configure bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(" ", intents=intents)

## CONFIGS ## TODO read in configs from JSON or env variables  
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
BUTTON_CHANNEL = "door-test" 
LOG_CHANNEL = "bot_spam"
MESSAGE = "Shop Door"
BUTTON_LABEL = "Unlock"
ROLES = ["The Beacon"]

UNLOCK_TIME = 5.0
LOG = None
BUSY = False

## Connecting to the discord channel 
@bot.listen("on_ready")
async def on_ready():    
    global LOG
    global MESSAGE 
    global UNLOCK_TIME

    ## Need to cast env variable to INT for some reason? 
    server = bot.get_guild(int(SERVER_ID))
    
    ## Lets log a succesful connection maybe in a channel? 
    print(f"Succesfully connected to {server.name}!")

    for channel in server.channels: 
        if channel.name == BUTTON_CHANNEL:
            working_channel = channel
        if channel.name == LOG_CHANNEL:
            LOG = channel
    
    ## Clear the channel when we boot up ##
    await working_channel.purge()

    ## Create Button ##
    button = Button(label=BUTTON_LABEL, style=discord.ButtonStyle.green)
    view = View()
    view.add_item(button)

    async def button_callback(interaction): 
        global BUSY
        global LOG
        global UNLOCK_TIME

        found = False

        for role in interaction.user.roles:
            ## Look for verified roles ## 
            if role.name in ROLES: 
                if not BUSY:                     
                    BUSY = True
                    await interaction.user.send("Welcome to the RAS shop! This message will self-destruct in 10 seconds.")
                    await interaction.response.edit_message()
                    ## TODO : add functionality to control door
                    await asyncio.sleep(UNLOCK_TIME)
                    BUSY = False
                    found = True
                    await LOG.send(f"<@{interaction.user.id}> accessed the shop door - GRANTED")
                else: 
                    await interaction.user.send("Yo chill... ")
                    await interaction.response.edit_message()
                    found = True
                    await LOG.send(f"<@{interaction.user.id}> is spamming the button... - DENIED")
                    break
                break
        
        if not found:
            await LOG.send(f"<@{interaction.user.id}> tried to access the shop door - DENIED")
            await interaction.user.send("Please contact one of the club officers about shop access.")
            await interaction.response.edit_message()

    button.callback = button_callback
    ## Send the message with button to the channel ##
    await working_channel.send(MESSAGE, view=view) 

@bot.listen("on_message")
async def on_message(message):
    global BUTTON_CHANNEL
    ## If the channel is not a DM and is the 'unlock door' designated channel 
    #   then delete any message else if the bot DM'd somebody, deleted after
    #   some time
    if not isinstance(message.channel, discord.DMChannel):
        if (message.author.id != bot.application_id) and (message.channel.name == BUTTON_CHANNEL):
            await message.delete()
    elif (bot.application_id == message.author.id):
        await asyncio.sleep(10)
        await message.delete()
        
bot.run(DISCORD_TOKEN)
