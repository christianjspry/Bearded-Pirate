import time
import mouse
import keyboard
import json
from emojis import encode
from math import floor
from typing import List
from PIL import ImageGrab, Image

##### Classes
class MouseAction:
    actionType = "Mouse"

    def __init__(self, mouseButton, mouseDirection, mouseX, mouseY, time):
        self.mouseButton = mouseButton
        self.mouseDirection = mouseDirection
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.time = time

    def toString(self):
        printStr = "{"
        for i, val in enumerate(vars(self).items()):
            printStr += "{}: {}".format(*val)
            if i != len(vars(self).items()) - 1:
                printStr += ", "
        return printStr + "}"

class KeyboardAction:
    actionType = "Keyboard"

    def __init__(self, keyboardKey, keyDirection, time):
        self.key = keyboardKey
        self.keyDirection = keyDirection
        self.time = time

    def toString(self):
        printStr = "{"
        for i, val in enumerate(vars(self).items()):
            printStr += "{}: {}".format(*val)
            if i != len(vars(self).items()) - 1:
                printStr += ", "
        return printStr + "}"

##### Globals
MOUSE_DELAY = .25
SCREENSHOT_DELAY = 75./100
eventActions: List[MouseAction or KeyboardAction] = []

##### Helpers
def printGlobals():
    for i in globals():
        print("{}: {}".format(i, globals()[str(i)]))

def clearEventActions():
    global eventActions
    eventActions = []

def mouseActionPrint(mouseAction: MouseAction):
    print("\t{}-click {} at ({},{})".format(
        mouseAction.mouseButton.capitalize(),
        mouseAction.mouseDirection.lower(),
        mouseAction.mouseX,
        mouseAction.mouseY
    ))

def keyboardActionPrint(keyboardAction: KeyboardAction):
    print("\t{} pressed {}".format(
        keyboardAction.key.capitalize(),
        keyboardAction.keyDirection.lower()
    ))

def confirmReady() -> bool:
    while True:
        instructions = """
        Before starting:
        - Have the pdf open and at the size you'd like to capture on one screen.
        - Move this console to a different screen.
        - Have the directory created that you'd like to store the screenshots.

        Steps:
        1. Open the snipping tool
        2. Press 'ctrl+N' with the snipping tool window as your focus
        3. After a delay, drag for the screenshot area
        4. Press 'ctrl+S' to save the screenshot
        5. Make sure the filepath is correct; can be changed as needed
        6. Rename the screenshot
            - The file name you start with should end with '1', and it will automatically increment with each page saved.
        7. Press 'enter' to save the file
        8. Click the next page on the pdf.
            - Since we're using ctrl+S, there's no need to close snipping tool. If the next page button is visible you should just click it
        9. Use the hotkey 'ctrl+alt+enter' to stop capturing.
            - This avoids unwanted actions from entering the sequence once you're finished
            - Saves some time on each iteration
        10. Click back here and press 'enter' to lock in the sequence
        """
        print(instructions)
        ready = input("Press the enter key to begin.")
        if ready.lower() == "":
            break
    return True 

def confirmExit() -> bool:
    while True:
        exit = input("\n==========\nThanks for letting me help! This was a lot of fun for me. Press enter to exit.")
        if exit == "":
            break
    return True

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

def collectInputs():
    global eventActions
    mouse.hook(onClickCallback)
    keyboard.hook(onKeystrokeCallback)

    retry = True
    done = False
    while retry == True and done == False:
        while True:
            print("\n==========\nBegin performing the steps above.\n")
            input("When you are finished, press enter. If you messed up and want to restart, " +
                                "press Ctrl+C and re-run the program.\n==========\n\n")
            for i in eventActions:
                if i.actionType == KeyboardAction.actionType and i.key.lower() == "ctrl+n":
                    done = True
                    break
            if done == True:
                break
            else:
                clearEventActions()
                print("\nError: ctrl+n was never selected. Clearing action history. You may now start over.")
    
    if onClickCallback in mouse._listener.handlers:
        mouse.unhook(onClickCallback)
    if onKeystrokeCallback in keyboard._hooks:
        keyboard.unhook(onKeystrokeCallback)

def onClickCallback(e):
    global eventActions

    if type(e) == mouse._mouse_event.ButtonEvent and e.button == mouse.LEFT:
        mouseAction = MouseAction(e.button, e.event_type, *mouse.get_position(), e.time)
        mouseActionPrint(mouseAction)
        eventActions.append(mouseAction)

def onKeystrokeCallback(e):
    global eventActions

    if e.event_type == keyboard.KEY_UP:
        return
    if e.name == "ctrl" or e.name == "shift" or e.name == "alt":
        return
    
    ctrl = True if keyboard.is_pressed('ctrl') else False
    shift = True if keyboard.is_pressed('shift') else False
    alt = True if keyboard.is_pressed('alt') else False

    hotkey = "{}{}{}{}".format(
        "ctrl+" if ctrl else "",
        "shift+" if shift else "",
        "alt+" if alt else "",
        e.name.lower()
    )
    if hotkey == "ctrl+alt+enter":
        keyboard.unhook(onKeystrokeCallback)
        mouse.unhook(onClickCallback)
        print("\n\t==========\n\t" +
              "\'ctrl+alt+enter\' has been pressed: no more keyboard entries are being captured" +
              "\n\t==========\n")
        return

    keyboardAction = KeyboardAction(hotkey, e.event_type, e.time)
    keyboardActionPrint(keyboardAction)
    eventActions.append(keyboardAction)

def getPageTotal() -> int:
    while True:
        try:
            pages = int(input("Enter total number of pages (including the one you just captured): "))-1
            print("\n==========\n")
            return pages 
        except KeyboardInterrupt:
            break
        except:
            pass

def reverseIndexByType(arr, actionType) -> int:
    l = len(arr)-1
    for i, val in enumerate(reversed(arr)):
        if (val.actionType == actionType and 
            val.key.lower() != "enter" and
            val.key.lower() != "ctrl" and
            val.key.lower() != "alt"):
            return l-i
    return -1

def recreateMouseAction(mouseAction, delay):
    time.sleep(delay)
    while (mouseAction.mouseX != mouse.get_position()[0] and
           mouseAction.mouseY != mouse.get_position()[1]):
        #mouse.move(mouseAction.mouseX, mouseAction.mouseY, duration=delay)
        mouse.move(mouseAction.mouseX, mouseAction.mouseY)
    if mouseAction.mouseDirection == mouse.DOWN:
        mouse.press()
    if mouseAction.mouseDirection == mouse.UP:
        mouse.release()

def recreateActions(pageTotal):
    global eventActions
    finalKeyboardIndex = reverseIndexByType(eventActions, KeyboardAction.actionType)


    delay = MOUSE_DELAY
    loadingBar = consoleLoadingBar(0, pageTotal)
    
    for i in range(pageTotal):
        previousAction = eventActions[0]

        for iAction, action in enumerate(eventActions):
            if ((previousAction.actionType == KeyboardAction.actionType
                and previousAction.key.lower() == 'ctrl+n')
                or (action.actionType == KeyboardAction.actionType
                    and action.key.lower() == 'ctrl+n')):
                time.sleep(SCREENSHOT_DELAY)

            previousAction = action

            ## append unique file names before continuing
            if iAction == finalKeyboardIndex:
                for digit in str(i+2):
                    keyboard.send(digit)
                continue

            if action.actionType == MouseAction.actionType:
                recreateMouseAction(action, delay)

            if action.actionType == KeyboardAction.actionType:
                keyboard.send(action.key)

        loadingBar = consoleLoadingBar(i, pageTotal)
    print(loadingBar)

def main():
    print("Program has been started")
    #exit = keyboard.hook(emergencyExitCallback)
    confirmReady()
    collectInputs()
    pageTotal = getPageTotal()

    start = time.time() 
    print("Beginning at {}.\n".format(time.strftime("%H:%M:%S", time.localtime())))
    recreateActions(pageTotal)
    finish = time.time()
    print("Elapsed duration of {}.\n".format(elapsedTime(start, finish)))

    confirmExit()

def init():
    f = open('config.json')
    data = json.load(f)
    print(data)
    main()

init()
