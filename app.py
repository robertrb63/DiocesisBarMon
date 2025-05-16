import os

from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

data = [
    {"unidad": "Fraga", "arcipestazgo": "Bajo Cinca", "arcipreste": "Ana", "animador": "Carlos", "nombre": "Don Benito", "poblacion": "Don Benito"},
    {"unidad": "Graus", "arcipestazgo": "Sobrarbe y Ribagorza", "arcipreste": "Paco", "animador": "Pedro", "nombre": "Juan Ignacio Cardona", "poblacion": "Torres de Obispo","telanimador": "324","telmoderador": "624", "telarcipreste": "324","telefono": "624083835", "moderador": "Juan Ignacio Cardona Orozco"},
    {"unidad": "Barbastro", "arcipestazgo": "Somontano", "arcipreste": "Paco", "animador": "Pedro", "nombre": "Valle", "poblacion": "Sopeira"},
    {"unidad": "Ainsa", "arcipestazgo": "Sobrarbe y Ribagorza", "arcipreste": "Paco", "animador": "Pedro", "nombre": "Vegas Bajas", "poblacion": "Montijo"},
    {"unidad": "Benasque", "arcipestazgo": "Sobrarbe y Ribagorza", "arcipreste": "Paco", "animador": "Pedro", "nombre": "Guadiana", "poblacion": "Guadiana"},
    {"unidad": "Binefar", "arcipestazgo": "Medio Cinca y Litera", "arcipreste": "Juan", "animador": "Maria", "nombre": "La Serena", "poblacion": "Castuera"},
    {"unidad": "Monzón", "arcipestazgo": "Medio Cinca y Litera", "arcipreste": "Juan", "animador": "Maria", "nombre": "Campiña Sur", "poblacion": "Llerena"},
    {"unidad": "Peralta de la Sal", "arcipestazgo": "Medio Cinca y Litera", "arcipreste": "Juan", "animador": "Maria", "nombre": "Sierra Suroeste", "poblacion": "Jerez de los Caballeros"},
    {"unidad": "Fraga", "arcipestazgo": "Bajo Cinca", "arcipreste": "Ana", "animador": "Carlos", "nombre": "Don Benito", "poblacion": "Don Benito"},
    {"unidad": "Fraga", "arcipestazgo": "Bajo Cinca", "arcipreste": "Ana", "animador": "Carlos", "nombre": "Villanueva", "poblacion": "Villanueva"},
    {"unidad": "Ainsa", "arcipestazgo": "Sobrarbe y Ribagorza", "arcipreste": "Ana", "animador": "Carlos", "nombre": "Miajadas", "poblacion": "Miajadas"},
    {"poblacion": "Aren","nombre": "Roberto Antonio Restrepo Builes","telefono": "624083835","unidad": "Robagorza y Sobrarbe", "moderador": "Juan Ignacio Cardona Orozco","telmoderador": "624", "arcipreste": "Jhon Mario Carmona", "telarcipreste": "324","animador": "Carlos","telanimador": "324"}
]

@app.route("/search")
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    results = []
    for item in data:
        if any(query.lower() in str(item.get(field, "")).lower() for field in ["nombre", "poblacion", "unidad", "arcipestazgo", "arcipreste", "animador, telefono, moderador"]):
            results.append(item)
    return jsonify(results)

@app.route("/")
def index():
    return send_file('src/index.html')

def main():
    app.run(port=int(os.environ.get('PORT', 8010)), host='0.0.0.0')

if __name__ == "__main__":
    main()
