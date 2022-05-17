#!/usr/bin/env python3
import numpy as np  #Seemingly only required for windows
import tkinter as tk

import game
import ui


t48 = game.Twenty48()
ui.init_ui(t48)

print(np.matrix(t48.board))
while True:
    ui.update_ui(t48)
    ui.window.update_idletasks()
    ui.window.update()
    if t48.hasLost:
        break
# Final update to show most recent move
ui.update_ui(t48)
tk.Label(ui.window,text="You lost").grid(row=t48.size,column=1)
# Make sure window doesn't freeze
while True:
    ui.window.update_idletasks()
    ui.window.update()
