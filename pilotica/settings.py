from flask_login import LoginManager

plugin_manager = None
secret_key = None

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"