import discord
import json
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(data):
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)

config = load_config()


class MyClient(discord.Client):
    async def setup_hook(self):
        self.deleted_messages = []  
client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return  

    log_message = (
        f"Message deleted in {'a DM' if isinstance(message.channel, discord.DMChannel) else message.guild.name}:"
        f"Author: {message.author} ({message.author.id})\n"
        f"Channel: {message.channel} ({message.channel.id})\n"
        f"Content: {message.content}\n"
        f"Attachments: {[attachment.url for attachment in message.attachments]}\n"
    )

    print(log_message)

    client.deleted_messages.append({
        "author": str(message.author),
        "author_id": message.author.id,
        "channel": str(message.channel),
        "channel_id": message.channel.id,
        "content": message.content,
        "attachments": [attachment.url for attachment in message.attachments],
    })

    if not isinstance(message.channel, discord.DMChannel):
        log_channel_id = config.get("log_channel_id") 
        if log_channel_id:
            log_channel = message.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"```{log_message}```")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!setlog"):
        try:
            log_channel_id = int(message.content.split()[1])
            config["log_channel_id"] = log_channel_id
            save_config(config)
            await message.channel.send(f"Log channel set to <#{log_channel_id}>")
        except (IndexError, ValueError):
            await message.channel.send("Usage: `!setlog <channel_id>`")

client.run(config.get("discord_token", "your-token"))
