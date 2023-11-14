# Aqui vão as rotas e os links
from tumbrl import app
from flask import flash, render_template, url_for, redirect
from flask_login import login_required, login_user, current_user, logout_user
from tumbrl.models import load_user
from tumbrl.forms import FormLogin, FormCreateNewAccount, FormCreateNewPost
from tumbrl import bcrypt
from tumbrl.models import User, Posts
from tumbrl import database

import os
from werkzeug.utils import secure_filename

# Login do usuario
@app.route('/login', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def login():
    # Verifica se o usuário já está autenticado (logado)
    if current_user.is_authenticated:
        # Se já estiver autenticado, redireciona para a página inicial
        return redirect(url_for('home', user_id=current_user.id))

    # Cria uma instância do formulário de login (presumo que seja um formulário Flask-WTF)
    _formLogin = FormLogin()
    
    # Verifica se o formulário foi submetido e é válido
    if _formLogin.validate_on_submit():
        # Busca o usuário no banco de dados com base no e-mail fornecido no formulário
        userToLogin = User.query.filter_by(email=_formLogin.email.data).first()
        
        # Verifica se o usuário existe e a senha fornecida está correta
        if userToLogin and bcrypt.check_password_hash(userToLogin.password, _formLogin.password.data):
            # Se as credenciais são válidas, loga o usuário e redireciona para a página inicial
            login_user(userToLogin, remember=_formLogin.remember.data)
            return redirect(url_for('home', user_id=current_user.id))

    # Se o formulário não foi submetido ou não é válido, renderiza a página de login
    return render_template('login.html', form=_formLogin)

# O cadastro do usuario caso não tenha login
@app.route('/new', methods=['POST', 'GET'])
def createAccount():
    # Cria uma instância do formulário de criação de nova conta
    _formCreateNewAccount = FormCreateNewAccount()

    # Verifica se o formulário foi submetido e é válido
    if _formCreateNewAccount.validate_on_submit():
        # Obtém a senha do formulário e a hashea usando o bcrypt
        password = _formCreateNewAccount.password.data
        password_hash = bcrypt.generate_password_hash(password)

        # Cria uma nova instância de usuário com os dados do formulário
        newUser = User(
            username=_formCreateNewAccount.usarname.data,
            email=_formCreateNewAccount.email.data,
            password=password_hash
        )

        # Adiciona o novo usuário ao banco de dados
        database.session.add(newUser)
        database.session.commit()

        # Realiza login do usuário recém-criado e redireciona para a página de perfil
        login_user(newUser, remember=True)
        return redirect(url_for('profile', user_id=newUser.id))

    # Se o formulário não foi submetido ou não é válido, renderiza a página 'new.html'
    return render_template('new.html', form=_formCreateNewAccount)


@app.route('/home')
@login_required
def home():
    _postagens = Posts.query.order_by(Posts.id.desc()).all()
    return render_template('home.html', postagens=_postagens)

@app.route('/profile/<user_id>', methods=['POST', 'GET'])
@login_required
def profile(user_id):
    # Verifica se o ID do usuário na rota é o mesmo do usuário autenticado
    if int(user_id) == int(current_user.id):
        # Cria uma instância do formulário para criar novos posts
        _formCreateNewPost = FormCreateNewPost()

        # Verifica se o formulário foi submetido e é válido
        if _formCreateNewPost.validate_on_submit():
            # Obtém o arquivo de imagem e salva no diretório de uploads
            photo_file = _formCreateNewPost.photo.data
            photo_name = secure_filename(photo_file.filename)
            photo_path = f'{os.path.abspath(os.path.dirname(__file__))}/{app.config["UPLOAD_FOLDER"]}/{photo_name}'
            photo_file.save(photo_path)

            # Obtém o texto do post do formulário
            _postText = _formCreateNewPost.text.data

            # Cria um novo objeto de post e o adiciona ao banco de dados
            newPost = Posts(post_text=_postText, post_img=photo_name, user_id=int(current_user.id))
            database.session.add(newPost)
            database.session.commit()

        # Renderiza o perfil do usuário autenticado com o formulário de criação de post
        return render_template('profile.html', user=current_user, form=_formCreateNewPost)
    else:
        # Se o ID do usuário na rota não corresponde ao usuário autenticado, busca o usuário correspondente
        _user = User.query.get(int(user_id))
        # Renderiza o perfil do usuário correspondente sem o formulário de criação de post
        return render_template('profile.html', user=_user, form=None)

    
    
@app.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    # Obtém o post a ser deletado do banco de dados com base no ID fornecido na URL
    post_to_delete = Posts.query.get(post_id)

    # Verifica se o post existe e se pertence ao usuário autenticado
    if post_to_delete and post_to_delete.user_id == current_user.id:
        # Verifica se o post possui uma imagem associada
        if post_to_delete.post_img:
            # Constrói o caminho completo para o arquivo de imagem
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], post_to_delete.post_img)
            
            # Verifica se o arquivo de imagem existe no sistema de arquivos
            if os.path.exists(file_path):
                # Remove o arquivo de imagem
                os.remove(file_path)

        # Remove o post do banco de dados
        database.session.delete(post_to_delete)
        database.session.commit()

    # Redireciona de volta para o perfil do usuário autenticado após a exclusão
    return redirect(url_for('profile', user_id=current_user.id))


# Desloga o usuario
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/like_post/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Posts.query.get_or_404(post_id)
    post.likes += 1
    database.session.commit()
    return redirect(url_for('home'))

