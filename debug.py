import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk

def update_image():
    global img, img_label
    alpha = scale.get() / 100
    overlay = img.copy()
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
    img_label.config(image=img_tk)
    img_label.image = img_tk

def toggle_checkbox():
    if var1.get() == 1:
        print("Checkbox 1 is checked")
    else:
        print("Checkbox 1 is unchecked")
    if var2.get() == 1:
        print("Checkbox 2 is checked")
    else:
        print("Checkbox 2 is unchecked")

# Load the image
img = cv2.imread('debug.png')
if img is None:
    raise FileNotFoundError("The image file 'debug.pdf' was not found.")

# Create the main window
root = Tk()
root.title("OpenCV Window with Slide Bar and Checkboxes")

# Convert the image to a format suitable for Tkinter
img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))

# Create a label to display the image
img_label = Label(root, image=img_tk)
img_label.pack()

# Create a scale (slide bar)
scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=lambda x: update_image())
scale.pack()

# Create checkboxes
var1 = IntVar()
var2 = IntVar()
checkbox1 = Checkbutton(root, text="Checkbox 1", variable=var1, command=toggle_checkbox)
checkbox2 = Checkbutton(root, text="Checkbox 2", variable=var2, command=toggle_checkbox)
checkbox1.pack()
checkbox2.pack()

# Start the main loop
root.mainloop()