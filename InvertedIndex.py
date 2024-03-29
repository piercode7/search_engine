import pickle
import string
import subprocess

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter, OrderedDict
from Sentiment import *


class InvertedIndex:
    def __init__(self, lemmatizer):
        self.index = {}  # indice vuoto
        self.stop_words = set(stopwords.words('english'))  # insieme stopwords
        self.lemmatizer = lemmatizer
        self.sentiment_scores = {}  # dizionario sentimenti - ID
        self.doc_lengths = {}

    def add_document(self, doc_id, filename, text):
        doc_sentiment = extract_sentiment(text)
        self.sentiment_scores[doc_id] = doc_sentiment

        words = word_tokenize(text.lower())  # Tokenizza il testo

        # Calcola la lunghezza del documento
        doc_length = len(words)
        self.doc_lengths[doc_id] = doc_length

        print("{:<10} {:<60} {:<30}".format(doc_id, filename, doc_sentiment))

        # Utilizza Counter per ottenere la frequenza di ciascuna parola nel documento
        word_frequencies = Counter(words)

        # Dentro il ciclo di tokenizzazione
        for position, w in enumerate(words):
            w_lower = w.lower()
            # Controlla se la parola non è una stop word e contiene solo caratteri alfabetici o numerici
            if w_lower not in self.stop_words and w_lower.isalnum():
                # Riduci la parola alla sua forma base
                w_lemma = self.lemmatizer.lemmatize(w_lower)
                # Aggiungi la parola all'indice
                if w_lemma not in self.index:
                    self.index[w_lemma] = []
                self.index[w_lemma].append((doc_id, filename, position, word_frequencies[w]))

    def get_ordered_index(self):
        return OrderedDict(sorted(self.index.items()))


# cerca DOCUMENTI in base a parole chiave
    def search_documents(self, query):
        # Splitta la query in parole e lemmatizza ciascuna parola trasformandola in minuscolo
        query_words = query.split()
        query_lemmas = [self.lemmatizer.lemmatize(word.lower()) for word in query_words]

        matching_documents = set()

        for query_lemma in query_lemmas:
            if query_lemma in self.index:
                print()
                print("MATCHING DI " + query_lemma + ":")
                for doc_info in self.index[query_lemma]:
                    # Estrai le informazioni sul documento
                    doc_id, filename, *positions, frequency = doc_info
                    for position in positions:
                        # Aggiungi il numero di frequenza alla stampa

                        matching_documents.add((doc_id, filename, position, frequency))
                        print(doc_id, filename, position, frequency)

        # Converti il set in una lista e ordina la lista per ID e posizione
        sorted_documents = sorted(list(matching_documents), key=lambda x: (x[0], x[2]))

        return sorted_documents

    # cerca DOCUMENTI in base a parole chiave e ORDINA PER SENTIMENTO (sentiment non fondamentale)
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
                sentiment_score = self.sentiment_scores.get(doc_id, 0.0)  # Se non ci sono punteggi, assume 0.0
                # Aggiungi id, nome e sentiment alla lista matching_documents
                matching_documents.append((doc_id, filename, sentiment_score))

            # Ordina la lista in base al sentiment
            matching_documents.sort(key=lambda x: x[2], reverse=True)

            return matching_documents
        return []

# cerca DOCUMENTI in base a parole chiave e ORDINA PER SENTIMENTO (ACCURATEZZA, sentimento fondamentale)
    def search_by_sentiment_complex(self, query):
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
                sentiment_score = self.sentiment_scores.get(doc_id, 0.0)  # Se non ci sono punteggi, assume 0.0
                # Aggiungi id, nome e sentiment alla lista matching_documents
                matching_documents.append((doc_id, filename, sentiment_score))

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


    def print_index_not_ordered(self):
        for key, value in self.index.items():
            print(f"{key}: {value}")

    def print_index_ordered(self):
        sorted_keys = sorted(self.index.keys())
        for key in sorted_keys:
            print(f"{key}: {self.index[key]}")


