from password_gen_app.config.mysqlconnection import connectToMySQL
from random import randint, shuffle
from cryptography.fernet import Fernet
from flask import flash,session


db='password_generator_schema'

class Password:
    def __init__(self, data):
        self.id = data['id']
        self.gen_password = data['gen_password']
        self.keygen = data['keygen']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.creator = data['users_id']
    
    @classmethod
    def create_password(cls):
        key = Fernet.generate_key().decode()
        pass_gen=Fernet(key)
        
        data ={
            'gen_password': pass_gen.encrypt(session['generated_password'].encode()),
            'keygen': key,
            'users_id': session['user_logged_id']
        }
        query = '''INSERT INTO passwords (gen_password, keygen, users_id) 
        VALUE( %(gen_password)s, %(keygen)s, %(users_id)s)'''
        return connectToMySQL(db).query_db(query,data)
    
    @classmethod
    def get_all_passwords(cls):
        query = 'SELECT * FROM passwords'
        results = Password.decode_password(connectToMySQL(db).query_db(query))
        passwords = []
        for row in results:
            passwords.append(cls(row))
        return passwords
    
    @classmethod
    def get_last_password(cls):
        query = 'SELECT * FROM passwords ORDER BY id DESC limit 1 '
        result = Password.decode_password(connectToMySQL(db).query_db(query))
        return cls(result[0])
    
    
    @classmethod
    def destroy(cls, id):
        query = f'SELECT * FROM passwords WHERE ID = {id}'
        return connectToMySQL(db).query_db(query)
    
    @classmethod
    def delete_password(cls):
        query = f'DELETE FROM passwords WHERE created_at < (NOW() - INTERVAL 90 DAY);'
        return connectToMySQL(db).query_db(query)
    
    @staticmethod
    def decode_password(db_data):
        if len(db_data) > 0 and db_data[0]['gen_password'] != None:
            for row in db_data:
                pass_gen=Fernet(row['keygen'])
                row['gen_password']= pass_gen.decrypt(row['gen_password']).decode()
        return db_data
    
    @staticmethod
    def password_form_validator(post_data):
        """This is a password validator for the password generation form.

        Args:
            post_data (dict): POST data that has the user's input information.

        Returns:
            Boolean: If this returns False validation fails and displays messages.
        """
        is_valid = True
        if len(post_data.getlist("params")) < 2:
            flash("Please select at least 2 conditions for your password.", "password_form")
            is_valid = False
        if post_data['password_length'] == '':
            flash("Password length can't be empty.", "password_form")
            is_valid = False
        elif int(post_data['password_length']) < 8:
            flash("Password length should be at least be 8 characters long.", "password_form")
            is_valid = False
        return is_valid
            
        
    
    @staticmethod
    def create_character_list(param, character_list):
        import string
        """This helper function creates a list called character list which determines the characters needed for each category

        Args:
            param (string): param is each string value from the list generated from request.form checkbox values
            character_list (list): a list that is being built with each iteration of the for in password generator function also where it's declaration exist. 

        Returns:
            list of lists that contains strings
        """    
        special_list = ['!', '^', '#', '*', '%', '$', '&', '@']
        if param == "special":
            character_list.append(special_list)
        elif param =="number":
            character_list.append(list(string.digits))
        elif param =="lowercase":
            character_list.append(list(string.ascii_lowercase))
        else:
            character_list.append(list(string.ascii_uppercase))
        return character_list

    @staticmethod
    def populate_and_shuffle(values_list, char_list):
        """This is a helper function that takes in several lists and creates a new list of strings that forms the generated password.   

        Args:
            values_list (list): This is a list that declared on line 118. The values in the list are the number of instances in each category of the params.  
            char_list (list): The finished and completed return value from create_character_list on line 111. 
        
        Other Variables:
            counter(integer): A count to keep track of when to iterate the character_list to access the new list of string values.
            
        Returns:
            password_generated(list): A list to store all values to make the generated password and joined as a single string value. 
        """    
        password_generated = []
        counter=0
        
        for index in range(len(values_list)):
            popped_character_list = char_list[counter].copy() 
            
            for each_instance in range(values_list[index]):
                
                if len(popped_character_list) == 1:
                    password_generated.append(popped_character_list[0])
                    popped_character_list.pop(0)
                    popped_character_list.extend(char_list[counter]) 
                else:
                    random_index = randint(1,len(popped_character_list)-1)
                    password_generated.append(popped_character_list[random_index-1:random_index][0])
                    popped_character_list.pop(random_index-1)
                shuffle(password_generated)
            counter+=1
        return "".join(password_generated)


    @staticmethod
    def password_generator(data,params_list):
        """This function is the top most function for password generation that determines the number of characters for each category and builds the generated passwords with the helper functions.

        Args:
            data (request.form): form data
            params_list (list): Values from the checkbox selections 
            num_of_each (dict): A dict that has params_list strings as keys and the value represents the number of each based off a percentage of the total password length.

        Returns:
            string: generated password
        """    
        num_of_each={}
        character_list=[]
        
        if len(params_list) == 4:
            percentages =[.2,.2,.2,.4]
            for index,param in enumerate(params_list):
                num_of_each[param] = round(int(data['password_length']) * (percentages[index]))
                character_list=Password.create_character_list(param,character_list)
                
        elif len(params_list) == 3:
            percentages =[.3,.3,.4]
            for index,param in enumerate(params_list):
                num_of_each[param] = round(int(data['password_length']) * (percentages[index]))
                character_list=Password.create_character_list(param,character_list)
        else:
            percentages =[.4,.6]
            for index,param in enumerate(params_list):
                num_of_each[param] = round(int(data['password_length']) * (percentages[index]))
                character_list=Password.create_character_list(param,character_list)
        
        values_list =[num_of_each[key] for key in num_of_each]
        if sum(values_list) == int(data['password_length']):
            return Password.populate_and_shuffle(values_list,character_list) 
        elif sum(values_list) > int(data['password_length']):
            values_list[randint(0,len(values_list)-2)]-=1
            return Password.populate_and_shuffle(values_list,character_list)
        else:
            values_list[randint(0,len(values_list)-2)]+=1
            return Password.populate_and_shuffle(values_list, character_list)

    
