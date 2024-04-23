# Version 1.4
After first run lst_helper will create file `lst_helper_config.txt`. This file contains various settings such as:
- **hs** - allows you to change default Hearthstone logs location
- **display** - settings for various types of information helper can output to console, allowed values are `1` and `0`
- **logging** - settings for `.log` file created alongside console output, allowed values are `1` and `0` for minions' properties, any utf-8 character, `TAB` or `SPACE` for separators

Different flavours:
- `lst_helper.exe` - Win
- `lst_helper.mac` - Mac (TBA)

Tool heavily relies on Zone log.
How to enable it:
- If you use Hearthstone Deck Tracker, this is sometimes already done for you, but still worth verifying
Go to %LocalAppData%/Blizzard/Hearthstone (paste that path in the run dialog - Win+R to open) on Windows, or /Users/USERNAME/Library/Preferences/Blizzard/Hearthstone on Mac
- Open (or create) the log.config file with any text editor (note: if creating yourself, make sure your text editor doesn’t save it as log.config.txt)
- Edit the file so that it has a [Zone] section that looks like this:
```
[Zone]
LogLevel=1
FilePrinting=true
ConsolePrinting=false
ScreenPrinting=false
Verbose=true
```

- Or you can just replace the entire file with [this file](https://gist.githubusercontent.com/IlyaHalsky/024db2ec71a4eabb660adb0cffcf5cb3/raw/1c099885c2d9a204b4910344d456f02d0244d525/log.config)
- Now go to C:\Program Files (x86)\Hearthstone or /Applications/Hearthstone on Mac
- Open (or create) the client.config file with any text editor (note: if creating yourself, make sure your text editor doesn’t save it as client.config.txt)
+ Edit the file so that it has a [Log] section that includes the following:
```
[Log]
FileSizeLimit.Int=-1
```
(This prevents the log files from getting truncated at a certain file size)