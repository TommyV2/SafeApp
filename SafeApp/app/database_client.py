from redis import Redis

class RedisClient:
    def connect(self, host):
        return Redis(host, decode_responses=True, charset="utf-8")
  
    def isEmpty(self):
        return self.db.dbsize() > 0

    def __init__(self, host):
        self.db = self.connect(host)
        if not self.isEmpty():      
            import app.init_redis

    def add_new_user(self, username, password, master_password):
        self.db.set("password_user:"+username, password)
        self.db.set("master_password_user:"+username, master_password)      
       
    def get_username(self, sid):
        username = self.db.hget("session:" + sid, "username")
        return username
        
    def username_exists(self, username):      
        account = self.db.keys(pattern='password_user:'+username)
        print(account)
        if not account:
            return False
        return True

    def get_password(self, username):
        password = self.db.get("password_user:" + username)
        return password
    
    def get_master_password(self, username):
        master_password = self.db.get("master_password_user:" + username)
        return master_password
        
    def get_all_accounts(self):
        accounts = self.db.keys(pattern='password_user:*')
        return accounts
    
    def add_password(self, username, service_name, password):       
        self.db.set("services_user:"+username+":service_name:"+service_name, password)
        self.db.set("decoded_services_user:"+username+":service_name:"+service_name, '') 
        
    def add_decoded_password(self, username, service_name, decoded):       
        self.db.set("decoded_services_user:"+username+":service_name:"+service_name, decoded) 
          
    def delete_password(self, username, service_name):      
        self.db.delete("services_user:"+username+":service_name:"+service_name)
        self.db.delete("decoded_services_user:"+username+":service_name:"+service_name)
        
    def get_all_passwords(self, username):
        all_services = self.db.keys(pattern="services_user:"+username+"*")
        passwords = []
        for service in all_services:           
            password = self.db.get(service)
            service_name = service.split(":")[-1]
            data = service_name+":"+password
            passwords.append(data)        
        return passwords 
        
    def get_all_decoded_passwords(self, username):
        all_services = self.db.keys(pattern="decoded_services_user:"+username+"*")
        passwords = []
        for service in all_services:           
            password = self.db.get(service)
            service_name = service.split(":")[-1]
            data = service_name+":"+password
            passwords.append(data)       
        return passwords 
        
    def clear_all_decoded_passwords(self, username):
        all_services = self.db.keys(pattern="decoded_services_user:"+username+"*")
        
        for service in all_services:                      
            service_name = service.split(":")[-1]
            self.db.set("decoded_services_user:"+username+":service_name:"+service_name, '')
                  


    def set_session(self, sid, username):
        self.db.hset("session:" + sid, "username", username)

    def add_new_password_for_service(self, username, service_name, password):
        self.db.set(username+":"+service_name, password)
    
    def get_password_for_service(self, username, service_name):
        password = self.db.get("services_user:"+username+":service_name:"+service_name)        
        return password 
    
    def set_timeout(self, timeout):
        self.db.set("timeout", timeout)
        
    def get_timeout(self):
        return self.db.get("timeout")    
    
    def reset_counter(self):
        self.db.set("counter",0)
        
    
    def get_counter(self):
        counter = self.db.get("counter")
        return counter
     
    def increment_counter(self):
        counter = self.db.get("counter")
        if counter == None:
            self.db.set("counter",0)
        else:
            counter = int(self.db.get("counter"))
            counter = counter + 1
            self.db.set("counter",counter)
            
    def change_master_password(self, username, master_password):       
        self.db.set("master_password_user:"+username, master_password)         
        
          
    


    
 