import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import webbrowser

urls = [
    'https://www.olx.pl/praca',
    'https://www.olx.pl/praca/?page=2',
    'https://www.olx.pl/praca/?page=3',
    'https://www.olx.pl/praca/?page=4'
]

provinces_file = "data/provinces.txt"
provinces = {}

with open(provinces_file, 'r', encoding='utf-8') as file:
    for line in file:
        key, value = line.strip().split(':')
        provinces[key] = value

def get_job_offers(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    offers = soup.find_all('div', class_='css-1sw7q4x')
    job_data = []
    for offer in offers:
        title_element = offer.find('h6', class_='css-1b96xlq')
        link_element = offer.find('a', class_='css-13gxtrp')
        city_element = offer.find('span', class_='css-d5w927')
        contract_element = offer.find('p', class_='css-1jnbm5x')
        # date_element = offer.find('p', class_='css-l3c9zc')
        if title_element and link_element and city_element and contract_element:
            title = title_element.text.strip()
            link = link_element['href']
            city = city_element.text.strip()
            contract = contract_element.text.strip()
            # date = date_element.text.strip()
            # if "dzisiaj" in date.lower():
            #     date = datetime.now().strftime('%d %B %Y')
            job_data.append({'title': title, 'link': link, 'city': city, 'contract': contract})
    return job_data

def get_all_job_offers(urls):
    all_job_offers = []
    for url in urls:
        job_offers = get_job_offers(url)
        all_job_offers.extend(job_offers)
    return all_job_offers

def fetch_data():
    selected_province = provinces_combobox.get()
    print(selected_province)
    if selected_province == 'Wszystkie':
        filtered_urls = urls
    elif selected_province != 'Wszystkie':   
        filtered_urls = [f"https://www.olx.pl/praca/{provinces[selected_province]}/"]
    job_offers = get_all_job_offers(filtered_urls)
    table.delete(*table.get_children())
    for i, offer in enumerate(job_offers):
        # Wstawienie danych ofert pracy do tabeli, pomijając kolumnę "Link"
        table.insert('', 'end', values=(offer['title'], offer['city'], offer['contract'], f'https://www.olx.pl{offer['link']}'), tags=('link',))

def link_click(event):
    selected_element = table.selection()
    if selected_element:
        item = table.selection()[0]
        link = table.item(item, 'values')[3]
        webbrowser.open_new_tab(link)
    else:
        print("Something went wrong.")
        pass

root = tk.Tk()
root.title("Michal Kasperek - olx web-scrap")

provinces_list = list(provinces.keys())
provinces_list.insert(0,"Wszystkie")

provinces_label = ttk.Label(root, text="Wybierz województwo:", font=("Times New Roman", 10))
provinces_label.pack()
provinces_combobox = ttk.Combobox(root, values = provinces_list, state='readonly')
provinces_combobox.current(0)
provinces_combobox.pack()

table = ttk.Treeview(root, columns=('Tytuł', 'Miasto', 'Wynagrodzenie', 'Link'), show='headings')
table.heading('Tytuł', text='Tytuł')
table.heading('Miasto', text='Miasto')
table.heading('Wynagrodzenie', text='Wynagrodzenie')
table.heading('Link', text='Link')
table.pack(expand=True, fill='both')
table.column('Link', width=0, stretch=False)

#click_event 
table.tag_configure('link',)
table.bind('<Double-1>', link_click)

fetch_button = tk.Button(root, text="Pobierz oferty pracy", command=fetch_data)
fetch_button.pack()

root.mainloop()

