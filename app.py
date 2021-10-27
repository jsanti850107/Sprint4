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
                    cur.execute("INSERT INTO califica_productos(id_linea,calificacion,descrip_calificacion)values(?,?,?)",(producto,calificacion,observaciones))
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

#!!!-----------------------¡¡COMIENZA PROVEEDORES!!------------------!!!
#CREAR PROVEEDOR COMIENZA AQUI

@app.route("/crear/proveedor", methods = ["GET", "POST"])
def crearProve():
    global nom
    if 'usuario' in session:
        if request.method == "GET":
            return render("crearProvee.html", nom=nom, rol=rol)

        else:
            with sqlite3.connect("inventario.db") as con:
                cur=con.cursor()

            if request.form["submit_button"] == "Guardar":
         #Tomando los datos de la variable pasadas por el input
                
                name = request.form["name"]
                razonsocial = request.form["razonsocial"]
                domicilio = request.form["domicilio"]
                postal = request.form["postal"]
                localidad = request.form["localidad"]
                provincia = request.form["provincia"]
                pais = request.form["pais"]
                tlf = request.form["tlf"]
                correo = request.form["correo"]
                web = request.form["web"]
                rut = request.form["rut"]

                cur.execute("INSERT INTO proveedor (nom_proveedor, rsocial, dom_proveedor, postal_provee, localidad_prov, provincia_prov, pais, tel_proveedor, email, web_prov, rut) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, razonsocial, domicilio, postal, localidad, provincia, pais, tlf, correo, web, rut))

                con.commit()

                name = ""
                razonsocial = ""
                domicilio = ""
                postal = ""
                localidad = ""
                provincia = ""
                pais = ""
                tlf = ""
                correo = ""
                web = ""
                rut = ""

                flash("Guardado con exito")
            return render ("crearProvee.html", nom=nom, rol=rol)
    else:
        return redirect("/ingreso")

#----------------COMIENZA ELIMINAR PROVEEDOR------------------

@app.route("/eliminar/proveedor", methods = ["GET", "POST"])
def delproveedor():
    global nom
    long = 0
    proveedor={}
    if 'usuario' in session:
        if request.method == "GET":
    
            with sqlite3.connect("inventario.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM proveedor")
                con.commit()
                proveedor=cur.fetchall()
                long=len(proveedor)
               
            return render("eliminarprovee.html", long=long, nom=nom, rol=rol, proveedor=proveedor)

        else:
            dato = request.form["eliminarp"]
            dato = int(dato)
            with sqlite3.connect("inventario.db") as con:
                cur = con.cursor()
                cur.execute("DELETE FROM proveedor WHERE id_proveedor=?",[dato])
                con.commit()
                if con.total_changes>0:
                    con.close
                    flash("Eliminado con exito")
                else:
                    flash("Proveedor no encontrado")
            
            with sqlite3.connect("inventario.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM proveedor")
                con.commit()
                proveedor=cur.fetchall()
                long=len(proveedor)
            return render("eliminarprovee.html", long=long, nom=nom, rol=rol, proveedor=proveedor)
    else:
        return redirect("/ingreso")

#-------------------COMIENZA BUSCAR PROVEEDOR-----------------

@app.route("/buscar/proveedor", methods = ["GET", "POST"])
def buscar_proveedor():
    global nom
    row = []
    long = 0
    if 'usuario' in session:
        if request.method == "POST":
            provee_buscado = request.form["datos"]
            if provee_buscado != "":

                with sqlite3.connect(rutadb) as con:

                    cur = con.cursor()

                    cur.execute("SELECT * FROM proveedor WHERE id_proveedor=?",[provee_buscado])
                    row = cur.fetchone()
                    if row:
                        long = len(row)
                    else:
                         flash("Proveedor no encontrado")
                
                    
              
            
            else:
                flash("El input esta vacio")
        return render("buscarprovee.html", nom=nom, rol=rol, row = row, long = long)
    else:
        return redirect("/ingreso")

#-------------------COMIENZA EDITAR PROVEEDOR-----------------

provee_buscado2 = ""
row2=[]

#Ruta que lleva a la pagina editar
@app.route("/editar/proveedor", methods = ["GET", "POST"])
def editar_prov():
    global nom
    global provee_buscado2
    row2 = []
    long = 0

    if 'usuario' in session:
        if request.method == "POST":
            provee_buscado2 = request.form["datos2"]
            if provee_buscado2 != "":
                with sqlite3.connect(rutadb) as con:

                    cur = con.cursor()

                    cur.execute("SELECT * FROM proveedor WHERE id_proveedor=?",[provee_buscado2])
                    row2 = cur.fetchone()
                    if row2:
                        long = len(row2)
                    else:
                        flash("Provedor no encontrado")
                    
                    
            else:
                flash("El input esta vacio")
        return render("editar_prov.html", nom=nom, rol=rol, row2 = row2, long = long)
    else:
        return redirect("/ingreso")

@app.route("/editar", methods = ["GET","POST"])
def editar():
    global nom

    name = request.form["name2"]
    razonsocial = request.form["razonsocial2"]
    domicilio = request.form["domicilio2"]
    postal = request.form["postal2"]
    localidad = request.form["localidad2"]
    provincia = request.form["provincia2"]
    pais = request.form["pais2"]
    tlf = request.form["tlf2"]
    correo = request.form["correo2"]
    web = request.form["web2"]
    rut = request.form["rut2"]
    if nom != "":
        if request.method == "POST":
            with sqlite3.connect(rutadb) as con:
                cur = con.cursor()
                cur.execute("UPDATE proveedor SET nom_proveedor=?, rsocial=?, dom_proveedor=?, postal_provee=?, localidad_prov=?, provincia_prov=?, pais=?, tel_proveedor=?, email=?, web_prov=?, rut=? WHERE id_proveedor=?",[name, razonsocial, domicilio, postal, localidad, provincia, pais, tlf, correo, web, rut, provee_buscado2])
            flash("Editado con exito")

        return render("editar_prov.html", row2=row2, nom=nom, rol=rol)
    else:
        return redirect("/ingreso")

#---------------COMIENZA VISUALIZAR PROVEEDORES---------------

@app.route("/proveedores")
def list_proveedores():
    if 'usuario' in session: 
        with sqlite3.connect(rutadb) as con:

            cur=con.cursor()
            cur.execute("SELECT * FROM proveedor")
            con.commit()
            proveedor=cur.fetchall()
            long=len(proveedor)
    
        return render("resultado.html",proveedor=proveedor, nom=nom, rol=rol,long=long)
    else:
        return redirect("/ingreso")

rowl=rowp=[]
longl=longp=0

#/////////////////////////////////////////Agregar Producto//////////////////////////////////////////////////////
@app.route("/crear/producto",methods=["GET","POST"])
def crearproducrtos():
    global nom,rowl,rowp,longl,longp
    if 'usuario' in session:
        if request.method=="GET":
            with sqlite3.connect(rutadb) as con: 
                con.row_factory=sqlite3.Row #vista de diccionario
                cur=con.cursor()
                cur.execute("select id_linea, nom_linea from linea")
                rowl=cur.fetchall()
                longl=len(rowl)
                cur.execute("select id_proveedor, nom_proveedor from proveedor")
                rowp=cur.fetchall()
                longp=len(rowp)

            return render("agregarProducto.html",nom=nom,rol=rol,rowl=rowl,rowp=rowp,longl=longl,longp=longp)
        else:
            with sqlite3.connect(rutadb) as con:    
                cur=con.cursor()
                #id_producto=request.form["numid"]#id_producto
                id_linea=request.values["selectlinea"]#id_linea
                proveedor= request.values["selectprov"]#id_proveedor
                # #calificacion= request.form["calinum"]#id_calificacion
                lote= request.form["lote"]#lote
                referencia=request.form["ref"]#codigo
                #nombre=request.form["nomtxt"]#nombre
                descrp=request.form["destxt"]#descrp
                serialprod=request.form["serpod"]#serial_prod
                fechaLote=request.form["fechlot"]#fecha_lote
                cantRequerida=request.form["num2"]#cant_requerida
                cantBodega=request.form["num1"]#stock
                precioProd=request.form["precio"]#precio_producto
                cur.execute("INSERT INTO productos ( id_linea, id_proveedor, lote, codigo,descrip_producto,stock,serial_producto,fecha_lote,cant_requerida,precio) VALUES(?,?,?,?,?,?,?,?,?,?)",[id_linea,proveedor,lote,referencia,descrp,cantBodega,serialprod,fechaLote,cantRequerida,precioProd])
                con.commit()
                flash("Guardado con exito")  
                return render("agregarProducto.html",nom=nom,rol=rol,rowl=rowl,rowp=rowp,longl=longl,longp=longp)
                  
    else:
        return redirect("/ingreso")
#////////////////////Buscar Producto/////////////////////////////
@app.route("/buscar/producto", methods = ["GET","POST"])
def buscarp():
    global nom
    rows=[]
    long=0
    if 'usuario' in session:
        if request.method=="POST":
            with sqlite3.connect(rutadb) as con:
                referencia=request.form["bp"]#codigo
                if referencia!="":
                    cur=con.cursor()
                    #sentencia para validar usuario
                    cur.execute("SELECT * FROM productos WHERE codigo=?",[referencia])
                    rows= cur.fetchone()
                    if rows:
                        long=len(rows)
                    else:
                        flash("Producto no ha sido encontrado")
                else:
                    return "encontrar producto"
        return render("buscarprod.html",nom=nom,rol=rol,rows=rows,long=long,session=session)                
    else:
        return redirect("/ingreso")  
#////////////////////////////////Eliminar Producto/////////////////
@app.route("/eliminar/producto", methods = ["POST","GET"])
def eliminarp():
    if 'usuario' in session:
        if request.method=="POST":
            referencia=request.form["eliproduc"]#codigo
            with sqlite3.connect(rutadb) as con:
                cur=con.cursor()
                cur.execute("DELETE FROM productos WHERE codigo=?",[referencia])
                con.commit()
                if con.total_changes>0:
                    con.close
                    flash("Eliminado con exito")
                else:
                    flash("Producto no encontrado")
        return render ("eliminarprod.html",nom=nom,rol=rol)

    else:
        return redirect("/ingreso") 

#/////////////////////////////Visualizar Productos///////////////////////////////////////////////
@app.route("/visualizar/producto")
def visualizar_producto():
    if 'usuario' in session: 
        with sqlite3.connect(rutadb) as con:
            cur=con.cursor()
            cur.execute("SELECT * FROM productos")
            con.commit()
            productos=cur.fetchall()
            long=len(productos)
    
        return render("visualizar.html",productos=productos, nom=nom, rol=rol,long=long)
    else:
        return redirect("/ingreso")
#/////////////////////////////Editar Producto///////////////////////////////////////////////
row=[]
@app.route("/editar/producto", methods = ["GET","POST"])
def edi_prod():
    global rowl,nom,rowp,longl,longp
    referencia=""
    row=[]
    long=0
    if 'usuario' in session:
        if request.method=="POST":
            with sqlite3.connect(rutadb) as con:
                referencia= request.form["busqueda"]#codigo
                if referencia!="":
                    with sqlite3.connect(rutadb) as con:
                        cur=con.cursor()
                        #sentencia para validar usuario
                        cur.execute("SELECT * FROM productos WHERE codigo=?",[referencia])
                        row= cur.fetchone()
                        if row:
                            long=len(row)
                            flash("Pruducto encontrado") 
                        else:
                            flash("Producto no encontrado :(")
                            
                    
                else:
                    return "busqueda vacia"
        else:
            with sqlite3.connect(rutadb) as con: 
                con.row_factory=sqlite3.Row #vista de diccionario
                cur=con.cursor()
                cur.execute("select id_linea, nom_linea from linea")
                rowl=cur.fetchall()
                longl=len(rowl)
                cur.execute("select id_proveedor, nom_proveedor from proveedor")
                rowp=cur.fetchall()
                longp=len(rowp)
            return render("editarProducto.html",nom=nom,rol=rol,rowl=rowl,rowp=rowp,longl=longl,longp=longp,long=long,row=row)
        return render("editarProducto.html",row = row, nom=nom,rol=rol,long=long,busqueda=referencia,rowl=rowl,rowp=rowp,longl=longl,longp=longp)                
    else:
        return redirect("/ingreso")

@app.route("/editar/p", methods = ["GET","POST"])
def editar_p():
     #id_producto=request.form["numid"]#id_producto
    id_linea=request.values["selectlinea"]#id_linea
    proveedor= request.values["selectprov"]#id_proveedor
    # #calificacion= request.form["calinum"]#id_calificacion
    lote= request.form["lote"]#lote
    referencia=request.form["ref"]#codigo
    #nombre=request.form["nomtxt"]#nombre
    descrp=request.form["destxt"]#descrp
    serialprod=request.form["serpod"]#serial_prod
    fechaLote=request.form["fechlot"]#fecha_lote
    cantRequerida=request.form["num2"]#cant_requerida
    cantBodega=request.form["num1"]#stock
    precioProd=request.form["precio"]#precio_producto
    
    if 'usuario' in session:
        if request.method == "POST":
            with sqlite3.connect(rutadb) as con:
                cur=con.cursor()
                cur.execute("UPDATE productos SET id_linea=?,id_proveedor=?, lote=?,descrip_producto=?,stock=?,serial_producto=?,fecha_lote=?,cant_requerida=?,precio=? WHERE codigo=?",[id_linea,proveedor,lote,descrp,cantBodega,serialprod,fechaLote,cantRequerida,precioProd,referencia])
                return"Editado con Exito"
        return render("editarProducto.html",nom=nom,rol=rol,row=row)
    else:
        return redirect("/ingreso")  

#//////////////////Listado Productos requeridos
@app.route("/reporte/list_prod_req", methods=["GET"])
def productos_requeridos():
    if ('usuario' in session):
        with sqlite3.connect(rutadb) as con:
            con.row_factory = sqlite3.Row
            cur=con.cursor()
            #sentencia para validar usuario
            cur.execute("SELECT productos.*, linea.nom_linea FROM productos inner join linea on linea.id_linea=productos.id_linea")
            rows= cur.fetchall()
            long=len(rows)   
        return render("lprequeridos.html",rows = rows, nom=nom,rol=rol,long=long)                
    else:
        return redirect("/ingreso")

@app.route("/reporte/b_proveexprod", methods=["GET","POST"])
def b_proveexprod():
    global nom
    rows=[]
    long=0
    if 'usuario' in session:
        if request.method=="POST":
            with sqlite3.connect(rutadb) as con:
                con.row_factory = sqlite3.Row
                referencia=request.form["bp"]#codigo
                if referencia!="":
                    cur=con.cursor()
                    #sentencia para validar usuario
                    cur.execute("select proveedor.*, productos.id_linea,linea.nom_linea from proveedor inner join productos on productos.id_proveedor=proveedor.id_proveedor inner join linea on linea.id_linea=productos.id_linea where linea.id_linea=?",[referencia])
                    rows= cur.fetchall()
                    long=len(rows)
                else:
                    return "encontrar producto"
        return render("buscarprovxprod.html",nom=nom,rol=rol,rows=rows,long=long,session=session)                
    else:
        return redirect("/ingreso")


if __name__=="__main__":
    app.run(debug=True)
 
