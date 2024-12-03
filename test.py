# Импортируй Flask
from flask import Flask

# Создай приложение
app = Flask(__name__)

# Определи маршрут для главной страницы
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Запусти приложение в режиме отладки
if __name__ == '__main__':
    app.run(debug=True)