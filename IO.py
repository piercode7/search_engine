import pickle


class IO:
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


    import pickle
    import os

    def backup_su_file(percorso, inverted_index):
        try:
            if not percorso:  # Se il percorso è vuoto, salva nella directory predefinita
                percorso = 'backup.pkl'

            # Verifico se il percorso esiste
            if os.path.exists(percorso):
                if os.path.isfile(percorso):
                    print(f"Il percorso {percorso} esiste ed è un file nel sistema.")
                else:
                    print(f"Il percorso {percorso} esiste, ma è una directory. Specificare il percorso di un file.")
                    return  # Esci dalla funzione se il percorso è una directory
            else:
                print(f"Il percorso {percorso} non esiste nel sistema. Salvataggio nella directory corrente.")

            backup_data = inverted_index

            with open(percorso, 'wb') as file:
                pickle.dump(backup_data, file)
            print(f"I dati sono stati salvati correttamente in {percorso}")
        except Exception as e:
            print(f"Si è verificato un errore durante il salvataggio dei dati: {e}")

    def restore_data(percorso):
        try:
            if not percorso:  # Se il percorso è vuoto, cerca nella directory predefinita
                percorso = 'backup.pkl'

            # Verifica se il percorso esiste
            if os.path.exists(percorso):
                if os.path.isfile(percorso):
                    with open(percorso, 'rb') as file:
                        inverted_index = pickle.load(file)
                    print(f"I dati sono stati ripristinati correttamente da {percorso}")
                    return inverted_index
                else:
                    print(
                        f"Il percorso {percorso} esiste, ma è una directory. Specificare un percorso valido per un file di backup.")
                    return None
            else:
                print(f"Errore: il file di backup non esiste in {percorso}")
                return None
        except Exception as e:
            print(f"Si è verificato un errore durante il ripristino dei dati: {e}")
            return None
