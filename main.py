# Welcome to my mini pycord Ticket System!
# first you need to install dhooks with "pip install dhooks"
# then you want to download Pycord with the command "pip install py-cord==2.0.0b4"

import datetime
from dhooks import Webhook
import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio


#-----------------------------------------------------#

# The Informations you need to have

guild_id = 943586896947322951 # The ID from your Guild
team_role = 944974401168875562 # The ID from your Support Role
ticket_create_channel = 944977847825612800 # The ID from the Channel, where the Ticket Create embed will be send in
category_id = 944580205249437706 # The ID from the Ticket category
archiv_category_id = 957363580557201458 # The ID from the Archiv Category (the category where the channel will be moved in if it gets closed)
ticketlog = Webhook("https://canary.discord.com/api/webhooks/953676324667555850/6QVN-zUDDfM2gtTgh8XP8VezMWrHJSqpmEDGYKuvPgcX2dXHBPP5U2UbwAYsWLxY9SX-") # The Webhook Link from your Ticketlog

#-----------------------------------------------------#

intent = discord.Intents.all() # All Discord Intents (discord.dev) you should activate all
bot = commands.Bot(command_prefix="!", intent=intent) # define the bot
bot.remove_command('help') # Remove the normal Help command


@bot.event
async def on_ready(): # Event if bot get started
    print(f'{bot.user.name} logged in') # will log if bot goes online

    async def status_task(): # automatic Status Changer
        while True:
            await bot.change_presence(activity=discord.Game(name='Status 1')) # first status
            await asyncio.sleep(10) # will wait 10 seconds
            await bot.change_presence(activity=discord.Game(name='Status 2')) # second status
            await asyncio.sleep(10) # will wait 10 seconds
            await bot.change_presence(activity=discord.Game(name='Status 3')) # third status
            await asyncio.sleep(10) # will wait 10 seconds

    bot.loop.create_task(status_task()) # create the loop from our status task rigt over us


@bot.event
async def on_interaction(interaction): # the on interaction event
    if interaction.channel.id == ticket_create_channel: # checks if the interaction was used in the right place
        if "ticket_button" in str(interaction.data): # checks if the custom id from the button is
            guild = bot.get_guild(guild_id) # get the guild id
            for ticket in guild.channels: # checks if a ticket is in our guild channels
                if str(interaction.user.id) in ticket.name: # checks if a Ticket is already existing from the user
                    await interaction.response.send_message(f"❌ Du kannst nur ein Ticket gleichzeitig aufhaben! {ticket.mention}", ephemeral=True) # response to that
                    return

            category = bot.get_channel(category_id) # get the category id from your ticket support
            ticket_channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", category=category, topic=f"**Ticket von** {interaction.user} \n**Nutzer ID:** {interaction.user.id}") # creates the channel

            await ticket_channel.set_permissions(guild.get_role(team_role), send_messages=True, read_messages=True, add_reactions=False, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True) # gives the team permissions

            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True) # gives the user permissions

            await ticket_channel.set_permissions(guild.get_role(guild_id), view_channel=False) # will make the Ticket private

            embed = discord.Embed(title=f"**Ticket Support**", description=f"deine Beschreibung! (Zeile: 50)") # The Embed if a user creates an Ticket
            abfrageclose = Button(emoji="🔒", label="close", style=discord.ButtonStyle.danger, custom_id="abfrage_button_ticket") # Close button
            claimbuttonclose = Button(emoji="📨", label="claim", style=discord.ButtonStyle.primary, custom_id="claim_button_ticket") # Claim button
            view = View() # define the view
            view.add_item(abfrageclose) # add the Button
            view.add_item(claimbuttonclose) # adds another Button
            embed.set_author(name=f'Neues Ticket!') # Set a mini Title
            await ticket_channel.send(f"{interaction.user.mention}, <@&{team_role}>") # ping the user and the team
            await ticket_channel.send(embed=embed, view=view) # send the embed and the buttons
            await interaction.response.send_message(f"📨 | Dein Ticket wurde geöffnet! {ticket_channel.mention}", ephemeral=True) # Will send an response
            ticketlogembed = discord.Embed(title="Ein Ticket wurde geöffnet!", description=f"**Ticketname:** {ticket_channel.mention}\n**TicketID:** {ticket_channel.id}\n**Nutzer:** <@{interaction.user.id}>", color=0x1aff00, timestamp=datetime.datetime.now()) # set the Ticketlog embed
            ticketlogembed.set_author(url=interaction.user.avatar, name=interaction.user.name, icon_url=interaction.user.avatar)
            ticketlog.send(embed=ticketlogembed) # send the ticketlog embed
            return
    if "abfrage_button_ticket" in str(interaction.data): # checks if the custom id from the button is
        abfrageja = Button(label="Schließen", style=discord.ButtonStyle.gray, custom_id="close_button_ticket") # set the button
        abfrageno = Button(label="Abbrechen", style=discord.ButtonStyle.gray, custom_id="abbrechen_button_ticket") # set the button
        abfrageview = View() # define the view
        abfrageview.add_item(abfrageja) # add the button
        abfrageview.add_item(abfrageno) # add another button
        await interaction.channel.send("Willst du das Ticket wirklich schließen?", view=abfrageview)
        return
    if "close_button_ticket" in str(interaction.data): # check if a button is the close button
        archiv = bot.get_channel(archiv_category_id) # get the archiv category
        closeembed = discord.Embed(description=f"**Das Ticket wurde geschlossen von** <@{interaction.user.id}>", color=0xcc0000) # message if ticket is closed
        ticketlogcloseembed = discord.Embed(title=f"Ein Ticket wurde geschlossen!", description=f"**Ticket:** {interaction.channel.id}\n**Nutzer:** <@{interaction.user.id}>", timestamp=datetime.datetime.now(), color=0xcc0000) # ticketlog embed
        ticketlogcloseembed.set_author(url=interaction.user.avatar, name=interaction.user.name, icon_url=interaction.user.avatar)
        ticketlog.send(embed=ticketlogcloseembed) # send the ticket log embed
        await interaction.channel.send(embed=closeembed) # send the close embed
        await asyncio.sleep(2) # wait 2 seconds
        await interaction.channel.edit(category=archiv) # move channel to archiv
        deletebutton_buttonticket = Button(emoji="🔒", label="Delete", style=discord.ButtonStyle.danger, custom_id="delete_button_ticket") # set delete button
        deletebutton = View() # define the view
        deletebutton.add_item(deletebutton_buttonticket) # add the button
        await interaction.channel.send(" ", view=deletebutton) # send the button
        return
    if "abbrechen_button_ticket" in str(interaction.data): # check if custum_id >
        await interaction.channel.send("Die Interaktion wurde abgebrochen!") # send the message
        return
    if "claim_button_ticket" in str(interaction.data): # check if custum_id >
        embed = discord.Embed(description=f'✅ **Ticket wurde von <@{interaction.user.id}> geclaimt**', color=0x00cc00)
        ticketlogembed = discord.Embed(title="Ein Ticket wurde geclaimt!", description=f"**Ticket:** <#{interaction.channel.id}>\n**Nutzer:** {interaction.user.mention}", color=0x55828b, timestamp=datetime.datetime.now())
        ticketlogembed.set_author(url=interaction.user.avatar, name=interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.channel.send(embed=embed) # send the embed
        await interaction.channel.edit(name=f"✅ {interaction.channel.name}") # edit the channel name
        ticketlog.send(embed=ticketlogembed) # send the ticketlog embed
        return
    if "delete_button_ticket" in str(interaction.data): # check if button deleted
        deleteembed = discord.Embed(title=f"Das Ticket wird in `5` Sekunden gelöscht!") # embed
        await interaction.channel.send(embed=deleteembed) # send the embed
        await asyncio.sleep(5) # wait 5 seconds
        await interaction.channel.delete() # delete the channel
        return

@bot.command()
@commands.is_owner()
async def sendticketmessage(ctx): # command name
    channel = bot.get_channel(ticket_create_channel) # get the channel
    embed = discord.Embed(title=f"Ticket Support", description=f"öffne ein Ticket mit der interaktion unter mir!", color=0x41fbe0) # embed
    buttoncreate = Button(label=f"Ticket öffnen", emoji="📨", custom_id="ticket_button") # button
    view = View() # buttons
    view.add_item(buttoncreate) # add a button
    await channel.send(embed=embed, view=view) # send the embed and the button

bot.run("OTQ2ODQ0MjIxMDc4Mzg4NzU3.YhknZQ.M1I7Mxkys1oLKS9iZWSAh0S3-wI") # paste the token in here!
