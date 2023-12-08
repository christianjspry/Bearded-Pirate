def saveScreenshots(screenshots):
    directoryPath = "./Pages_" + str(round(time.time()%10000))
    if not os.path.exists(directoryPath):
        os.mkdir(directoryPath)

    for i in enumerate(screenshots):
        #element index
        index = i[0]
        screenshot = i[1]

        filePathString = directoryPath + "/Page_00" + str(index+1) + ".png"
        screenshot.save(filePathString)

def screenshotCaptureRegion(numberOfPages) -> list[Image]:
    screenshots = [];
    regionArr = [captureRegionLeft, captureRegionTop, captureRegionRight, captureRegionBottom]
    screenshotArgs = [None if sum(regionArr) == 0 else regionArr, False, False, None]

    # move cursor to position:
    mouse.move(nextPageX, nextPageY)

    for i in range(numberOfPages):
        consoleLoadingBar(i+1, numberOfPages)
        screenshot = ImageGrab.grab(*screenshotArgs) # spread operator
        #screenshot = i
        screenshots.append(screenshot)
        pageTurn()
        time.sleep(1/10)

    print() #new line after the loading bar

    return screenshots

def pageTurn():
    if (nextPageX, nextPageY) != mouse.get_position():
        mouse.move(nextPageX, nextPageY)
    mouse.press(button="left")
    time.sleep(1./120)
    mouse.release(button="left")

def pageTurnSetup() -> int:
    pagesToCapture = ""
    pagesToCapture = input("\nStep 2: Enter the amount of pages to capture: ")
    pagesToCapture = int(pagesToCapture)

    print("\nStep 3: Left-click to select where the 'Next Page' button is.")
    winput.hook_mouse(pageTurnMouseCallback)
    winput.wait_messages()
    winput.unhook_mouse()
    winput.stop()

    return pagesToCapture


def pageTurnMouseCallback(mouseEvent):
    global nextPageX, nextPageY
    if mouseEvent.action == winput.WM_LBUTTONDOWN:
        print("Page turn button selected at {}".format(mouseEvent.position))
        nextPageX = mouseEvent.position[0]
        nextPageY = mouseEvent.position[1]
        return winput.WP_STOP

#def clearCaptureRegion():
#    global captureRegionLeft, captureRegionTop, captureRegionRight, captureRegionBottom
#    captureRegionLeft = captureRegionTop = captureRegionRight = captureRegionBottom = 0

def captureRegionSetup():
    print("Step 1: Left-click and drag to capture the region of your screen you would like to be captured. " +
          "Right click to capture the full screen."
    )
    winput.hook_mouse(captureRegionMouseCallback)
    winput.wait_messages()
    winput.unhook_mouse()

    print("You selected a region starting at ({}, {}) and ending at ({}, {})".format(
        captureRegionLeft, 
        captureRegionTop, 
        captureRegionRight, 
        captureRegionBottom
    ))
    print("Your selected region size is: {}x{}".format(
            captureRegionRight - captureRegionLeft, 
            captureRegionBottom - captureRegionTop
    ))



def captureRegionMouseCallback(mouseEvent):
    global captureRegionLeft, captureRegionTop, captureRegionRight, captureRegionBottom
    if mouseEvent.action == winput.WM_RBUTTONDOWN:
        winput.WP_STOP
    if mouseEvent.action == winput.WM_LBUTTONDOWN:
        print("Left mousebutton pressed at {}".format(mouseEvent.position))
        captureRegionLeft = mouseEvent.position[0]
        captureRegionTop = mouseEvent.position[1]
    if mouseEvent.action == winput.WM_LBUTTONUP:
        print("Left mousebutton released at {}".format(mouseEvent.position))
        # covering for different dragging methods for consistent region selects
        if captureRegionLeft < mouseEvent.position[0]:
            captureRegionRight = mouseEvent.position[0]
        else:
            captureRegionRight = captureRegionLeft
            captureRegionLeft = mouseEvent.position[0]

        if captureRegionTop < mouseEvent.position[1]:
            captureRegionBottom = mouseEvent.position[1]
        else:
            captureRegionBottom = captureRegionTop
            captureRegionTop = mouseEvent.position[1]
        return winput.WP_STOP

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


eventActions: List[MouseAction or KeyboardAction] = []

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


