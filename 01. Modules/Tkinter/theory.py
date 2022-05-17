import tkinter

window = tkinter.Tk()
window.title("My First GUI Program")
window.minsize(width = 500, height = 300)
window.config(padx = 20, pady = 20)

# Label

my_label = tkinter.Label(text="I am a Label", font=("Arial", 24, "bold"))
my_label.grid(column=0, row=0)

# Button
def button_clicked():
    new_text = input.get()
    my_label.config(text = new_text)
    print("I got clicked")

Button = tkinter.Button(text="Click me", command=button_clicked)
Button_1 = tkinter.Button(text="Click me", command=button_clicked)
Button.grid(column=1, row = 1)
Button_1.grid(column=2, row = 0)

# Entry - 텍스트를 입력받는 컴포넌트
input = tkinter.Entry(width=10)
input.get()
input.grid(column=3,row=2)


window.mainloop()