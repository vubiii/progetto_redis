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
            print("Connection riuscita")
        except Exception as e:
            print(f"Errore: {e}")

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                print("Connesione chiusa")
            except Exception as e:
                print(f"Errore durante la connessione: {e}")

if __name__ == "__main__":
    redis_manager = RedisManager(
        host='redis-11706.c281.us-east-1-2.ec2.cloud.redislabs.com',
        port=11706,
        password='01wNM4dZYmFHBCfiHGGUzLOFpo69MTxk'
    )

    redis_manager.open()

    redis_manager.close()
