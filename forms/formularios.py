from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField
from wtforms.validators import DataRequired

class Registro(FlaskForm):
    usuario = StringField("Usuario: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    nombres = StringField("Nombres: ", validators=[DataRequired()])
    apellidos = StringField("Apellidos: ", validators=[DataRequired()])
    rol = SelectField("Rol: ", choices=[("0","- Eliga una opción -"),("1","Usuario Final"),("2","Administrador"),("3","SuperAdministrador")],coerce=int,validators=[DataRequired(message="Seleccione un Rol")])
    enviar = SubmitField("Registrar")
    editar = SubmitField("Editar", render_kw=({"onfocus":"cambiaRuta('/usuario/update')"}))
    eliminar = SubmitField("Eliminar", render_kw=({"onfocus":"cambiaRuta('/usuario/delete')"}))
    consultar = SubmitField("Eliminar")

class Login(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    entrar = SubmitField("Entrar") 

class Buscar(FlaskForm):
    ubusqueda = StringField("Usuario a buscar", validators=[DataRequired()])
    buscar = SubmitField("Buscar", render_kw=({"onfocus":"cambiaRuta('/usuarios/busqueda')"})) 


class Productos(FlaskForm):
    codigo = StringField("Código")
    nombre = StringField("Nombre")
    precio = StringField("Precio")
    stock = StringField("Stock")
    guardar = SubmitField("Guardar", render_kw=({"onfocus":"cambiaRuta('/producto/save')"}))
    consultar = SubmitField("Consultar", render_kw=({"onfocus":"cambiaRuta('/producto/get')"}))
    editar = SubmitField("Editar", render_kw=({"onfocus":"cambiaRuta('/producto/update')"}))
    eliminar = SubmitField("Eliminar", render_kw=({"onfocus":"cambiaRuta('/producto/delete')"}))

class Editar(FlaskForm):
    usuario = StringField("Usuario: ")
    password = PasswordField("Password: ")
    nombres = StringField("Nombres: ")
    apellidos = StringField("Apellidos: ")
    rol = StringField("Rol: ")
    editar = SubmitField("Editar", render_kw=({"onfocus":"cambiaRuta('/usuario/update')"}))
    eliminar = SubmitField("Eliminar", render_kw=({"onfocus":"cambiaRuta('/usuario/delete')"}))

class Chpass(FlaskForm):
    pwd=PasswordField("Contraseña actual: ", validators=[DataRequired()])
    npwd=PasswordField("Nueva contraseña: ", validators=[DataRequired()])
    cnpwd=PasswordField("Confirmar contraseña: ", validators=[DataRequired()])
    enviar = SubmitField("cambiar") 