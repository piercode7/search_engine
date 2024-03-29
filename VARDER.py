import pickle
# ricorda ordine inserimento
from collections import OrderedDict
# interazione con directory dell'os
import os
# processi di linguaggio
import nltk
# lista stopwords
from nltk.corpus import stopwords
# divide testo in tokens
from nltk.tokenize import word_tokenize
# riduce parole in forma base
from nltk.stem import WordNetLemmatizer
# manipolare string contiene punctuaction
import string
# per comandi del os da python
import subprocess
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
#from BM25Model import BM25Model


nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('vader_lexicon')


class InvertedIndex:
    def __init__(self, lemmatizer):
        self.index = {} # indice vuoto
        self.stop_words = set(stopwords.words('english')) # insieme stopwords
        self.lemmatizer = lemmatizer
        self.sentiment_scores = {} # dizionario sentimenti - ID
        self.doc_lengths = {}
#
    def add_document(self, doc_id, filename, text):
        words = word_tokenize(text)  # testo tokenizzato
        # Registra ID + Sentimento del documento
        sentiment_analyzer = SentimentIntensityAnalyzer()
        doc_sentiment = sentiment_analyzer.polarity_scores(text)
        self.sentiment_scores[doc_id] = doc_sentiment

        # Calcola la lunghezza del documento
        doc_length = len(words)
        self.doc_lengths[doc_id] = doc_length

        print("{:<10} {:<60} {:<30}".format(doc_id, filename, doc_sentiment['compound']))

        # Utilizza Counter per ottenere la frequenza di ciascuna parola nel documento
        word_frequencies = Counter(words)

        for position, w in enumerate(words):
            w_lower = w.lower()
            # se w non è in sw e in punct
            if w_lower not in self.stop_words and w_lower not in set(string.punctuation):
                # w è ridotto in forma base
                w_lemma = self.lemmatizer.lemmatize(w_lower)

                # crea lista di w, w è key, aggiungendo anche la frequenza di quella parola nel documento
                if w_lemma not in self.index:
                    self.index[w_lemma] = []

                self.index[w_lemma].append((doc_id, filename, position, word_frequencies[w]))



    def get_ordered_index(self):
        return OrderedDict(sorted(self.index.items()))



    def search_documents2(self, query):
        # Splitta la query in parole e lemmatizza ciascuna parola trasformandola in minuscolo
        query_words = query.split()
        query_lemmas = [self.lemmatizer.lemmatize(word.lower()) for word in query_words]

        matching_documents = set()

        for query_lemma in query_lemmas:
            if query_lemma in self.index:
                print()
                print("MATCHING DI " + query_lemma + ":")
                for doc_info in self.index[query_lemma]:
                    for position in doc_info[2:]:
                        matching_documents.add((doc_info[0], doc_info[1], position))
                        print(doc_info[0], doc_info[1], position)

        # Converti il set in una lista e ordina la lista per ID e posizione
        sorted_documents = sorted(list(matching_documents), key=lambda x: (x[0], x[2]))

        return sorted_documents


   # def search_by_bm25model(sel, query):


    def search_documents_complex(self, query):
        # Splitta la query in parole e lemmatizza ciascuna parola trasformandola in minuscolo
        query_words = query.split()
        query_lemmas = [self.lemmatizer.lemmatize(word.lower()) for word in query_words]

        matching_documents = []

        # Inizializza una lista vuota per contenere gli insiemi di documenti associati a ciascuna parola nella query
        matching_document_ids = []

        for query_lemma in query_lemmas:
            if query_lemma in self.index:
                document_ids_for_word = [(doc_info[0], doc_info[1]) for doc_info in self.index[query_lemma]]
                matching_document_ids.append(set(document_ids_for_word))

        # Calcola l'intersezione di tutti gli insiemi nella lista matching_document_ids
        if matching_document_ids:
            final_matching_documents_ids = set.intersection(*matching_document_ids)

        # Estrae informazioni per ciascun documento nell'insieme finale
            for doc_id, filename in final_matching_documents_ids:
            # Ottieni il sentiment del documento
                sentiment_score = self.sentiment_scores.get(doc_id, {'compound': 0.0})
            # Aggiungi id, nome e sentiment alla lista matching_documents
                matching_documents.append((doc_id, filename, sentiment_score['compound']))
        # Ordina la lista in base al sentiment
            matching_documents.sort(key=lambda x: x[0], reverse=False)
            
            return matching_documents
        return []

    def search_by_sentiment_complex(self, query):
        # Splitta la query in parole e lemmatizza ciascuna parola trasformandola in minuscolo
        query_words = query.split()
        query_lemmas = [self.lemmatizer.lemmatize(word.lower()) for word in query_words]


        matching_documents=[]
        # Inizializza una lista vuota per contenere gli insiemi di documenti associati a ciascuna parola nella query
        matching_document_ids = []

        for query_lemma in query_lemmas:
            if query_lemma in self.index:
                document_ids_for_word = [(doc_info[0], doc_info[1]) for doc_info in self.index[query_lemma]]
                matching_document_ids.append(set(document_ids_for_word))

        # Calcola l'intersezione di tutti gli insiemi nella lista matching_document_ids
        if matching_document_ids:

            final_matching_documents_ids = set.intersection(*matching_document_ids)

        # Estrae informazioni per ciascun documento nell'insieme finale
            for doc_id, filename in final_matching_documents_ids:
             # Ottieni il sentiment del documento
                sentiment_score = self.sentiment_scores.get(doc_id, {'compound': 0.0})
            # Aggiungi id, nome e sentiment alla lista matching_documents
                matching_documents.append((doc_id, filename, sentiment_score['compound']))
        # Ordina la lista in base al sentiment
            matching_documents.sort(key=lambda x: x[2], reverse=True)
            return matching_documents
        return []
    def open_document_with_external_app(self, doc_path):
        try:
            subprocess.Popen(["gedit", doc_path])
        except FileNotFoundError:
            print(
                f"Errore: Il programma esterno non è stato trovato. Assicurati che l'applicazione associata ai file di testo sia installata e accessibile.")

    def get_unique_document_names(self, documents):
        unique_names = set()
        result = []

        for doc_id, filename in documents:
            if filename not in unique_names:
                unique_names.add(filename)
                result.append((doc_id, filename))

        return result


    def save_index(self, filename):
        with open(filename, 'wb') as file:
            data_to_save = {'index': self.index}
            pickle.dump(data_to_save, file)

    def load_index(self, filename):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                self.index = data.get('index', {})
        except FileNotFoundError:
            # Se il file non esiste, inizializza un nuovo indice vuoto
            self.index = {}


def read_file(file_path):
    # r: lettura, utf-8: encoding
    # with: chiusura in seguito
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def show_ordered_docs(matching_documents):
    print()
    print("{:<15} {:<60} {:<15}".format("Documento ID", "Nome del file", "Sentimento"))
    print("-" * 90)

    for doc_id, filename, sentiment,  in matching_documents:
        print("{:<15} {:<60} {:<15}".format(doc_id, filename, sentiment))
    print()

def show_sorted_docs(matching_documents):
    print()
    print("{:<15} {:<60} {:<15}".format("Documento ID", "Nome del file", "Sentimento"))
    print("-" * 90)

    for doc_id, filename, sentiment in matching_documents:
        print("{:<15} {:<60} {:<15}".format(doc_id, filename, sentiment))
    print()


def count_occ(word, document):
    return document.count(word)



#documents_directory = "/home/pierdeb/Documenti/Docs_for_engine"
documents_directory = "/home/pierdeb/Documenti/Docs_for_engine"

word_lemmatizer = WordNetLemmatizer()
# indice ha un lematizer suo
indice = InvertedIndex(word_lemmatizer)
print()
print("{:<10} {:<60} {:<30}".format("ID", "Nome Documento    ", "Sentimento"))
print("-" * 80)
# for: attraversa i file in documents_directory
# os.listdir: da lista nomi dei file
# enumerate: mette contatore ID agli elem in lista
# start=1: parte da 1
for doc_id, filename in enumerate(os.listdir(documents_directory), start=1):
# crea percorso completo: path+namefile
    file_path = os.path.join(documents_directory, filename)
# legge contenuto percorso e lo da a doc_text
    doc_text = read_file(file_path)
# aggiunge doc all'indice

    indice.add_document(doc_id, filename, doc_text)

#for word, positions, in indice.index.items():
#   print(f"{word}: {positions}")

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

    matching_positions = indice.search_documents2(query_string)
    #print(matching_positions)
    matching_documents_simple = indice.search_documents_complex(query_string)
    sorted_documents_simple = indice.search_by_sentiment_complex(query_string)

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
                        show_sorted_docs(sorted_documents_simple)

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