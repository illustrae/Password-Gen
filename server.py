from password_gen_app import app
from password_gen_app.controllers import users_controller, passwords_controller


if __name__ =='__main__':
    app.run(debug=True)