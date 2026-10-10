from flask import Flask, request, render_template_string, send_file
from PIL import Image
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Очистка печати от фона</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: #f4f6f9; text-align: center; padding: 50px 20px; color: #333; }
        .container { background: white; padding: 40px 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); display: inline-block; max-width: 450px; width: 100%; box-sizing: border-box; }
        h2 { margin-top: 0; color: #111; }
        p { color: #666; font-size: 14px; margin-bottom: 30px; }
        .file-input { margin: 20px 0; font-size: 16px; }
        button { background: #007BFF; color: white; border: none; padding: 14px 28px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; transition: background 0.2s; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔮 Удаление фона печати</h2>
        <p>Загрузите фото, алгоритм автоматически сотрёт белую бумагу и оставит только печать.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="seal_image" accept="image/*" required class="file-input"><br>
            <button type="submit">Очистить фон полностью</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload():
    if 'seal_image' not in request.files:
        return "Файл не найден", 400

    file = request.files['seal_image']
    img = Image.open(io.BytesIO(file.read())).convert("RGBA")

    # Алгоритм: перебираем пиксели и делаем светлые (белую бумагу) прозрачными
    datas = img.getdata()
    new_data = []

    for item in datas:
        # item[0] - Красный, item[1] - Зеленый, item[2] - Синий
        # Если пиксель очень светлый (близок к белому цвету бумаги), стираем его
        if item[0] > 180 and item[1] > 180 and item[2] > 180:
            new_data.append((255, 255, 255, 0)) # Делаем полностью прозрачным
        else:
            new_data.append(item) # Оставляем цвет печати (синий, красный и т.д.)

    img.putdata(new_data)

    # Сохраняем в формате PNG
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='stamp_only.png')

# Настройка для запуска на Vercel
app.debug = False
