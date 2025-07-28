from flask import Flask, request, jsonify
from utils.extractor import extraer_datos
from models import Session, Candidato
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/subir_cv", methods=["POST"])
def subir_cv():
    if "archivo" not in request.files:
        return jsonify({"error": "No se envió archivo"}), 400

    archivo = request.files["archivo"]
    ruta = os.path.join(UPLOAD_FOLDER, archivo.filename)
    archivo.save(ruta)

    datos = extraer_datos(ruta)

    session = Session()
    candidato = Candidato(
        nombre=datos["nombre"],
        email=datos["email"],
        telefono=datos["telefono"],
        archivo=archivo.filename
    )
    session.add(candidato)
    session.commit()
    session.close()

    return jsonify({"mensaje": "CV procesado y guardado", "datos": datos})

@app.route("/candidatos", methods=["GET"])
def listar_candidatos():
    session = Session()
    candidatos = session.query(Candidato).all()
    resultado = []
    for c in candidatos:
        resultado.append({
            "id": c.id,
            "nombre": c.nombre,
            "email": c.email,
            "telefono": c.telefono,
            "archivo": c.archivo,
            "fecha_subida": c.fecha_subida.strftime("%Y-%m-%d %H:%M:%S")
        })
    session.close()
    return jsonify(resultado)
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
