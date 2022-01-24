from importlib.metadata import entry_points
from tkinter import *
from random import *
import numpy as np

FONT_NAME = 'a아시아헤드1'
YELLOW = "#f7f5dd"

one = 0
two = 0
three = 0
four = 0
five = 0
fail = 0

window = Tk()
window.title("Lotto")
window.config(padx = 100, pady = 50, bg = YELLOW)

# Label
numbers = np.random.choice(45, 7)

def count(my_numbers):
    count = 0
    bonus = 0
    for i in my_numbers:
        if i in numbers[:6]:
            count += 1
        if i in numbers[6:]:
            bonus += 1
    return count, bonus

def run():
    global one
    global two
    global three
    global four
    global five
    global fail
    num = 10000
    
    while num != 0:
        my_numbers = np.random.choice(45, 6)
        my_answer_1_label.config(text = my_numbers[0])
        my_answer_2_label.config(text = my_numbers[1])
        my_answer_3_label.config(text = my_numbers[2])
        my_answer_4_label.config(text = my_numbers[3])
        my_answer_5_label.config(text = my_numbers[4])
        my_answer_6_label.config(text = my_numbers[5])

        price, bonus = count(my_numbers)
        if price == 6:
            one += 1
            rank_1_count.config(text = f"{one}")
        elif price + bonus == 6:
            two += 1
            rank_2_count.config(text = f"{two}")
        elif price + bonus == 5:
            three += 1
            rank_3_count.config(text = f"{three}")
        elif price + bonus == 4:
            four += 1
            rank_4_count.config(text = f"{four}")
        elif price + bonus == 3:
            five += 1
            rank_5_count.config(text = f"{five}")
        else:
            fail += 1
            rank_6_count.config(text = f"{fail}")
        num -= 1
        
        
website_entry = Entry(width=21)
website_entry.grid(row=10, column=0)
website_entry.focus()
title_label = Label(text="Lotto", font = (FONT_NAME, 30), bg = YELLOW)
title_label.grid(row = 0, column = 1, columnspan=6)

canvas = Canvas(width = 200, height = 224, bg = YELLOW, highlightthickness=0)

same_label = Label(text="당첨 번호", font = (FONT_NAME, 10), bg = YELLOW)
same_label.grid(row = 1, column = 0)

answer_1_label = Label(text = numbers[0], font = (FONT_NAME, 10), bg = YELLOW)
answer_1_label.grid(row = 1, column = 1)

answer_2_label = Label(text = numbers[1], font = (FONT_NAME, 10), bg = YELLOW)
answer_2_label.grid(row = 1, column = 2)

answer_3_label = Label(text = numbers[2], font = (FONT_NAME, 10), bg = YELLOW)
answer_3_label.grid(row = 1, column = 3)

answer_4_label = Label(text = numbers[3], font = (FONT_NAME, 10), bg = YELLOW)
answer_4_label.grid(row = 1, column = 4)

answer_5_label = Label(text = numbers[4], font = (FONT_NAME, 10), bg = YELLOW)
answer_5_label.grid(row = 1, column = 5)

answer_6_label = Label(text = numbers[5], font = (FONT_NAME, 10), bg = YELLOW)
answer_6_label.grid(row = 1, column = 6)

answer_7_label = Label(text = numbers[6], font = (FONT_NAME, 10), bg = YELLOW)
answer_7_label.grid(row = 1, column = 7)

my_label = Label(text = "내 번호", font = (FONT_NAME, 10), bg = YELLOW)
my_label.grid(row = 2, column = 0)

my_answer_1_label = Label(text = "", font = (FONT_NAME, 10), bg = YELLOW)
my_answer_1_label.grid(row = 2, column = 1)

my_answer_2_label = Label(text = "", font = (FONT_NAME, 10), bg = YELLOW)
my_answer_2_label.grid(row = 2, column = 2)

my_answer_3_label = Label(text = "", font = (FONT_NAME, 10), bg = YELLOW)
my_answer_3_label.grid(row = 2, column = 3)

my_answer_4_label = Label(text = "", font = (FONT_NAME, 10), bg = YELLOW)
my_answer_4_label.grid(row = 2, column = 4)

my_answer_5_label = Label(text = "", font = (FONT_NAME, 10), bg = YELLOW)
my_answer_5_label.grid(row = 2, column = 5)

my_answer_6_label = Label(text = "", font = (FONT_NAME, 10), bg = YELLOW)
my_answer_6_label.grid(row = 2, column = 6)

rank_1 = Label(text = "1등", font = (FONT_NAME, 10), bg = YELLOW)
rank_1.grid(row = 3, column = 0)
rank_1_count = Label(text = "0", font = (FONT_NAME, 10), bg = YELLOW)
rank_1_count.grid(row = 3, column = 7)

rank_2 = Label(text = "2등", font = (FONT_NAME, 10), bg = YELLOW)
rank_2.grid(row = 4, column = 0)
rank_2_count = Label(text = "0", font = (FONT_NAME, 10), bg = YELLOW)
rank_2_count.grid(row = 4, column = 7)

rank_3 = Label(text = "3등", font = (FONT_NAME, 10), bg = YELLOW)
rank_3.grid(row = 5, column = 0)
rank_3_count = Label(text = "0", font = (FONT_NAME, 10), bg = YELLOW)
rank_3_count.grid(row = 5, column = 7)

rank_4 = Label(text = "4등", font = (FONT_NAME, 10), bg = YELLOW)
rank_4.grid(row = 6, column = 0)
rank_4_count = Label(text = "0", font = (FONT_NAME, 10), bg = YELLOW)
rank_4_count.grid(row = 6, column = 7)

rank_5 = Label(text = "5등", font = (FONT_NAME, 10), bg = YELLOW)
rank_5.grid(row = 7, column = 0)
rank_5_count = Label(text = "0", font = (FONT_NAME, 10), bg = YELLOW)
rank_5_count.grid(row = 7, column = 7)

rank_6 = Label(text = "꽝", font = (FONT_NAME, 10), bg = YELLOW)
rank_6.grid(row = 8, column = 0)
rank_6_count = Label(text = "0", font = (FONT_NAME, 10), bg = YELLOW)
rank_6_count.grid(row = 8, column = 7)

button = Button(text = "시작", command = run)
button.grid(row = 9, column = 7)


window.mainloop()