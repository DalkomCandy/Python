from tkinter import *
# ---------------------------- PASSWORD GENERATOR ------------------------------- #

# ---------------------------- SAVE PASSWORD ------------------------------- #
def add_clicked():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    print(website)
    f = open("My Website Info", "a")
    f.write('---------------------------' + '\n')
    f.write("Website : " + website + '\n')
    f.write("Email : " + email+ '\n')
    f.write("Password : " + password+ '\n')
    f.write('---------------------------' + '\n')
    f.close()
    website_entry.delete(0, END)
    password_entry.delete(0, END)
# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Password_Manager")
window.config(padx = 20, pady = 20)

canvas = Canvas(height=200, width=200)
logo_img = PhotoImage(file = "logo.png")
canvas.create_image(100, 100, image = logo_img)
canvas.grid(row=0, column = 1)
# Labels
website_label = Label(text = "Website")
website_label.grid(row=1, column = 0)
email_label = Label(text="Email/Username")
email_label.grid(row=2, column = 0)
password_label = Label(text = "password")
password_label.grid(row=3, column = 0)

# Entries
website_entry = Entry(width=35)
website_entry.grid(row=1, column = 1, columnspan=2)
email_entry = Entry(width = 35)
email_entry.grid(row=2, column = 1, columnspan=2)
email_entry.insert(0, "gyumin1009@naver.com")
password_entry = Entry(width=21)
password_entry.grid(row=3, column = 1)

# Buttons
generate_password_button = Button(text="Generate Password")
generate_password_button.grid(row=3, column=2)
add_button = Button(text="Add", width=36, command=add_clicked)
add_button.grid(row=4, column=1)


window.mainloop()