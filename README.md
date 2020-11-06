#**Weclome** to PySend!

## What is *PySend*?
PySend is a simple application to send file(s) over a TCP connection!

## How do you *use* PySend?!
It's simple! I swear!

###### Want to run as a server?!
```main.py --serv```

The default address is 127.0.0.1:5000

###### Whaa?! You don't like the default address/port?!?!
```main.py --serv --addr 1.2.3.4 --port 98765```

Don't worry! ```--addr``` and ```--port``` can be used separately!
###### PySend is used to send files... What files?!
```main.py --dir THIS_DIR_TOTALLY_EXISTS```

You can use ```--dir``` to specify a directory! 
Don't worry if you forget it, it will default to the current working directory
###### OK! So you're tired of that *'server'* mumbo-jumbo!
```main.py --addr 1.1.1.1 --port 12345```

See! It's not *that* hard! Now remember if you omit the ```--addr``` 
and/or the ```--port``` the default args are used. 
I.E. That's how you specify the address or port!
###### *WAIT!* Before you go! There's one more arg!
```main.py --debug```

It basically spits out a whole bunch of junk to the console! *USE AT YOUR OWN RISK ;)*

##
###### P.S. This is currently a work in progress! :)
Hope you enjoy this program, may it serve many uses for you!
