from tkinter import *
from tkinter import messagebox
from random import choice, randint, shuffle
import pyperclip
import json

# -------------------------------SEARCH WEBSITE--------------------------------------#
def search():
    search_website = website_entry.get()
    if len(search_website) == 0:
        messagebox.showinfo(title = "Warning",
                            message = "Need Website Name")
    else:
        try:
            with open("data.json", "r") as data_file:
                data = json.load(data_file)
                
                try:
                    email = data[search_website]['email']
                    password = data[search_website]['password']
                    messagebox.showinfo(title = "Summary",
                    message = 
                    f"These are following Infos "
                    f"\nEmail : {email}"
                    f"\nPassword : {password}")
                    
                except KeyError:
                    messagebox.showinfo(title="Warning",
                                        message = f"No password saved with {search_website}")

        except FileNotFoundError:
            messagebox.showinfo(title="Warning",
                                message = "You don't have Password saved")
            
# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate():
    password_entry.delete(0, END)
    low_letters = list(chr(i) for i in range(65, 91))
    high_letters = list(chr(i) for i in range(97, 123))

    letters = low_letters + high_letters
    symbols = list(chr(i) for i in range(33 ,44))
    numbers = list(str(i) for i in range(0,10))    

    password_letters = [choice(letters) for _ in range(randint(8, 10))]
    password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
    password_numbers = [choice(numbers) for _ in range(randint(2, 4))]

    password_list = password_letters + password_numbers + password_symbols

    shuffle(password_list)

    password = "".join(password_list)
    password_entry.insert(0, password)
    
    pyperclip.copy(password)
    
# ---------------------------- SAVE PASSWORD ------------------------------- #
def save():
    
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    new_data = {website : {
        "email" : email,
        "password" : password,
    }
}
    
    if len(password) == 0 or len(website) == 0:
        messagebox.showinfo(title="Warning", 
                            message = "Please don't leave any fields empty")
        return False
    
    messagebox.askokcancel(title = website, 
                            message = 
                        f"These are the details entered: "
                        f"\nEmail : {email}"
                        f"\nPassword : {password}"
                        f"\nIs it ok to save?")
    
    try:
        with open("data.json", "r") as data_file:  
            data = json.load(data_file)
            data.update(new_data)
            
        with open("data.json", "w") as data_file:
            json.dump(data, data_file, indent=4)
            
    except FileNotFoundError:
        with open("data.json", "w") as data_file:
            json.dump(new_data, data_file, indent=4)

    website_entry.delete(0, END)
    password_entry.delete(0, END)
        
# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

canvas = Canvas(height=200, width=200)
logo_img = PhotoImage(file="C:\\Code\\Python\\Projects\\Tkinter\\Password_Manager\\logo.png")
canvas.create_image(100, 100, image=logo_img)
# canvas.grid(row=0, column=1)

#Labels
website_label = Label(text="Website:")
website_label.grid(row=1, column=0)
email_label = Label(text="Email/Username:")
email_label.grid(row=2, column=0)
password_label = Label(text="Password:")
password_label.grid(row=3, column=0)

#Entries
website_entry = Entry(width=21)
website_entry.grid(row=1, column=1)
website_entry.focus()
email_entry = Entry(width=36)
email_entry.grid(row=2, column=1, columnspan=2)
email_entry.insert(0, "gyumin0815@gmail.com")
password_entry = Entry(width=21)
password_entry.grid(row=3, column=1)

# Buttons
search_button = Button(text="Search", width=13, command=search)
search_button.grid(row=1, column=2)
generate_password_button = Button(text="Generate Password", command=generate)
generate_password_button.grid(row=3, column=2)
add_button = Button(text="Add", width=36, command=save)
add_button.grid(row=4, column=1, columnspan=2)

window.mainloop()