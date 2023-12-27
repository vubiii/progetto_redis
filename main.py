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
                decode_responses=True,
                encoding='utf-8'  
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
    
    # dobbiamo strutturare il metodo registrazione 
    def register(self):
      print("Registrazione Utente")
      while True:
          username_input = input("Inserire il nome utente: ")
          password_input = input("Inserire password: ")

          u = self.connection.hget('utenti:1', 'username')  
          print(f'valore ritornato di u: {u}')  
          # se l'utente non esiste oppure se il contenuto della chiave e diversa dal input si può registrare
          if u is None or u != username_input: 
              try:
                  self.connection.hset('utenti:1', mapping={'username': f'{username_input}'
                                                            , 'password':f'{password_input}'
                                                            , 'user_ID':f'{1}'})
                  print(f"Registrazione utente completato, benvenuto {username_input}")
                  break 
              except Exception as e:
                  print(f"Errore durante l'inserimento: {e}")
          else:
              print("Utente già esistente!")
              temp = input("Se sei già registrato accedi, \nInserire '/a' per accedere: ")
              if temp.lower() == '/a': 
                  self.login(username_input, password_input)
                  break  

    def login(self, username, password):
        print("-----. Login Utente .-----")

        stored_utente = self.connection.hgetall(name='utenti:1')

        if stored_utente['username'] == username and stored_utente['password'] == password:
            print(f"Accesso effettuato con successo, benvenuto {username}")
            return True
        else:
            print("Credenziali errate. Riprova.")
            return False

    #temporaneo
    def get_connection(self):
        return self.connection
  

if __name__ == "__main__":

    redis_manager = RedisManager(
        host='redis-10048.c304.europe-west1-2.gce.cloud.redislabs.com',
        port= 10048,
        password='1x5x6xi9x0SGA4uOuErpndO5H8xYH9dG'
    )
    print("----.Redis Chat.----")
    print("")
    
    #redis_manager.open()
    
    #Interfaccia Iniziale
    while True:
        print('\n----- Opzioni disponibili -----'
              '\n   1 - Login'
              '\n   2 - Registrazione'
              '\n   0 - Uscire'
              '\n----- Opzioni disponibili -----')

        choice = input('Inserisci un numero: ')
        
        redis_manager.open()

        #Conessione per l'inserimento-recupero dati:
        connection = redis_manager.get_connection()

        match choice:
            case '1':
                user = input('Inserisic il nome utente :') 
                password = input('Inserisice la password :')

                if redis_manager.login(user, password):
                    while True:
                        print('\n----Interfaccia Utente Loggato-----:'
                              '\n   1 - Contatti'
                              '\n   2 - Modalità'
                              '\n   3 - Logout'
                              '\n------------------------------------')
                        
                        user_choice = input('Inserisci un numero: ')
                        
                        match user_choice:
                            case '1':
                                print('Visualizza lista contatti')
                                # Implementa la logica per la gestione dei contatti
                            case '2':
                                print('Seleziona modalità')
                                # Implementa la logica per la selezione della modalità
                            case '3':
                                print('Logout effettuato')
                                redis_manager.close()
                                break
            case '2':
                redis_manager.register()
                #print(connection.hgetall('utenti:1')) # -> ritorna un dizionario
                print('hgetall di utenti:1 -> ', connection.hgetall('utenti:1')) 
            case '0':
                break