from flask import Flask, request, jsonify
import os
import requests
import json
from shapely.geometry import shape, Point

app = Flask(__name__)

FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN", "")
TARGET_WA = os.environ.get("TARGET_WA", "")

# 1. Memuat Poligon GeoJSON Kantor YJP saat server menyala
yjp_polygon = None
try:
    with open('yjp_office.geojson', 'r') as f:
        geo_data = json.load(f)
        # Mengambil bentuk geometri dari fitur pertama dalam GeoJSON
        yjp_polygon = shape(geo_data['features'][0]['geometry'])
        print("✅ Peta GeoJSON YJP Office berhasil dimuat!")
except Exception as e:
    print("⚠️ Gagal memuat GeoJSON (pastikan nama file yjp_office.geojson):", e)

@app.route('/', methods=['GET'])
def home():
    return "✅ Server EWS Drone DJI 4T KHDTK Samboja Aktif!", 200

@app.route('/webhook-dji', methods=['POST'])
def terima_data_drone():
    try:
        data = request.json
        print("🚨 Data masuk dari Drone:", data)
        
        suhu = data.get('suhu', 'N/A')
        # Konversi koordinat dari drone menjadi angka desimal (float)
        lat = float(data.get('lat', -0.972644))
        lon = float(data.get('lon', 116.936903))
        
        # 2. Logika Deteksi Lokasi (Titik dalam Poligon)
        lokasi_target = "⚠️ AREA HUTAN (KHDTK SAMBOJA / SEKITARNYA)"
        if yjp_polygon:
            # Shapely menggunakan format (Longitude, Latitude) untuk Point
            titik_api = Point(lon, lat) 
            if yjp_polygon.contains(titik_api):
                lokasi_target = "Uji Coba Drum Api (Kantor YJP)"
        
        # 3. Merakit pesan WhatsApp
        pesan = f"🚨 *PERINGATAN THERMAL DRONE* 🚨\n\n"
        pesan += f"*Target:* _{lokasi_target}_\n"
        pesan += f"*Suhu Maksimum:* {suhu}°C\n"
        pesan += f"*Koordinat Api:* `{lat}, {lon}`\n\n"
        pesan += f"📍 *Buka di Google Maps:* https://maps.google.com/?q={lat},{lon}"
        
        # 4. Mengirim ke Grup Fonnte
        headers = {'Authorization': FONNTE_TOKEN}
        payload = {'target': TARGET_WA, 'message': pesan}
        response = requests.post("https://api.fonnte.com/send", headers=headers, data=payload)
        
        return jsonify({"status": "berhasil", "pesan": "Notifikasi WA terkirim!", "lokasi": lokasi_target}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "gagal", "pesan": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
