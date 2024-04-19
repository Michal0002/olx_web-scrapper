import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Michal Kasperek - olx web-scrap")
provinces = []
provinces.insert(0,"Wszystkie")

provinces_label = ttk.Label(root, text="Wybierz województwo:", font=("Times New Roman", 10))
provinces_label.pack()
provinces_combobox = ttk.Combobox(root, values = provinces, state='readonly')
provinces_combobox.current(0)
provinces_combobox.pack()

table = ttk.Treeview(root, columns=('Data dodania', 'Tytuł', 'Miasto', 'Wynagrodzenie', 'Link'), show='headings')
table.heading('Data dodania', text='Data dodania')
table.heading('Tytuł', text='Tytuł')
table.heading('Miasto', text='Miasto')
table.heading('Wynagrodzenie', text='Wynagrodzenie')
table.heading('Link', text='Link')
table.pack(expand=True, fill='both')

fetch_button = tk.Button(root, text="Pobierz oferty pracy", command="")
fetch_button.pack()

root.mainloop()