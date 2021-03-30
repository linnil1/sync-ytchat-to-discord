# sync-ytchat
A simple discord bot that mirror youtube chat to discord channel

## install
```
git clone https://github.com/linnil1/sync-ytchat-to-discord
cd sync-ytchat-to-discord
pip3 install -r requirments.txt
```

## Configuration
Add a bot into your channel and edit discord token in `env.py`

## Run
```
python3 listen_discord.py
```

## Usage
```
.synchat start EfzvWiFANYg
.synchat stop EfzvWiFANYg
```

The bot will start reading the chat in `EfzvWiFANYg` and
post message in the same channel when there have more chats.

Demo
* The youtube chat in https://www.youtube.com/watch?v=EfzvWiFANYg
![](https://i.imgur.com/f4ar4Ut.jpg)
* The discord bot notification
![](https://i.imgur.com/MKqezQI.png)
* I have fixed datetime and using thumbnail instead of image
![](https://i.imgur.com/YD8QzHC.png)


## TODO
* [x] Monitor multiple videos in same time
* [x] Add or del videos in command
* [x] Better design of embed form
* [ ] Recover after break(Now I write id in `./state` not in redis)
* [ ] Write chat into database(Now the chat is appended in each file `./chat/xx.xx.data`)
* [ ] unit test
* [ ] user/channel permission
* [ ] Automatically start to sync the chat from specific channel (This would take lots of works dealing with subscribtion and feeds)
