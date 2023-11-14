# Importações necessárias
from tumbrl import database
from datetime import datetime
from tumbrl import login_manager
from flask_login import UserMixin

# Função para carregar usuário pelo ID 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Classe de Usuário (representa a tabela 'user' no banco de dados)
class User(database.Model, UserMixin):
    # Campos da tabela 'user'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False, unique=True)
    email = database.Column(database.String, nullable=False, unique=True)
    password = database.Column(database.String, nullable=False)
    
    # Relacionamento com a tabela 'posts' (um usuário pode ter vários posts)
    posts = database.relationship("Posts", backref="user", lazy=True)

# Representa a tabela 'posts' no banco de dados)
class Posts(database.Model):
    # Campos da tabela 'posts'
    id = database.Column(database.Integer, primary_key=True)
    post_text = database.Column(database.String, default='')
    post_img = database.Column(database.String, default='default.png')
    creation_date = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())
    likes = database.Column(database.Integer, default=0)
    # Chave estrangeira para associar o post a um usuário específico
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
