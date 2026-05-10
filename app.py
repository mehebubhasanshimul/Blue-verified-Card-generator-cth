from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import string
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# লোকাল ডেটা স্টোরেজ (সার্ভার রিস্টার্ট দিলে এটি মুছে যাবে, স্থায়ী করতে ডাটাবেস লাগে)
users = {}
generated_cards = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/settings', methods=['GET'])
def settings():
    return jsonify({
        "success": True,
        "settings": {
            "site_name": "Cyber Team Help - Meta Card",
            "site_tagline": "Developed by SHADOW JOKER",
            "developer_info": "WhatsApp: 01950178309 | Telegram: @SHADOW_JOKER_CTH",
            "admin_contact": "@SHADOW_JOKER_CTH"
        },
        "notices": [{"title": "Welcome", "content": "সরাসরি সাইন-আপ করে আপনার কার্ড তৈরি করুন।"}]
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    if email in users:
        return jsonify({"success": False, "message": "এই ইমেইলটি আগে ব্যবহার করা হয়েছে।"})
    
    users[email] = {
        "name": data.get('name'),
        "email": email,
        "password": data.get('password'),
        "status": "approved", # সরাসরি অ্যাপ্রুভড
        "cards_generated": 0
    }
    return jsonify({"success": True, "message": "রেজিস্ট্রেশন সফল হয়েছে! এখন লগইন করুন।"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = users.get(data.get('email'))
    if user and user['password'] == data.get('password'):
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        return jsonify({"success": True, "token": token, "user": user})
    return jsonify({"success": False, "message": "ভুল ইমেইল বা পাসওয়ার্ড!"})

@app.route('/api/profile', methods=['GET'])
def profile():
    # রেন্ডার বা ডেমো পারপাস প্রোফাইল ডেটা
    email = request.args.get('email') # সিম্পল রাখার জন্য ইমেইল দিয়ে ট্র্যাক করা হচ্ছে
    user = next(iter(users.values())) if users else {"name": "User", "status": "approved", "cards_generated": 0}
    cards = generated_cards.get(email, [])
    return jsonify({"success": True, "user": user, "cards": cards})

@app.route('/api/generate-card', methods=['POST'])
def generate_card():
    data = request.json
    holder = data.get('holder_name', 'SHADOW JOKER')
    
    card_type = random.choice(['visa', 'mastercard'])
    prefix = "4242" if card_type == 'visa' else "5573"
    card_num = prefix + ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    card = {
        "number": card_num,
        "holder": holder.upper(),
        "cvv": random.randint(100, 999),
        "month": str(random.randint(1, 12)).zfill(2),
        "year": "2029",
        "type": card_type,
        "card_number": card_num, # History display-র জন্য
        "card_holder": holder.upper(),
        "card_type": card_type,
        "expiry_month": str(random.randint(1, 12)).zfill(2),
        "expiry_year": "29",
        "created_at": "2026-05-11"
    }
    
    # ইতিহাসে জমা রাখা (ডেমো)
    if 'history' not in generated_cards: generated_cards['history'] = []
    generated_cards['history'].append(card)
    
    return jsonify({"success": True, "card": card})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
