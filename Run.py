import os
import nltk
from nltk.stem import WordNetLemmatizer
from InvertedIndex import *
from IO import *

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('vader_lexicon')


def count_occ(word, document):
    return document.count(word)


def show_ordered_docs(matching_documents):
    print("Documenti corrispondenti per indice:")
    print("{:<10} {:<60} {:<15}".format("ID", "Nome del file", "Sentimento"))
    print("-" * 95)

    # Ordina i documenti per indice
    matching_documents.sort(key=lambda x: x[0])

    for doc_id, filename, position in matching_documents:
        # Apri il file in modalità lettura
        with open("/home/pierdeb/Documenti/Docs_easy/"+filename, 'r') as file:
            # Leggi tutte le righe del file
            lines = file.readlines()

            # Assicurati che ci sia almeno una seconda riga
            if len(lines) >= 2:
                # Estrai la stringa dalla seconda riga
                second_line = lines[1].strip()  # Rimuovi eventuali spazi bianchi o caratteri di nuova riga

                # Stampa la stringa per verificarne l'estrazione
                #print("Stringa dalla seconda riga:", second_line)

                # Puoi salvare questa stringa in una nuova variabile, se necessario
                nuova_stringa = second_line

                # Ora puoi utilizzare la variabile 'nuova_stringa' per ulteriori operazioni, come desiderato
                #print("Nuova stringa:", nuova_stringa)
            else:
                print("Il file ha meno di due righe.")

        # Il file verrà chiuso automaticamente alla fine del blocco 'with'

        print("{:<10} {:<60} {:<15}".format(doc_id, nuova_stringa, position))
    print()

def show_sorted_docs(matching_documents):
    print("Documenti corrispondenti per sentiment:")
    print("{:<10} {:<60} {:<15}".format("ID", "Nome del file", "Sentimento"))
    print("-" * 95)

    # Ordina i documenti per sentimento in ordine decrescente
    matching_documents.sort(key=lambda x: x[2], reverse=True)

    for doc_id, filename, sentiment in matching_documents:
        # Apri il file in modalità lettura
        with open("/home/pierdeb/Documenti/Docs_easy/"+filename, 'r') as file:
            # Leggi tutte le righe del file
            lines = file.readlines()

            # Assicurati che ci sia almeno una seconda riga
            if len(lines) >= 2:
                # Estrai la stringa dalla seconda riga
                second_line = lines[1].strip()  # Rimuovi eventuali spazi bianchi o caratteri di nuova riga

                # Stampa la stringa per verificarne l'estrazione
                #print("Stringa dalla seconda riga:", second_line)

                # Puoi salvare questa stringa in una nuova variabile, se necessario
                nuova_stringa = second_line

                # Ora puoi utilizzare la variabile 'nuova_stringa' per ulteriori operazioni, come desiderato
                #print("Nuova stringa:", nuova_stringa)
            else:
                print("Il file ha meno di due righe.")

        # Il file verrà chiuso automaticamente alla fine del blocco 'with'

        print("{:<10} {:<60} {:<15}".format(doc_id, nuova_stringa, sentiment))
    print()

try:
    # Inserire il percorso con i documenti
    # documents_directory = "/home/pierdeb/Documenti/Docs_for_engine"
    documents_directory = "/home/pierdeb/Documenti/Docs_easy"

    word_lemmatizer = WordNetLemmatizer()
    # indice ha un lematizer suo
    indice = InvertedIndex(word_lemmatizer)
    print()
    print("{:<10} {:<60} {:<15}".format("ID", "Nome del file", "Sentimento"))
    print("-" * 95)

    import re


    # Funzione di ordinamento personalizzata
    def alphanumeric_sort(filename):
        # Divide il nome del file in parti alfabetiche e numeriche
        parts = re.split(r'(\d+)', filename)
        # Ordina le parti alfabetiche in ordine alfabetico
        # Ordina le parti numeriche in ordine numerico
        return [int(part) if part.isdigit() else part for part in parts]


    # Ottieni la lista dei file nella directory e ordinatela usando la funzione di ordinamento personalizzata
    file_list = sorted(os.listdir(documents_directory), key=alphanumeric_sort)

    # Itera sui file ordinati
    for doc_id, filename in enumerate(file_list, start=0):
        # Crea percorso completo: path+nomefile
        file_path = os.path.join(documents_directory, filename)

        # Leggi il contenuto del file e assegnalo a doc_text
        doc_text = read_file(file_path)

        # Aggiungi il documento all'indice
        indice.add_document(doc_id, filename, doc_text)

    print("SENTIMENTI")
    print(indice.sentiment_scores)
    print("LUNGHEZZE")
    print(indice.doc_lengths)

    query_string = ""
    while True:
        print("Enter your query:")
        query_string = input()
        if query_string == "_exit_":
            break
        if query_string == "_print_":
            indice.print_index_ordered()
            continue

        # mostra POSIZIONI esatte

        print("MATCHING 1")
# [( INDICE, NOME, POSIZIONE, FREQUENZA), ...]
        matching_positions = indice.search_documents(query_string)
        print(matching_positions)
        print()


        print("MATCHING 2")
# [( INDICE, NOME, SETNIMENTO), ...]
        matching_documents_simple = indice.search_documents_complex(query_string)
        print(matching_documents_simple)
        print()


 # [( INDICE, NOME, SETNIMENTO), ...]
        print("MATCHING 3")
        sorted_documents_simple = indice.search_by_sentiment_complex(query_string)
        print(sorted_documents_simple)
        print()

        if matching_positions:
            print()
            if matching_documents_simple:
                show_ordered_docs(matching_documents_simple)

            scelta = ""
            while True:
                if matching_positions:
                    try:
                        print(
                            "Quale documento vuoi aprire? Inserisci l'ID del documento da aprire o digita 'exit' per tornare al menu:")
                        print(
                            "Oppure digita (I) per passare ad ordinamento per indici, (S) per l'ordinamento per sentiment")
                        selected_input = input().lower()

                        if selected_input == 'exit':
                            break
                        elif selected_input == 'i':
                            show_ordered_docs(matching_documents_simple)
                        elif selected_input == 's':
                            show_sorted_docs(matching_documents_simple)


                        elif selected_input.isdigit():
                            selected_id = int(selected_input)
                            selected_doc_info = next(
                                (doc_info for doc_info in matching_positions if doc_info[0] == selected_id), None)

                            if selected_doc_info:
                                selected_doc_path = os.path.join(documents_directory, selected_doc_info[1])
                                indice.open_document_with_external_app(selected_doc_path)
                            else:
                                print("Documento non trovato con l'ID inserito.")
                        else:
                            print("Input non valido. Inserisci 'I', 'S', un ID numerico o 'exit'.")
                    except ValueError:
                        print("Inserisci un numero valido come ID.")
                else:
                    print("Non ci sono occorrenze da aprire.")


        else:
            print(f"Nessuna posizione trovata per la query '{query_string}'.")
    print("Goodbye!")
except KeyboardInterrupt:
    print("\nInterruzione con CTRL+c")
