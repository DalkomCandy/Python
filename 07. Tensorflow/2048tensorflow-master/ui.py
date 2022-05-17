import tkinter as tk

global colors
colors = {0:"#CCC0B3",2:"#EDE3DA",4:"#ECDFC8",8:"#F1B07C",16:"#F39568",32:"#F47D64",64:"#F46146",128:"#EDCF72",256:"#EDCC61",512:"#EDC850",1024:"#E2B913",2048:"#ECC400"}


def init_ui(game):
    global window
    global ui_board
    global score
    window = tk.Tk()

    # Fill UI board with zeroes
    ui_board = [[tk.Label(window,text="0",font="Helvetica 18 bold") for i in range(game.size)] for j in range(game.size)]
    # Setup geometry managers for each label in ui_board
    row_iterator = 0
    for row in ui_board:
        # Make rows fill up extra space
        window.grid_rowconfigure(row_iterator,minsize=100,weight=1)
        for label_iterator in range(0,len(row)):
            ui_board[row_iterator][label_iterator].grid(row=row_iterator,column=label_iterator,sticky="nsew")
            window.grid_columnconfigure(label_iterator,minsize=100,weight=1)
        row_iterator += 1
    # Create score label at bottom of screen
    score = tk.Label(text=game.score+1)
    score.grid(row=game.size,column=0)
    # Bind arrow keys to shift board
    window.bind("<Up>", lambda a: game.shift_up())
    window.bind("<Right>", lambda a: game.shift_right())
    window.bind("<Down>", lambda a: game.shift_down())
    window.bind("<Left>", lambda a: game.shift_left())


def update_ui(game):
    row_iterator = 0
    # Update all labels with backend values
    for row in ui_board:
        for label_iterator in range(0,len(row)):
            new_value = game.board[row_iterator][label_iterator]
            try:
                # 0 tiles should be blank
                if new_value == 0:
                    ui_board[row_iterator][label_iterator].config(text=" ",bg=colors[new_value])
                else:
                    ui_board[row_iterator][label_iterator].config(text=new_value,bg=colors[new_value])
            # If color is not in dictionary fallback to red
            except KeyError:
                ui_board[row_iterator][label_iterator].config(text=new_value,bg="#FF0000")
        row_iterator += 1
    score.config(text="Score: " + str(game.score))
