# Telecat
What is telecat, the telecat can  

The **telecat** is a combination of **telegram** and
**netcat** two words.

## Setup
``` bash
pip install python-telegram-bot

git clone https://github.com/r888800009/telecat.git
cd telecat
```

## Telegram Shell Bot 
Set up a shell bot is easy.
``` bash
./telecat.py /bin/sh 
```

Maybe you want to set the shell bot only you can use the config.

## Use terminal chat with telegram
Using Netcat open a port telegram
``` bash
# tty1
./telecat.py nc -l -p 1234 
```

then type `/start` in telegram,
Then enter the following command at the terminal

``` bash
# tty2
nc localhost 1234
```
