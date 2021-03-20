from pytchat import LiveChatAsync
import asyncio
from setup import logger


class YTchat:
    def __init__(self, id, func_send, only_money=False):
        self.id = id
        self.livechat = LiveChatAsync(id, callback=self.post)
        self.only_money = only_money
        self.send = func_send
        logger.info(id + " is added")

    def is_alive(self):
        return self.livechat.is_alive()

    async def close(self):
        logger.info(self.id + " to stopped")
        await self.send(f"{self.id} is stopped", text_only=True)
        self.livechat.terminate()

    def raise_for_status(self):
        return self.livechat.raise_for_status()

    async def post(self, chatdata):
        for c in chatdata.items:
            if not (c.type == "textMessage" and self.only_money):
                logger.debug("send " + str(c.json()))
                await self.send(c)
            await chatdata.tick_async()


async def console_print(c, text_only=False):
    if text_only:
        logger.info(c)
    else:
        logger.info(f"{c.datetime} {c.author.name}: "
                    f"{c.amountString} -- {c.message}")


class YTchats:
    def __init__(self):
        self.videos = []

    def add_video(self, id, func_send=console_print):
        chat = YTchat(id, func_send, True)
        self.videos.append(chat)

    async def remove_video(self, id):
        videos = []
        for chat in self.videos:
            logger.debug(f"{chat.id} {id}")
            if chat.id == id:
                await chat.close()
            else:
                videos.append(chat)
        if len(videos) == len(self.videos):
            return False
        self.videos = videos
        return True

    async def main(self, allow_empty=True):
        while True:
            # check if finished
            fin_chat = []
            for chat in self.videos:
                if not chat.is_alive():
                    fin_chat.append(chat.id)

            # remove finish
            for id in fin_chat:
                await self.remove_video(id)

            if len(self.videos) == 0 and not allow_empty:
                break

            logger.info("check: " + ",".join([i.id for i in self.videos]))
            await asyncio.sleep(10)


if __name__ == "__main__":
    chats = YTchats()
    # chats.add_video("BJlB8bD0dSI")
    chats.add_video("fok5dkdbz4A")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(chats.main(allow_empty=False))
