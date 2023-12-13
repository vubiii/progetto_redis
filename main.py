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
    
    # dobbiamo strutturare il metodo registrazione 
    def register(self):
      print("Registrazione Utente")
      while True:
          username_input = input("Inserire il nome utente: ")
          password_input = input("Inserire password: ")
          u = self.connection.get(f"username:{username_input}")  
          if u is None:
              try:
                  self.connection.set(f"username:{username_input}", f"password:{password_input}")
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
        print("Login Utente")
        stored_password = self.connection.get(f"username:{username}")
        if stored_password == f"password:{password}":
            print(f"Accesso effettuato con successo, benvenuto {username}")
        else:
            print("Credenziali errate. Riprova.")


  

if __name__ == "__main__":
    redis_manager = RedisManager(
        host='redis-11706.c281.us-east-1-2.ec2.cloud.redislabs.com',
        port=11706,
        password='01wNM4dZYmFHBCfiHGGUzLOFpo69MTxk'
    )
    print("Redis Chat")
    print("")
    redis_manager.open()
    

    redis_manager.close()


