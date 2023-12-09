import json
import keyboard
import logging
import mouse
import os
import time
from emojis     import encode
from PIL        import ImageGrab, Image
from subprocess import Popen
from typing     import List

##### Globals
c = open("./config.json")
CONFIG = json.load(c)
OPEN_SNIPPING_TOOL_DELAY = CONFIG["OPEN_SNIPPING_TOOL_DELAY"]
KEYBOARD_DELAY           = CONFIG["KEYBOARD_DELAY"]
NUMBER_OF_BOOKS          = CONFIG["NUMBER_OF_BOOKS"]
BOOK_NAMES               = CONFIG["BOOK_NAMES"]
NUMBER_OF_PAGES          = CONFIG["NUMBER_OF_PAGES"]
BASE_FILEPATH            = CONFIG["BASE_FILEPATH"]
FILENAMES                = CONFIG["FILENAMES"]
SNIPPING_TOOL_FILEPATH   = CONFIG["SNIPPING_TOOL_FILEPATH"]
STARTING_PAGE_NUMS       = CONFIG["STARTING_PAGE_NUMS"]

X1 = Y1 = X2 = Y2 = 0
nextPagePosition: tuple[int] = []


#### Logging - unneccessary but cool
logging.basicConfig(
    filename="output.txt",
    filemode="w",
    level=logging.INFO,
    format='%(levelname)s - %(asctime)s | %(message)s'
)
logger = logging.getLogger("MyLogger")

##### Helpers
# unused but could be helpful for debugging later
def printGlobals():
    for i in globals():
        print("{}: {}".format(i, globals()[str(i)]))

def visualSeparation(character: str, length: int):
    print("{}".format(character)*length)

def confirmExit() -> bool:
    mouse.unhook_all()
    keyboard.unhook_all()
    msg: str = "All screen captures are complete. You may press enter to exit program."
    visualSeparation("=", len(msg))
    input(msg)

def elapsedTime(start, finish) -> str:
    duration = int(round(finish-start)) # in seconds

    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)

    return "{}h{}m{}s".format(h,m,s)

# unused but it makes me happy so it stays
def consoleLoadingBar(current, total) -> str:
    current += 1
    loadingBarLength = 50 
    text = ""
    cum = 0
    completeMessage = emojis.encode("- Pdf scan cumplete :sweat_drops:")

    for i in range(total):
        progress = round((current/total)*loadingBarLength)
        remainingLength = loadingBarLength - progress

        if progress == 0:
            text = "[{}]".format(" "*loadingBarLength)
        elif progress == 1:
            text = "[E{}]".format(" "*remainingLength)
        elif progress == 2:
            text = "[ED{}]".format(" "*remainingLength)
        elif progress == 3:
            text = "[E=D{}]".format(" "*remainingLength)
        elif progress == loadingBarLength:
            text = ("[E{}D~{}] " + completeMessage).format(("=" * (progress-3)), ("~"*remainingLength))
        elif progress > 4:
            text = "[E{}D~{}]".format(("=" * (progress-3)), ("~"*remainingLength))
            if progress + cum != loadingBarLength:
                cum += 1
            else:
                cum -= 1
        else:
            text = "[E=D~{}]".format("~"*(loadingBarLength-4))
        print(text, end="\r", flush=True)
    return text

# returns a string list of all components of a filepath  
def explodePath(pathDirs: str) -> [str]:
    head, tail = os.path.split(pathDirs[0])
    print(head)
    print(tail)
    if len(tail) != 0:
        explode = explodePath([head])

    pathDirs.append(tail)
    return pathDirs

def emergencyExit():
    keyboard.hook(emergencyExitCallback)

#### Callbacks
def onClickCallback():
    global X1, Y1, X2, Y2
    
    if X1 and X1 and X2 and Y2:
        return

    if mouse.is_pressed():
        X1 = Y1 = X2 = Y2 = 0
        X1, Y1 = mouse.get_position()
        print("\t({},{})".format(X1, Y1), end="")
    if not mouse.is_pressed() and X1 and Y1:
        X2, Y2 = mouse.get_position()
        print(" - ({},{})\t\t".format(X2, Y2) +
            "Region size of {}x{}.".format(abs(X2-X1),abs(Y2-Y1)))
        logger.info("Screen capture region coordinates: (%s,%s) - (%s,%s)", X1, Y1, X2, Y2)
        logger.info("Screen capture region size of %sx%s", abs(X2-X1), abs(Y2-Y1))

def nextPageCallback():
    global nextPagePosition
    nextPagePosition = mouse.get_position()
    print("\t{}\n".format(nextPagePosition))
    logger.info("Next Page Button coordiantes: (%s,%s)", *nextPagePosition)

def cleanUpLastHook():
    mouse._listener.handlers = mouse._listener.handlers[:(len(mouse._listener.handlers)-1)]

def emergencyExitCallback(e):
    print(e)
    if keyboard.is_pressed("alt+shift+enter"):
        exit()

#### Main
def openSnippingTool() -> Popen:
    global SNIPPING_TOOL_FILEPATH
    return Popen(SNIPPING_TOOL_FILEPATH) 

# Solution to having capitalized characters in the config.json file.
# Necessary, but admittedly a bad solution
def capitalizationToShiftKey(string: str) -> [str]:
    newString: [str] = []
    for i, char in enumerate(string):
        #special characters:
        if char == "!":
            newString.append("shift+1")
        elif char == "@":
            newString.append("shift+2")
        elif char == "#":
            newString.append("shift+3")
        elif char == "$":
            newString.append("shift+4")
        elif char == "%":
            newString.append("shift+5")
        elif char == "^":
            newString.append("shift+6")
        elif char == "&":
            newString.append("shift+7")
        elif char == "*":
            newString.append("shift+8")
        elif char == "(":
            newString.append("shift+9")
        elif char == ")":
            newString.append("shift+0")
        elif char == "_":
            newString.append("shift+-")
        elif char == "+":
            newString.append("shift+=")
        elif char == "{":
            newString.append("shift+[")
        elif char == "}":
            newString.append("shift+]")
        elif char == "|":
            newString.append("shift+\\")
        elif char == ":":
            newString.append("shift+;")
        elif char == "\"":
            newString.append("shift+'")
        elif char == "<":
            newString.append("shift+,")
        elif char == ">":
            newString.append("shift+.")
        elif char == "?":
            newString.append("shift+/")
        elif char == "~":
            newString.append("shift+`")
        elif char != char.lower():
            newString.append("shift+{}".format(char.lower()))
        else:
            newString.append(char)

    return newString 

# could be made generic with a different filepath as an argument
def createFileName(bookNum, pageNum, filepath: int) -> str:
    global FILENAMES

    fileName: str = FILENAMES[bookNum]
    fileName = fileName[:len(fileName)] 
    fileName = fileName + str(pageNum) + ".png"
    return fileName

def captureSequence(sequence):
    for i, action in enumerate(sequence):
        while i != 0 and keyboard.is_pressed(sequence[i-1]):
            time.sleep(KEYBOARD_DELAY)

        parsedHotkey = keyboard.parse_hotkey(action)
        keyToSend: [int] = [] 

        for i in parsedHotkey[0]:
            keyToSend.append((i[0]))
        keyToSend = tuple(keyToSend)
        
        if action == "shift+-":
            keyboard.send(tuple([42,12]))
            continue

        keyboard.send(keyToSend)

def snippingToolSequence(bookNum, pageNum, filepath) -> str:
    global FILENAMES, BASE_FILEPATH, BOOK_NAMES 

    fileName: str = createFileName(bookNum, pageNum, filepath)
    imageFilepath: str = filepath + "\\" + fileName
    overwrite: bool = os.path.isfile(imageFilepath)
    keyboardFileName: [str] = capitalizationToShiftKey(fileName)
    keyboardFilepath: [str] = capitalizationToShiftKey(filepath)

    windowCaptureSequence: [str] = ["alt+m", "up", "enter"]
    saveScreenshotSequence: [str] = ["ctrl+s"]
    fileSaveSequence: [str] = [*keyboardFileName, "f4", "ctrl+a","backspace", *keyboardFilepath, "alt+s"]
    overwriteSequence: [str] = ["alt+y"]

    sequences: [[str]] = [windowCaptureSequence, saveScreenshotSequence, fileSaveSequence]

    overwrite: bool = os.path.isfile(imageFilepath)
    if overwrite:
        sequences.append(overwriteSequence)
        print("File exists - Overwriting - ", end="")
        logger.warning("Overwriting an existing file of %s.", fileName)

    for sequence in sequences:
        captureSequence(sequence)
        time.sleep(KEYBOARD_DELAY)

    return imageFilepath, fileName

def captureScreenshot(bookNum, pageNum, filepath) -> [str, str]:
    global OPEN_SNIPPING_TOOL_DELAY 

    snippingToolPipe: Popen = openSnippingTool()
    time.sleep(OPEN_SNIPPING_TOOL_DELAY)
    imagePath = snippingToolSequence(bookNum, pageNum, filepath)
    pipeOpen = snippingToolPipe.terminate()

    return imagePath

def makeFolders(bookNames: str) -> [str]: 
    global BASE_FILEPATH

    filepaths: [str] = []

    for bookName in bookNames:
        path: str = BASE_FILEPATH + bookName
        pathExists: bool = os.path.isdir(BASE_FILEPATH + path) #folder for book already created
        if pathExists:
            continue
       
        head, tail = os.path.split(path)
        pathDirs: [str] = [tail]
        for i in range(len(path)):
            head, tail = os.path.split(head)
            if len(tail) == 0:
                pathDirs.insert(0, head)
                break
            pathDirs.insert(0, tail)

        for i, _ in enumerate(pathDirs):
            if i == 0:
                continue

            d = os.path.join(*pathDirs[:i+1])
            if not os.path.isdir(d):
                os.mkdir(d)
                print("\tCreated directory at {}".format(d))
                logger.info("Directory created: %s", d)

        filepaths.append(d)
    return filepaths

def setCaptureRegion():
    while not X1 and not Y1 and not X2 and not Y2:
        e = mouse.on_button(onClickCallback, buttons=(mouse.LEFT), types=(mouse.UP, mouse.DOWN))
        input("\nDrag the area of the screen you would like to capture. " + 
            "The coordinates chosen and capture region size will be shown below.\n" +
            "Press enter to continue once finished\n")

    mouse.unhook(mouse._listener.handlers[0]) # can't figure out its name here lol :)

def setNextPageButton():
    print("Click the next page button on the pdf reader.")
    mouse.on_click(nextPageCallback)
    mouse.wait(target_types=(mouse.UP))
    cleanUpLastHook()

def getDisplayBounds() -> tuple[int]:
    startingPoint = mouse.get_position()
    previousPoint: tuple[int] = mouse.get_position()
    newPoint: tuple[int] = []
    # left and up
    while newPoint != previousPoint:
        # up left
        if len(newPoint) == 0:
            mouse.move(previousPoint[0]-1,previousPoint[1]-1)
            newPoint = mouse.get_position()

        previousPoint = newPoint
        mouse.move(previousPoint[0]-1,previousPoint[1]-1)
        newPoint = mouse.get_position()

    mouse.move(*startingPoint)
    return newPoint

def openAndCropImage(imagePath: str, topLeftCoords: tuple[int]):
    global X1, Y1, X2, Y1
    top = Y1 if Y1 < Y2 else Y2
    left = X1 if X1 < X2 else X2
    bottom = Y1 if Y1 > Y2 else Y2
    right = X1 if X1 > X2 else X2

    top = top + abs(topLeftCoords[1])
    left = left + abs(topLeftCoords[0])
    bottom = bottom + abs(topLeftCoords[1])
    right = right + abs(topLeftCoords[0])


    box: tuple(int) = (left, top, right, bottom)
    try: 
        imagePath = os.path.normpath(imagePath)

        image = Image.open(imagePath)
        croppedImage = image.crop(box)
        croppedImage.save(imagePath)
    except Exception as e:
        print("Error cropping image: {}".format(e))
        print("Exiting to reconfigure.")
        logger.error("%s",e)
        exit()

def mouseMoveClick(position: tuple[int], button: str):
    mouse.move(*position)
    mouse.click(button)

def openBookSequences() -> [[mouse.MoveEvent | mouse.ButtonEvent | mouse.WheelEvent]]:
    global BOOK_NAMES 

    sequences: mouse.MouseEvent = []
    # This cannot occur with configCheck()
    if len(BOOK_NAMES) <= 1:
        return sequences

    for i, book in enumerate(BOOK_NAMES):
        if i == 0:
            continue
        sequence: mouse.MouseEvent = []

        ready: str = "Get ready to record your mouse movements for opening up book number {}, {}.".format(i+1, book)
        instructions: str = "Click enter when ready to begin. Click the middle mouse button when ready to end the recording."
        visualSeparation("=", len(instructions) if len(instructions) > len(ready) else len(ready))
        input(ready+"\n"+instructions)
        
        title:str = "RECORDING FOR\t{}\tBOOK {} OF {}".format(book, i+1, len(BOOK_NAMES))
        print(title)

        sequence = mouse.record(button=mouse.MIDDLE)
        print("\t{} actions captured to open book {}-{}\n".format(len(sequence), i+1, book))
        sequences.append(sequence)
        logger.info("Open book sequence %s has %s inputs over %ss",
            i+1,
            len(sequence),
             sequence[len(sequence)-1].time-sequence[0].time
        )

    return sequences
            
# TODO generic on click with a callback?
def configCheck():
    global FILENAMES, BOOK_NAMES, NUMBER_OF_PAGES, NUMBER_OF_BOOKS, STARTING_PAGE_NUMS
    bookArrs: [int] = [FILENAMES, BOOK_NAMES, NUMBER_OF_PAGES, STARTING_PAGE_NUMS]

    if NUMBER_OF_BOOKS < 1:
        print("Number of books selected in the config.json must be 1 or greater. Exiting")
        exit()

    if len(BASE_FILEPATH) == 0 or len(SNIPPING_TOOL_FILEPATH) == 0:
        print("The length of your base filepath or snipping tool filepath is empty in the config.json. Exiting")

    for i, bookArr in enumerate(bookArrs):
        if len(bookArr) != NUMBER_OF_BOOKS:
            print("The length of at least one of the book configurations in config.json does not " +
                  "equal the number of books selected. Exiting.")
            exit()

def main():
    global NUMBER_OF_BOOKS, NUMBER_OF_PAGES, BOOK_NAMES, STARTING_PAGE_NUMS, nextPagePosition

    #emergencyExit()

    print()
    logger.info("Program Start")
    greeting: str = "Program has been started"
    configCheck()
    visualSeparation("=", len(greeting))
    print(greeting)
    input("\nBe sure to check out the README.md for some general info. Press enter when you're ready to begin.")
    scriptStart: time.time = time.time() 
    print("Beginning at {}.\n".format(time.strftime("%H:%M:%S", time.localtime())))

    # Get useful coordinates for cropping later
    topLeftCoords: tuple[int] = getDisplayBounds()
    logger.info("X/Y offset from the top left corner: %s", (topLeftCoords))
    # Create the folders specified in the config file if they don't yet exist
    filepaths: [str] = makeFolders(BOOK_NAMES)
    for i, filepath in enumerate(filepaths):
        logger.info("Filepath for book %s of %s: %s", str(i+1), str(NUMBER_OF_BOOKS), filepath)

    # Capture region for the screenshot area
    setCaptureRegion()
    # Position of the next page button on the screen and it's hook cleanup
    setNextPageButton()

    # Record the opening functions of the next few books, if there are multiple
    openSequences: [[mouse.MoveEvent | mouse.ButtonEvent | mouse.WheelEvent]] = openBookSequences()

    input("Capturing complete. Return to the STARTING PAGE of the first book, {}, ".format(BOOK_NAMES[0]) +
"and then hit enter to begin the page capturing process\n")

    for bookNum in range(NUMBER_OF_BOOKS):
        bookName: str = BOOK_NAMES[bookNum]
        startingPage: int = STARTING_PAGE_NUMS[bookNum]
        bookStartMsg: str = "Beginning capture for {}".format(bookName)
        print(bookStartMsg)
        visualSeparation("=", len(bookStartMsg))

        for pageNum in range(NUMBER_OF_PAGES[bookNum]):
            pageStart: time.time = time.time()
            # Opens snipping tool, captures all screens, saves the file to specified foler, and closes snipping tool
            imagePath, filename = captureScreenshot(bookNum, startingPage+pageNum, filepaths[bookNum]) # adding 1 b/c zero-index
            # Opens the saved file and crops to the screen region specified and resaves 
            openAndCropImage(imagePath, topLeftCoords)
            ##Clicks the next page button after screen capture complete
            mouseMoveClick(nextPagePosition, mouse.LEFT)
            pageFinish: time.time = time.time()
            print("{} page {}:\t{} saved in {} secs.".format(
                bookName,
                startingPage+pageNum,
                filename,
                round(pageFinish-pageStart, 3)))
            logger.info("Book %s: page %s of %s saved in %s secs",
                        bookName,
                        pageNum+startingPage,
                        startingPage+NUMBER_OF_PAGES[bookNum]-1,
                        pageFinish-pageStart
                        )

        # All book pages are finished and it recreates the sequence to open the next book
        if bookNum <= len(openSequences)-1:
            print("Playing back mouse sequence to open up {}.".format(BOOK_NAMES[bookNum+1]))
            mouse.play(openSequences[bookNum])
            mouse.release(button=mouse.MIDDLE) # the final button captured is pressed but not released

        if bookNum != len(range(NUMBER_OF_BOOKS))-1:
            print("Capture for {} complete.\n".format(bookName))
            logger.info("Capture for %s completed.", bookName)

    scriptFinish: time.time = time.time()
    print("\nElapsed duration of {}.\n".format(elapsedTime(scriptStart, scriptFinish)))
    confirmExit()

def run():
    main()

run()
