from flask import Flask, render_template as render,request,flash, redirect, session
import sqlite3
import os
from werkzeug.utils import escape

from wtforms import meta
from forms.formularios import Buscar, Calificar, Chpass, Editar, Registro,Login,Productos, Editar
import hashlib

app=Flask(__name__)
app.secret_key= os.urandom(24)
nom=""
rol=""
pwdor=""
rutadb="inventario.db"
#ruta inicial
@app.route("/")
def inicio():
    global nom,rol
    nom=""
    rol=""
    return render("inicio.html",nom=nom,rol=rol)

@app.route("/salir")
def salir():
        global nom,rol
        nom=""
        rol=""
        session.clear()
        return redirect("/ingreso")

#///Ruta para mostrar el perfil
@app.route("/usuarios/<id_usuario>", methods=["GET"])
def info_usuario(id_usuario):
    if 'usuario' in session:
        with sqlite3.connect(rutadb) as con:
            con.row_factory=sqlite3.Row #lista de diccionario
            cur=con.cursor()
            #sentencia para validar usuario
            cur.execute("SELECT * FROM usuarios WHERE usuario =?",[id_usuario])
            rows= cur.fetchone()
            long=len(rows)
            return render("pusuario.html",rows=rows,long=long)
    else:
        return redirect("/ingreso")

#ruta para ingresar
@app.route("/ingreso",methods=["GET", "POST"])
def ingreso():
    global nom,rol
    #si el metodo es get envia al login, significa que no se ha logueado
    if request.method=="GET":
        return render("login.html")
    else: 
          
        #asigna a variables los campos del formulario login
        nom=request.form["nombre"]    
        pwd=request.form["psw"]    
        #/////////////////////////////
        #cifra la contraseña
        encrip = hashlib.sha256(pwd.encode('utf-8'))
        pass_enc = encrip.hexdigest()
        #conecta a la base de datos
        with sqlite3.connect(rutadb) as con:
            con.row_factory = sqlite3.Row
            cur=con.cursor()
            #sentencia para validar usuario
            cur.execute("SELECT * FROM usuarios WHERE usuario =? AND password=?",[nom,pass_enc])
            row= cur.fetchone()
            #si row tiene informacion significa que los datos de ingreso son correctos, si no refirige a login con mensaje de error
            if row:
                session['usuario']=nom
                session['pwd']=row['password']
                session['rol']=row['rol']
                rol=row[5]
                return redirect("/servicios")
            else: 
                flash("Usuario/Password incorrecto")
                return render("login.html")
               
#envio a pagina servicios
@app.route("/servicios", methods=["GET"])
def servicios():
    global nom,rol
    if 'usuario' in session:
    #if nom!="":
        return render("servicios.html",nom=nom,rol=rol)
    else:
        return redirect("/ingreso")

#registrar usuario
@app.route("/usuario/registro",methods=["GET","POST"])
def registrar():
    global nom,rol
    if 'usuario' in session:
        frm=Registro()
        if frm.validate_on_submit():
            username = frm.usuario.data
            #/////
            with sqlite3.connect(rutadb) as con:
                # crea un cursor para manipular la base de datos
                cur=con.cursor()
                #prepara sentencia SQL, preferiblemente no concatenar
                cur.execute("SELECT * FROM usuarios where usuario=?",[username])
                #se ejecuta la sentencia
                con.commit()
                row=cur.fetchone()
                if row:
                    flash("Usuario existente, intente con otro")
                    frm.usuario.data=""
                else:
                    
                    password = frm.password.data
                    nombres = frm.nombres.data
                    apellidos = frm.apellidos.data
                    vrol = frm.rol.data
                    if vrol== 1:
                        vrol = "UsuarioFinal"
                    elif vrol==2:
                        vrol = "Admin"
                    elif vrol==3:
                        vrol = "SuperAdmin"
                    
                    #cifra la contraseña
                    encrip = hashlib.sha256(password.encode('utf-8'))
                    pass_enc = encrip.hexdigest()
                    #conecta a la base de datos
                    with sqlite3.connect(rutadb) as con:
                        # crea un cursor para manipular la base de datos
                        cur=con.cursor()
                        #prepara sentencia SQL, preferiblemente no concatenar
                        cur.execute("INSERT INTO usuarios(usuario,password,nombres,apellidos,rol)values(?,?,?,?,?)",(username,pass_enc,nombres,apellidos,vrol))
                        #se ejecuta la sentencia
                        con.commit()
                        frm.usuario.data=""
                        frm.password.data=""
                        frm.nombres.data=""
                        frm.apellidos.data=""
                        frm.rol.data=""
                        flash("Guardado con exito")
                        #return "guardado con exito <a href='/servicios'>Servicios</a>"
        return render("registro.html",frm=frm)
    else:
        return redirect("/ingreso")

#Ruta para renderizar pagina de busqueda
@app.route("/usuarios/busqueda", methods=["GET","POST"])
def busuarios():
    if 'usuario' in session:
        global pwdor
        frm=Buscar()
        frm1=Registro()
        #conecta a la base de datos
        if frm.validate_on_submit():
            busqueda = frm.ubusqueda.data
            frm1.usuario.data=""
            frm1.nombres.data=""
            frm1.apellidos.data=""
            frm1.rol.data=""
            with sqlite3.connect(rutadb) as con:
                # crea un cursor para manipular la base de datos
                cur=con.cursor()
                #prepara sentencia SQL, preferiblemente no concatenar
                cur.execute("SELECT * FROM usuarios WHERE usuario=?",[busqueda])
                row=cur.fetchone()
                
                if row:
                    frm1.usuario.data=row[1]
                    frm1.nombres.data=row[3]
                    frm1.apellidos.data=row[4]
                    pwdor=row[2]
                    if row[5]=="Admin":
                        frm1.rol.choices=[("2","Administrador"), ("1","Usuario Final"),("3","SuperAdministrador")]
                    elif row[5]=="SuperAdmin":
                        frm1.rol.choices=[("3","SuperAdministrador"), ("1","Usuario Final"),("2","Administrador")]
                    else:
                        frm1.rol.choices=[("1","Usuario Final"), ("2","Administrador"),("3","SuperAdministrador")]
                    return render("busuarios.html",frm=frm, frm1=frm1,nom=nom,rol=rol,row=row) 
                else:
                     
                    frm1.usuario.data=""
                    frm1.nombres.data=""
                    frm1.apellidos.data=""
                    frm1.rol.data=""
                    flash("Usuario no encontrado")
                    return render("busuarios.html",frm=frm,nom=nom,rol=rol) 

        return render("busuarios.html",frm=frm,nom=nom,rol=rol)
    else:
        return redirect("/ingreso")

#//////////////////////////////////////////////////
#eliminar
@app.route("/usuario/delete", methods=["POST"])
def eusuario():
    if 'usuario' in session:
        frm1=Registro()
        frm=Buscar()
        user=escape(frm1.usuario.data)
        if user!=nom:
            with sqlite3.connect(rutadb) as con:
                cur=con.cursor()
                cur.execute("DELETE FROM usuarios WHERE usuario=?",[user])
                con.commit()
                if con.total_changes>0:
                    frm.ubusqueda.data=""
                    frm1.usuario.data=""
                    frm1.nombres.data=""
                    frm1.apellidos.data=""
                    frm1.rol.data=""
                    flash  ("Usuario eliminado")
                else:
                    flash("Usuario No se pudo eliminar")
        else:
            flash("Usuario logueado no se puede eliminar")
        return render("busuarios.html",frm=frm, frm1=frm1,nom=nom,rol=rol)
    else:
       return redirect("/ingreso")
#/////////////////////////////////////
#editar
@app.route("/usuario/update", methods=["POST"])
def uusuario():
    global nom,pwdor
    #//////////////////////////////
    #/////Revisar esta logica/////
    #/////////////////////////////
    if 'usuario' in session:
        frm=Buscar()
        frm1=Registro()
        if frm.validate_on_submit():
            #se asigna a variable la busqueda, e el campo de usuario obtenido para luego hacer validaciones
            usuario=escape(frm1.usuario.data)
            busqueda=escape(frm.ubusqueda.data)
            #si usuario igual a busqueda significa que el usuario no se modifico
            if usuario==busqueda:
                nombres=escape(frm1.nombres.data)
                apellidos=escape(frm1.apellidos.data)
                password=request.form["clave"]
                encrip = hashlib.sha256(password.encode('utf-8'))
                pass_enc = encrip.hexdigest()
                if frm1.rol.data==1:
                    erol="UsuarioFinal"
                elif frm1.rol.data==2:
                    erol="Admin"
                elif frm1.rol.data==3:
                    erol="SuperAdmin" 
                if pwdor == password:
                    with sqlite3.connect(rutadb) as con:
                        cur=con.cursor()
                        #prepara sentencia SQL, preferiblemente no concatenar
                        cur.execute("UPDATE usuarios SET nombres =?, apellidos=?,rol=? WHERE usuario=?",[nombres,apellidos,erol,usuario])
                        
                else:
                    with sqlite3.connect(rutadb) as con:
                        cur=con.cursor()
                        cur.execute("UPDATE usuarios SET password=?, nombres =?, apellidos=?,rol=? WHERE usuario=?",[pass_enc,nombres,apellidos,erol,usuario])
                flash("Usuario actualizado")
                pwdor=""
            else:#si no, el usuario si fue modificado
                with sqlite3.connect(rutadb) as con:
                    con.row_factory=sqlite3.Row #vista de diccionario
                    cur=con.cursor()
                    #se realiza consulta para verificar si usuario existe
                    cur.execute("SELECT * FROM usuarios where usuario=?",[usuario])
                    rows=cur.fetchone()
                    #si rows tiene informacion significa que el usuario existe, si no procede con la actualizacion
                    if rows:
                        frm1.usuario.data=""
                        flash("Usuario Existente, intente con otro")
                    else:
                        password=request.form["clave"]
                        encrip = hashlib.sha256(password.encode('utf-8'))
                        pass_enc = encrip.hexdigest()
                        nombres=escape(frm1.nombres.data)
                        apellidos=escape(frm1.apellidos.data)
                        if frm1.rol.data==1:
                            erol="UsuarioFinal"
                        elif frm1.rol.data==2:
                            erol="Admin"
                        elif frm1.rol.data==3:
                            erol="SuperAdmin"
                        
                        if pwdor == password:  
                            with sqlite3.connect(rutadb) as con:
                                cur=con.cursor()             
                                #prepara sentencia SQL, preferiblemente no concatenar, como el usuario fue cambiado, se debe buscar con la variable busqueda debido a que esta aun contiene su valor inicial
                                cur.execute("UPDATE usuarios SET usuario=?, nombres =?, apellidos=?,rol=? WHERE usuario=?",[usuario,nombres,apellidos,erol,busqueda])                            
                        else:
                            with sqlite3.connect(rutadb) as con:
                                cur=con.cursor()             
                                cur.execute("UPDATE usuarios SET  usuario=?, password=?, nombres =?, apellidos=?,rol=? WHERE usuario=?",[usuario, pass_enc,nombres,apellidos,erol,busqueda])
                        flash("usuario Actualizado")
                        pwdor=""
                        #si busqueda es igual a nom y usuario es diferente de nom, significa que el usuario editado fue el logueado por lo que se deben refrescar la variable global nom y el campo de busqueda en el formulario
                        if busqueda==nom and usuario!=nom:
                            nom=usuario
                            session['usuario']=nom
                            #frm.ubusqueda.data=nom
    else:
        return redirect("/ingreso")
    return render("busuarios.html",frm=frm, frm1=frm1,nom=nom,rol=rol)
    

#//////////////////////////////////////////////////
#Cambiar Contraseña
@app.route("/usuario/cmbpassword", methods=["POST","GET"])
def cbiopassword():
    if 'usuario' in session:
        frm=Chpass()
        if frm.validate_on_submit():
            password=frm.pwd.data
            encrip = hashlib.sha256(password.encode('utf-8'))
            pass_enc = encrip.hexdigest()
            with sqlite3.connect(rutadb) as con:
                con.row_factory=sqlite3.Row #lista de diccionario
                # crea un cursor para manipular la base de datos
                cur=con.cursor()
                #prepara sentencia SQL, preferiblemente no concatenar
                cur.execute("SELECT * FROM usuarios WHERE usuario=?",[nom])
                row=cur.fetchone()
                if row['password']== pass_enc:
                    if frm.npwd.data == frm.cnpwd.data:
                        password=frm.npwd.data
                        encrip = hashlib.sha256(password.encode('utf-8'))
                        pass_enc = encrip.hexdigest()
                        cur.execute("UPDATE usuarios SET password =? WHERE usuario=?",[pass_enc,nom])
                        con.commit()
                        flash ("Cambio de contraseña realizado con éxito" )
                    else:
                        frm.npwd.data=""
                        frm.cnpwd.data=""
                        flash ("Contraseña nueva y la confirmacion no coinciden" )
                else:
                    frm.pwd.data=""
                    frm.npwd.data=""
                    frm.cnpwd.data=""
                    flash ("Contraseña actual no es correcta") 
    else:
        return redirect("/ingreso")
    return render("cmbpassword.html",nom=nom,rol=rol,frm=frm)

#Ruta para renderizar pagina de visualizar usuarios
@app.route("/usuarios/visualizar", methods=["GET"])
def vusuarios():
    if 'usuario' in session:
        #conecta a la base de datos
        with sqlite3.connect(rutadb) as con:
            # crea un cursor para manipular la base de datos
            cur=con.cursor()
            #prepara sentencia SQL, preferiblemente no concatenar
            cur.execute("SELECT * FROM usuarios")
            #se ejecuta la sentencia
            con.commit()
            usuarios=cur.fetchall()
            long=len(usuarios)
        #return f"{usuarios[0][1]}"
        return render("vusuarios.html",usuarios=usuarios,long=long)
    else:
        return redirect("/ingreso")

#Ruta a Dashboard
@app.route("/servicios/dash", methods=["GET"])
def dash():
    if 'usuario' in session:
        varp=['Month', 'TAOS', 'T-CROSS', 'BEATTLE', 'GOL', 'SAVEIRO PLUS', 'POLO']
        var1=[2017, 500,      938,         522,             998,           450,      614.6]
        return render("dashboard.html",varp=varp,var1=var1)
    else:
        return redirect("/ingreso")

@app.route("/servicios/calificar", methods=["GET","POST"])
def calificar():
    if 'usuario' in session:
        frm=Calificar()
        #////////////////
        with sqlite3.connect(rutadb) as con:
            con.row_factory=sqlite3.Row #lista de diccionario
            cur = con.cursor()
            cur.execute("select id_linea, nom_linea from linea order by nom_linea" )
            rows=cur.fetchall()
                 
            #convierte los datos en una lista de tuplas y lo asigna al select marca
            lista=[tuple(r) for r in rows]
            lista.insert(0,("","-- Seleccione una opción --"))  
            frm.sf_producto.choices=lista
        #///////////////////////////////////////////
        if frm.validate_on_submit:
            calificacion=request.values.get("star")
            producto=frm.sf_producto.data
            observaciones=frm.observaciones.data
            if calificacion!=None:
                with sqlite3.connect(rutadb) as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO califica_productos(id_linea,calificacion,observaciones)values(?,?,?)",(producto,calificacion,observaciones))
                    #se ejecuta la sentencia
                    con.commit()
                flash("Producto calificado con éxito")
            else:
                flash("No olvide calificar el producto")
                calificacion=""
        return render("calificacion.html",frm=frm,rows=rows)
    else:
        return redirect("/ingreso")

@app.route("/servicios/calificar/listar", methods=["GET"])
def listarCalificiacion():
    if 'usuario' in session:
         #conecta a la base de datos
        with sqlite3.connect(rutadb) as con:
            con.row_factory=sqlite3.Row #lista de diccionario
            # crea un cursor para manipular la base de datos
            cur=con.cursor()
            #prepara sentencia SQL, preferiblemente no concatenar
            cur.execute("select califica_productos.*, linea.nom_linea from califica_productos inner join linea on linea.id_linea = califica_productos.id_linea")
            #se ejecuta la sentencia
            rows=cur.fetchall()
            long=len(rows)
        return render("listarcalificacion.html",nom=nom,rol=rol,calificaciones=rows,long=long)
    else:
        return redirect("/ingreso")

if __name__=="__main__":
    app.run(debug=True)