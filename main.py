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

try:
    with open(provinces_file, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(':')
            provinces[key] = value
except FileNotFoundError:
    print("Nie można odnaleźć pliku z województwami.")

def get_job_offers(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

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
    
    except requests.exceptions.RequestException as e:
        print(f"Wystąpił problem z pobraniem strony: {e}")
        return[] 

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
    job_counter_label.config(text=f'Liczba ofert: {len(job_offers)} \n Województwo: {selected_province}')
    
def link_click(event):
    selected_element = table.selection()
    if selected_element:
        item = table.selection()[0]
        link = table.item(item, 'values')[3]
        webbrowser.open_new_tab(link)
    else:
        print("Something went wrong.")
        pass

def analyze_keywords():
    keywords = {}
    provinces_counter = {}

    for offer in get_all_job_offers(urls):
        title = offer['title'].lower()
        city = offer['city']
        black_words = ["praca", "zdalnie", "zaraz", "zatrudnię", "klienta", "zatrudnimy", "zatrudni"]
        for word in title.split():
            if len(word) > 4 and word not in black_words:
                keywords[word] = keywords.get(word, 0) + 1

        province = city.split(', ')[0].strip()
        provinces_counter[province] = provinces_counter.get(province, 0) + 1

    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)

    with open("data/analyze.txt", "w", encoding="UTF-8") as file:
        file.write("Top 5 słów kluczowych: \n")
        for word, freq in sorted_keywords[:5]:
            file.write(f"{word}: {freq}\n")
        file.write("\nTop 5 miast:\n")
        top_5_cities = sorted(provinces_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        for city, freq in top_5_cities:
            file.write(f"{city}: {freq}\n")
        file.write("\nDane dotyczące miast:\n")
        for city, freq in provinces_counter.items():
            file.write(f"{city}: {freq}\n")
        file.write("\nDane dotyczące słów kluczowych:\n")
        for word, count in sorted_keywords:
            file.write(f"{word}: {count}\n")

    keyword_label.config(text="Analiza zakończona. Wyniki zapisano do pliku data.txt")
    root.after(4000, lambda: keyword_label.config(text=""))


root = tk.Tk()
root.title("Michal Kasperek - olx web-scrap")

provinces_list = list(provinces.keys())
provinces_list.insert(0,"Wszystkie")

provinces_label = ttk.Label(root, text="Wybierz województwo:", font=("Times New Roman", 10))
provinces_label.pack()

provinces_combobox = ttk.Combobox(root, values = provinces_list, state='readonly', font=('Helvetica', 12))
provinces_combobox.current(0)
provinces_combobox.pack(pady=10)

table = ttk.Treeview(root, columns=('Tytuł', 'Miasto', 'Wynagrodzenie', 'Link'), show='headings')
table.heading('Tytuł', text='Tytuł')
table.heading('Miasto', text='Miasto')
table.heading('Wynagrodzenie', text='Wynagrodzenie')
table.heading('Link', text='Link')
table.pack(expand=True, fill='both')
table.column('Link', width=0, stretch=False)

#click_event 
table.tag_configure('link', font=('Helvetica', 10,))
table.bind('<Double-1>', link_click)

fetch_button = tk.Button(root, text="Pobierz oferty pracy", command=fetch_data, bg='#4CAF50', fg='white', font=('Helvetica', 12))
fetch_button.pack(pady=10)

analysis_button = tk.Button(root, text="Analizuj słowa kluczowe", command=analyze_keywords, bg='#FFA500', fg='white', font=('Helvetica', 12))
analysis_button.pack(pady=10)

job_counter_label = tk.Label(root, text="", font=('Helvetica', 12))
job_counter_label.pack(pady=5)

keyword_label = tk.Label(root, text="", font=('Helvetica', 12))
keyword_label.pack(pady=5)

root.mainloop()

