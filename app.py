from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
import json
import os
from models import Almacen, Mensaje, Carpeta

app = Flask(__name__)
# Agrega una clave secreta para la seguridad de las sesiones
app.secret_key = 'una_clave_secreta_muy_fuerte_y_unica' # CAMBIA ESTO EN PRODUCCIÓN

# =========================
# LISTA ENLAZADA DE USUARIOS
# =========================

class NodoUsuario:
    def __init__(self, nombre, email, contraseña):
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña
        self.siguiente = None

class ListaUsuarios:
    def __init__(self):
        self.cabeza = None
        self.cargar_desde_json()

    def registrar_usuario(self, nombre, email, contraseña):
        if self.buscar_por_email(email):
            return False  # Ya existe

        nuevo = NodoUsuario(nombre, email, contraseña)
        if not self.cabeza:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo

        self.guardar_en_json()
        return True

    def buscar_por_email(self, email):
        actual = self.cabeza
        while actual:
            if actual.email == email:
                return actual
            actual = actual.siguiente
        return None

    def obtener_todos(self):
        usuarios = []
        actual = self.cabeza
        while actual:
            usuarios.append({
                "nombre": actual.nombre,
                "email": actual.email,
                "contraseña": actual.contraseña
            })
            actual = actual.siguiente
        return usuarios

    def guardar_en_json(self):
        with open("usuarios.json", "w") as archivo:
            json.dump(self.obtener_todos(), archivo, indent=4)

    def cargar_desde_json(self):
        # Asegurarse de que la lista esté vacía antes de cargar
        self.cabeza = None 
        
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r") as archivo:
                datos = json.load(archivo)
                actual = None
                
                for usuario in datos:
                    # Construcción directa de la lista enlazada
                    nuevo = NodoUsuario(usuario["nombre"], usuario["email"], usuario["contraseña"])
                    
                    if not self.cabeza:
                        self.cabeza = nuevo
                        actual = self.cabeza
                    else:
                        actual.siguiente = nuevo
                        actual = nuevo


usuarios = ListaUsuarios()

# =========================
# Almacen persistente de carpetas y mensajes
# =========================

# Crea/usa data.json en el directorio del proyecto
almacen = Almacen(path='data.json')


# =========================
# RUTAS FLASK (TODAS DEBEN IR ANTES DE app.run())
# =========================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = ""
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form['contraseña']

        if usuarios.registrar_usuario(nombre, email, contraseña):
            mensaje = "✅ Usuario registrado con éxito!"
        else:
            mensaje = "❌ El email ya está registrado."

    return render_template('registro.html', mensaje=mensaje)

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ""
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        usuario = usuarios.buscar_por_email(email)

        if usuario and usuario.contraseña == contraseña:
            # ✅ Almacenar el email en la sesión
            session['usuario_email'] = usuario.email 
            # Redirigir a 'componer_correo' sin parámetros en la URL
            return redirect(url_for('componer_correo')) 
        else:
            mensaje = "❌ Email o contraseña incorrectos."

    return render_template('login.html', mensaje=mensaje)

@app.route('/usuarios')
def ver_usuarios():
    lista = usuarios.obtener_todos()
    return render_template('usuarios.html', usuarios=lista)

@app.route('/correo', methods=['GET', 'POST'])
def componer_correo():
    # 🛑 Verificar si el usuario está logueado
    if 'usuario_email' not in session:
        # Si no hay sesión, redirigir al login
        return redirect(url_for('login')) 
    
    # 🚀 Obtener el email del remitente de la sesión
    remitente = session['usuario_email']
    
    mensaje = ""
    # El request.args.get('remitente_email', 'Desconocido') ya no es necesario
    # porque lo obtienes de la sesión

    if request.method == 'POST':
        destinatario = request.form['destinatario']
        asunto = request.form['asunto']
        cuerpo = request.form['cuerpo']

        # Insertar el mensaje en el almacen persistente (Inbox por defecto)
        nuevo = Mensaje(remitente, destinatario, asunto, cuerpo)
        almacen.agregar_mensaje(nuevo)
        mensaje = "✅ Mensaje enviado y guardado con éxito!"
        flash(mensaje, 'success')

    # Pasamos el email del remitente (de la sesión) a la plantilla
    return render_template('correo.html', mensaje=mensaje, remitente_email=remitente)

@app.route('/logout')
def logout():
    session.pop('usuario_email', None) # Elimina el email de la sesión
    return redirect(url_for('login')) # Redirige al login

@app.route('/mensajes')
def ver_mensajes():
    # Construir lista de mensajes con info de carpeta (añadir carpeta actual)
    lista = []
    for m in almacen.mensajes.values():
        d = m.to_dict()
        carpeta = almacen.carpeta_de_mensaje(m.id)
        d['carpeta_id'] = carpeta.id if carpeta else None
        d['carpeta_ruta'] = '/'.join(['Inbox']) if carpeta is None else None
        if carpeta:
            # construir ruta legible
            # (usar listar_carpetas_con_ruta para buscar la ruta por id)
            rutas = [c for c in almacen.listar_carpetas_con_ruta() if c['id'] == carpeta.id]
            d['carpeta_ruta'] = rutas[0]['ruta'] if rutas else carpeta.nombre
        lista.append(d)

    carpetas = almacen.listar_carpetas_con_ruta()
    return render_template('mensajes.html', mensajes=lista, carpeta_raiz=almacen.raiz, carpetas=carpetas)


@app.route('/carpetas/crear', methods=['POST'])
def crear_carpeta():
    nombre = request.form.get('nombre')
    padre_id = request.form.get('padre_id')
    if not nombre:
        return redirect(url_for('ver_mensajes'))
    padre = almacen.raiz if not padre_id else almacen.raiz.buscar_por_id(padre_id)
    if padre is None:
        padre = almacen.raiz
    nueva = Carpeta(nombre)
    padre.hijos.append(nueva)
    almacen.guardar()
    flash(f"Carpeta '{nombre}' creada en {padre.nombre}", 'success')
    return redirect(url_for('ver_mensajes'))


@app.route('/mensajes/mover', methods=['POST'])
def mover_mensaje():
    mensaje_id = request.form.get('mensaje_id')
    destino_id = request.form.get('destino_id')
    if not mensaje_id or not destino_id:
        flash('Faltan datos para mover el mensaje.', 'error')
        return redirect(url_for('ver_mensajes'))
    ok = almacen.mover_mensaje(mensaje_id, destino_id)
    if ok:
        flash('✅ Mensaje movido correctamente.', 'success')
    else:
        flash('❌ No se pudo mover el mensaje. Verifica IDs.', 'error')
    return redirect(url_for('ver_mensajes'))


@app.route('/buscar')
def buscar():
    termino = request.args.get('q', '')
    resultados = []
    if termino:
        resultados = almacen.buscar_mensajes(termino)
    mensajes = [r['mensaje'] for r in resultados]
    # adjuntar carpeta actual y lista de carpetas
    lista = []
    for m in mensajes:
        carpeta = almacen.carpeta_de_mensaje(m['id'])
        m['carpeta_id'] = carpeta.id if carpeta else None
        rutas = [c for c in almacen.listar_carpetas_con_ruta() if c['id'] == (carpeta.id if carpeta else 'root')]
        m['carpeta_ruta'] = rutas[0]['ruta'] if rutas else ('Inbox' if not carpeta else carpeta.nombre)
        lista.append(m)
    carpetas = almacen.listar_carpetas_con_ruta()
    return render_template('mensajes.html', mensajes=lista, resultados=resultados, carpeta_raiz=almacen.raiz, carpetas=carpetas)


@app.route('/')
def home():
    return redirect(url_for('registro'))

if __name__ == '__main__':
    app.run(debug=True)