## Description
The config.json file will give you some control over parameters inside of the program, such as mouse speed and numbers of pages, numbers of books, etc.

The values in there are the default values that I've found to work pretty well
but they can be changed as needed.

These are generally the steps you'll do:
1. Click and drag for the the screen region you want to want to capture.
2. Click the next page button on the pdf reader.
3. Record the mouse movements you'd take to open up the subsequent books. 
- You'll begin recording the mouse movements when you hit enter, and right clicking will end the recording for that book.
- These movements will be played back at a 1:1 speed.
4. Program will start capturing all of your screens, save the file, save it with the name and at the path you specify, open the file to crop it, and save it again. It will repeat this for each page, and for each book.

~~Because this can lock your computer up for an extended period of time, I added an emergency shut-off keybind of `alt+shift+enter`. If you press this, the program should stop where it's at and turn off.~~ Yeah I can't get that to work correctly mid-capture. Alt f4 sometimes works though :) 

## DELAYS
These values can be adjusted after you give it a few attempts. I've left in the values that were as quick as I could make it without having noticeable errors with the capture.
### "OPEN_SNIPPING_TOOL_DELAY"
A delay in seconds to wait to open the snipping tool before beginning the screen cpature sequence.
- If this is too low, the image capture sequence will begin before it's open and the screenshot will not be gotten at all.
- I wasn't able to find a reliable way to tell once the Snipping Tool was open and ready to receive keyboard shortcuts.

### "KEYBOARD_DELAY"
Interval to use between certain parts of the screen capture sequence. The areas where this interval is used:
1. Between the "Full-screen snip" keyboard shortcut sequence and the "ctrl+s" to save the resulting image.
2. Between the "ctrl+s" and the File Explorer window opening up. The sequence to enter filepath and file info on that window has no delays in keyboard capture.
3. *If you have a file with the same name in that folder already*, the keyboard delay will occur between attempting to save the file with the same name, and the keyboard shortcut to *overwrite* the existing file.

- If this is set too low, you may run into the "Full-screen snip" attempting to be saved mid-image generation. You may end up with a partial image, which may affect the cropping afterwards.

## BOOK CONFIGURATION
### "NUMBER_OF_BOOKS"
The number of books you plan to scan during this one execution of the program.
If the value is 0 (or negative, if you're trolling), the program will end shortly after starting. This will affect how many "Book opening sequences" you will have to record before the image capturing begins.
There also needs to be one corresponding entry in the following four lists for each additional book written here.

### "BOOK_NAMES"
Defines the names of the books. It can be a shorthand. 
The names of the books will be used as folders at the end of your `"BASE_FILEPATH"` to store their respective images.
NOTE: You do not need to create these folders manually, the program will detect if all directories in your "BASE_FILEPATH" and if your "BOOK_NAMES" directories exist, and create them for you if they do not.
*Must have one name for each `"NUMBER_OF_BOOKS"`*. 
> "BOOK_NAMES" = [ "Jets", "Planes", "Trains" ]

### "FILENAMES"
Defines the name of all of the files that will be saved. The resulting filename of each image capture will be FILEPATH/*FILENAME*.png. 
NOTE: The page number will be appended to this filename. 
Ex. [ "Jets-Page-", "PlanesP", "Train_" ] -> In this example, filenames will be FILEPATH/Jets-Page-*1*.png, FILEPATH/Planes*P55*.png, or FILEPATH/Train_*2000*.png, depending on your starting page numbers (below)

### "STARTING_PAGE_NUMS"
Defines the starting page number to be used for file naming. This program cannot detect the page you're starting on, so it's purely for naming conventions.
*Must have one name for each `"NUMBER_OF_BOOKS"`*. 
Ex. [ 1, 55, 2000 ]

### "NUMBER_OF_PAGES"
Defines the number of pages you plan to capture. I decided not to implement this as an "ending" page mostly because I had stuff written for total number of pages first :), but I admit it would be a little easier to define the page range by configuring "pages 150-200", rather than "start at 150 for 50 pages".
If you're doing quick math, just add some more pages to be safe. You'd rather overcapture than undercapture. It will likely just be copies of the final page after you cannot turn any longer. 
*Must have one name for each `"NUMBER_OF_BOOKS"`*. 
Ex. [ 50, 45, 1500 ]

## DIRECTORY
### "BASE_FILEPATH"
The root filepath where each book will have a folder created, and then its screenshots will be saved in those created folders. Windows filepaths use backslashes, which will need to be "escaped" by writing two backslashes in the filepath. 
Ex. `C:\\Users\\Christian\\`
*This MUST end with a trailing (back)slash* (depending on OS)

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
- If the Target file path or Location file path say "%windir%", then replace "%windir% with `C:\\Windows`. Note the escaped backslashes.

