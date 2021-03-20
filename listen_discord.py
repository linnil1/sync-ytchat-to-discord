import discord
from read_ytchat import YTchats
from datetime import datetime

from setup import logger, DISCORD_TOKEN

client = discord.Client()
chats = YTchats()


@client.event
async def on_ready():
    logger.debug(client.guilds)
    logger.info(f"{client.user} has connected to Discord!")
    await chats.main()


def discord_notify(channel):
    async def send(c, text_only=False):
        if text_only:
            await client.guilds[0].get_channel(channel).send(c)
            return

        # If new member: message = join message
        if c.amountString:
            text = f"[{c.amountString}]\n{c.message}"
        else:
            text = f"[{c.message}]"
        dtime = datetime.utcfromtimestamp(c.timestamp / 1000)
        # name, color and time
        embed = discord.Embed(title=c.author.name,
                              colour=c.bgColor % 0x1000000,  # no A channel
                              description=text,
                              timestamp=dtime)
        # thumbnail
        embed.set_thumbnail(url=c.author.imageUrl)
        # send
        await client.guilds[0].get_channel(channel).send(embed=embed)
    return send


def read_arg(content):
    sp = content.split(" ")
    if len(sp) < 2:
        return None, None
    videoid = sp[2].strip()
    if len(videoid):
        return sp[1].strip(), videoid
    else:
        return None, None


@client.event
async def on_message(message):
    # Only read command from author
    if message.author == client.user:
        return
    if not message.content.startswith(".synchat"):
        return

    # read command and videoid
    logger.debug(message.content)
    method, id = read_arg(message.content)
    if id is None:
        await message.channel.send("Fail: No video ID provieded")
        return

    # start to monitor
    if method == "start":
        dc_channel = message.channel.id
        logger.info(f"Sync {id} to {dc_channel}")
        try:
            chats.add_video(id, discord_notify(dc_channel))
            await message.channel.send(f"OK {id}")
        except BaseException as e:
            logger.warning(str(type(e)) + str(e))
            await message.channel.send(f"Fail to add {id}")

    # stop monitor
    elif method == "stop":
        ok = await chats.remove_video(id)
        if ok:
            await message.channel.send("OK")
        else:
            await message.channel.send(f"No {id} found")
    else:
        await message.channel.send(f"{method} not implemented")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
