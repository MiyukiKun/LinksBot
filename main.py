from telethon import events, Button
import asyncio
import json
from config import bot, bot_username, approved_users
from telethon.tl.functions.messages import ExportChatInviteRequest
import helper
from datetime import datetime, timezone, timedelta
from motormongo import UsersDB, SettingsDB, LinksDB

LinksDB = LinksDB()
UsersDB = UsersDB()
SettingsDB = SettingsDB()

last_run_times = {}


async def upate_link(channel_id):
    global last_run_times

    last_run = last_run_times.get(channel_id)
    time_gap = await SettingsDB.find({'_id': 'time_gap'})
    time_gap = time_gap['gap']
    now = datetime.now(timezone.utc)
    expiry = (now + timedelta(minutes=time_gap)).replace(microsecond=0)
    
    if not last_run or now - last_run >= timedelta(minutes=time_gap):
        o = await LinksDB.find({'_id': channel_id})
        r = o['req']
        if r == "T":
            req = True
        else:
            req = False
        result = await bot(
            ExportChatInviteRequest(
                peer=channel_id,
                request_needed=req, 
                expire_date=expiry
            )
        )
        
        await LinksDB.modify({'_id': channel_id}, {'_id': channel_id, 'link': result.link, 'req': r})
    
        last_run_times[channel_id] = now


@bot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await UsersDB.add(
        {
            "_id": event.chat_id, 
            "username": event.sender.username, 
            "name": f"{event.sender.first_name} {event.sender.last_name}",
            "uid": int(await UsersDB.count()) + 1,
        }
    )
    if event.raw_text == "/start":
        await event.reply("Im running.")
    data = event.raw_text.strip().split(" ")[-1]
    channel_id = int(helper.decrypt(data))
    await upate_link(channel_id)
    link = await LinksDB.find({'_id': channel_id})
    link = link["link"]
    buttons = [Button.url("Join Channel Now", link)]
    await bot.send_message(event.chat_id, "Click the button below.", buttons=buttons)
    

@bot.on(events.NewMessage(pattern="/add_channel", chats=approved_users))
async def _(event):
    global last_run_times

    _, channel_id, r = event.raw_text.strip().split(" ")
    channel_id = int(channel_id)
    if r == "T":
        req = True
    else:
        req = False
    time_gap = await SettingsDB.find({'_id': 'time_gap'})
    time_gap = time_gap['gap']
    now = datetime.now(timezone.utc)
    expiry = (now + timedelta(minutes=time_gap)).replace(microsecond=0)
    result = await bot(
            ExportChatInviteRequest(
                peer=channel_id,
                request_needed=req,
                expire_date=expiry
            )
        )
        
    await LinksDB.add({'_id': channel_id, 'link': result.link, 'r': r})

    last_run_times[channel_id] = now
    data = helper.encrypt(str(channel_id))
    await event.reply(f"t.me/{bot_username}?start={data}")


@bot.on(events.NewMessage(pattern="/broadcast", chats=approved_users))
async def _(event):
    msg = await event.get_reply_message()
    offset = None
    limit = None
    count = 0
    if event.raw_text == "/broadcast":
        users = await UsersDB.full()
    else:
        _, offset, limit = event.raw_text.split()
        if offset == "random":
            users = await UsersDB.rando(sample_size=limit)
        else:
            users = await UsersDB.range(offset=int(offset), limit=int(limit))
    for i in users:
        try:
            await bot.send_message(i['_id'], msg)
            await asyncio.sleep(0.5)
        except Exception as e:
            count += 1
            print(e)
    await event.reply(f"Broadcast Done, Offset={offset}, Limit={limit}, Count={count}")


@bot.on(events.NewMessage(pattern="/timegap", chats=approved_users))
async def _(event):
    gap = int(event.raw_text.strip().split(" ")[-1])
    await SettingsDB.modify({"_id": "time_gap"}, {"_id": "time_gap", "gap": gap})
    await event.reply(f'Time gap updated to {gap}')


@bot.on(events.NewMessage(pattern="/req", chats=approved_users))
async def _(event):
    _, channel_id, r = event.raw_text.strip().split(" ")
    old_link = await LinksDB.find({'_id': channel_id})
    old_link = old_link['link']
    channel_id = int(channel_id)
    await LinksDB.modify({'_id': channel_id}, {'_id': channel_id, 'link': old_link, 'req': r})
    await event.reply(f'Request required set to {r} for channel {channel_id}')


@bot.on(events.NewMessage(pattern="/stats"))
async def _(event):
    count = await UsersDB.count()
    await event.reply(f"Statistics for bot:\n Total number of users: {count}", link_preview=False)
    if "export" in event.raw_text:
        await event.reply("Uploading file please wait...")
        userdata = await UsersDB.full()
        with open("userdata.json", "w") as final:
            json.dump(userdata, final, indent=4)
        await event.reply(f"Statistics for bot:\n Total number of users: {count}", file="userdata.json")


bot.start()

bot.run_until_disconnected()
