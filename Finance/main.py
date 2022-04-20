from risk_free_rates import find_data_by_treasury as rft
from tkinter import *

window = Tk()
window.title("CAPM")
window.config(padx=50, pady=50)

canvas = Canvas(height=200, width=200)
formula_label = Label(text="Rf + β*(Rm-Rf)")
formula_label.grid(row=1, column = 0)

window.mainloop()

#TODO
# CAPM = Risk_Free_rate + Beta * (Market_risk_premium - Risk_free_rate)