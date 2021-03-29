import discord
from read_ytchat import YTchats
from datetime import datetime
from setup import DISCORD_TOKEN, setup_parser, logger

client = discord.Client()
chats = YTchats(state=True, save=True)
parser = setup_parser()


@client.event
async def on_ready():
    logger.debug(client.guilds)
    logger.info(f"{client.user} has connected to Discord!")
    # Overwrite the post function after Discord client initized
    for v in chats.videos:
        v.send = discord_notify(int(v.chid))
    await chats.main()


def discord_notify(channel):
    async def send(c):
        if type(c) is str:
            await client.get_channel(channel).send(c)
            return

        # If new member: message = join message
        if c.amountString:
            text = f"[{c.amountString}]\n{c.message}"
        elif c.type != "textMessage":
            text = f"[{c.message}]"
        else:
            text = f"{c.message}"
        dtime = datetime.utcfromtimestamp(c.timestamp / 1000)
        # name, color(ARGB) and time
        embed = discord.Embed(title=c.author.name,
                              colour=c.bgColor % 0x1000000,
                              description=text,
                              timestamp=dtime)
        # thumbnail
        embed.set_thumbnail(url=c.author.imageUrl)
        # send
        await client.get_channel(channel).send(embed=embed)
    return send


@client.event
async def on_message(message):
    # Only read command exclude bot itself
    if message.author == client.user:
        return
    if not message.content.startswith(".synchat"):
        return

    # if no args
    if not message.content.startswith(".synchat "):
        await message.channel.send("```" + parser.format_help() + "```")
        return

    # read command and videoid
    logger.debug(message.content)
    try:
        args = parser.parse_args(message.content.split()[1:])
    except BaseException as e:
        # Fix this in Python3.9
        logger.warning(str(type(e)) + str(e))
        await message.channel.send("```" + parser.format_help() + "```")
        return

    method, id = args.method, args.id
    dc_channel = message.channel.id

    # list monitor list
    if method == "list":
        ids = [v.ytid for v in chats.videos if v.chid == str(dc_channel)]
        await message.channel.send("sync list: " + ",".join(ids))
        return

    # id cannot be null if user wants to start or stop the chat
    if id is None:
        await message.channel.send("Fail: No video ID provieded")
        return

    # start to monitor
    if method == "start":
        logger.info(f"Sync {id} to {dc_channel}")
        try:
            chats.add_video(id, dc_channel, discord_notify(dc_channel),
                            save=True)
            await message.channel.send(f"OK {id}")
        except BaseException as e:
            logger.warning(str(type(e)) + str(e))
            await message.channel.send(f"Fail to add {id}")

    # stop monitor
    elif method == "stop":
        ok = await chats.remove_video(id, dc_channel)
        if ok:
            await message.channel.send("OK")
        else:
            await message.channel.send(f"No {id} found")
    else:
        await message.channel.send(f"{method} not implemented")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
