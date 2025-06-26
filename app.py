from flask import Flask, render_template, request, send_file, jsonify
import os
from PIL import Image
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

# Pastikan folder uploads ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress/image', methods=['POST'])
def compress_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Tidak ada file yang dipilih'}), 400

        # Validasi file gambar
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            return jsonify({'error': 'Format file tidak didukung. Gunakan format gambar yang valid.'}), 400

        # Ambil nilai kualitas dari form
        quality = int(request.form.get('quality', 50))
        
        # Baca file gambar
        img = Image.open(file.stream)
        
        # Konversi ke RGB jika mode RGBA (untuk kompatibilitas JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Buat background putih untuk gambar transparan
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Kompres gambar
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='compressed_' + file.filename
        )
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Converter Routes
@app.route('/convert/image', methods=['POST'])
def convert_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Tidak ada file yang dipilih'}), 400

        # Validasi file gambar
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            return jsonify({'error': 'Format file tidak didukung. Gunakan format gambar yang valid.'}), 400

        # Ambil format output dari form
        output_format = request.form.get('format', 'png').upper()
        
        if not output_format:
            return jsonify({'error': 'Format output harus dipilih'}), 400
        
        # Baca file gambar
        img = Image.open(file.stream)
        
        # Konversi gambar
        output = io.BytesIO()
        
        # Tentukan format output
        if output_format == 'JPG':
            # Konversi ke RGB jika mode RGBA (untuk kompatibilitas JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Buat background putih untuk gambar transparan
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            else:
                img = img.convert('RGB')
            img.save(output, format='JPEG', quality=95)
            mimetype = 'image/jpeg'
        elif output_format == 'PNG':
            img.save(output, format='PNG')
            mimetype = 'image/png'
        elif output_format == 'GIF':
            img.save(output, format='GIF')
            mimetype = 'image/gif'
        elif output_format == 'WEBP':
            img.save(output, format='WEBP')
            mimetype = 'image/webp'
        elif output_format == 'BMP':
            img = img.convert('RGB')
            img.save(output, format='BMP')
            mimetype = 'image/bmp'
        elif output_format == 'TIFF':
            img.save(output, format='TIFF')
            mimetype = 'image/tiff'
        else:
            return jsonify({'error': 'Format tidak didukung'}), 400
        
        output.seek(0)
        
        # Buat nama file output
        filename = os.path.splitext(file.filename)[0] + '.' + output_format.lower()
        
        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True) 