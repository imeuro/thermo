import sys
import os
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assetsdir = os.path.join(basedir, 'assets')
libdir = os.path.join(basedir, 'lib')
scriptsdir = os.path.join(basedir, 'scripts')

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in7
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button

btn1 = Button(5)                              # assign each button to a variable
btn2 = Button(6)                              # by passing in the pin number
btn3 = Button(13)                             # associated with the button
btn4 = Button(19)  

epd = epd2in7.EPD()
epd.init()
print("Clear...")
epd.Clear(0xFF)

def printToDisplay(string):
    
    # Drawing on the Horizontal image. We must create an image object for both the black layer
    # and the red layer, even if we are only printing to one layer
    HBlackImage = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)  # 298*126

    # create a draw object and the font object we will use for the display
    draw = ImageDraw.Draw(HBlackImage)
    font = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 18)

    # draw the text to the display. First argument is starting location of the text in pixels
    draw.text((25, 65), string, font = font, fill = 0)
    
    # Add the images to the display. Both the black and red layers need to be passed in, even
    # if we did not add anything to one of them
    epd.display(epd.getbuffer(HBlackImage))
    
# Handle button presses
# param Button (passed from when_pressed)
def handleBtnPress(btn):
    
    # get the button pin number
    pinNum = btn.pin.number
    
    # python hack for a switch statement. The number represents the pin number and
    # the value is the message we will print
    switcher = {
        5: "Hello, World!",
        6: "This is my first \nRPi project.",
        13: "Hope you liked it.",
        19: "Goodbye"
    }
    
    # get the string based on the passed in button and send it to printToDisplay()
    msg = switcher.get(btn.pin.number, "Error")
    printToDisplay(msg)
    
# tell the button what to do when pressed
btn1.when_pressed = handleBtnPress
btn2.when_pressed = handleBtnPress
btn3.when_pressed = handleBtnPress
btn4.when_pressed = handleBtnPress




from signal import pause
pause()