import os
from telethon import TelegramClient, events


api_id = ""
api_hash = ""


client = TelegramClient("sess", api_id, api_hash, system_version="4.16.30-vxCUSTOM")
client.start()


