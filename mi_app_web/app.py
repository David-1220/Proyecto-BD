from flask import Flask, render_template, request, redirect, session
import oracledb
from db_config import get_connection

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=:1 AND password=:2", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/menu')
        else:
            error = 'Credenciales incorrectas'

    return render_template('login.html', error=error)

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect('/login')
    return render_template('menu.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/inicio')
def inicio():
    if 'username' not in session:
        return redirect('/login')
    return render_template('inicio.html', username=session['username'], active='inicio')

@app.route('/clientes')
def clientes():
    orden = request.args.get('orden', 'id')

    connection = get_connection()
    cursor = connection.cursor()

    query = f"""
        SELECT c.id_cliente, c.nombre, c.correo, c.rfc, t.telefono
        FROM Clientes c
        LEFT JOIN Telefonos_clientes t ON c.id_cliente = t.id_cliente
        ORDER BY c.{"nombre" if orden == "nombre" else "id_cliente"}
    """

    cursor.execute(query)
    clientes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('clientes.html', clientes=clientes, orden=orden, active='clientes')

@app.route('/agregar_cliente', methods=['POST'])
def agregar_cliente():
    if 'username' not in session:
        return redirect('/login')

    nombre = request.form['nombre']
    correo = request.form['correo']
    rfc = request.form['rfc']
    telefono = request.form['telefono']

    connection = get_connection()
    cursor = connection.cursor()

    try:
        
        cursor.execute("""
            INSERT INTO Clientes (id_cliente, nombre, correo, rfc)
            VALUES (Clientes_SEQ.NEXTVAL, :nombre, :correo, :rfc)
        """, {'nombre': nombre, 'correo': correo, 'rfc': rfc})

        cursor.execute("SELECT Clientes_SEQ.CURRVAL FROM dual")
        cliente_id = cursor.fetchone()[0]

        cursor.execute("SELECT TELEFONOS_CLIENTES_SEQ.NEXTVAL FROM DUAL")
        id_telefono = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO TELEFONOS_CLIENTES (ID_TELEFONO, ID_CLIENTE, TELEFONO)
            VALUES (:id_telefono, :id_cliente, :telefono)
        """, {
            'id_telefono': id_telefono,
            'id_cliente': cliente_id,
            'telefono': telefono
        })

        connection.commit()

    except Exception as e:
        print("Error al agregar cliente y teléfono:", e)
        connection.rollback()

    finally:
        cursor.close()
        connection.close()

    return redirect('/clientes')

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        rfc = request.form['rfc']
        telefono = request.form['telefono']

        cursor.execute("""
            UPDATE clientes SET Nombre = :1, Correo = :2, RFC = :3 WHERE ID_cliente = :4
        """, (nombre, correo, rfc, id))

        cursor.execute("""
            SELECT COUNT(*) FROM Telefonos_clientes WHERE ID_cliente = :1
        """, (id,))
        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute("""
                UPDATE Telefonos_clientes SET Telefono = :1 WHERE ID_cliente = :2
            """, (telefono, id))
        else:
            cursor.execute("""
                INSERT INTO Telefonos_clientes (ID_cliente, Telefono) VALUES (:1, :2)
            """, (id, telefono))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/clientes')

    else:
        cursor.execute("SELECT * FROM clientes WHERE ID_cliente = :1", (id,))
        cliente = cursor.fetchone()

        cursor.execute("""
            SELECT Telefono FROM Telefonos_clientes WHERE ID_cliente = :1
        """, (id,))
        telefono = cursor.fetchone()
        telefono = telefono[0] if telefono else '' 

        cursor.close()
        conn.close()

        return render_template('editar_cliente.html', cliente=cliente, telefono=telefono)

@app.route('/eliminar_cliente/<int:id>', methods=['POST']) 
def eliminar_cliente(id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE ID_cliente = :1", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/clientes')

@app.route("/expedientes")
def expedientes():
    connection = get_connection()
    cursor = connection.cursor()

    orden = request.args.get('orden', 'id_cliente')  

    if orden == 'nombre_cliente':
        orden_sql = 'c.NOMBRE'
    else:
        orden_sql = 'c.ID_CLIENTE'

    cursor.execute("SELECT ID_CLIENTE, NOMBRE FROM CLIENTES")
    clientes = cursor.fetchall()
    
    cursor.execute("SELECT ID_EMPRESA, NOMBRE_EMPRESA FROM EMPRESA")
    empresas = cursor.fetchall()

    cursor.execute("SELECT ID_ABOGADO, NOMBRE_ABOGADO FROM ABOGADOS")
    abogados = cursor.fetchall()

    cursor.execute("SELECT ID_ETAPA, NOMBRE_ETAPA FROM ETAPAS")
    etapas = cursor.fetchall()

    cursor.execute("SELECT ID_ESTADO, NOMBRE_ESTADO FROM ESTADOS")
    estados = cursor.fetchall()

    cursor.execute(f"""
        SELECT 
            e.ID_EXPEDIENTES,
            c.ID_CLIENTE,
            c.NOMBRE AS nombre_cliente,
            emp.NOMBRE_EMPRESA AS nombre_empresa,
            ab.NOMBRE_ABOGADO AS nombre_abogado,
            et.NOMBRE_ETAPA AS nombre_etapa,
            es.NOMBRE_ESTADO AS estado,
            e.NUMERO_EXPEDIENTE,
            TO_CHAR(e.FECHA_INICIO, 'YYYY-MM-DD') AS fecha_inicio
        FROM 
            EXPEDIENTES e
        JOIN CLIENTES c ON e.ID_CLIENTE = c.ID_CLIENTE
        JOIN EMPRESA emp ON e.ID_EMPRESA = emp.ID_EMPRESA
        JOIN ABOGADOS ab ON e.ID_ABOGADO = ab.ID_ABOGADO
        JOIN ETAPAS et ON e.ID_ETAPA = et.ID_ETAPA
        JOIN ESTADOS es ON e.ID_ESTADO = es.ID_ESTADO
        ORDER BY {orden_sql}
    """)

    columns = [col[0].lower() for col in cursor.description]
    expedientes = [dict(zip(columns, row)) for row in cursor.fetchall()]

    connection.close()

    return render_template(
        "expedientes.html",
        clientes=clientes,
        empresas=empresas,
        abogados=abogados,
        etapas=etapas,
        estados=estados,
        expedientes=expedientes,
        orden=orden,  
        active="expedientes"
    )



@app.route("/agregar_expediente", methods=["POST"])
def agregar_expediente():
    print("Datos recibidos:", request.form)
    connection = get_connection()
    cursor = connection.cursor()

    id_cliente = request.form["id_cliente"]
    id_empresa = request.form["id_empresa"]
    id_abogado = request.form["id_abogado"]
    id_etapa = request.form["id_etapa"]
    id_estado = request.form["id_estado"]
    numero_expediente = request.form["numero_expediente"]
    fecha_inicio = request.form["fecha_inicio"]

    try:
        cursor.execute("""
            INSERT INTO EXPEDIENTES (
                ID_EXPEDIENTES, ID_CLIENTE, ID_EMPRESA, ID_ABOGADO, 
                ID_ETAPA, ID_ESTADO, NUMERO_EXPEDIENTE, FECHA_INICIO
            )
            VALUES (
                seq_expedientes.NEXTVAL, :1, :2, :3, :4, :5, :6, TO_DATE(:7, 'YYYY-MM-DD')
            )
        """, (id_cliente, id_empresa, id_abogado, id_etapa, id_estado, numero_expediente, fecha_inicio))

        connection.commit()
    except Exception as e:
        print("Error al agregar expediente:", e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/expedientes")



@app.route('/editar_expediente/<int:id_expediente>', methods=['GET', 'POST'])
def editar_expediente(id_expediente):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        numero_expediente = request.form['numero_expediente']
        fecha_inicio = request.form['fecha_inicio']
        id_cliente = request.form['id_cliente']
        id_empresa = request.form['id_empresa']
        id_abogado = request.form['id_abogado']
        id_etapa = request.form['id_etapa']
        id_estado = request.form['id_estado']

        cursor.execute("""
            UPDATE Expedientes
            SET numero_expediente = :1,
                fecha_inicio = TO_DATE(:2, 'YYYY-MM-DD'),
                id_cliente = :3,
                id_empresa = :4,
                id_abogado = :5,
                id_etapa = :6,
                id_estado = :7
            WHERE id_expedientes = :8
        """, (
            numero_expediente,
            fecha_inicio,
            id_cliente,
            id_empresa,
            id_abogado,
            id_etapa,
            id_estado,
            id_expediente
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/expedientes')

    cursor.execute("""
        SELECT E.numero_expediente, TO_CHAR(E.fecha_inicio, 'YYYY-MM-DD'),
               C.nombre, EM.nombre_empresa, A.nombre_abogado,
               ET.nombre_etapa, ES.nombre_estado,
               C.id_cliente, EM.id_empresa, A.id_abogado, ET.id_etapa, ES.id_estado
        FROM Expedientes E
        JOIN CLIENTES C ON E.id_cliente = C.id_cliente
        JOIN EMPRESA EM ON E.id_empresa = EM.id_empresa
        JOIN ABOGADOS A ON E.id_abogado = A.id_abogado
        JOIN ETAPAS ET ON E.id_etapa = ET.id_etapa
        JOIN ESTADOS ES ON E.id_estado = ES.id_estado
        WHERE E.id_expedientes = :1
    """, (id_expediente,))
    fila = cursor.fetchone()

    if not fila:
        cursor.close()
        conn.close()
        return "Expediente no encontrado", 404

    expediente = {
        'numero_expediente': fila[0],
        'fecha_inicio': fila[1],
        'nombre_cliente': fila[2],
        'nombre_empresa': fila[3],
        'nombre_abogado': fila[4],
        'nombre_etapa': fila[5],
        'nombre_estado': fila[6],
        'id_cliente': fila[7],
        'id_empresa': fila[8],
        'id_abogado': fila[9],
        'id_etapa': fila[10],
        'id_estado': fila[11],
    }


    cursor.execute("SELECT id_cliente, nombre FROM CLIENTES")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id_empresa, nombre_empresa FROM EMPRESA")
    empresas = cursor.fetchall()

    cursor.execute("SELECT id_abogado, nombre_abogado FROM ABOGADOS")
    abogados = cursor.fetchall()

    cursor.execute("SELECT id_etapa, nombre_etapa FROM ETAPAS")
    etapas = cursor.fetchall()

    cursor.execute("SELECT id_estado, nombre_estado FROM ESTADOS")
    estados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'editar_expediente.html',
        expediente=expediente,
        clientes=clientes,
        empresas=empresas,
        abogados=abogados,
        etapas=etapas,
        estados=estados,
        active='expedientes'
    )

@app.route('/eliminar_expediente/<int:id_expediente>', methods=['POST'])
def eliminar_expediente(id_expediente):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Expedientes WHERE id_expedientes = :1", (id_expediente,))
    conn.commit()

    cursor.close()
    conn.close()
    return redirect('/expedientes')

@app.route("/nueva_empresa", methods=["GET", "POST"])
def nueva_empresa():
    if request.method == "POST":
        nombre_empresa = request.form["nombre_empresa"]
        rfc_empresa = request.form["rfc_empresa"]
        direccion = request.form["direccion_empresa"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO EMPRESA (NOMBRE_EMPRESA, RFC_EMPRESA, DIRECCION)
            VALUES (:1, :2, :3)
        """, (nombre_empresa, rfc_empresa, direccion))

        connection.commit()
        connection.close()

        return redirect("/expedientes")

    return render_template("nueva_empresa.html", active="expedientes")



@app.route('/contactos')
def contactos():
    if 'username' not in session:
        return redirect('/login')
    
    orden = request.args.get('orden', 'id')  

    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT a.id_abogado, a.nombre_abogado, a.correo, t.telefono
        FROM abogados a
        LEFT JOIN telefonos_abogados t ON a.id_abogado = t.id_abogado
        ORDER BY a.{"nombre_abogado" if orden == "nombre" else "id_abogado"}
    """

    cursor.execute(query)
    abogados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('contactos.html', abogados=abogados, orden=orden, active='contactos')


@app.route('/agregar_abogado', methods=['POST'])
def agregar_abogado():
    if 'username' not in session:
        return redirect('/login')

    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO abogados (id_abogado, nombre_abogado, correo)
            VALUES (abogados_seq.NEXTVAL, :nombre, :correo)
        """, {'nombre': nombre, 'correo': correo})

        cursor.execute("SELECT abogados_seq.CURRVAL FROM dual")
        id_abogado = cursor.fetchone()[0]

        cursor.execute("SELECT telefonos_abogados_seq.NEXTVAL FROM dual")
        id_tel = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO telefonos_abogados (id_telefono, id_abogado, telefono)
            VALUES (:id_tel, :id_abogado, :telefono)
        """, {'id_tel': id_tel, 'id_abogado': id_abogado, 'telefono': telefono})

        conn.commit()
    except Exception as e:
        print("Error al agregar abogado:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect('/contactos')

@app.route('/editar_abogado/<int:id>', methods=['GET', 'POST'])
def editar_abogado(id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']

        cursor.execute("""
            UPDATE abogados 
            SET nombre_abogado = :1, correo = :2 
            WHERE id_abogado = :3
        """, (nombre, correo, id))

        cursor.execute("SELECT COUNT(*) FROM telefonos_abogados WHERE id_abogado = :1", (id,))
        if cursor.fetchone()[0] > 0:
            cursor.execute("UPDATE telefonos_abogados SET telefono = :1 WHERE id_abogado = :2", (telefono, id))
        else:
            cursor.execute("""
                INSERT INTO telefonos_abogados (id_abogado, telefono)
                VALUES (:1, :2)
            """, (id, telefono))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/contactos')

    else:
        cursor.execute("SELECT * FROM abogados WHERE id_abogado = :1", (id,))
        abogado = cursor.fetchone()

        cursor.execute("SELECT telefono FROM telefonos_abogados WHERE id_abogado = :1", (id,))
        telefono = cursor.fetchone()
        telefono = telefono[0] if telefono else ''

        cursor.close()
        conn.close()
        return render_template('editar_abogado.html', abogado=abogado, telefono=telefono)


@app.route('/eliminar_abogado/<int:id>', methods=['POST'])
def eliminar_abogado(id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM abogados WHERE id_abogado = :1", (id,))
        conn.commit()
    except Exception as e:
        print("Error al eliminar abogado:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect('/contactos')

if __name__ == '__main__':
    app.run(debug=True)