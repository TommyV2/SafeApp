from os import getenv
from flask import Flask
from flask import request, make_response, render_template, url_for, session, redirect, jsonify
from .database_client import RedisClient
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
import hashlib, uuid
from datetime import datetime, date, time, timedelta
from flask_wtf.csrf import CSRFProtect



PREFIX = getenv('PREFIX','')
app = Flask(__name__)
app.secret_key = 'T!9lA5%2'
app.permanent_session_lifetime = timedelta(minutes=5)
csrf = CSRFProtect(app)
database_client = RedisClient("redis")

def hash_password(password):
    salt = app.secret_key
    text = password + salt
    text = text.encode('utf-8')
    hashed_password = hashlib.sha512(text).hexdigest()
    return hashed_password
    
#Adding honeypots 
#1 ciężkie hasło
pass1 = hash_password("A2zX12h&k$vL5")
master1 = hash_password("sU%17823cu5s#")
database_client.add_new_user("Tajniak", pass1, master1)
#2 łatwe hasło, zdublowane 
pass2 = hash_password("haslo123")
master2 = hash_password("haslo123")
database_client.add_new_user("admin", pass2, master2)

@app.route('/main')
def main():
    if 'loggedin' in session:             
        return render_template('main.html', msg="Logout", method="logout")
    return render_template('main.html', msg="Login", method="login")
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    type='msg'
    if is_timeout() == False:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form["username"]
            password = request.form["password"]
            if isFieldSafe(username) and isFieldSafe(password):
                hashed_password = hash_password(password)
                if isUserInDatabase(username,hashed_password)!=None:
                    key = isUserInDatabase(username,hashed_password)
                    session['loggedin'] = True
                    session['id'] = key
                    session['username'] = username           
                    database_client.reset_counter()
                    if isHoneyPot(username) == True:
                        app.logger.warning("Włamanie na honeypot:" + username)
                    url = "https://localhost/passwords"
                    return redirect(url)
              
                else:
                    database_client.increment_counter()
                    counter = int(database_client.get_counter())
                    print(counter)
                    if counter >= 3:
                        now = datetime.now()
                        added = timedelta(minutes = 1)
                        timeout = now + added
                        string_timeout = str(timeout)
                        database_client.set_timeout(string_timeout)                   
                    msg = 'Incorrect username/password!'
    else:
        msg = 'You still have 1 minute timeout!'
    if msg=='':
        type='blank'
    return render_template('login.html', msg=msg, type=type)

def is_timeout():
    string_timeout = database_client.get_timeout()
    if string_timeout != None:        
        now = datetime.now()
        timeout = datetime.strptime(string_timeout,'%Y-%m-%d %H:%M:%S.%f')
        if now < timeout:
            return True
    return False

    
@app.route('/logout')  
def logout():
    username = session['username']
    database_client.clear_all_decoded_passwords(username)
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)  
    
    return redirect(url_for('main'))
    
    
@app.route('/register', methods=['GET', 'POST'])   
def register():
    msg = ''
    type='blank'
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'repeat_password' in request.form and 'master_password' in request.form and 'repeat_master_password' in request.form:
 
        username = request.form["username"]
        password = request.form["password"]
        repeat_password = request.form["repeat_password"]
        master_password = request.form["master_password"]
        repeat_master_password = request.form["repeat_master_password"]
        if isFieldSafe(username) and isFieldSafe(password) and isFieldSafe(master_password):
            hashed_password = hash_password(password)
            
            if isUserInDatabase(username, hashed_password)!=None:
                msg = 'Account already exists'
                type='msg'
            elif isOccupiedLogin(username) == True:
                msg = 'Username occupied!'
                type='msg'
            elif usernameCorrect(username) == False:
                msg = 'Username invalid!'
                type='msg'
            elif passwordCorrect(password) == False:
                msg = 'Password invalid'
                type='msg'
            elif repasswordCorrect(password, repeat_password) == False:
                msg = 'Repeated password invalid!'
                type='msg'
            elif passwordCorrect(master_password) == False:
                msg = 'Master password invalid!'
                type='msg'
            elif repasswordCorrect(master_password, repeat_master_password) == False:
                msg = 'Repeated master password invalid!'
                type='msg'
            else:    
                hashed_password = hash_password(password)
                hashed_master_password = hash_password(master_password)
                database_client.add_new_user(username, hashed_password, hashed_master_password)
                 
                msg = 'You have successfully registered!'
                type='msg-success'
                 
    elif request.method == 'POST':     
        msg = 'Please fill out the form!'
        type='msg'
         
    return render_template('register.html', msg=msg, type=type)
    
@app.route('/passwords')  
def passwords():
    if 'loggedin' in session:    
        username = session['username'] 
        list = database_client.get_all_passwords(username)
        decoded_list = database_client.get_all_decoded_passwords(username)         
        my_passwords = []
        my_decoded_passwords = []
        if list is not None:
            my_passwords = create_password_objects_list(list)
            my_decoded_passwords = create_password_objects_list(decoded_list)         
        return render_template('passwords.html', username=username, msg = "Logout",method="logout", my_passwords=my_passwords, my_decoded_passwords = my_decoded_passwords )     
    return redirect(url_for('login'))

@app.route("/add", methods=['GET', 'POST'])
def add(): 
    if 'loggedin' in session:
        username = session['username']    
        msg = ''
        type='blank'
        if request.method == 'POST' and 'service_name' in request.form and 'password' in request.form:  
                          
            service_name = request.form["service_name"]       
            password = request.form["password"] 
            if isFieldSafe(service_name) and isFieldSafe(password):
                encrypted_password = encrypt_password(password)
                p = encrypted_password.decode('charmap')
                database_client.add_password(username, service_name, p)                   
                msg = 'You have successfully added new password!'
                type='msg-success'
                       
        elif request.method == 'POST':     
            msg = 'Please fill out the form!'
            type='msg'
            
        return render_template('add.html', msg=msg, type=type)  
        
    return redirect(url_for('login'))

@app.route('/delete')    
def delete_password(): 
    if 'loggedin' in session:
        username = session['username']
        service_name = request.args.get('service_name')
        database_client.delete_password(username, service_name)      
        return redirect(url_for('passwords'))
    return redirect(url_for('login'))   
    
@app.route('/decode')    
def decode_password(): 
    if 'loggedin' in session:
        username = session['username']
        service_name = request.args.get('service_name')
        input = request.args.get('input') 
        if isFieldSafe(input) and isFieldSafe(service_name) and isFieldSafe(username):
            hashed = hash_password(input) 
            master_password = database_client.get_master_password(username)
            
            if hashed == master_password:
                password = database_client.get_password_for_service(username, service_name)
                encoded = password.encode('charmap')
                decryped_password = decrypt_password(encoded)
                database_client.add_decoded_password(username, service_name, decryped_password)  
        return redirect(url_for('passwords'))
    return redirect(url_for('login')) 
    
@app.route('/hide')    
def hide_password():
    if 'loggedin' in session:
        username = session['username']
        service_name = request.args.get('service_name')
        
        password = database_client.get_password_for_service(username, service_name)
        database_client.add_decoded_password(username, service_name, '')  
        return redirect(url_for('passwords'))
    return redirect(url_for('login')) 
    
@app.route("/change_password", methods=['GET', 'POST'])
def change_password():     
    return render_template('change_password.html')  
    
    
@app.route("/check_credentials", methods=['GET', 'POST'])
def check_credentials():     
    username = request.args.get('username')
    master_password = request.args.get('master_password') 
    if isFieldSafe(username):   
        if isUserInDatabase2(username,master_password)!=None:        
            return jsonify(answer = "True")         
    return jsonify(answer = "False")  
    
   

BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])] 

def isHoneyPot(username):
    if username == "admin" or username == "Tajniak":       
        return True
    return False    

def get_string(string):
    length = len(string)
    result = string[2: length-1]
    return result
 
def encrypt_password(password):
    raw = pad(password)
    password_bytes = raw.encode()  
    key = app.secret_key.encode()        
    des = DES.new(key, DES.MODE_ECB)
    encrypted = des.encrypt(password_bytes)
    return encrypted
  
def decrypt_password(password):
    key = app.secret_key.encode()
    des = DES.new(key, DES.MODE_ECB)
    decrypted = des.decrypt(password)
    dec = unpad(decrypted)
    return dec
    
    

def create_password_objects_list(password_list):
    passwords = []    
    for password in password_list:        
        data = password.split(':')          
        p = Password(data[0], data[1])        
        passwords.append(p)
       
    return passwords


class Password:
    def __init__(self, service_name, password):
        self.service_name = service_name
        self.password = password

def isFieldSafe(value):
    if "'" in value or "<" in value or ">" in value or ";" in value or "|" in value or "`" in value:
        return False
    return True
    
def isUserInDatabase(username, password):   
    password1 = database_client.get_password(username)    
    if password1 == password:
        return "key:"+username
    return None
    
def isUserInDatabase2(username, master_password): 
    hashed = hash_password(master_password)
    master_password1 = database_client.get_master_password(username)    
    if master_password1 == hashed :
        return "key:"+username
    return None    
    
def isOccupiedLogin(username):
    result = database_client.username_exists(username)           
    return result
    
def usernameCorrect(username):
    if len(username) <5 or not username.isalpha() or "'" in username or "<" in username or ">" in username:
                return False;
    return True;
    
def passwordCorrect(password):
    if len(password) <8 or "'" in password or "<" in password or ">" in password:
                return False;
    return True;
    
def repasswordCorrect(password, repeat_password):
    if password != repeat_password:
                return False;
    return True;    
    