import redis
import time
from datetime import datetime
# Esame redis
class RedisManager:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.connection = None
        self.posizione_messaggi = {}

    def open(self):
        # Metodo per aprire la connessione a Redis
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
        # Metodo per chiudere la connessione a Redis
        if self.connection:
            try:
                self.connection.close()
                loggato = ""
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
        global loggato 
        print("Login Utente")
        username = input("Inserire il nome utente: ")
        password = input("Inserire password: ")
        try:
            password_registrata = self.connection.hget('utente:'f'{username}', 'password')

            if password_registrata == password:
                loggato = username
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
                        if self.connection.sismember('contatti:' f'{username}:', f'{utente_selezionato}') == 0 and self.connection.sismember('utente:'f'{utente_selezionato}:Contatti', f'{username}') == 0:
                            self.connection.sadd(f'contatti:{username}', f'{utente_selezionato}')
                            self.connection.sadd(f'contatti:{utente_selezionato}', f'{username}')
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
        chiave = f'contatti:{username}'
        chiavi = self.connection.keys(chiave)
        for chiave in chiavi:
            lista_amici = self.connection.smembers(chiave)
            amici.extend(lista_amici)

        if amici:
            amici_trovati_str = ', '.join(amici)
            print(f'Lista Amici :\n {amici_trovati_str}')
            return list(lista_amici)
        else:
            print("Nessun amico nella lista amici")
            return []

    def ricerca_utenti(self):
        print("Ricerca utenti avviata")  
        chiave = 'username'    
        utente_ricerca = input("Selezionare l'utente da ricercare <- ")
        chiave_utente = f"utente:{utente_ricerca}*"
        keys = self.connection.scan_iter(match=chiave_utente)
        utenti_trovati = [] 
        
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
                return [] 
        
        except Exception as e:
            print(f"Errore - {e}")
            return None

    def non_disturbare(self, username):
        print("Non disturbare - ON e OFF")

        chiave_dnd = f'utente:{username}'
        
        while True:
            stato_corrente = int(self.connection.hget(chiave_dnd, 'DnD') or 0)

            if stato_corrente == 1:
                stato = "ATTIVO"
            elif stato_corrente == 0:
                stato = "SPENTO"
            else:
                stato = "Non Definito"

            print(f"Lo stato corrente è: {stato}")
            scelta = input("Desideri attivare (A) o disattivare (D) lo stato?").upper()
            if scelta == "A" and stato_corrente == 0:
                self.connection.hset(chiave_dnd, 'DnD', 1)
                print("Lo stato DND è stato attivato. Premere qualsiasi tasto per tornare alla home")
            elif scelta == "D" and stato_corrente == 1:
                self.connection.hset(chiave_dnd, 'DnD', 0)
                print("Lo stato DND è stato disattivato. Premere qualsiasi tasto per tornare alla home")
            else:
                print("Reindirizzamento alla home")
                break

    def chatta(self, username):
            while True:
                print(f"Chat - Benvenuto {username} ")
                print("Invia Messaggio - 1 \nVisualizza Messaggi - 2 \nTorna alla Home - 3 \n")

                scelta = input("Inserisci la tua scelta: ")

                if scelta == '1':
                    self.invia_messaggio(username=username)
                elif scelta == '2':
                    self.leggi_messaggi(username=username)
                elif scelta == '3':
                    break
                else:
                    print("Scelta non valida. Riprova.")

    def invia_messaggio(self, username):
        lista_amici = self.visualizza_lista_amici(username=username)
        print("Hai selezionato chatta - seleziona con quale utente vuoi chattare")
                
        for indx, contatto in enumerate(lista_amici):
            print(f'>>>   {indx} - {contatto}   <<<')
        if lista_amici:
            scelta = int(input("Inserisci la scelta: "))
            contatto = lista_amici[scelta]
            chiave_dnd = f'utente:{contatto}'

            scelta = input("Desideri fare una chat temporizzata? Sì(S) - No(N)")

            if scelta.upper() == "N":
                print("Inizio chat classica")

                chiave_chat = f"chat:{username}:{contatto}"
                chiave_inversa= f"chat:{contatto}:{username}"

                temp = self.connection.exists(chiave_inversa)
                
                if temp == True:
                    #per verificare che la chat non sia stata già avviata
                    chiave_chat = chiave_inversa
                data_ora = time.time()
                print(f"Inizio chat tra {username} e {contatto} - inserire exit per uscire ")
                if not self.connection.exists(chiave_chat):
                    self.connection.xadd(chiave_chat, {'mittente':"--",'messaggio': f"Inizio chat con {contatto}", 'timestamp':data_ora })
                while True:
                    messaggio = input(f"{username}> ")
                    if messaggio.lower() != "exit":
                        
                        stato_corrente = int(self.connection.hget(chiave_dnd, 'DnD') or 0)
                        if stato_corrente == 1:
                            self.connection.xadd(chiave_chat, {'mittente': username, 'messaggio':messaggio, 'timestamp':data_ora})

                        elif stato_corrente == 0:
                            messaggio_errore = "Non è stato possibile inviare il messaggio perché l'utente è in modalità non disturbare"
                            self.connection.xadd(chiave_chat, {'mittente': username, 'messaggio':messaggio_errore, 'timestamp':data_ora})
                            print(f"< {messaggio_errore}")
                            break
                        else:
                            print("Errore")
                            break
                    else:
                        print("Chiusura")
                        break
            elif scelta.upper() == "S":
                print("Hai selezionato chat temporizzata")
                
                chiave_chat = f"chat:{username}:{contatto}"
                chiave_inversa= f"chat:{contatto}:{username}"

                temp = self.connection.exists(chiave_inversa)
                
                if temp == True:
                    chiave_chat = chiave_inversa
                
                chiave_chat_temporanea = "temp:"+chiave_chat
                
                print(f"Inizio chat con {contatto}, inserire exit per uscire ")
                data_ora = time.time()
                stato_corrente = int(self.connection.hget(chiave_dnd, 'DnD') or 0)
                if not self.connection.exists(chiave_chat_temporanea) and stato_corrente == 1:
                    self.connection.xadd(chiave_chat_temporanea, {'mittente': username, 'messaggio': f"Inizio chat con {contatto}", 'timestamp': data_ora })
                print(f"Inizio timer")
                inizio = time.time()
                while True:
                    tempo_rimasto = time.time() - inizio

                    if tempo_rimasto >= 60:
                        try:
                            print("Limite di tempo superato - autodistruzione della chat")
                            self.connection.delete(chiave_chat_temporanea)
                            break
                        except Exception as e:
                            print(f"Errore - {e}")

                    messaggio = input(f"{username}> ")
                    if messaggio.lower() == "exit":
                        print("Chiusura")
                        break

                    chiave_dnd = f'utente:{contatto}'
                    stato_corrente = int(self.connection.hget(chiave_dnd, 'DnD') or 0)

                    if stato_corrente == 1:
                        self.connection.xadd(chiave_chat_temporanea, {'mittente': username, 'messaggio': messaggio, 'timestamp': time.time()})
                    elif stato_corrente == 0:
                        print("Non è stato possibile inviare il messaggio perché l'utente è in modalità non disturbare")
                        break
                    else:
                        print("Errore")
                        break
            else:
                print("!!! La scelta effettuata non è consentita !!!")
        elif not lista_amici:
            print("Non hai amici nella lista con cui chattare")   
        else:
            print("Errore generico") 

    def leggi_messaggi(self, username):
            lista_amici = self.visualizza_lista_amici(username=username)
            print("Hai selezionato visualizza lo storico - seleziona la chat da visionare")
            
            for indx, contatto in enumerate(lista_amici):
                print(f'>>>   {indx} - {contatto}   <<<')

            while True:
                try:
                    scelta = int(input("Inserisci la scelta: "))
                    contatto = lista_amici[scelta]
                    break
                except:
                    print("Scelta non valida")

            esistenza_chat = False

            chiave_stream = f'chat:{username}:{contatto}'
            if self.connection.exists(chiave_stream) == False:
                chiave_stream_inversa = f'chat:{contatto}:{username}'
                temp = self.connection.exists(chiave_stream_inversa)    
                if temp == True:
                    chiave_stream = chiave_stream_inversa
                    esistenza_chat = True
                
            else:
                esistenza_chat = True

            if esistenza_chat:
                while True:
                    ultimo_messaggio = self.posizione_messaggi.get(chiave_stream, '0')
                    messaggi = self.connection.xread({chiave_stream: '0'})
                    for element in messaggi:
                        chiave_stream, lista_messaggi = element
                        for id_messaggio, messaggio in lista_messaggi:
                            stringa_in_ou = ""  
                            testo = ""
                            data_stampa = ""
                            
                            for chiave, valore in messaggio.items():
                                if chiave == "mittente" and valore == username:
                                    stringa_in_ou = ">>"
                                elif chiave == "mittente" and valore == contatto:
                                    stringa_in_ou = "<<"
                                elif chiave == "messaggio":
                                    testo = valore
                                elif chiave == "timestamp":
                                    formato_data = datetime.utcfromtimestamp(float(valore))
                                    data_trasformata = formato_data.strftime('%Y-%m-%d %H:%M:%S')
                                    data_stampa = f"[{data_trasformata}]"
                            
                            stringa_unica = f"{stringa_in_ou}{testo}\t\t{data_stampa}\n"
                            print(stringa_unica, end=' ')
                    time.sleep(5)
                    risposta = input("Vuoi tornare indietro? (S): ")
                    if risposta.upper() == 'S':
                        return  
            else:
                print(f"Non hai conversazioni con l'utente {contatto}")

    def notifiche_push(self, contatto):
        username = loggato  
        chiave_stream = f'chat:{username}:{contatto}'

        while True:
            if self.connection.exists(chiave_stream):
                messaggi = self.connection.xread({chiave_stream: '0'})
                for element in messaggi:
                    chiave_stream, lista_messaggi = element
                    for id_messaggio, messaggio in lista_messaggi:
                        stringa_in_ou = ""  
                        testo = ""
                        data_stampa = ""
                        
                        for chiave, valore in messaggio.items():
                            if chiave == "mittente" and valore == username:
                                stringa_in_ou = ">>"
                            elif chiave == "mittente" and valore == contatto:
                                stringa_in_ou = "<<"
                            elif chiave == "messaggio":
                                testo = valore
                            elif chiave == "timestamp":
                                formato_data = datetime.utcfromtimestamp(float(valore))
                                data_trasformata = formato_data.strftime('%Y-%m-%d %H:%M:%S')
                                data_stampa = f"[{data_trasformata}]"
                        
                        stringa_unica = f"{stringa_in_ou}{testo}{data_stampa}\n"
                        print("Nuovo messaggio!")
                        print(stringa_unica)  

                time.sleep(5)



    def home(self, username, password):
        while True:
            print(f"\n --------------------- HOME ---------------------- \n")
            print(f"--- Ricerca Utenti (R)    -   Aggiungi Utenti (A) ---\n")
            print(f"--- Non Disturbare (O)    -   Chatta!         (C) ---\n ")
            print(f"--- Lista Amici    (L)    -   Esci         (E) ---\n")
            print(f"-------------------------------------------------")
            scelta = input("Inserisci la tua scelta: ").upper()

            if scelta == 'R' :
                self.ricerca_utenti()
            elif scelta == 'A':
                self.aggiungi_utenti(username=username)
            elif scelta == 'O':
                self.non_disturbare(username=username)
            elif scelta == 'C':
                self.chatta(username)
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