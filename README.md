## Description
The config.json file will give you some control over some of the parameters inside of the program, such as mouse speed and numbers of pages, numbers of books, etc.

The values in there are the default values that I've found to work pretty well
but they can be changed as needed.

## It looks like capitalized values really mess it up

## Values
### "MOUSE_MOVE_STANDARD"
Normal mouse movement timeout delay (seconds)
move mouse to (x,y) and then click
i.e. Clicking snipping tool in the task bar

### "MOUSE_MOVE_DELAYED"
A slower interval used for mouse movements (seconds)
used when things may need an additional moment to open/close/become available
i.e. waiting to drag a screen region after pressing "ctrl+N" in the snipping tool

### "KEYBOARD_DELAY"
Interval to use for keystrokes. Useful to configure if things are loading more slowly 
and inputs are being wasted

### "NUMBER_OF_BOOKS"
Number of the books you'd like to scan at this time. 
There will be additional setups you do before the program begins executing.

### "BOOK_NAMES"
Defines the names of the books. It can be a shorthand. This is the name of the folders
that the screenshots will be added to. *Must one name for each book*. The length of this
value should be equal to the "NUMBER_OF_BOOKS". Ex.
> "BOOK_NAMES" = [ "Jets", "Planes", "Trains" ]
In this example, "NUMBER_OF_BOOKS" must be 3.

### "NUMBER_OF_PAGES"
Defines the number of pages used in each book. *There should be one entry for each value in
"NUMBER_OF_BOOKS"*. The format should be like below:
> "NUMBER_OF_PAGES": [ 20, 50, 100 ]
In this example, "NUMBER_OF_BOOKS" must be 3.

### "BASE_FILEPATH"
The root filepath where each book will have a folder created, and then its screenshots added to 
its particular folder. *This needs to end with a trailing slash*

### "FILENAMES"
Defines the way that you would like the pages to be named. You should give the value for the first
screenshot in each book. Be sure to label the first page as the first page by ending it with a "1".
Ex. [ "Jets-Page-1", "PlanesP1", "Train_1" : In this example, "NUMBER_OF_BOOKS" must be 3.

### "SNIPPING_TOOL_FILEPATH"
You can find this by: 
- Searching "Snipping Tool" in your windows taskbar search bar
- Right-click the Snipping Tool icon and then click "Open File Location"
- Right-click the Snipping Tool file in the opened file location and select "Properties"
- In the "General" tab, if the "Type of file" says Application, you will paste the "Location" from the
General tab into "SNIPPING_TOOL_FILEPATH
- If the "Type of file" says "Shortcut", click the "Shortcut" tab in the properties window and then paste
the "Target" location into the "SNIPPING_TOOL_FILEPATH".
NOTES: 
- *All backslashes have to be "escaped" by doubling them whenever they're used* (on Windows).
> ex. C:\Windows\System32\SnippingTool.exe --> C:\\Windows\\System32\\SnippingTool.exe
- If the Target file path or Location file path say "%windir%", then replace "%windir% with `C:\\Windows`.
Note the double backslashes.

### "EXIT_KEYBIND"
This can be any key you'd like press to exit the recording sequence of opening up additional books.
Some rules to be mindful of:
- The key names need to be lowercase
- There should be no spaces if using modifier keys
- Each key should be separated with a plus sign '+' if using modifiers
- The library key names are pretty intuitive for the most part. It uses a lot of aliases for key names in the lookups, i.e. "esc" is the same as "escape" for this situation.

