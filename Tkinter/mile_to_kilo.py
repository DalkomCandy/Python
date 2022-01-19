import tkinter

window = tkinter.Tk()
window.title("Miles to Kilometer")
window.minsize(width = 500, height = 300)
window.config(padx = 20, pady = 20)

# Label

miles_label = tkinter.Label(text="Miles", font=("Arial", 10))
km_label = tkinter.Label(text="Km", font=("Arial", 10))
same_label = tkinter.Label(text="is equal to", font=("Arial", 10))

miles_label.grid(column = 2, rows = 1)
km_label.grid(column = 2, rows = 1)
same_label.grid(column = 0, row = 1)

answer_label = tkinter.Label(text = "0", font=("Arial", 10))
answer_label.grid(column=1, row=1)

# Button
def button_clicked():
    new_int = input_1.get()
    my_answer = (int(new_int)) * 1.60934
    answer_label.config(text = str(round(my_answer, 2)))

Button_1 = tkinter.Button(text="Calculate", command=button_clicked)
Button_1.grid(column = 1, row = 2)

# Entry - 텍스트를 입력받는 컴포넌트
input_1 = tkinter.Entry(width=10)

input_1.grid(column = 1,row = 0)



window.mainloop()