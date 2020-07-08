# criar um interface entre o python(Flask) e o HTML
from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'teste' # resposta segreta
# conexao com o banco
mydb = mysql.connector.connect(user='myDbUser',password='myPassword123',host='0.0.0.0',database='mydesenv')
cur = mydb.cursor()
# querys de crud
SQL_SHOW = 'SELECT * FROM TB_PWD WHERE NOME = %s AND SENHA = %s'
SQL_INSERT = 'INSERT INTO TB_PWD (NOME, SENHA, EMAIL) values (%s, %s, %s)'
SQLPDW = 'SELECT * FROM TB_PWD WHERE NOME = %s'
SQL_SELECT = '''select nome_localidade, nome_produto, sum(d.quantidade * d.preco_unitario) as total
from TB_LOCALIDADE a, TB_PRODUTO b, TB_PEDIDOS c, TB_ITENS_PEDIDO d 
where a.id_localidade = c.ID_LOCALIDADE 
  and b.ID_PRODUTO = d.ID_PRODUTO
  and c.ID_TRANSACAO = d.ID_TRANSACAO
group by nome_localidade, nome_produto
order by nome_localidade, nome_produto'''

# logando na pagina
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'usuario' in request.form and 'senha' in request.form:
        usuario = request.form['usuario']
        senha = request.form['senha']
        cur.execute(SQL_SHOW,(usuario, senha))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['nome'] = account[1]
            return redirect(url_for('dados'))
        else:
            msg = 'Nome/Senha estão incorreta'
    return render_template('login.html', msg=msg)

# tela de logout
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# registrar novo usuario 
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'usuario' in request.form and 'senha' in request.form and 'email' in request.form:
        usuario = request.form['usuario']
        senha   = request.form['senha']
        email   = request.form['email']
        cur.execute(SQLPDW,(usuario, ))
        account = cur.fetchone()
        if account:
            msg = 'A conta já existe !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Endereço de email envalido'
        elif not re.match(r'[A-Za-z0-9]+', usuario):
            msg = 'Usuario contem muitos caracteres e numeros !'
        elif not usuario or not senha or not email:
            msg = 'Favor preencha o campos!'
        else:
            cur.execute(SQL_INSERT,(usuario, senha, email))
            mydb.commit()
            msg = 'Cadastra realizado com sucesso !'
        return redirect(url_for('login'))
        
    return render_template('register.html', msg=msg)
# Exibira resultado dos dados 
@app.route('/dados')
def dados():
    cur.execute(SQL_SELECT)
    dados = cur.fetchall()
    return render_template('dados.html', value= dados )


if __name__ == "__main__":
    app.run(debug=True)
