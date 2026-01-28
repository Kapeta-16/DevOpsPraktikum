from flask import Flask, request, jsonify
import os
import random
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

@app.route("/")
def home():
    return jsonify({"message": "Firebase spojen"})

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
    
    user_ref = db.collection("Users").document(username)
    user = user_ref.get()

    
    now = datetime.now()
    # Random deliveri
    delivery_minutes = random.randint(15, 30)
    eta = now + timedelta(minutes=delivery_minutes)

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

    # Save order reference to user's ordered collection
    if username:
        user_ref.collection("ordered").document(str(broj_narudbe)).set({
            "orderId": str(broj_narudbe),
            "placed_at": now.isoformat()
        })
    
    return jsonify({
        "poruka": "naruđba kreirana",
        "order_id": narudba_ref.id, 
        "ukupno": ukupno,
        "eta_delivery": eta.isoformat()
    })  

# NARUDBE PO ID-U
@app.route("/narudba/<order_number>", methods=["GET"])
def get_narudba(order_number):
    narudba_ref = db.collection("Orders").document(str(order_number))
    narudba = narudba_ref.get()

    if not narudba.exists:
        return jsonify({"error": "Narudžba ne postoji"}), 404

    narudba_data = narudba.to_dict()
    narudba_data["order_number"] = order_number

    # fallback za starije narudbe
    if not narudba_data.get("eta_delivery") and narudba_data.get("placed_at"):
        try:
            placed = datetime.fromisoformat(narudba_data["placed_at"])
            eta = placed + timedelta(minutes=random.randint(15, 60))
            narudba_data["eta_delivery"] = eta.isoformat()
            narudba_ref.update({"eta_delivery": eta.isoformat()})
        except:
            pass

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
            # fallback za starije narudbe
            if not order_data.get("eta_delivery") and order_data.get("placed_at"):
                try:
                    placed = datetime.fromisoformat(order_data["placed_at"])
                    eta = placed + timedelta(minutes=random.randint(15, 60))
                    order_data["eta_delivery"] = eta.isoformat()
                    db.collection("Orders").document(order_id).update({"eta_delivery": eta.isoformat()})
                except:
                    pass
            orders.append(order_data)
    return jsonify(orders)

# sve narudbe (za admina)
@app.route("/all-orders", methods=["GET"])
def get_all_orders():
    orders = []
    docs = db.collection("Orders").stream()
    
    for doc in docs:
        order_data = doc.to_dict()
        order_data["order_number"] = doc.id
        # fallback za starije narudbe
        if not order_data.get("eta_delivery") and order_data.get("placed_at"):
            try:
                placed = datetime.fromisoformat(order_data["placed_at"])
                eta = placed + timedelta(minutes=random.randint(15, 60))
                order_data["eta_delivery"] = eta.isoformat()

                db.collection("Orders").document(doc.id).update({"eta_delivery": eta.isoformat()})
            except:
                pass
        orders.append(order_data)
    
    return jsonify(orders)

# update statusa narudbe (za admina)
@app.route("/narudba/<order_number>/status", methods=["PATCH"])
def update_order_status(order_number):
    data = request.json
    new_status = data.get("status")
    
    if not new_status:
        return jsonify({"error": "Status je obavezan"}), 400
    
    valid_statuses = ["pending", "preparing", "delivering", "delivered", "rejected"]
    if new_status not in valid_statuses:
        return jsonify({"error": f"Nevazeci status. Dozvoljeni: {valid_statuses}"}), 400
    
    narudba_ref = db.collection("Orders").document(str(order_number))
    narudba = narudba_ref.get()
    
    if not narudba.exists:
        return jsonify({"error": "Narudzba ne postoji"}), 404
    
    narudba_ref.update({"status": new_status})
    
    return jsonify({"poruka": "Status azuriran", "status": new_status})

# SIGNUP

@app.route("/signup", methods=["POST"])
def signup():
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
