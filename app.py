from flask import Flask, request, jsonify, render_template
import requests
import smtplib
from email.mime.text import MIMEText

API_KEY = "a9e95ba84964a501eb8772453c5cee76"
app = Flask(__name__)

last_prediction = {}



def send_email(receiver, msg):
    try:
        print("📧 Sending email to:", receiver)

        sender = "work.suryaveer@gmail.com"
        app_password = "tzbhbhnvykaxlqxx"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, app_password)

        message = MIMEText(msg, "plain", "utf-8")
        message["Subject"] = "Disaster Alert"
        message["From"] = sender
        message["To"] = receiver

        server.send_message(message)
        server.quit()

        print("✅ Email Sent Successfully")

    except Exception as e:
        print("❌ Email ERROR:", e)

@app.route('/')
def home():
    return render_template("index.html")


# 🔥 AUTO PREDICTION
@app.route('/auto_predict', methods=['POST'])
def auto_predict():
    global last_prediction

    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    city = data.get('city')   # ✅ NEW
    email = data.get('email') # already added 

    try:
        if city:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        else:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        
        response = requests.get(url)
        weather = response.json()
        print("API:", weather)

        if "main" not in weather:
            return jsonify({"error": "City not found or API failed"})

        rain = weather.get("rain", {}).get("1h", 0)
        humidity = weather.get("main", {}).get("humidity", 50)
        pressure = weather.get("main", {}).get("pressure", 1010)
        wind = weather.get("wind", {}).get("speed", 5)

        location_name = weather.get("name", "Unknown")
        country = weather.get("sys", {}).get("country", "")

        # 🎯 DISASTER LOGIC
        if rain > 50:
            disaster = "Flood"
            pred = min(rain / 100, 1)

        elif wind > 20 and pressure < 1000:
            disaster = "Hurricane"
            pred = min(wind / 100, 1)

        else:
            disaster = "Safe"
            pred = 0.2

        # 🚨 ALERT
        if pred < 0.4:
            alert = "Low Risk"
        elif pred < 0.7:
            alert = "Medium Risk"
        else:
            alert = "High Risk 🚨"

        print("ALERT:", alert) 

        last_prediction = {"type": disaster, "risk": alert}

        # 📊 SMART RISK CALCULATION

        # 🌧️ Flood Risk (rain + humidity
        
        flood_val = min((rain / 50) + (humidity / 200), 1)
        
        # 🌪️ Hurricane Risk (wind + pressure)
        
        hurricane_val = min((wind / 30) + ((1010 - pressure) / 100), 1)
        # 🌍 Earthquake (baseline)
        earthquake_val = 0.2

        # 📧 EMAIL ALERT
        if email:
            send_email(email, f"""
Disaster Alert 🚨

Location: {location_name}, {country}
Disaster Type: {disaster}
Risk Level: {alert}

Rain: {rain}
Wind: {wind}
Pressure: {pressure}
Humidity: {humidity}

Stay safe.
""")

        return jsonify({
            "disaster": disaster,
            "prediction": pred,
            "alert": alert,
            "location": f"{location_name}, {country}",
            "flood": flood_val,
            "earthquake": earthquake_val,
            "hurricane": hurricane_val
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# 🤖 CHATBOT
@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message").lower()

    dtype = last_prediction.get("type")
    risk = last_prediction.get("risk")

    # ❗ If no prediction yet
    if not dtype:
        return jsonify({"reply": "⚠️ Please analyze location first."})

    # 🌊 FLOOD
    if "flood" in user_msg:
        reply = "Move to higher ground, avoid water, and keep emergency kit ready."

    # 🌪️ HURRICANE
    elif "hurricane" in user_msg or "cyclone" in user_msg or "storm" in user_msg:
        reply = "Stay indoors, avoid windows, and follow official alerts."

    # 🧠 GENERAL ACTION
    elif "what should i do" in user_msg or "what to do" in user_msg:
        if dtype == "Flood":
            reply = "Flood risk detected. Move to higher ground immediately."
        elif dtype == "Hurricane":
            reply = "Hurricane risk detected. Stay indoors and secure windows."
        else:
            reply = "No major risk. Stay alert."

    # 🔒 SAFETY CHECK
    elif "safe" in user_msg:
        if "High" in str(risk):
            reply = "❌ Not safe. Stay indoors."
        else:
            reply = "✅ Relatively safe."

    # ❓ WHY
    elif "why" in user_msg:
        reply = "Risk is calculated using rain, wind speed, pressure, and humidity."

    # 🧾 DEFAULT
    else:
        reply = "Ask about flood, hurricane, safety, or precautions."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    send_email("suryaayush18@gmail.com", "Test email working")  # ✅ runs first
    app.run(debug=True)