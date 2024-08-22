import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import re
import streamlit as st

st.set_page_config(layout="wide", page_title="Lead Generator Tool")

def enrich_data_from_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', content)
        phone = re.search(r'\b\d{2,4}[-.\s]??\d{3,4}[-.\s]??\d{4}\b', content)
        return email.group(0) if email else '', phone.group(0) if phone else ''
    except:
        return '', ''

def save_to_csv(data, filename):
    headers = ['Nome', 'Categoria', 'Telefono', 'Email', 'Sito Web', 'Numero Recensioni', 'Valutazione Media', 'Score']
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        data.sort(key=lambda x: -x[-1])
        writer.writerows(data)

def calculate_score(row):
    score = 0
    # Numero Recensioni
    try:
        num_reviews = int(row[5]) if row[5].isdigit() else 0
    except ValueError:
        num_reviews = 0
    score += num_reviews * 0.5

    # Valutazione Media
    try:
        avg_rating = float(row[6].replace(' ⭐', ''))
    except ValueError:
        avg_rating = 0
    score += avg_rating * 2

    # Email
    if row[3]:
        score += 10

    # Telefono
    if row[2]:
        score += 10

    return score


def process_html_data(file, enrich=False, only_first_email=False):
    
    soup = BeautifulSoup(file, 'html.parser')
    
    total_leads = leads_with_contact_info = leads_enriched = leads_with_full_contact = leads_with_website = 0
    all_data = []

    rows = soup.find_all(class_='tabulator-row')
    total_rows = len(rows)
    progress_bar = st.progress(0)
    for i, row in enumerate(rows):
        cells = row.find_all(class_='tabulator-cell')
        email = cells[2].get_text(strip=True).split(',')[0] if only_first_email else cells[2].get_text(strip=True)
        website = cells[3].get_text(strip=True)
        data_row = [
            cells[0].get_text(strip=True), cells[13].get_text(strip=True),
            cells[1].get_text(strip=True), email,
            website if website else '',
            cells[14].get_text(strip=True) if cells[14].get_text(strip=True) else '0',
            cells[15].get_text(strip=True) + ' ⭐' if cells[15].get_text(strip=True) else '0 ⭐'
        ]
        
        total_leads += 1
        if website:
            leads_with_website += 1
            if cells[1].get_text(strip=True) or email:
                leads_with_contact_info += 1
                if cells[1].get_text(strip=True) and email:
                    leads_with_full_contact += 1
                if enrich and website and not (cells[1].get_text(strip=True) and email):
                    email_found, phone_found = enrich_data_from_website(website)
                    data_row[2] = data_row[2] if data_row[2] else phone_found
                    data_row[3] = data_row[3] if data_row[3] else email_found
                    if email_found or phone_found:
                        leads_enriched += 1
                data_row.append(calculate_score(data_row))
                all_data.append(data_row)
        
        progress_bar.progress((i + 1) / total_rows)

    df = pd.DataFrame(all_data, columns=['Nome', 'Categoria', 'Telefono', 'Email', 'Sito Web', 'Numero Recensioni', 'Valutazione Media', 'Score'])
    save_to_csv(all_data, 'all_leads.csv')
    save_to_csv([row for row in all_data if row[2] and row[3]], 'profiled_leads.csv')
    save_to_csv([row for row in all_data if row[3]], 'email_leads.csv')
    
    return total_leads, leads_with_website, leads_with_contact_info, leads_enriched, leads_with_full_contact, df

def streamlit_app():
    st.title("🚀 Generatore di Lead per Google Maps One-Time-Payment")
    with st.expander("Tutorial: Come Installare l'Ultimo Scraper per Google Maps"):
            st.markdown("""
            ### Come Installare l'Ultimo Scraper per Google Maps
            
            Segui questa guida passo passo per installare l'ultima versione dello scraper:
            """)

            st.write("#### 1. **Scarica la Versione più Recente (1.2.0):**")
            st.markdown("""
            Clicca sul link qui sotto per scaricare l'ultima versione:
            [Scarica google_maps_scraper_v1.2.0.zip](https://www.gmapsemailextractor.com/downloads/google_maps_scraper_v1.2.0.zip)
            """)
            st.image("https://www.gmapsemailextractor.com/_next/static/media/unzip.bcfa646d.png", caption="Esempio di file scaricato")

            st.write("#### 2. **Decomprimi il File Scaricato:**")
            st.image("https://www.gmapsemailextractor.com/_next/static/media/load_unpacked.3c1e9c2c.png", caption="Decomprimi il file")

            st.write("#### 3. **Apri la Pagina delle Estensioni in Chrome:**")
            st.markdown("""
            Apri la pagina delle estensioni, attiva la modalità Sviluppatore e clicca su 'Carica scompattato'.
            """)
            st.image("https://www.gmapsemailextractor.com/_next/static/media/selectfiles.a4beb8b2.png", caption="Seleziona i file dell'estensione")

            st.write("#### 4. **Fissa l'Estensione nella Barra degli Strumenti di Chrome:**")
            st.image("https://www.gmapsemailextractor.com/_next/static/media/pin.93cc2a38.png", caption="Fissa l'estensione")

            st.write("#### 5. **Usa l'Estensione per Trovare Lead B2B da Google Maps.**")
            st.image("https://www.gmapsemailextractor.com/_next/static/media/popup.6c32e4a0.png", caption="Popup dell'estensione")

            st.write("#### 6. **Esempio di Dati Estratti da Google Maps: NON esportare direttamente dal dashboard!**")
            st.markdown("NON esportare direttamente dal dashboard! Altrimenti dovrai pagare di nuovo per i dati.")
            st.image("https://www.gmapsemailextractor.com/_next/static/media/demodata.9a54d092.png", caption="Dati di esempio")

            st.write("#### 7. **Scarica la Pagina Utilizzando CTRL-S e Caricala Qui.**")
    
    
    uploaded_file = st.file_uploader("Carica il tuo file HTML", type="html")
    token = st.text_input("Inserisci il tuo token di accesso", type="password")
    col1, col2,col3 = st.columns(3)
    enrich_option = col1.checkbox("Arricchisci i dati visitando i siti web? 🌐")
    first_email_only = col2.checkbox("Prendo solo la prima email disponibile? 📧")
    if col3.button("Elabora Dati 🔄") and token=="AleAI":
        with st.spinner('Elaborazione in corso...'):
            file_path = uploaded_file.name
            total_leads, leads_with_website, leads_with_contact_info, leads_enriched, leads_with_full_contact, data = process_html_data(uploaded_file, enrich=enrich_option, only_first_email=first_email_only)
            cola, colb, colc, cold, cole = st.columns(5)
            st.success("Elaborazione completata con successo! 🎉")
            cola.metric("Lead Totali", total_leads)
            colb.metric("Lead con Sito Web", leads_with_website)
            colc.metric("Lead con Informazioni di Contatto", leads_with_contact_info)
            cold.metric("Lead Arricchiti", leads_enriched)
            cole.metric("Lead Profilati Completi", leads_with_full_contact)
            #sort data by score
            data = data.sort_values(by='Score', ascending=False)
            st.dataframe(data)
            colf, colg, colh = st.columns(3)
            colf.download_button("Scarica Tutti i Lead", data=open('all_leads.csv', "rb"), file_name='all_leads.csv')
            colg.download_button("Scarica Lead Chiamabili Profilati", data=open('profiled_leads.csv', "rb"), file_name='profiled_leads.csv')
            colh.download_button("Scarica Lead Email", data=open('email_leads.csv', "rb"), file_name='email_leads.csv')

if __name__ == "__main__":
    streamlit_app()
