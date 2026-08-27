from flask import Flask, request, jsonify
import os
import requests
import json
from shapely.geometry import shape, Point

app = Flask(__name__)

FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN", "")
TARGET_WA = os.environ.get("TARGET_WA", "")

yjp_polygon = None
try:
    with open('yjp_office.geojson', 'r') as f:
        geo_data = json.load(f)
        yjp_polygon = shape(geo_data['features'][0]['geometry'])
except Exception as e:
    print("⚠️ Gagal memuat GeoJSON:", e)

@app.route('/', methods=['GET'])
def home():
    return "✅ Server EWS Drone DJI 4T Aktif!", 200

# 🌟 UBAH DISINI: Menambahkan 'GET' agar lolos tes koneksi remote DJI
@app.route('/webhook-dji', methods=['GET', 'POST'])
def terima_data_drone():
    # Jika remote DJI hanya mengecek koneksi (Muncul teks ini di layar remote Anda nanti)
    if request.method == 'GET':
        return "✅ Server Siap Menerima Data Thermal dari DJI!", 200
        
    # Jika drone mengirim data thermal sesungguhnya
    try:
        data = request.json
        suhu = data.get('suhu', 'N/A')
        lat = float(data.get('lat', -0.972644))
        lon = float(data.get('lon', 116.936903))
        
        lokasi_target = "⚠️ AREA HUTAN (KHDTK SAMBOJA / SEKITARNYA)"
        if yjp_polygon:
            titik_api = Point(lon, lat) 
            if yjp_polygon.contains(titik_api):
                lokasi_target = "Uji Coba Drum Api (Kantor YJP)"
        
        pesan = f"🚨 *PERINGATAN THERMAL DRONE* 🚨\n\n"
        pesan += f"*Target:* _{lokasi_target}_\n"
        pesan += f"*Suhu Maksimum:* {suhu}°C\n"
        pesan += f"*Koordinat Api:* `{lat}, {lon}`\n\n"
        pesan += f"📍 *Buka di Google Maps:* https://maps.google.com/?q={lat},{lon}"
        
        headers = {'Authorization': FONNTE_TOKEN}
        payload = {'target': TARGET_WA, 'message': pesan}
        requests.post("https://api.fonnte.com/send", headers=headers, data=payload)
        
        return jsonify({"status": "berhasil"}), 200
    except Exception as e:
        return jsonify({"status": "gagal", "pesan": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
