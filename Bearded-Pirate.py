import time
import mouse
import keyboard
import json
import os
from subprocess import Popen
from emojis import encode
from math import floor
from typing import List
from PIL import ImageGrab, Image

##### Globals
c = open("./config.json")
CONFIG = json.load(c)
MOUSE_MOVE_TIMEOUT      = CONFIG["MOUSE_MOVE_TIMEOUT"]
MOUSE_MOVE_ADDED_DELAY  = CONFIG["MOUSE_MOVE_ADDED_DELAY"]
KEYBOARD_DELAY          = CONFIG["KEYBOARD_DELAY"]
NUMBER_OF_BOOKS         = CONFIG["NUMBER_OF_BOOKS"]
BOOK_NAMES              = CONFIG["BOOK_NAMES"]
NUMBER_OF_PAGES         = CONFIG["NUMBER_OF_PAGES"]
BASE_FILEPATH           = CONFIG["BASE_FILEPATH"]
FILENAMES               = CONFIG["FILENAMES"]
SNIPPING_TOOL_FILEPATH  = CONFIG["SNIPPING_TOOL_FILEPATH"]

X1 = Y1 = X2 = Y2 = 0
nextPagePosition: tuple[int] = []


##### Helpers
def printGlobals():
    for i in globals():
        print("{}: {}".format(i, globals()[str(i)]))

def visualSeparation(character: str, length: int):
    print("{}".format(character)*length)

def confirmExit() -> bool:
    while True:
        input("Screen captures complete press enter to exit program")
        break

def elapsedTime(start, finish) -> str:
    duration = int(round(finish-start)) # in seconds

    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)

    return "{}h{}m{}s".format(h,m,s)

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

#### Main

def openSnippingTool() -> Popen:
    global SNIPPING_TOOL_FILEPATH
    return Popen(SNIPPING_TOOL_FILEPATH) 

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

def snippingToolSequence(bookNum, pageNum, filepath) -> str:
    global FILENAMES, BASE_FILEPATH, BOOK_NAMES, MOUSE_MOVE_TIMEOUT


    def createFileName(pageNum: int) -> str:
        fileName: str = FILENAMES[bookNum]
        fileName = fileName[:len(fileName)-1] #remove the 1 
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

            keyboard.send(keyToSend)

    fileName: str = createFileName(pageNum)
    keyboardFileName: [str] = capitalizationToShiftKey(fileName)
    keyboardFilepath: [str] = capitalizationToShiftKey(filepath)

    windowCaptureSequence: [str] = ["alt+m", "up", "enter"]
    saveScreenshotSequence: [str] = ["ctrl+s"]
    fileSaveSequence: [str] = [*keyboardFileName, "f4", "ctrl+a","backspace", *keyboardFilepath, "alt+s"]

    #remove later
    overwriteSequence: [str] = ["alt+y"]

    captureSequence(windowCaptureSequence)
    time.sleep(KEYBOARD_DELAY)
    captureSequence(saveScreenshotSequence)
    time.sleep(KEYBOARD_DELAY)
    captureSequence(fileSaveSequence)

    time.sleep(KEYBOARD_DELAY)
    # remove later
    captureSequence(overwriteSequence)

    return filepath + "\\" + fileName

def captureScreenshot(bookNum, pageNum, filepath) -> str:
    snippingToolPipe: Popen = openSnippingTool()
    time.sleep(1)
    imagePath = snippingToolSequence(bookNum, pageNum, filepath)

    pipeOpen = snippingToolPipe.terminate()
    return imagePath

def explodePath(pathDirs):
    head, tail = os.path.split(pathDirs[0])
    print(head)
    print(tail)
    if len(tail) != 0:
        explode = explodePath([head])

    pathDirs.append(tail)
    return pathDirs

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
                print("\tCreated directory at {}\n".format(d))

        filepaths.append(d)
    return filepaths

def onClickCallback():
    global X1, Y1, X2, Y2
    
    if X1 and X1 and X2 and Y2:
        return

    if mouse.is_pressed():
        X1 = Y1 = X2 = Y2 = 0
        X1, Y1 = mouse.get_position()
        print("\t({},{})".format(X1, Y1), end="")
    if not mouse.is_pressed():
        X2, Y2 = mouse.get_position()
        print(" - ({},{})\t\t".format(X2, Y2) +
            "Region size of {}x{}.".format(abs(X2-X1),abs(Y2-Y1)))

def setCaptureRegion():
    while not X1 and not Y1 and not X2 and not Y2:
        e = mouse.on_button(onClickCallback, buttons=(mouse.LEFT), types=(mouse.UP, mouse.DOWN))
        input("Drag the area of the screen you would like to capture. " + 
            "The coordinates chosen and capture region size will be shown below.\n" +
            "Press enter to continue once finished\n")

    mouse.unhook(mouse._listener.handlers[0]) # can't figure out its name here lol :)

def nextPageCallback():
    global nextPagePosition
    nextPagePosition = mouse.get_position()
    print("\t{}\n".format(nextPagePosition))

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
    except:
        print("Error cropping image")

def mouseMoveClick(position: tuple[int], button: str):
    mouse.move(*position)
    mouse.click(button)

def openBookSequences() -> [[mouse.MoveEvent | mouse.ButtonEvent | mouse.WheelEvent]]:
    global BOOK_NAMES 

    sequences: mouse.MouseEvent = []
    if len(BOOK_NAMES) <= 1:
        return sequences

    for i, book in enumerate(BOOK_NAMES):
        i += 2
        sequence: mouse.MouseEvent = []
        
        title:str = "RECORDING FOR\t{}\tBOOK {} OF {}".format(book, i, len(BOOK_NAMES))
        info: str = "All mouse events are captured until you press the right mouse button"
        visualSeparation("=", len(title) if len(title) > len(info) else len(info))
        print(title)
        print(info)
        visualSeparation("=", len(title) if len(title) > len(info) else len(info))

        sequence = mouse.record()
        print("{} actions captured to open book {}-{}".format(len(sequence), i, book))
        sequences.append(sequence)

    return sequences
            
# TODO generic on click with a callback?
def cleanUpLastHook():
    mouse._listener.handlers = mouse._listener.handlers[:(len(mouse._listener.handlers)-1)]

def main():
    global NUMBER_OF_BOOKS, NUMBER_OF_PAGES, BOOK_NAMES, nextPagePosition
    print()
    greeting: str = "Program has been started"
    visualSeparation("=", len(greeting))
    print(greeting)
    start = time.time() 
    print("Beginning at {}.\n".format(time.strftime("%H:%M:%S", time.localtime())))

    # Get useful coordinates for cropping later
    topLeftCoords: tuple[int] = getDisplayBounds()
    # Create the folders specified in the config file if they don't yet exist
    filepaths: [str] = makeFolders(BOOK_NAMES)

    # Capture region for the screenshot area
    setCaptureRegion()
    # Position of the next page button on the screen and it's hook cleanup
    setNextPageButton()

    # Record the opening functions of the next few books, if there are multiple
    openSequences: [[mouse.MoveEvent | mouse.ButtonEvent | mouse.WheelEvent]] = openBookSequences()

    for bookNum in range(NUMBER_OF_BOOKS):
        for pageNum in range(NUMBER_OF_PAGES[bookNum]):
            # Opens snipping tool, captures all screens, saves the file to specified foler, and closes snipping tool
            imagePath = captureScreenshot(bookNum, pageNum+1, filepaths[bookNum]) # adding 1 b/c zero-index
            print("Page {}\t-\tPath:{}".format(pageNum+1, imagePath))
            # Opens the saved file and crops to the screen region specified and resaves 
            openAndCropImage(imagePath, topLeftCoords)
            print("Page {}\t-\tCrop Complete".format(pageNum+1))
            #Clicks the next page button after screen capture complete
            mouseMoveClick(nextPagePosition, mouse.LEFT)
            time.sleep(MOUSE_MOVE_TIMEOUT*5)

        # All book pages are finished and it recreates the sequence to open the next book
        if bookNum <= len(openSequences)-1:
            mouse.play(openSequences[bookNum])

    finish = time.time()
    print("Elapsed duration of {}.\n".format(elapsedTime(start, finish)))
    confirmExit()

def init():
    main()

init()

