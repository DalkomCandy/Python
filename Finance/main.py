from risk_free_rates import find_risk_free_by_treasury as rft
from market_risk_premium import historical as mrp

from datetime import datetime as dt
from tkinter import *

#TODO
# CAPM = Risk_Free_rate + Beta * (Market_risk_premium - Risk_free_rate)

CODE = '042700.KS' # 한미반도체 코드
FIRST = '2000-01-04'
TODAY = '2022-04-22' #dt.strftime(dt.today(),"%Y-%m-%d")

def main():
    rf = rft()
    erp = mrp(stock_code = CODE, start = FIRST, end = TODAY, interval='3mo')
    rm = rf + erp

    print(rm)

# UI Setup

root = Tk()
root.geometry('200x150')
root.title("CAPM")

canvas = Canvas(height=200, width=200)
formula_label = Label(text="Rf + β*(Rm-Rf)")
formula_label.grid(row=0, column=0)

asset_label = Label(text="Asset")
asset_input = Text(width=10, height = 1)
asset_label.grid(row=1, column=0)
asset_input.grid(row=1, column=1)

date_label = Label(text="From-To")
date_start = Text(width=10, height = 1)
date_end = Text(width=10, height = 1)
date_label.grid(row=2, column=0)
date_start.grid(row=2, column=1)
date_end.grid(row=2, column=2)

option = StringVar()

Rf_label = Label(text = "Rf")
Rf_1 = Radiobutton(root, text="1", value="1", var = option)
Rf_2 = Radiobutton(root, text="2", value="2", var = option)
Rf_3 = Radiobutton(root, text="3", value="3", var = option)

Rf_label.grid(row=3, column = 0)
Rf_1.grid(row=3, column = 1)
Rf_2.grid(row=3, column = 2)
Rf_3.grid(row=3, column = 3)

Rm_label = Label(text = "Rm")
Rm_1 = Radiobutton(root, text="4", value="4", var = option)
Rm_2 = Radiobutton(root, text="5", value="5", var = option)
Rm_3 = Radiobutton(root, text="6", value="6", var = option)

Rm_label.grid(row=4, column = 0)
Rm_1.grid(row=4, column = 1)
Rm_2.grid(row=4, column = 2)
Rm_3.grid(row=4, column = 3)




root.mainloop()