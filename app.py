from flask import Flask, render_template,request,redirect,url_for,flash,Response, session
from flask_mysqldb import MySQL
from flask_paginate import Pagination, get_page_args
from random import sample
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from random import sample
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired




app=Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static'
#CONFIGURACION DE LA BASE DE DATOS
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='genaro'
app.config['MYSQL_PASSWORD']='password'
app.config['MYSQL_DB']='sistema-ventas'
mysql=MySQL(app)
#-----------------------------------------------------


#CONFIGURACION DE FLASK MAIL
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'gpanelli3@gmail.com'
app.config['MAIL_PASSWORD'] = 'qsxl bfml iosb beta'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail= Mail(app)

app.secret_key="secret_key"
s = URLSafeTimedSerializer('Thisisasecret!')


mysql=MySQL(app)

app.secret_key = 'mysectrectkey'





 
@app.route('/')
def index():
    categorias = listabebidas()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    
    # Establecer el número de productos por página
    per_page = 6  # Cambiar este valor para ajustar el número de productos por página
    offset = page * per_page - per_page
    
    # Obtener el número total de productos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM producto')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM producto LIMIT %s OFFSET %s', (per_page, offset))
    productos = cursor.fetchall()
    cursor.close()
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('inicio.html', productos=productos, categorias=categorias, pagination=pagination)





@app.route('/agregarProd')
def agregarProd():
    return render_template('agregarProd.html')


@app.route('/ingresarProd', methods=['POST'])
def ingresarProd():
    if 'archivo' not in request.files:
        return 'ningún archivo'
    imagen = request.files['archivo']
    if imagen.filename == '':
        return 'ningún archivo'
    if imagen:
        name = request.form['nombre']
        descr = request.form['descripcion']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        cat = request.form['categoria']
        imagen = request.files['archivo']
        nombre_archivo = secure_filename(imagen.filename)
        tipo_archivo = nombre_archivo.rsplit('.', 1)[1]
        nombre_archivo = nombre_archivo.rsplit('.', 1)[0]
        nombre_modificado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.{tipo_archivo}"
        nombre_final = nombre_archivo+nombre_modificado
        imagen.save('static/'+nombre_final)
        try:
            cursor = mysql.connection.cursor()
            sql = f"INSERT INTO `producto` (`nombre`, `descripcion`, `precio`, `cantidad`,`id_cat_corresp`, `imagen`) VALUES ('{name}', '{descr}', '{precio}', '{cantidad}', '{cat}','{nombre_final}');"
            cursor.execute(sql)
            mysql.connection.commit()
        except Exception as e:
            print("Error MySQL:", str(e))
        return redirect('inicio')

       


@app.route('/update', methods=['GET', 'POST'])
def update():
    
    idProducto = request.form.get('idProducto') 
    
    
    cursor = mysql.connection.cursor()
    cursor.execute (f"select * FROM producto WHERE (`idProducto` = '{idProducto}')")
    productos = cursor.fetchone()
    cursor.close()

    return render_template("update.html", productos=productos)

#CONFIRMAR MODIFICACION DEL PRODUCTO
from flask import redirect

@app.route('/confirmarcambios', methods=['POST'])
def confirmarcambios():
    idProducto = request.form.get('ID') 
    nombre = request.form.get('nombre') 
    descripcion = request.form.get('descripcion') 
    precio = request.form.get('precio') 
    cantidad = request.form.get('cantidad') 

    cursor = mysql.connection.cursor()
    cursor.execute(f"UPDATE producto SET descripcion = '{descripcion}', precio = '{precio}', cantidad = '{cantidad}' WHERE idProducto = {idProducto};")
    mysql.connection.commit()  # Guardar los cambios en la base de datos
    cursor.close()

    return redirect('/homeAdmin')

#ELIMINAR PRODUCTOS
@app.route('/borrar', methods=['GET', 'POST'])
def ue():
    
    idProducto = request.form.get('idProducto') 
    print(idProducto)
    
    cursor = mysql.connection.cursor()
    cursor.execute (f"Delete FROM producto WHERE (`idProducto` = '{idProducto}')")
    mysql.connection.commit()  # Guardar los cambios en la base de datos
    cursor.close()

    return redirect('/homeAdmin')


def listabebidas():
    data = {}

    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM categorias"
    cursor.execute(sql)
    categorias = cursor.fetchall()
    
    return(categorias)



@app.route("/categ", methods=['POST'])
def seleccion():
    if request.method == 'POST':

        id= request.form['pc']
        
        cursor = mysql.connection.cursor()
        sql= "SELECT * FROM producto WHERE id_cat_corresp = %s " 
        cursor.execute(sql,(id,))
        resultados = cursor.fetchall()
        categorias=listabebidas()
        sql = "SELECT * FROM categorias WHERE idcategorias = %s " 
        cursor.execute(sql,(id,))
        productos = cursor.fetchone()
        cursor.close()

        return render_template('seleccionado.html', resultados=resultados, categorias=categorias, productos=productos)




@app.route('/usuario') 
def usuario():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * from usuario")
    usuarios=[]
    for i in cursor:
        usuarios.append(i)
    
    nom='gpanelli3'
    con='123456'
        
    for x in usuarios:
        if x[1] == nom and x[2] == con:
            usu=x[1]
            print("puede ingresar", usu)
            return redirect("/inicio")
        else:
            print("usuario incorrecto")
            return render_template("index.html")


@app.route('/homeAdmin')
def homeAdmin():
    
    categorias = listabebidas()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    
    # Establecer el número de productos por página
    per_page = 6  # Cambiar este valor para ajustar el número de productos por página
    offset = page * per_page - per_page
    
    # Obtener el número total de productos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM producto')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM producto LIMIT %s OFFSET %s', (per_page, offset))
    productos = cursor.fetchall()
    cursor.close()
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('homeAdmin.html', productos=productos, categorias=categorias,pagination=pagination, mensaje="Rol actual: Administrador")

@app.route('/homeUser')
def homeUser():
    
    categorias = listabebidas()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    
    # Establecer el número de productos por página
    per_page = 6  # Cambiar este valor para ajustar el número de productos por página
    offset = page * per_page - per_page
    
    # Obtener el número total de productos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM producto')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM producto LIMIT %s OFFSET %s', (per_page, offset))
    productos = cursor.fetchall()
    cursor.close()
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('homeUser.html', productos=productos, categorias=categorias,pagination=pagination, mensaje="Rol actual: Usuario")


#DEVOLUCION AL LOGIN
@app.route('/login')
def login():
    return render_template('login.html')


#INGRESO DE USUARIO
@app.route('/ingreso', methods=['GET', 'POST']) 
def ingreso():


    if request.method == 'POST' and 'nombre' in request.form and 'contra' in request.form:
        usuario = request.form.get('nombre') 
        contra = request.form.get('contra')


        cursor=mysql.connection.cursor()

        cursor.execute("SELECT * from usuario where usuario = %s AND contra = %s", (usuario,contra))
        account=cursor.fetchone()

        if account:
            session['logueado'] = True
            session['usuario'] = usuario


            if account[3]==1:
                return redirect(url_for('homeAdmin'))

            elif account[3]==2:
                return redirect(url_for('homeUser'))
        
        else:
            return render_template('login.html', mensaje="USUARIO O CONTRASEÑA INCORRECTA")
        
        

#REGISTRO DE USUARIOS
@app.route("/registro")
def registro():
    return render_template("registro.html")



@app.route('/crearRegistro', methods=['GET', 'POST'])
def crearRegistro():   

    nom = request.form.get('nombre') 
    contra = request.form.get('contra')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT usuario FROM usuario')
    resultados = cursor.fetchall()

    for resultado in resultados: 
        if resultado[0] == nom:
            return render_template('registro.html', mensaje='Este usuario ya se encuentra registrado')
    
    cursor.execute('INSERT INTO usuario(usuario,contra,id_rol) VALUES(%s,%s,%s)', (nom, contra, 2))
    mysql.connection.commit()

    #aca esta la confirmacion del mail de la cuenta que se registra
    #MAIL--------------------------------------------------------------------------
    token= s.dumps(nom)

    msg=Message ('Confirmar email', sender=app.config['MAIL_USERNAME'], recipients=[nom])
    link= url_for('confirm_email', token=token, _external=True)
    msg.body='tu link es {}'.format(link)
    mail.send(msg)

    return "<h1>Revisa tu mail y confirma tu cuenta</h1>"

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, max_age=3600)
    except SignatureExpired:
        return '<h1>El token expiro</h1>'
    return redirect(url_for('login', mensaje="Usuario registrado correctamente"))
#MAIL---------------------------------------------------------------------

@app.route('/buscarprod', methods=['POST'])
def buscarprod():
    consulta = request.form.get('consulta')
    cursor = mysql.connection.cursor()
    # Utilizamos el formato de placeholders %s y pasamos 'consulta' como parámetro en un tuple
    query = "SELECT * FROM producto WHERE nombre LIKE %s"
    like_pattern = f"%{consulta}%"  # Crea el patrón para la búsqueda LIKE
    cursor.execute(query, (like_pattern,))
    prodobtenido = cursor.fetchall()
    cursor.close()  # No olvides cerrar el cursor
    print(prodobtenido)
    
    return render_template('productobuscado.html', prodobtenido=prodobtenido)
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=8000, debug=True)
















