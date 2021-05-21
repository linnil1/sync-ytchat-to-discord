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

        if not self.is_alive():
            raise ValueError("Is not live")
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
                logger.debug("post")
                await self.send(c)

            if self.live:
                await chatdata.tick_async()


async def console_print(c):
    if type(c) is str:
        logger.info(c)
    else:
        logger.debug(f"Print data: {str(c.json())}")


class YTchats:
    def __init__(self, state=False, **kwargs):
        self.videos = []
        # save the list of videos id into files
        self.state = state
        self.state_file = "./state"
        if state:
            self.load_state(**kwargs)
            logger.debug(f"State will save to {self.state_file} while checking")

    def load_state(self, **kwargs):
        if not os.path.exists(self.state_file):
            return
        logger.info(f"Read last state from {self.state_file}")
        for id in open("state"):
            id = id.strip()
            self.add_video(id.split('.')[1], id.split('.')[0], **kwargs)

    def write_state(self):
        with open(self.state_file, "w") as f:
            f.writelines([i.id for i in self.videos])

    def add_video(self, id, channel="", func_send=console_print, **kwargs):
        try:
            chat = YTchat(id, channel, func_send, **kwargs)
            self.videos.append(chat)
            return True
        except BaseException as e:
            logger.warning(str(type(e)) + str(e))
            logger.warning(f"{id} cannot be added")
        return False

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

    async def remove_offline_video(self):
        # check if finished
        fin_chat = []
        for chat in self.videos:
            if not chat.is_alive():
                fin_chat.append(chat.id)

        # remove offline stream
        for id in fin_chat:
            await self.remove_video(id)

    def show_status(self):
        logger.info("check: " + ",".join([i.id for i in self.videos]))

        # save state to file
        if self.state:
            self.write_state()

    async def main(self, allow_empty=True):
        while True:
            await self.remove_offline_video()

            if len(self.videos) == 0 and not allow_empty:
                break

            self.show_status()
            await asyncio.sleep(10)


if __name__ == "__main__":
    async def main():
        chats = YTchats(state=False)
        chats.add_video("ejGH1BC1l98", "backup", normal_msg=True, save=True, live=False)
        await chats.main(allow_empty=True)
    asyncio.run(main())
