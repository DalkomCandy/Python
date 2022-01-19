from tkinter import *
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
REPS = 0
timer = None
# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    window.after_cancel(timer)
    canvas.itemconfig(timer_text, text = "00:00")
    title_label.config(text = "Timer", fg = GREEN)
    check_marks.config(text= "")
    global REPS
    REPS = 0
# ---------------------------- TIMER MECHANISM ------------------------------- # 
def start_timer():
    global REPS
    REPS += 1
    if REPS % 8 == 0:
        count_down(LONG_BREAK_MIN*60)
        title_label.config(text = "Break", fg = RED)

    elif REPS % 2 == 0:
        count_down(SHORT_BREAK_MIN*60)
        title_label.config(text = "Break", fg = PINK)
        check_marks.config(text= "✔" * int(REPS / 2))

    else:
        count_down(WORK_MIN*60)
        title_label.config(text = "Work", fg = GREEN)
    

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 
def count_down(count):
    canvas.itemconfig(timer_text, text = "{}:{}".format(str(count // 60).zfill(2), str(count % 60).zfill(2)))
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)
    else:
        start_timer()

# ---------------------------- UI SETUP ------------------------------- #

window = Tk()

window.title("Pomodoro")
window.config(padx = 100, pady = 50, bg = YELLOW)

title_label = Label(text = "Timer", fg = GREEN, bg = YELLOW, font = (FONT_NAME, 50))
title_label.grid(column=1, row = 0)

canvas = Canvas(width = 200, height = 224, bg = YELLOW, highlightthickness=0)
my_image = PhotoImage(file ="C:\\Code\\Python\\Projects\\Tkinter\\Pomodoro\\tomato.png")

canvas.create_image(100, 112, image = my_image)
timer_text = canvas.create_text(100, 130, text = "00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(column = 1, rows = 1)

start_button = Button(text = "Start", highlightthickness = 0, command = start_timer)
start_button.grid(column = 0, row = 2)

reset_button = Button(text = "Reset", highlightthickness = 0, command = reset_timer)
reset_button.grid(column = 2, row = 2)

check_marks = Label(text ="", fg = GREEN, bg = YELLOW)
check_marks.grid(column = 1, row = 3)

window.mainloop()