from flask import Flask, render_template_string, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = '/data/library.db'

def init_db():
    os.makedirs('/data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    ''')
    # Add sample books if empty
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ('Clean Code', 'Robert Martin', 'Technology', 'Available'),
            ('The DevOps Handbook', 'Gene Kim', 'Technology', 'Borrowed'),
            ('Kubernetes in Action', 'Marko Luksa', 'Technology', 'Available'),
            ('Docker Deep Dive', 'Nigel Poulton', 'Technology', 'Available'),
            ('The Phoenix Project', 'Gene Kim', 'Novel', 'Borrowed'),
        ]
        cursor.executemany(
            'INSERT INTO books (title, author, genre, status) VALUES (?,?,?,?)',
            sample_books
        )
    conn.commit()
    conn.close()

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Library Management System</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; }
        .navbar {
            background: #1a252f;
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar h1 { font-size: 20px; }
        .badge {
            background: #e74c3c;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
        }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        .stat {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .stat h2 { font-size: 32px; color: #1a252f; }
        .stat p { color: #7f8c8d; font-size: 13px; margin-top: 5px; }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow: hidden;
        }
        .card-header {
            background: #1a252f;
            color: white;
            padding: 12px 20px;
            font-size: 15px;
            font-weight: bold;
        }
        .form-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            padding: 20px;
        }
        input, select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            width: 100%;
        }
        button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 9px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 0 20px 20px;
        }
        table { width: 100%; border-collapse: collapse; }
        th {
            background: #ecf0f1;
            padding: 10px 20px;
            text-align: left;
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
        }
        td { padding: 12px 20px; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
        tr:hover { background: #fafafa; }
        .available { color: #27ae60; font-weight: bold; }
        .borrowed { color: #e74c3c; font-weight: bold; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>📚 Library Management System</h1>
        <span class="badge">☸️ Running on Kubernetes</span>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat">
                <h2>{{ total }}</h2>
                <p>Total Books</p>
            </div>
            <div class="stat">
                <h2>{{ available }}</h2>
                <p>Available</p>
            </div>
            <div class="stat">
                <h2>{{ borrowed }}</h2>
                <p>Borrowed</p>
            </div>
        </div>
        <div class="card">
            <div class="card-header">➕ Add New Book</div>
            <form method="POST" action="/add">
                <div class="form-row">
                    <input name="title" placeholder="Book Title" required>
                    <input name="author" placeholder="Author" required>
                    <input name="genre" placeholder="Genre" required>
                </div>
                <button type="submit">Add Book</button>
            </form>
        </div>
        <div class="card">
            <div class="card-header">📋 Book Records</div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Author</th>
                        <th>Genre</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for book in books %}
                    <tr>
                        <td>{{ book[0] }}</td>
                        <td>{{ book[1] }}</td>
                        <td>{{ book[2] }}</td>
                        <td>{{ book[3] }}</td>
                        <td class="{{ book[4]|lower }}">{{ book[4] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div class="footer">
            Library Management System | Deployed with Jenkins + Docker + Kubernetes
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    total = len(books)
    available = sum(1 for b in books if b[4] == 'Available')
    borrowed = sum(1 for b in books if b[4] == 'Borrowed')
    conn.close()
    return render_template_string(HTML, books=books,
                                 total=total,
                                 available=available,
                                 borrowed=borrowed)

@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO books (title, author, genre) VALUES (?,?,?)',
        (title, author, genre)
    )
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
