"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Favorites, Planet

app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    user = User.query.all()
    results = list(map(lambda usuarios : usuarios.serialize(), user))
    
    return jsonify(results), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def handle_user(user_id):
    user = User.query.filter_by(id = user_id).first() 
    results = user.serialize()
    
    return jsonify(results), 200

@app.route('/personajes', methods=['GET'])
def get_all_people():
    people = Character.query.all()
    results = list(map(lambda character : character.serialize(), people))

    json_text = jsonify(results)
    return json_text, 200

@app.route('/personajes/<int:character_id>', methods=['GET'])
def get_person(character_id):
    character = Character.query.filter_by(id = character_id).first()
    results = character.serialize()
    return results

@app.route('/planetas', methods=['GET'])
def get_all_planets():
    planet_list = Planet.query.all()
    results = list(map(lambda planeta : planeta.serialize(), planet_list))
    return results , 200

@app.route('/planetas/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(id = planet_id).first()
    results = planet.serialize()
    return results , 200

@app.route('/planetas', methods=['POST'])
def add_planet():
    body = json.loads(request.data)

    new_Planet = Planet(
        name = body['name'],
        rotation_period = body['rotation_period'],
        orbital_period = body['orbital_period'],
        diameter = body['diameter'],
        climate = body['climate'],
        gravity = body['gravity'],
        surface_water = body['surface_water'],
        population = body['population'])
    
    db.session.add(new_Planet)
    db.session.commit()

    response_body = {"msg": "el planeta ha sido creado"}
    return jsonify(response_body), 201

@app.route('/planetas/<int:planet_id>', methods=['PUT'])
def put_planet(planet_id):
    planet = Planet.query.filter_by(id = planet_id).first()
    body = json.loads(request.data)
    if planet is None:
        return jsonify({'message': 'el planeta no existe'}), 404
    
    if 'name' in body:
        planet.name = body['name']
    
    if "climate" in body:
        planet.climate = body['climate']

    if "rotation_period" in body:
        planet.rotation_period = body['rotation_period']

    if "orbital_period" in body:
        planet.orbital_period = body["orbital_period"]

    if "diameter" in body:
        planet.diameter = body['diameter']

    if "gravity" in body:
        planet.gravity = body['gravity']
    
    if "surface_water" in body:
        planet.surface_water = body["surface_water"]

    if "population" in body:
        planet.population = body['population']

    db.session.commit()

    return jsonify({'message': 'planeta modificado'})    

@app.route('/planetas/<int:planet_id>', methods=['DELETE'])
def death_star(planet_id):
    planet = Planet.query.filter_by(id = planet_id).first()

    if planet is None:
        return ({"message": "el planeta no existe"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    return ({"message": "no sé que poner aquí"}), 200

@app.route('/favoritos', methods=['GET'])
def get_all_favorites():
    all_favorites = Favorites.query.all()
    results = list(map(lambda favorite : favorite.serialize(), all_favorites))
    return results, 200

@app.route('/user/<int:id_user>/favorites', methods=['GET'])
def get_user_favorites(id_user):
    user_favorites = Favorites.query.filter_by(user_id = id_user)
    results = list(map(lambda favorite: favorite.serialize(), user_favorites))
    return results , 200

@app.route('/user/<int:id_user>/favorites', methods=['POST'])
def add_new_todo(id_user):
    data = request.json 
    data['user_id'] = str(id_user) 
    new_record = Favorites(**data)

    db.session.add(new_record)
    db.session.commit()

    return jsonify({'message': 'Se ha creado correctamente'}), 201

@app.route('/favoritos', methods=['POST'])
def add_Favorites():
    body = json.loads(request.data)
    new_Favorito = Favorites(
         user_id=body["user_id"], 
         planets_id=body["planets_id"], 
         character_id=body["character_id"])

    db.session.add(new_Favorito)
    db.session.commit()
                    
    response_body = {"msg": "El favorito se ha creado"}
    return jsonify(response_body), 201

@app.route('/favoritos/<int:id_favorite>', methods=['DELETE'])
def delete_favorite(id_favorite):
    
    planet = Favorites.query.filter_by(id = id_favorite).first()
   
    if planet is None:
        return ({"message": "el favorito no existe"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    return ({"message": "el favorito ha sido eliminado"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)