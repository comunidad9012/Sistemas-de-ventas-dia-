from flask import Flask, render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL
from flask_paginate import Pagination, get_page_args
from random import sample
from werkzeug.utils import secure_filename
import os
from datetime import datetime




app=Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'PROGRAMACION2023'
app.config['MYSQL_DB'] = 'sistemadeventas'

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
    if request.method == 'POST':
        idProducto = request.form.get('idProducto') 
        nuevoPrecio = request.form.get('precio')
        nuevaCantidad = request.form.get('cantidad')

        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE producto SET precio = %s, cantidad = %s WHERE idProducto = %s',
                           (nuevoPrecio, nuevaCantidad, idProducto))
            mysql.connection.commit()
            cursor.close()
            print("Actualización correcta")
        except mysql.connector.Error as error:
            print("Error MySQL:", error)

    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp")
    productos = cursor.fetchall()
    cursor.close()

    return render_template("update.html", title="Pagina Principal", user="PRODUCTOS INGRESADOS CORRECTAMENTE", productos=productos)


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

        return render_template('seleccionado.html', resultados=resultados, categorias=categorias)




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






if __name__ == '__main__':
    app.run(port=8000, debug=True)
















