import streamlit as st
import pandas as pd
import sqlite3
import re
import unicodedata

from db import crear_tablas
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

crear_tablas()

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

import random
import string

def generar_codigo():
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=6
        )
    )

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
    [
        "👨‍👩‍👧‍👦 Crear Grupo",
        "➕ Unirme a Grupo",
        "🎁 Crear Mi Reto",
        "🧠 Responder Reto",
        "🏆 Ranking",
        "🔒 Solo Personal Autorizado"
    ]
)

# --------------------------------------------------
# CREAR GRUPO
# --------------------------------------------------
if menu == "👨‍👩‍👧‍👦 Crear Grupo":

    st.header("Crear Grupo")

    creador = st.text_input(
        "Tu nombre completo"
    )

    nombre_grupo = st.text_input(
        "Nombre del grupo"
    )

    if st.button("Crear grupo"):

        codigo = generar_codigo()

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO grupos
            (
                nombre,
                codigo,
                creador
            )
            VALUES (?,?,?)
            """,
            (
                nombre_grupo,
                codigo,
                creador
            )
        )

        grupo_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO participantes
            (
                grupo_id,
                nombre
            )
            VALUES (?,?)
            """,
            (
                grupo_id,
                creador
            )
        )

        conn.commit()
        conn.close()

        st.success(
            f"Código del grupo: {codigo}"
        )

# --------------------------------------------------
# UNIRSE AL GRUPO
# --------------------------------------------------
if menu == "➕ Unirme a Grupo":

    st.header("Unirme a Grupo")

    nombre = st.text_input(
        "Tu nombre completo"
    )

    codigo = st.text_input(
        "Código del grupo"
    )

    if st.button("Unirme"):

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM grupos
            WHERE codigo=?
            """,
            (codigo,)
        )

        grupo = cursor.fetchone()

        if grupo:

            cursor.execute(
                """
                INSERT INTO participantes
                (
                    grupo_id,
                    nombre
                )
                VALUES (?,?)
                """,
                (
                    grupo[0],
                    nombre
                )
            )

            conn.commit()

            st.success(
                "Te uniste correctamente"
            )

        else:
            st.error(
                "Código inválido"
            )

        conn.close()


# --------------------------------------------------
# CREAR RETO
# --------------------------------------------------

if menu == "🎁 Crear Mi Reto":

    st.header("Crear Mi Reto")

    nombre = st.text_input("Tu nombre completo")

    if nombre == "":
        st.warning(
            "Primero debes registrar tu nombre."
        )
        st.stop()

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.id, g.nombre
        FROM grupos g
        INNER JOIN participantes p
        ON g.id = p.grupo_id
        WHERE p.nombre = ?
    """, (nombre,))

    grupos = cursor.fetchall()

    if not grupos:
        st.warning(
            "No perteneces a ningún grupo. Primero crea un grupo o únete a uno."
        )
        conn.close()
        st.stop()

    grupo_seleccionado = st.selectbox(
        "Selecciona el grupo",
        grupos,
        format_func=lambda x: x[1]
    )

    grupo_id = grupo_seleccionado[0]

    respuestas_creador = []

    for pregunta in preguntas:

        respuesta = st.text_input(
            pregunta,
            key=f"creador_{pregunta}"
        )

        respuestas_creador.append(
            respuesta.lower().strip()
        )

    if st.button("Guardar reto"):

        cursor.execute("""
            INSERT INTO retos (
                grupo_id,
                creador,
                p1,p2,p3,p4,p5,
                p6,p7,p8,p9,p10
            )
            VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?
            )
        """,
        (
            grupo_id,
            nombre,
            respuestas_creador[0],
            respuestas_creador[1],
            respuestas_creador[2],
            respuestas_creador[3],
            respuestas_creador[4],
            respuestas_creador[5],
            respuestas_creador[6],
            respuestas_creador[7],
            respuestas_creador[8],
            respuestas_creador[9]
        ))

        conn.commit()
        conn.close()

        st.success(
            "✅ Reto guardado correctamente"
        )

        st.info(
            f"Tu reto fue guardado para el grupo {grupo_seleccionado[1]}"
        )


# --------------------------------------------------
# RESPONDER RETO
# --------------------------------------------------

if menu == "🧠 Responder Reto":

    st.header("Responder reto")

    jugador = st.text_input("Tu nombre completo")

    if jugador == "":
        st.stop()

    conn = conectar_db()
    cursor = conn.cursor()

    # Buscar grupos del jugador
    cursor.execute("""
    SELECT g.id, g.nombre
    FROM grupos g
    INNER JOIN participantes p
    ON g.id = p.grupo_id
    WHERE p.nombre = ?
    """, (jugador,))

    grupos = cursor.fetchall()

    if not grupos:

        st.warning(
            "No perteneces a ningún grupo."
        )

        conn.close()
        st.stop()

    grupo_seleccionado = st.selectbox(
        "Selecciona tu grupo",
        grupos,
        format_func=lambda x: x[1]
    )

    grupo_id = grupo_seleccionado[0]

    # Obtener retos solo del grupo seleccionado
    df = pd.read_sql_query(
        """
        SELECT *
        FROM retos
        WHERE grupo_id = ?
        """,
        conn,
        params=(grupo_id,)
    )

    if df.empty:

        st.warning(
            "No existen retos en este grupo."
        )

        conn.close()
        st.stop()

    # Opcional: ocultar el propio reto
    retos_disponibles = df[
        df["creador"].str.lower() != jugador.lower()
    ]

    if retos_disponibles.empty:

        st.info(
            "Todavía no existen retos de otras personas en este grupo."
        )

        conn.close()
        st.stop()

    creador_seleccionado = st.selectbox(
        "¿A quién deseas adivinar?",
        retos_disponibles["creador"].unique()
    )

    fila = retos_disponibles[
        retos_disponibles["creador"] == creador_seleccionado
    ].iloc[0]

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

            respuesta_real = str(
                fila[f"p{i+1}"]
            ).lower().strip()

            respuesta_usuario = respuestas_jugador[i]

            if comparar_respuestas(
                respuesta_real,
                respuesta_usuario
            ):
                aciertos += 1

            else:

                errores.append({

                    "pregunta":
                    preguntas[i],

                    "tu_respuesta":
                    respuesta_usuario,

                    "respuesta_correcta":
                    respuesta_real

                })

        porcentaje = round(
            (
                aciertos /
                len(preguntas)
            ) * 100
        )

        # Guardar resultado
        cursor.execute("""
        INSERT INTO resultados (
            reto_id,
            jugador,
            porcentaje
        )
        VALUES (?,?,?)
        """,
        (
            int(fila["id"]),
            jugador,
            porcentaje
        ))

        conn.commit()

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

            st.subheader(
                "❌ Preguntas en las que te equivocaste"
            )

            for error in errores:

                st.markdown(f"""
**Pregunta:** {error['pregunta']}

🔹 Tu respuesta: **{error['tu_respuesta']}**

✅ Respuesta correcta: **{error['respuesta_correcta']}**
                """)

        else:

            st.success(
                "🎉 ¡Perfecto! Respondiste correctamente todas las preguntas."
            )

    conn.close()


# --------------------------------------------------
# RANKING
# --------------------------------------------------

if menu == "🏆 Ranking":

    st.header("🏆 Ranking")

    usuario = st.text_input(
        "Tu nombre completo"
    )

    if usuario == "":
        st.stop()

    conn = conectar_db()
    cursor = conn.cursor()

    # Buscar grupos donde pertenece
    cursor.execute("""
    SELECT g.id, g.nombre
    FROM grupos g
    INNER JOIN participantes p
        ON g.id = p.grupo_id
    WHERE p.nombre = ?
    """, (usuario,))

    grupos = cursor.fetchall()

    if not grupos:

        st.warning(
            "No perteneces a ningún grupo."
        )

        conn.close()
        st.stop()

    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo",
        grupos,
        format_func=lambda x: x[1]
    )

    grupo_id = grupo_seleccionado[0]

    # Obtener total de participantes del grupo
    cursor.execute("""
        SELECT COUNT(*)
        FROM participantes
        WHERE grupo_id = ?
    """, (grupo_id,))

    total_participantes = cursor.fetchone()[0]

    df_rank = pd.read_sql_query(
    """
    SELECT
        r.jugador,
        COUNT(*) AS partidas,
        SUM(r.porcentaje) AS puntos,
        MAX(r.porcentaje) AS mejor_puntaje
    FROM resultados r
    INNER JOIN retos t
        ON r.reto_id = t.id
    WHERE t.grupo_id = ?
    GROUP BY r.jugador
    """,
    conn,
    params=(grupo_id,)
    )

    df_rank["promedio"] = round(df_rank["puntos"] / max(total_participantes - 1, 1),0)

    df_rank = df_rank.sort_values(by="promedio", ascending=False)

    conn.close()

    if df_rank.empty:

        st.info(
            "Todavía no existen resultados para este grupo."
        )

    else:

        st.subheader(
            f"🏆 Ranking del grupo: {grupo_seleccionado[1]}"
        )

        # Líder actual
        ganador = df_rank.iloc[0]

        st.success(
            f"🥇 Líder actual: {ganador['jugador']} "
            f"con un promedio de {int(ganador['promedio'])}%"
        )

        st.dataframe(
            df_rank,
            use_container_width=True
        )

        st.divider()

        for i, row in df_rank.iterrows():

            if i == 0:
                emoji = "🥇"




# --------------------------------------------------
# ADMINISTRAR BASE DE DATOS
# --------------------------------------------------
if menu == "🔒 Solo Personal Autorizado":



    st.header("🔒 Área Restringida")



    password = st.text_input(
        "Ingrese la contraseña",
        type="password"
    )



    if password == "":



        st.info("Ingrese la contraseña para continuar")
        st.stop()



    elif password != st.secrets["ADMIN_PASSWORD"]:



        st.error("❌ Contraseña incorrecta")
        st.stop()



    else:



        st.success("✅ Acceso autorizado")



        conn = conectar_db()
        cursor = conn.cursor()

            # ==========================
    # VER TABLAS
    # ==========================

    st.subheader("📊 Información almacenada")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎁 Retos",
        "👨‍👩‍👧‍👦 Grupos",
        "👥 Participantes",
        "🏆 Resultados"
    ])

    # ==================================================
    # RETOS
    # ==================================================

    with tab1:

        df = pd.read_sql_query(
            "SELECT * FROM retos",
            conn
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        if not df.empty:

            accion = st.radio(
                "Seleccione una acción",
                [
                    "✏️ Editar reto",
                    "🗑️ Eliminar reto"
                ]
            )

            # ELIMINAR RETO
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

                if st.button(
                    "Eliminar registro"
                ):

                    cursor.execute(
                        """
                        DELETE FROM retos
                        WHERE id = ?
                        """,
                        (id_reto,)
                    )

                    conn.commit()

                    st.success(
                        "✅ Registro eliminado correctamente"
                    )

                    st.rerun()

            # EDITAR RETO
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

                respuestas = []

                for i in range(10):

                    respuestas.append(
                        st.text_input(
                            preguntas[i],
                            value=fila[f"p{i+1}"],
                            key=f"edit_{i}"
                        )
                    )

                if st.button(
                    "Guardar cambios"
                ):

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
                        respuestas[0],
                        respuestas[1],
                        respuestas[2],
                        respuestas[3],
                        respuestas[4],
                        respuestas[5],
                        respuestas[6],
                        respuestas[7],
                        respuestas[8],
                        respuestas[9],
                        id_reto
                    ))

                    conn.commit()

                    st.success(
                        "✅ Registro actualizado correctamente"
                    )

                    st.rerun()

    # ==================================================
    # GRUPOS
    # ==================================================

    with tab2:

        df_grupos = pd.read_sql_query(
            "SELECT * FROM grupos",
            conn
        )

        st.dataframe(
            df_grupos,
            use_container_width=True
        )

        if not df_grupos.empty:

            opciones = {
                f"{row['id']} - {row['nombre']}":
                row["id"]
                for _, row in df_grupos.iterrows()
            }

            seleccion = st.selectbox(
                "Grupo a eliminar",
                list(opciones.keys())
            )

            if st.button(
                "🗑️ Eliminar grupo"
            ):

                cursor.execute(
                    """
                    DELETE FROM grupos
                    WHERE id=?
                    """,
                    (opciones[seleccion],)
                )

                conn.commit()

                st.success(
                    "✅ Grupo eliminado"
                )

                st.rerun()

    # ==================================================
    # PARTICIPANTES
    # ==================================================

    with tab3:

        df_participantes = pd.read_sql_query(
            "SELECT * FROM participantes",
            conn
        )

        st.dataframe(
            df_participantes,
            use_container_width=True
        )

        if not df_participantes.empty:

            opciones = {
                f"{row['id']} - {row['nombre']}":
                row["id"]
                for _, row in df_participantes.iterrows()
            }

            seleccion = st.selectbox(
                "Participante a eliminar",
                list(opciones.keys())
            )

            if st.button(
                "🗑️ Eliminar participante"
            ):

                cursor.execute(
                    """
                    DELETE FROM participantes
                    WHERE id=?
                    """,
                    (opciones[seleccion],)
                )

                conn.commit()

                st.success(
                    "✅ Participante eliminado"
                )

                st.rerun()

    # ==================================================
    # RESULTADOS
    # ==================================================

    with tab4:

        df_resultados = pd.read_sql_query(
            """
            SELECT
                r.id,
                r.jugador,
                t.creador,
                r.porcentaje,
                r.fecha
            FROM resultados r
            INNER JOIN retos t
                ON r.reto_id = t.id
            ORDER BY r.fecha DESC
            """,
            conn
        )

        st.dataframe(
            df_resultados,
            use_container_width=True
        )

        if not df_resultados.empty:

            opciones = {
                f"{row['id']} - {row['jugador']}":
                row["id"]
                for _, row in df_resultados.iterrows()
            }

            seleccion = st.selectbox(
                "Resultado a eliminar",
                list(opciones.keys())
            )

            if st.button(
                "🗑️ Eliminar resultado"
            ):

                cursor.execute(
                    """
                    DELETE FROM resultados
                    WHERE id=?
                    """,
                    (opciones[seleccion],)
                )

                conn.commit()

                st.success(
                    "✅ Resultado eliminado"
                )

                st.rerun()

            conn.close()
            st.stop()



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