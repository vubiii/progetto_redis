import redis
import time
from datetime import datetime

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
            password_registrata = self.connection.hget('utente:'f'{username_input}', 'username')


            if password_registrata is None:
                try:
                    self.connection.hset('utente:'f'{username_input}', mapping={'username':f'{username_input}', 
                                                                                'password':f'{password_input}',
                                                                                'DnD': 0})
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
        try:
            password_registrata = self.connection.hget('utente:'f'{username}', 'password')

            if password_registrata == password:
                global logatto 
                logatto = username

                return [True, username, password]
            else:
                print("Credenziali errate. Riprova.")
                return [False]
        except:
            print("Login Fallito - impossibile trovare utente")
            return[False]

    def aggiungi_utenti(self, username):
        dizionario_utenti = {}

        while True:
            print("Hai selezionato aggiungi utenti alla lista amici")
            
            try:
                utenti_trovati = self.ricerca_utenti()
                print(f"Ecco una lista di utenti trovati :")

                if utenti_trovati is not None:
                    for i, utente in enumerate(utenti_trovati):
                        dizionario_utenti[i] = utente
                        print(f"{i} : {utente}")

                    print("Selezionare l'utente da aggiungere (inserire numero)")
                    scelta = int(input("Inserisci -> "))
                
                if scelta not in dizionario_utenti or not dizionario_utenti:
                    raise ValueError("Scelta non valida")

                utente_selezionato = dizionario_utenti[scelta]
                azione = input(f"Hai selezionato {utente_selezionato}\n Sicuro di volerlo aggiungere? Sì(S) - No(N)")

                if azione.upper() == "S":
                    print(f"Sto aggiungendo utente: {utente_selezionato}")
                    
                    try:
                        if self.connection.sismember('utente:'f'{username}:Contatti', f'{utente_selezionato}') == 0:
                            self.connection.sadd(f'utente:{username}:Contatti', f'{utente_selezionato}')
                            print(f"Utente {utente_selezionato} aggiunto come amico.")
                            break
                        else:
                            print("Errore: Utente non esistente.")
                    except Exception as e:
                        print(f"Errore - {e}")

                elif azione.upper() == "N":
                    print(f"Non desideri aggiungere utente: {utente_selezionato}")
                    chiusura = input("Desideri cercare altri utenti? Sì(S) - No(N)")

                    if chiusura.upper() == "N":
                        return
                    elif chiusura.upper() == "S":
                        continue
                    else:
                        raise ValueError("Scelta non valida.")
                else:
                    raise ValueError("Scelta non valida. Riprova.")

            except ValueError as ve:
                print(f"Errore - {ve}")
                return

    def visualizza_lista_amici(self, username):
        amici = []
        print("Visualizza lista amici avviato")
        chiave = f'utente:{username}:Contatti'
        chiavi = self.connection.keys(chiave)
        for chiave in chiavi:
            lista_amici = self.connection.smembers(chiave)
            amici.extend(lista_amici)

        if amici:
            amici_trovati_str = ', '.join(amici)
            print(f'Lista Amici :\n {amici_trovati_str}')
            return lista_amici
        else:
            print("Nessun amico nella lista amici")

    def ricerca_utenti(self):
        print("Ricerca utenti avviata")  
        chiave = 'username'    
        utente_ricerca = input("Selezionare l'utente da ricercare <- ")
        chiave_utente = f"utente:{utente_ricerca}*"
        keys = self.connection.scan_iter(match=chiave_utente)
        utenti_trovati = []  # utenti trovati che corrispondono a
        
        try:
            for key in keys:
                nickname = key.split(':')[-1]
                utenti_trovati.append(nickname)
            
            if utenti_trovati:
                utenti_trovati_str = ', '.join(utenti_trovati)
                print(f'Ecco gli utenti trovati -> {utenti_trovati_str}')
                return utenti_trovati
            else:
                print(f'Nessun utente trovato che comincia con "{utente_ricerca}"')
                return []  # o None, a seconda delle tue esigenze
        
        except Exception as e:
            print(f"Errore - {e}")
            return None

    def non_disturbare(self, username):
        chiave_dnd = f'utente:{username}', 'DnD'
        
        print("Non disturbare - ON e OFF")

        while True:
            stato_corrente = self.connection.hget(chiave_dnd)
            if stato_corrente == 1:
                stato = "ATTIVO"
            elif stato_corrente == 0:
                stato = "SPENTO"
            else:
                stato = "Non Definito"

            print(f"Lo stato corrente è: {stato}")
            scelta = input("Desideri attivare (S) o disattivare (N) lo stato?").upper()

            if scelta == "S" and stato_corrente == 0:
                self.connection.set(chiave_dnd, 1)
                print("Lo stato DND è stato attivato.")
            elif scelta == "N" and stato_corrente == 1:
                self.connection.set(chiave_dnd, 0)
                print("Lo stato DND è stato disattivato.")
            else:
                print("Reindirizzamento alla home")
                break

    # Questo va integrato al tuo
    def chatta_vecchio(self, username):
        # Verifica se utente nella lista contatti - necessario
        print("Con quale utente desidera chattare?")
        chiave = "username"
        dizionario_contatti = {}
        try:
            utenti_trovati = self.visualizza_lista_amici(username=username)
            print(f"Ecco una lista di utenti trovati :")

            if utenti_trovati is not None:
                for i, utente in enumerate(utenti_trovati):
                    dizionario_contatti[i] = utente
                    print(f"{i} : {utente}")
            
            print("Selezionare l'utente con cui chattare (inserire numero)")
            scelta = int(input("Inserisci -> "))
            utente_selezionato = dizionario_contatti[scelta]
            print(f"Hai selezionato {utente_selezionato}\n")


            #da qua cambiare

            chiave_utente = f"{chiave}:{username}"
            chiave_ricevitore = f"{chiave}:{utente_selezionato}"
            chiave_dnd_ricevitore = f"{username}:dnd"
            stato_corrente = self.connection.get(chiave_dnd_ricevitore)
            

            tipologia_chat = input("Chat classica(0) - Chat temporizzata(1)")  
            # Ora devo verificare se l'utente è disponibile alla chat
            if self.connection.exists(chiave_utente) and self.connection.exists(chiave_ricevitore):
                # Qua deve essere possibile inviare il primo messaggio
                if stato_corrente == "1":
                    print(f"Utente {utente_selezionato} è disponibile per chattare")
                    if int(tipologia_chat) == 0:
                        print("Hai selezionato chat classica")
                    elif int(tipologia_chat) == 1:
                        print("Hai selezionato chat temporizzata")
                        durata_minuto = 60  # Durata in secondi
                        tempo_inizio = time.time()
                        tempo_scaduto = False
                        # inizio timer
                    else:
                        print("Errore nella selezione")
                    
                else:
                    print(f"L'utente {utente_selezionato} non è disponibile \n- Modalità dnd attiva")
            else:
                print("Errore")

                
        except :
            print("errore")


        # i messaggi devono essere inviati a chi è nella propria lista contatti
        # se dnd attivo allora si messaggi se no no messaggi
        # lettura dei messaggi username > mmmmmmmm    username_2 < mmmmm

    # Metodi Jose
    def invia_messaggio(self):
            for indx, contatto in enumerate(self.contatti()):
                print(f'>>>   {indx} - {contatto}   <<<')

            scelta = int(input("Inserisci la scelta: "))
            contatto = self.contatti()
            messaggio = input("Inserisci il messaggio: ")

            if self.connection.hget(f'utente:{contatto[scelta]}', 'DnD') == 1:
                self.connection.xadd(f'utente:{logatto}:chat:{contatto[scelta]}', {'mittente': messaggio, 'destinatario': ''})
            else:
                print(">>>  Non è stato possibili inviare il messagio perche l'utente è in modalita non disturbare  <<<")

            self.connection.xgroup_create(f'utente:{logatto}:chat:{contatto[scelta]}', f'{logatto}-{contatto[scelta]}')
    
    def leggi_messagi(self):
        for indx, contatto in enumerate(self.contatti()):
            print(f'>>>   {indx} - {contatto}   <<<')

        scelta = int(input("Inserisci la scelta: "))
        contatto = self.contatti()

        messaggio = self.connection.xread(f'utente:{logatto}:chat:{contatto[scelta]}', count = 10)
        print(messaggio)
    
    def crea_chat(self, user):
        self.connection.sadd('utente:greta' , 'greta:',user )

    def contatti(self):
        amici = []
        c = self.connection.keys(f'utente:{logatto}:Contatti')
        for obj in c:
            l_amici = self.connection.smembers(f'utente:{logatto}:Contatti')
            amici.extend(l_amici)
        return amici
        
    def chatta(self):
        while True:
            print("CHAT")
            print("1. Invia Messaggio\n2. Visualizza Messaggi\n3. Torna alla Home")

            choice = input("Inserisci la tua scelta: ")

            if choice == '1': 
                self.invia_messaggio()
            elif choice == '2':
                self.leggi_messagi()
            elif choice == '3':
                break
            else:
                print("Scelta non valida. Riprova.")

    def home(self, username, password):
        while True:
            print(f"\n --------------------- HOME ---------------------- \n")
            print(f"--- Ricerca Utenti (R)    -   Aggiungi Utenti (A) ---\n")
            print(f"--- Non Disturbare (O)    -   Chatta!         (C) ---\n ")
            print(f"--- Lista Amici    (L)    -   Esci         (E) ---\n")
            scelta = input("Inserisci la tua scelta: ").upper()

            if scelta == 'R' :
                self.ricerca_utenti()
            elif scelta == 'A':
                self.aggiungi_utenti(username=username)
            elif scelta == 'O':
                self.non_disturbare(username=username)
            elif scelta == 'C':
                self.chatta(username=username)
            elif scelta == 'L':
                self.visualizza_lista_amici(username=username)
            elif scelta == 'E':
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