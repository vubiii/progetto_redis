import redis
import time

class RedisManager:
    def __init__(self, host, port): #aggiungere il parametro password
        self.host = host
        self.port = port
        #self.password = password
        self.connection = None

    def open(self):
        print("Connessione al database")
        try:
            self.connection = redis.Redis(
                host=self.host,
                port=self.port,
                #password=self.password,
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
            stored_password = self.connection.hget('utente:'f'{username_input}', 'username')

            if stored_password is None:
                try:
                    self.connection.hset('utente:'f'{username_input}', mapping={'username':f'{username_input}', 
                                                                                'password':f'{password_input}',
                                                                                'DnD': 1})
                    
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
        password_registrata = self.connection.hget('utente:'f'{username}', 'password')

        if password_registrata == password:
            print(f"Accesso effettuato con successo, benvenuto {username}")
            global logatto 
            logatto = username

            return [True, username, password]
        else:
            print("Credenziali errate. Riprova.")
            return [False]
        
    def agg_utenti(self):
         while True:
            print("Hai selezionato aggiungi utenti")
            utenti_trovati = self.ricerca_utenti()
            print("Ecco una lista di utenti trovati:")

            for i, utente in enumerate(utenti_trovati):
                print(f"{i} : {utente}")

            print("Selezionare l'utente da aggiungere (inserire numero)")
            scelta = int(input("Inserisci -> "))

            if 0 <= scelta < len(utenti_trovati):
                utente_selezionato = utenti_trovati[scelta]
                azione = input(f"Hai selezionato {utente_selezionato}\nSicuro di volerlo aggiungere? Sì(S) - No(N)")

                if azione.upper() == "S":
                    print(f"Sto aggiungendo utente: {utente_selezionato}")

                    if self.connection.sismember('utente:'f'{logatto}:Contatti', f'{utente_selezionato}') == 0:
                        self.connection.sadd(f'utente:{logatto}:Contatti', f'{utente_selezionato}')
                    else : 
                        print(f'\n Utente già presenta nei contatti')
                    break
                
                elif azione.upper() == "N":
                    print(f"Non desideri aggiungere utente: {utente_selezionato}")
                    chiusura = input("Desideri cercare altri utenti? Sì(S) - No(N)")

                    if chiusura.upper() == "N":
                        break
                    elif chiusura.upper() == "S":
                        continue
                    else:
                        print("Errore nell'inserimento - conclusione")
                        break
                else:
                    print("Errore nell'inserimento, ricomincio procedimento...")
                    continue
            else:
                print("Errore: Scelta non valida. Riprova.")
    '''
    def aggiungi_utenti(self):
        dizionario_utenti = {}

        while True:
            print("Hai selezionato aggiungi utenti")
            utenti_trovati = self.ricerca_utenti()
            print(f"Ecco una lista di utenti trovati :")

            for i, utente in enumerate(utenti_trovati):
                dizionario_utenti[i] = utente
                print(f"{i} : {utente}")

            print("Selezionare l'utente da aggiungere (inserire numero)")
            scelta = int(input("Inserisci -> "))

            if scelta in dizionario_utenti:
                utente_selezionato = dizionario_utenti[scelta]
                azione = input(f"Hai selezionato {utente_selezionato}\n Sicuro di volerlo aggiungere? Sì(S) - No(N)")

                if azione.upper() == "S":
                    print(f"Sto aggiungendo utente: {utente_selezionato}")
                    
                    if self.connection.exists(f"username:{utente_selezionato}"):
                        chiave1 = f"amici:{username}:{utente_selezionato}"
                        chiave2 = f"amici:{utente_selezionato}:{username}"
                        self.connection.sadd(chiave1, utente_selezionato)
                        self.connection.sadd(chiave2, utente_selezionato)
                        print(f"Utente {utente_selezionato} aggiunto come amico.")
                    else:
                        print("Errore: Utente non esistente.")

                elif azione.upper() == "N":
                    print(f"Non desideri aggiungere utente: {utente_selezionato}")
                    chiusura = input("Desideri cercare altri utenti? Sì(S) - No(N)")

                    if chiusura.upper() == "N":
                        break
                    elif chiusura.upper() == "S":
                        continue
                    else:
                        print("Errore nell'inserimento - conclusione")
                        break
                else:
                    print("Errore nell'inserimento, ricomincio procedimento...")
                    continue
            else:
                print("Errore: Scelta non valida. Riprova.")
    '''
    def ricerca_utenti(self):
        utente_ricerca = input("Inserire l'utente da cercare: ")
        matching_keys = self.connection.keys(f"utente:{utente_ricerca}*")

        utenti_trovati = []

        for key in matching_keys:
            
            user_data = self.connection.hgetall(key)
            
            utenti_trovati.append(user_data['username'])
            if logatto in utenti_trovati:
                utenti_trovati.remove(logatto)
        print(utenti_trovati)

        if utenti_trovati:
            utenti_trovati_str = ', '.join(utenti_trovati)
            print(f'Ecco gli utenti trovati -> "{utente_ricerca}": {utenti_trovati_str}')
            return utenti_trovati
        else:
            print(f'Nessun utente trovato che comincia con "{utente_ricerca}"')
            return False
        
    '''
    def ricerca_utenti(self):
        print("Ricerca utenti avviata")  
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
            return utenti_trovati
        else:
            print(f'Nessun utente trovato che comincia con "{utente_ricerca}"')
            return False
        '''
    def non_disturbare(self):
        if self.connection.hget(f'utente:{logatto}', 'DnD') == 1:
            print(">>>  Sei in modalita non disturbare  <<<")
        else:
            print(">>>  Non sei in modalita disturbare  <<<")

        while True:
            print("1. Attiva modalita non disturbare\n2. Disattiva modalita non disturbare\n3. Torna alla Home")
            x = input("Inserisci la tua scelta: ")
            match x:
                case '1':
                    self.connection.hset(f'utente:{logatto}', 'DnD', 1)
                    print("Modalita non disturbare attivata")
                    break
                case '2':
                    self.connection.hset(f'utente:{logatto}', 'DnD', 0)
                    print("Modalita non disturbare disattivata")
                    break
                case '3':
                    break
                case _:
                    print("Scelta non valida. Riprova.")
                    continue

    def invia_messaggio(self):
        self.connection.xgroup_create()
    
    def leggi_messagi(self, chatroom, ultimo_msg='0'):
        messaggio = self.connection.xread({chatroom: ultimo_msg}, count = 10)
        return messaggio
    
    def crea_chat(self, user):
        self.connection.sadd('utente:greta' , 'greta:',user )

    def chatta(self):
        while True:
            print("CHAT")
            print("1. Invia Messaggio\n2. Visualizza Messaggi\n3. Torna alla Home")

            choice = input("Inserisci la tua scelta: ")

            if choice == '1': 
                chatroom  = input('Inserisci in quale chatroom vuoi inviare i messaggi: ')
                mitttente = input('mittente: ')  # -> Provisorio
                messaggio = input('Inserisci il messaggio: ')
                self.invia_messaggio(chatroom, mitttente, messaggio)

            elif choice == '2':
                chatroom = input('Di quale chatroom vuoi leggere i messaggi: ')
                print(self.leggi_messagi(chatroom))
            elif choice == '3':
                break
            else:
                print("Scelta non valida. Riprova.")

    def home(self, username, password):
        while True:
            print(f"HOME \n")
            print(f"Seleziona cosa desideri fare :\n")
            print(f" Ricerca Utenti (R)\n Aggiungi Utenti (A)\n Non Disturbare (O)\n Chatta! (C)\n Esci (E)")

            choice = input("Inserisci la tua scelta: ").upper()

            if choice == 'R':
                self.ricerca_utenti()
            elif choice == 'A':
                #self.aggiungi_utenti(username=username)
                self.agg_utenti()
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
        host='localhost',  #per un db cloud cambiare close e aggiungere la password
        port=6379,
    )
    print("Redis Chat")
    redis_manager.open()

    print(" Login(1)\n Registrazione(2)")
    scelta = input("Inserire cosa desideri fare <- ")

    if scelta == '1':
        informazioni_login = redis_manager.login()
        if informazioni_login[0] == True:
            username = informazioni_login[1]
            password = informazioni_login[2]
            redis_manager.home(username=username, password=password)
        else:
                print("Errore durante il login")
    elif scelta == '2':
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
    elif scelta == '3':
        redis_manager.chatta()
    else:
        print("Opzione selezionata non valida")

    redis_manager.close()