import redis

class RedisManager:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.connection = None

    def open(self):
        print("Connessione al database")
        try:
            self.connection = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=True  
            )
            print("Connessione riuscita")
        except Exception as e:
            print(f"Errore: {e}")

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                print("Connesione chiusa")
            except Exception as e:
                print(f"Errore durante la connessione: {e}")
    
    def register(self):
        print("Registrazione Utente")
        while True:
            username_input = input("Inserire il nome utente: ")
            password_input = input("Inserire password: ")
            stored_password = self.connection.get(f"username:{username_input}")

            if stored_password is None:
                try:
                    self.connection.set(f"username:{username_input}", f"password:{password_input}")
                    print(f"Registrazione utente completata, benvenuto {username_input}")
                    return True
                except Exception as e:
                    print(f"Errore durante l'inserimento: {e}")
                    return False
            else:
                print("Utente già esistente!")
                return False

    def login(self):
        print("Login Utente")
        username = input("Inserire il nome utente: ")
        password = input("Inserire password: ")
        password_registrata = self.connection.get(f"username:{username}")

        if password_registrata == f"password:{password}":
            print(f"Accesso effettuato con successo, benvenuto {username}")
            return [True, username, password]
        else:
            print("Credenziali errate. Riprova.")
            return [False]

    def aggiungi_utenti(self):
        print("Hai selezionato aggiungi utenti")
       

    def ricerca_utenti(self):
        print("Hai selezionato ricerca utenti")  
        chiave = 'username'    
        utente_ricerca = input("Selezionare l'utente da ricercare <- ")
        chiave_utente = chiave + ":" + utente_ricerca + '*'
        keys = self.connection.scan_iter(match=chiave_utente)
        utenti_trovati = []  # utenti trovati che corrispondono a
        for key in keys:
            nickname = key.split(':')[-1]
            utenti_trovati.append(nickname)
        
        if utenti_trovati:
            utenti_trovati_str = ', '.join(utenti_trovati)
            print(f'Ecco gli utenti trovati -> "{utente_ricerca}": {utenti_trovati_str}')
        else:
            print(f'Nessun utente trovato che comincia con "{utente_ricerca}"')

    def non_disturbare(self):
        print("Non disturbare")

    def chatta(self):
        pass

    def home(self, username, password):
        while True:
            print(f"HOME \n")
            print(f"Seleziona cosa desideri fare :\n")
            print(f"Ricerca Utenti (R) - Aggiungi Utenti (A) \n Non Disturbare (O) - Chatta! (C) - \n Esci (E)")

            choice = input("Inserisci la tua scelta: ").upper()

            if choice == 'R':
                self.ricerca_utenti()
            elif choice == 'A':
                self.aggiungi_utenti()
            elif choice == 'O':
                self.non_disturbare()
            elif choice == 'C':
                self.chatta()
            elif choice == 'E':
                break
            else:
                print("Scelta non valida. Riprova.")

if __name__ == "__main__":
    redis_manager = RedisManager(
        host='redis-10048.c304.europe-west1-2.gce.cloud.redislabs.com',
        port=10048,
        password='1x5x6xi9x0SGA4uOuErpndO5H8xYH9dG'
    )
    print("Redis Chat")
    redis_manager.open()

    print("Login(1) - Registrazione(0)")
    scelta = input("Inserire cosa desideri fare <- ")

    if scelta == '1':
        informazioni_login = redis_manager.login()
        if informazioni_login[0] == True:
            username = informazioni_login[1]
            password = informazioni_login[2]
            redis_manager.home(username=username, password=password)
        else:
                print("Errore durante il login")
    elif scelta == '0':
        if redis_manager.register():
            print("L'utente è stato registrato, effettua il login")
            informazioni_login = redis_manager.login()
            if informazioni_login[0] == True:
                username = informazioni_login[1]
                password = informazioni_login[2]
                redis_manager.home(username=username, password=password)
            else:
                print("Errore durante il login")
        else:
            print("L'utente non è stato registrato, prova ad effettuare il login")
            informazioni_login = redis_manager.login()
            if informazioni_login[0] == True:
                username = informazioni_login[1]
                password = informazioni_login[2]
                redis_manager.home(username=username, password=password)
            else:
                print("Errore durante il login")
    else:
        print("Opzione selezionata non valida")

    redis_manager.close()