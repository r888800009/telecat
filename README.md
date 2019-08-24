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

## Start With Simple C Program
create a c file `simple.c`.
``` c
#include <stdio.h>

int main()
{
  while (1) {
    char buf[32];
    scanf("%31s", buf);
    printf("%s\n", buf);
    fflush(stdout); # important
  }

  return 0;
}
```

then compile
``` bash
gcc simple.c
```

Run `telecat`
``` bash
./telecat.py ./a.out
```

Input `/start` in telegram then type some word you got an echo.

## Use Terminal Chat With Telegram
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
