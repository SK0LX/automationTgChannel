const express = require('express');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const cookieParser = require('cookie-parser');
require('dotenv').config();

// Конфигурация
const app = express();
const port = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET || 'your_secret_key';
const pool = new Pool({
    user: process.env.POSTGRES_USER,
    host: process.env.POSTGRES_HOST || 'localhost',
    database: process.env.POSTGRES_DB,
    password: process.env.POSTGRES_PASSWORD,
    port: process.env.POSTGRES_PORT || 5432,
});

// Middleware
app.use(bodyParser.json());
app.use(cookieParser());
app.use(express.static('public'));

// Авторизация

// Middleware для проверки токена
function authenticateToken(req, res, next) {
    const token = req.cookies.token;
    if (!token) {
        return res.status(403).send('Access denied. No token provided.');
    }

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(400).send('Invalid token.');
    }
}

// Middleware для проверки, является ли пользователь администратором
function authenticateAdmin(req, res, next) {
    authenticateToken(req, res, () => {
        if (req.user.role !== 'admin') {
            return res.status(403).send('<body style="margin: 0; background: #1a1a1a; color: #f0f0f0; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh;"><div style="background: #333; color: #f0f0f0; padding: 20px; border: 1px solid #555; border-radius: 10px; text-align: center; font-size: 18px; font-weight: bold; text-transform: uppercase; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">Access Denied. Not an Admin.</div></body>');
        }
        next();
    });
}

// Эндпоинт для страницы модерации
app.get('/moderation', authenticateAdmin, (req, res) => {
    res.sendFile(__dirname + '/public/moderation.html');
});

// Эндпоинт для получения списка групп
app.get('/api/groups', authenticateAdmin, async (req, res) => {
    try {
        const result = await pool.query('SELECT id, name FROM groups');
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching groups:', err);
        res.status(500).send('Server error');
    }
});
// Эндпоинты
app.get('/api/groups', authenticateAdmin, async (req, res) => {
    try {
        const result = await pool.query('SELECT id, name FROM groups');
        res.json(result.rows);
    } catch {
        res.status(500).send('Server error.');
    }
});

// Регистрация пользователя
app.post('/api/register', async (req, res) => {
    const { username, password, telegramId, groupId } = req.body;
    try {
      // Хешируем пароль
      const hashedPassword = await bcrypt.hash(password, 10);
  
      // Записываем данные в БД
      const result = await pool.query(
        'INSERT INTO admins (username, password, telegram_id, group_id) VALUES ($1, $2, $3, $4) RETURNING *',
        [username, hashedPassword, telegramId, groupId]
      );
  
      res.status(201).json({ message: 'User registered successfully', user: result.rows[0] });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: 'Registration failed' });
    }
});

app.get('/api/max-group-id', async (req, res) => {
    try {
        const result = await pool.query('SELECT MAX(group_id) AS max_group_id FROM admins');
        const maxGroupId = result.rows[0].max_group_id || 0; // Если нет данных, возвращаем 0
        res.json({ max_group_id: maxGroupId });
    } catch (err) {
        console.error('Error fetching max group ID:', err);
        res.status(500).send('Error fetching max group ID');
    }
});


app.listen(port, () => console.log(`Server running on port ${port}`));

















