import streamlit as st
import pandas as pd
import sqlite3
import re
import unicodedata

from db import crear_tabla
from db import conectar_db


st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #FFF8FA 0%,
        #FFE4EC 100%
    );
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="¿Qué tan bien me conoces?",
    page_icon="🎁",
    layout="centered"
)

crear_tabla()

preguntas = [
    "¿Cuál es mi comida favorita?",
    "¿Cuál es mi color favorito?",
    "¿Cuál es mi película favorita?",
    "¿Cuál es mi hobby favorito?",
    "¿Qué país me gustaría visitar?",
    "¿Cuál es mi animal favorito?",
    "¿Cuál es mi bebida favorita?",
    "¿Cuál es mi estación del año favorita?",
    "¿Cuál es mi deporte favorito?",
    "¿Cuál es mi canción favorita?"
]

def normalizar(texto):

    texto = texto.lower().strip()

    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

    texto = re.sub(
        r'\b(el|la|los|las|the)\b',
        '',
        texto
    )

    texto = re.sub(
        r'[^a-z0-9 ]',
        '',
        texto
    )

    texto = " ".join(texto.split())

    return texto

def singularizar(texto):

    palabras = []

    for palabra in texto.split():

        if palabra.endswith("es") and len(palabra) > 4:
            palabra = palabra[:-2]

        elif palabra.endswith("s") and len(palabra) > 3:
            palabra = palabra[:-1]

        palabras.append(palabra)

    return " ".join(palabras)

equivalencias = {
    "gladiator": "gladiador",
    "the gladiator": "gladiador",
    "last samurai": "ultimo samurai",
    "the last samurai": "ultimo samurai"
}

def comparar_respuestas(
        respuesta_real,
        respuesta_usuario):

    real = normalizar(respuesta_real)
    usuario = normalizar(respuesta_usuario)

    real = singularizar(real)
    usuario = singularizar(usuario)

    real = equivalencias.get(real, real)
    usuario = equivalencias.get(usuario, usuario)

    if real == usuario:
        return True

    palabras_real = set(real.split())
    palabras_usuario = set(usuario.split())

    coincidencias = len(
        palabras_real.intersection(
            palabras_usuario
        )
    )

    if len(palabras_real) >= 2:
        if coincidencias >= 2:
            return True

    return False

st.title("🎁 ¿Qué tan bien me conoces?")

menu = st.sidebar.radio(
    "Selecciona una opción",
    ["Crear mi reto", "Responder reto", "🔒 Solo Personal Autorizado"]
)

# --------------------------------------------------
# CREAR RETO
# --------------------------------------------------

if menu == "Crear mi reto":

    st.header("Crea tu reto")

    creador = st.text_input("Tu nombre")

    respuestas_creador = []

    for pregunta in preguntas:
        respuesta = st.text_input(
            pregunta,
            key=f"creador_{pregunta}"
        )
        respuestas_creador.append(respuesta)

    if st.button("Guardar reto"):

        if creador == "":
            st.warning("Ingresa tu nombre")
        else:

            conn = conectar_db()

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO retos (
                creador,
                p1,p2,p3,p4,p5,
                p6,p7,p8,p9,p10
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
            (
                creador,
                respuestas_creador[0].lower().strip(),
                respuestas_creador[1].lower().strip(),
                respuestas_creador[2].lower().strip(),
                respuestas_creador[3].lower().strip(),
                respuestas_creador[4].lower().strip(),
                respuestas_creador[5].lower().strip(),
                respuestas_creador[6].lower().strip(),
                respuestas_creador[7].lower().strip(),
                respuestas_creador[8].lower().strip(),
                respuestas_creador[9].lower().strip()
            ))

            conn.commit()
            conn.close()

            st.success("✅ Reto guardado correctamente")
            st.info(
                f"Ahora comparte tu nombre ({creador}) para que alguien intente adivinar tus respuestas."
            )


# --------------------------------------------------
# RESPONDER RETO
# --------------------------------------------------

if menu == "Responder reto":

    st.header("Responder reto")

    conn = conectar_db()

    df = pd.read_sql_query(
    "SELECT * FROM retos",
    conn
    )

    conn.close()

    if df.empty:
        st.warning("Aún no existen retos.")
        st.stop()

    creador_seleccionado = st.selectbox(
    "¿A quién deseas adivinar?",
    df["creador"].unique()
    )

    fila = df[df["creador"] == creador_seleccionado].iloc[0]

    jugador = st.text_input("Tu nombre")

    respuestas_jugador = []

    for pregunta in preguntas:
        respuesta = st.text_input(
            pregunta,
            key=f"jugador_{pregunta}"
        )
        respuestas_jugador.append(
            respuesta.lower().strip()
        )

    if st.button("Ver resultado"):

        aciertos = 0
        errores = []

        for i in range(len(preguntas)):
            respuesta_real = str(fila[f"p{i+1}"]).lower().strip()
            respuesta_usuario = respuestas_jugador[i]
            if comparar_respuestas(respuesta_real,respuesta_usuario):
                aciertos += 1
            else:
                errores.append({
                    "pregunta": preguntas[i],
                    "tu_respuesta": respuesta_usuario,
                    "respuesta_correcta": respuesta_real
            })
        porcentaje = round(
            (aciertos / len(preguntas)) * 100
        )

        st.subheader("Resultado")

        st.metric(
            "Compatibilidad",
            f"{porcentaje}%"
        )

        if porcentaje >= 90:
            st.balloons()
            st.success(
                "🔥 Increíble. Parece que lo conoces mejor que nadie."
            )

        elif porcentaje >= 70:
            st.success(
                "👏 Muy bien. Hay una gran conexión."
            )

        elif porcentaje >= 50:
            st.info(
                "🙂 Lo conoces bastante bien."
            )

        else:
            st.warning(
                "😅 Necesitan pasar más tiempo juntos."
            )

        st.write(
            f"Respuestas correctas: {aciertos} de {len(preguntas)}"
        )

        if len(errores) > 0:

            st.subheader("❌ Preguntas en las que te equivocaste")

            for error in errores:

                st.markdown(
                    f"""
                    **Pregunta:** {error['pregunta']}

                    🔹 Tu respuesta: **{error['tu_respuesta']}**

                    ✅ Respuesta correcta: **{error['respuesta_correcta']}**
                    """
                )

            st.divider()

        else:

            st.success(
                "🎉 ¡Perfecto! Respondiste correctamente todas las preguntas."
            )

# --------------------------------------------------
# ADMINISTRAR BASE DE DATOS
# --------------------------------------------------
if menu == "🔒 Solo Personal Autorizado":

    st.header("🔒 Área Restringida")

    password = st.text_input(
        "Ingrese la contraseña",
        type="password"
    )

    if password == st.secrets["ADMIN_PASSWORD"]:

            st.success("✅ Acceso autorizado")

    conn = conectar_db()

    df = pd.read_sql_query(
        "SELECT * FROM retos",
        conn
    )

    st.subheader("📋 Registros almacenados")

    st.dataframe(df)

    accion = st.radio(
        "Seleccione una acción",
        [
            "✏️ Editar reto",
            "🗑️ Eliminar reto"
        ]
    )

    # ==========================
    # ELIMINAR
    # ==========================

    if accion == "🗑️ Eliminar reto":

        opciones = {
            f"{row['id']} - {row['creador']}":
            row["id"]
            for _, row in df.iterrows()
        }

        seleccion = st.selectbox(
            "Seleccione el reto a eliminar",
            list(opciones.keys())
        )

        id_reto = opciones[seleccion]

        if st.button("Eliminar registro"):

            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM retos WHERE id = ?",
                (id_reto,)
            )

            conn.commit()

            st.success(
                "✅ Registro eliminado correctamente"
            )

            st.rerun()

    # ==========================
    # EDITAR
    # ==========================

    if accion == "✏️ Editar reto":

        opciones = {
            f"{row['id']} - {row['creador']}":
            row["id"]
            for _, row in df.iterrows()
        }

        seleccion = st.selectbox(
            "Seleccione el reto a editar",
            list(opciones.keys()),
            key="editar"
        )

        id_reto = opciones[seleccion]

        fila = df[
            df["id"] == id_reto
        ].iloc[0]

        creador = st.text_input(
            "Nombre",
            value=fila["creador"]
        )

        p1 = st.text_input(
            preguntas[0],
            value=fila["p1"]
        )

        p2 = st.text_input(
            preguntas[1],
            value=fila["p2"]
        )

        p3 = st.text_input(
            preguntas[2],
            value=fila["p3"]
        )

        p4 = st.text_input(
            preguntas[3],
            value=fila["p4"]
        )

        p5 = st.text_input(
            preguntas[4],
            value=fila["p5"]
        )

        p6 = st.text_input(
            preguntas[5],
            value=fila["p6"]
        )

        p7 = st.text_input(
            preguntas[6],
            value=fila["p7"]
        )

        p8 = st.text_input(
            preguntas[7],
            value=fila["p8"]
        )

        p9 = st.text_input(
            preguntas[8],
            value=fila["p9"]
        )

        p10 = st.text_input(
            preguntas[9],
            value=fila["p10"]
        )

        if st.button("Guardar cambios"):

            cursor = conn.cursor()

            cursor.execute("""
            UPDATE retos
            SET
                creador=?,
                p1=?,
                p2=?,
                p3=?,
                p4=?,
                p5=?,
                p6=?,
                p7=?,
                p8=?,
                p9=?,
                p10=?
            WHERE id=?
            """,
            (
                creador,
                p1,
                p2,
                p3,
                p4,
                p5,
                p6,
                p7,
                p8,
                p9,
                p10,
                id_reto
            ))

            conn.commit()

            st.success(
                "✅ Registro actualizado correctamente"
            )

            st.rerun()

        conn.close()
   
    elif password:

        st.error("❌ Contraseña incorrecta")
