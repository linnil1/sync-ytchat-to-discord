import asyncio
import os
from pytchat import LiveChatAsync
from setup import logger


class YTchat:
    def __init__(self, ytid, chid, func_send, normal_msg=False,
                 save=False, live=True):
        # main
        self.livechat = LiveChatAsync(ytid, callback=self.post)
        if chid:
            self.id = str(chid) + "." + ytid
        else:
            self.id = ytid

        # discord channel and post function
        self.chid = str(chid)
        self.send = func_send

        # pytchat parameters
        self.ytid = ytid
        self.normal_msg = normal_msg
        self.live = live

        # save the chat
        self.save = save
        self.folder = "chat/"
        if save:
            os.makedirs(self.folder, exist_ok=True)

        logger.info(self.id + " is added")

    def is_alive(self):
        return self.livechat.is_alive()

    async def close(self):
        logger.info(self.id + " to stopped")
        await self.send(f"{self.ytid} is stopped")
        self.livechat.terminate()

    def raise_for_status(self):
        return self.livechat.raise_for_status()

    async def post(self, chatdata):
        for c in chatdata.items:
            if self.save:
                with open(self.folder + self.id + ".data", "a") as f:
                    f.write(c.json() + "\n")

            if c.type != "textMessage" or self.normal_msg:
                logger.debug(f"{self.id} send {str(c.json())}")
                await self.send(c)

            if self.live:
                await chatdata.tick_async()


async def console_print(c):
    if type(c) is str:
        logger.info(c)
    else:
        logger.info(f"{c.datetime} {c.author.name}: "
                    f"{c.amountString} -- {c.message}")


class YTchats:
    def __init__(self, state=False, **kwargs):
        self.videos = []
        # save the list of videos id into files
        self.state = state
        self.state_file = "./state"
        if state:
            self.load_state(**kwargs)

    def load_state(self, **kwargs):
        if not os.path.exists(self.state_file):
            return
        logger.info(f"Read last state from {self.state_file}")
        for id in open("state"):
            id = id.strip()
            try:
                self.add_video(id.split('.')[1], id.split('.')[0], **kwargs)
            except BaseException as e:
                logger.warning(str(type(e)) + str(e))
                logger.warning(f"{id} cannot be added")

    def write_state(self):
        logger.info(f"Save state to {self.state_file}")
        with open(self.state_file, "w") as f:
            f.writelines([i.id for i in self.videos])

    def add_video(self, id, channel="", func_send=console_print, **kwargs):
        chat = YTchat(id, channel, func_send, **kwargs)
        self.videos.append(chat)

    async def remove_video(self, id, channel=""):
        if channel:
            id = str(channel) + "." + id
        videos = []
        for chat in self.videos:
            if chat.id == id:
                logger.debug(f"Remove {chat.id}")
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

            # remove offline stream
            for id in fin_chat:
                await self.remove_video(chat.id)

            if len(self.videos) == 0 and not allow_empty:
                break

            # save state to file
            logger.info("check: " + ",".join([i.id for i in self.videos]))
            if self.state:
                self.write_state()
            await asyncio.sleep(10)


if __name__ == "__main__":
    chats = YTchats(state=True)
    # chats.add_video("fok5dkdbz4A", "123", save=True, live=False)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(chats.main(allow_empty=False))
