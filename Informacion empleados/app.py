from flask import Flask, flash
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime
import os
 
app = Flask(__name__)

mysql = MySQL()

# Inicializar la base de datos
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'empleados'
mysql.init_app(app)

# Acceder a la ruta de UPLOADS
CARPETA = os.path.join("uploads")
app.config['CARPETA'] = CARPETA


@app.route('/')
def index():

    conexion = mysql.connect() # conectar con la DB
    cursor = conexion.cursor() # establecer cursor
    cursor.execute("SELECT * FROM empleados")

    empleados = cursor.fetchall()

    return render_template('empleados/index.html', empleados=empleados)

@app.route("/destroy/<int:id>")
def destroy(id):

    conexion = mysql.connect()
    cursor = conexion.cursor()

    # eliminar imagen de la carpeta
    cursor.execute("SELECT foto FROM empleados WHERE id = %s;", (id))
    fila = cursor.fetchone()
    os.remove(os.path.join(app.config['CARPETA'], fila[0]))

    cursor.execute("DELETE FROM empleados WHERE id = %s;", (id))
    conexion.commit()

    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):

    conexión = mysql.connect() #estableces la conexion con la base de datos
    cursor = conexión.cursor() #crea cursor

    cursor.execute("SELECT * FROM empleados WHERE id = %s;", (id))

    empleados = cursor.fetchall()
    return render_template("/empleados/edit.html", empleados=empleados)

@app.route('/create')
def create():
    return render_template('/empleados/create.html')

@app.route('/store', methods = ["POST"])
def storage():

    nombre = request.form["txtNombre"]
    correo = request.form["txtCorreo"]
    foto = request.files["txtFoto"]

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if foto.filename != "":
        nuevoNombreFoto = tiempo + foto.filename
        foto.save("uploads/" + nuevoNombreFoto)


    datos = (nombre, correo, nuevoNombreFoto)

    sql = "INSERT INTO empleados (nombre, correo, foto) VALUES (%s,%s,%s);"
    conexion = mysql.connect() # conectar con la DB
    cursor = conexion.cursor() # establecer cursor
    cursor.execute(sql, datos)
    conexion.commit() # guardar cambios

    return redirect("/")

@app.route("/update", methods = ["POST"])
def update():

    nuevoNombre = request.form["txtNombre"]
    nuevoCorreo = request.form["txtCorreo"]
    foto = request.files["txtFoto"]
    id = request.form["txtId"]

    conexion = mysql.connect()
    cursor = conexion.cursor()

    #codificar imagen
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if foto.filename != "":
        nuevoNombreFoto = tiempo + foto.filename
        foto.save("uploads/" + nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id = %s;", (id))
        fila = cursor.fetchone()

        os.remove(os.path.join(app.config['CARPETA'], fila[0]))
        cursor.execute("UPDATE empleados SET foto = %s WHERE id = %s", (nuevoNombreFoto, id))

    datos = (nuevoNombre, nuevoCorreo, id)
    cursor.execute("UPDATE empleados SET "+
                    "nombre = %s,"+
                    "correo = %s" +
                    "WHERE id = %s;",
                    datos)
    conexion.commit()

    return redirect("/")


if __name__ == '__main__':
    app.run(debug = True)

