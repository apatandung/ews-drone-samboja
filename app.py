from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Ini adalah halaman utama untuk mengecek apakah server kita hidup
@app.route('/', methods=['GET'])
def home():
    return "✅ Server EWS Drone DJI 4T KHDTK Samboja Aktif dan Menunggu Sinyal!", 200

# Ini adalah 'Pintu Khusus' (Webhook) tempat Drone DJI akan melempar datanya
@app.route('/webhook-dji', methods=['POST'])
def terima_data_drone():
    try:
        # Menangkap data (JSON) yang dikirim lewat internet oleh SIM Card Drone
        data_drone = request.json
        print("🚨 Menerima Sinyal dari Drone:", data_drone)
        
        # (Nanti di sini kita akan memasukkan kode pengirim WA Fonnte ke Grup)
        
        return jsonify({"status": "berhasil", "pesan": "Sinyal diterima server"}), 200
    except Exception as e:
        print("Error saat memproses data:", e)
        return jsonify({"status": "gagal", "pesan": str(e)}), 400

if __name__ == '__main__':
    # Memastikan server berjalan di port yang disediakan oleh sistem Cloud
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
