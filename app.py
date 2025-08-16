
from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Download folder
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# HTML UI (Mobile Friendly)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>📥 Mobile Video Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #121212;
            color: #fff;
            text-align: center;
            padding: 20px;
        }
        input {
            width: 90%;
            padding: 10px;
            font-size: 16px;
            margin-bottom: 10px;
            border-radius: 5px;
            border: none;
        }
        button {
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            font-size: 16px;
            border: none;
            border-radius: 5px;
        }
        button:hover {
            background: #45a049;
        }
        #status {
            margin-top: 20px;
            font-weight: bold;
        }
        a {
            color: #00ffcc;
        }
    </style>
</head>
<body>
    <h1>📥 Mobile Video Downloader</h1>
    <input type="text" id="url" placeholder="Enter video URL here">
    <br>
    <button onclick="startDownload()">Download</button>
    <div id="status"></div>
    <script>
        function startDownload() {
            const url = document.getElementById("url").value.trim();
            if (!url) {
                alert("Please enter a URL");
                return;
            }
            document.getElementById("status").innerHTML = "⏳ Downloading... Please wait.";
            fetch("/download", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({url: url})
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    document.getElementById("status").innerHTML = "❌ Error: " + data.error;
                } else {
                    document.getElementById("status").innerHTML =
                        `✅ Done! <a href="${data.download_url}">Click to Download</a>`;
                }
            })
            .catch(err => {
                document.getElementById("status").innerHTML = "❌ Error: " + err;
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML_PAGE

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    file_id = str(uuid.uuid4())
    out_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    try:
        ydl_opts = {
            "outtmpl": out_template,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
            file_path = f"{DOWNLOAD_DIR}/{file_id}.{ext}"

        return jsonify({"download_url": f"/get/{file_id}.{ext}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get/<filename>")
def get_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    # Host on 0.0.0.0 so other devices on same Wi-Fi can access
    app.run(host="0.0.0.0", port=5000)