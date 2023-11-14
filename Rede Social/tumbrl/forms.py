# Importações necessárias
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

# Importa o modelo User para validar se o e-mail já está em uso
from tumbrl.models import User

# Importa o widget TextArea para o campo de texto do formulário de criação de post
from wtforms.widgets import TextArea

# Formulário de Login
class FormLogin(FlaskForm):
    email = StringField('E-mail')  # Campo para inserção do e-mail
    password = PasswordField('Senha')  # Campo para inserção da senha
    btn = SubmitField('Login')  # Botão de submissão do formulário
    remember = BooleanField('Lembrar')  # Campo para lembrar usuário

# Formulário de Criação de Nova Conta
class FormCreateNewAccount(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])  # Campo para inserção do e-mail, com validação de dados obrigatórios e formato de e-mail
    usarname = StringField('Usuário', validators=[DataRequired()])  # Campo para inserção do nome de usuário, com validação de dados obrigatórios
    password = PasswordField('Senha', validators=[DataRequired(), Length(6, 25)])  # Campo para inserção da senha, com validação de dados obrigatórios e comprimento entre 6 e 25 caracteres
    checkPassword = PasswordField('Confirme a senha', validators=[DataRequired(), Length(6, 25), EqualTo('password')])  # Campo para confirmar a senha, com validação de dados obrigatórios, comprimento entre 6 e 25 caracteres e igualdade com o campo de senha
    btn = SubmitField('Criar Conta')  # Botão de submissão do formulário

    # Método para validar se o e-mail já está em uso
    def validate_email(self, email):
        email_of_user = User.query.filter_by(email=email.data).first()
        if email_of_user:
            raise ValidationError('~ email já existe ~')  # Levanta uma exceção se o e-mail já estiver em uso

# Formulário de Criação de Novo Post
class FormCreateNewPost(FlaskForm):
    text = StringField('Texto', widget=TextArea(), validators=[DataRequired()])  # Campo para inserção do texto do post, com widget TextArea para suportar texto multilinha e validação de dados obrigatórios
    photo = FileField('Foto', validators=[DataRequired()])  # Campo para upload de uma foto, com validação de dados obrigatórios
    btn = SubmitField('Publicar!')  # Botão de submissão do formulário

# Formulário para Deletar Post
class DeletePost(FlaskForm):
    post_id = HiddenField('Post ID')  # Campo oculto para armazenar o ID do post a ser deletado
    submit = SubmitField('Deletar Post')  # Botão de submissão para deletar o post



