from flask import Flask, request, jsonify
import os
import firebase_admin
from flask_cors import CORS
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/")
def home():
    return jsonify({"message": "Firebase spojen"})


#backend funckije za narucivanje i potvrdivanje dostave ako si ulogiran (jednostavno jedan korisnik na firebaseu kao collection users 
# (admin i admin123 kao user i lozinka) <- za naruceno mogu  i ja)

# MENI otvoren za guest i users
@app.route("/meni", methods=["GET"])
def get_meni():
    items = []
    docs = db.collection("MenuItems").stream()

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        items.append(item)

    return jsonify(items)           
           
# NARUĐBA

@app.route("/narudba", methods=["POST"])
def create_narudba():
    data = request.json

    username = data.get("username")
    items = data.get("items")

    if not items:
        return jsonify({"error": "Fale podaci"}), 400
    
    now = datetime.now()
    eta = now + timedelta(minutes=45)

    ukupno = 0
    for item in items:
        ukupno += item.get("cijena", 0) * item.get("kolicina", 1)


    brojac_ref = db.collection("BrojNarudba").document("narudbe")
    brojac_snapshot = brojac_ref.get()
    data = brojac_snapshot.to_dict() if brojac_snapshot.exists else {}

    broj_narudbe = data.get("trenutni", 0) + 1
    brojac_ref.set({"trenutni": broj_narudbe})

    narudba = {
        "order_number": broj_narudbe,
        "customer_info": username,
        "status": "pending",
        "placed_at": now.isoformat(),
        "eta_delivery": eta.isoformat(),
        "ukupno": ukupno
    }

    narudba_ref = db.collection("Orders").document(str(broj_narudbe))
    narudba_ref.set(narudba)

    item_id = 1
    for item in items:
        narudba_ref.collection("items").document(str(item_id)).set({
            "ime": item.get("ime"),
            "cijena": item.get("cijena"),
            "kolicina": item.get("kolicina")
        })
        item_id += 1


    
    return jsonify({"poruka": "naruđba kreirana","order_id": narudba_ref.id, "ukupno": ukupno})  

# NARUDBE PO ID-U
@app.route("/narudba/<order_number>", methods=["GET"])
def get_narudba(order_number):
    narudba_ref = db.collection("Orders").document(str(order_number))
    narudba = narudba_ref.get()

    if not narudba.exists:
        return jsonify({"error": "Narudžba ne postoji"}), 404

    narudba_data = narudba.to_dict()

    items = []
    for doc in narudba_ref.collection("items").stream():
        items.append(doc.to_dict())

    narudba_data["items"] = items

    return jsonify(narudba_data)

# sve narudbe za korisnika
@app.route("/user-orders/<username>")
def get_user_orders(username): 
    ordered_ref = db.collection("Users").document(username).collection("ordered").stream()
    order_ids = []

    for doc in ordered_ref: 
        data = doc.to_dict()
        order_id = data.get("orderId") or doc.id
        order_ids.append(order_id)

    orders = []
    for order_id in order_ids:
        order_doc = db.collection("Orders").document(order_id).get()
        if order_doc.exists:
            order_data = order_doc.to_dict()
            order_data["order_number"] = order_id
            orders.append(order_data)
    return jsonify(orders)

# SIGNIN

@app.route("/signin", methods=["POST"])
def signin():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Fale podaci"}), 400
    
    user_ref = db.collection("Users").document(username)

    if user_ref.get().exists:
        return jsonify ({"error": "User vec postoji"}), 409
    

    user_ref.set({
        "username": username,
        "password": password,
        "admin": False
    })

    return jsonify({"poruka": "Registracija uspjesna"})

# LOGIN

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Fale podaci"}), 400
    
    user_ref = db.collection("Users").document(username)
    user = user_ref.get()

    if not user.exists:
        return jsonify({"error", "User ne postiji"}), 404
    
    user_data = user.to_dict()

    if user_data["password"] != password:
        return jsonify({"error", "Pogresan password"}), 401
    
    return jsonify({
        "poruka": "Uspjesan login",
        "username": username,
        "admin": user_data.get("admin", False)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
