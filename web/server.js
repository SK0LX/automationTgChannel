const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');

require('dotenv').config();

const app = express();
const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: 'localhost',
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: 5432,
});

app.use(cookieParser()); // Используем cookie-parser
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public')); // Статические файлы

// Secret key for JWT
const JWT_SECRET = process.env.JWT_SECRET || 'your_secret_key_here';

// Middleware for token verification
function authenticateToken(req, res, next) {
    const token = req.cookies.token;
    if (!token) return res.redirect('/login'); // Редирект на страницу логина, если токена нет
  
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.redirect('/login'); // Редирект на страницу логина, если токен невалиден
        req.user = user;
        next();
    });
}

// Route: Страница логина
app.get('/login', (req, res) => {
    res.sendFile(__dirname + '/public/login.html');
});

// Route: Страница админки
app.get('/admin', authenticateToken, (req, res) => {
    res.sendFile(__dirname + '/public/admin.html');
});

// Route: Login
app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    try {
        const result = await pool.query('SELECT * FROM admins WHERE username = $1', [username]);
        const user = result.rows[0];

        if (!user || !(await bcrypt.compare(password, user.password))) {
            return res.redirect('/login?error=Invalid credentials');
        }

        // Create JWT token
        const token = jwt.sign({ username: user.username }, JWT_SECRET, { expiresIn: '1h' });

        // Сохраняем токен в cookie и перенаправляем на админку
        res.cookie('token', token, { httpOnly: true }); // Устанавливаем токен в cookie
        res.redirect('/admin'); // Перенаправляем на админку
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Получение всех топиков
app.get('/topics', authenticateToken, async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM topics');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Добавление нового топика
app.post('/topics/add', authenticateToken, async (req, res) => {
    const { name } = req.body;

    try {
        await pool.query('INSERT INTO topics (name) VALUES ($1)', [name]);
        res.status(201).send('Topic added');
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Получение постов по топику
app.post('/admin', authenticateToken, async (req, res) => {
    const { topic } = req.body;

    try {
        const result = await pool.query('SELECT * FROM posts WHERE topic_id = $1', [topic]);
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Обработка действий с постами (принять/отклонить)
app.post('/posts/:postId/:action', authenticateToken, async (req, res) => {
  const { postId, action } = req.params;

  if (action === 'accept') {
    // Если действие "accept", обновляем статус поста
    try {
      await pool.query(
        'UPDATE posts SET is_accepted = $1 WHERE id = $2',
        [true, postId]
      );
      res.send('Post accepted');
    } catch (err) {
      console.error(err);
      res.status(500).send('Server error');
    }
  } else if (action === 'reject') {
    // Если действие "reject", удаляем пост из базы данных
    try {
      await pool.query('DELETE FROM posts WHERE id = $1', [postId]);
      res.send('Post rejected and deleted');
    } catch (err) {
      console.error(err);
      res.status(500).send('Server error');
    }
  } else {
    res.status(400).send('Invalid action');
  }
});


// Route: Получение сайтов по топику
app.get('/sites/:topicId', authenticateToken, async (req, res) => {
    const { topicId } = req.params;
    try {
        const result = await pool.query('SELECT * FROM sites WHERE topic_id = $1', [topicId]);
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Добавление нового сайта
app.post('/sites/add', authenticateToken, async (req, res) => {
    const { site, topicId } = req.body;

    if (!site || !topicId) {
        return res.status(400).send('Site and topic ID are required');
    }

    try {
        await pool.query('INSERT INTO sites (topic_id, site_url) VALUES ($1, $2)', [topicId, site]);
        res.status(201).send('Site added');
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});


// Route: Получение промтов по топику
app.get('/prompts/:topicId', authenticateToken, async (req, res) => {
    const { topicId } = req.params;
    try {
        const result = await pool.query('SELECT * FROM prompts WHERE topic_id = $1', [topicId]);
        res.json(result.rows);
        //console.log(res);
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Добавление нового промта
app.post('/prompts/add', authenticateToken, async (req, res) => {
    const { text, topicId } = req.body;

    try {
        await pool.query('INSERT INTO prompts (prompt_text, topic_id) VALUES ($1, $2)', [text, topicId]);
        res.status(201).send('Prompt added');
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// Route: Добавление нового Telegram-канала
app.post('/tg-channels/add', authenticateToken, async (req, res) => {
    const { channelName, channelId, topicId } = req.body;

    if (!channelName || !channelId || !topicId) {
        return res.status(400).send('Missing required fields');
    }

    try {
        await pool.query(
            'INSERT INTO telegram_channels (channel_name, channel_id, topic_id) VALUES ($1, $2, $3)',
            [channelName, channelId, topicId]
        );
        res.status(201).send('Telegram channel added');
    } catch (err) {
        console.error(err);
        if (err.code === '23505') { // Unique constraint violation
            res.status(400).send('Channel ID already exists');
        } else {
            res.status(500).send('Server error');
        }
    }
});


// Route: Получение Telegram-канала для топика
app.get('/tg-channel/:topicId', authenticateToken, async (req, res) => {
    const { topicId } = req.params;

    try {
        const result = await pool.query(
            'SELECT channel_name, channel_id FROM telegram_channels WHERE topic_id = $1 LIMIT 1',
            [topicId]
        );

        if (result.rows.length > 0) {
            res.status(200).json(result.rows[0]); // Отправляем найденные данные о канале
        } else {
            res.status(404).send('No Telegram channel found for this topic');
        }
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});



// Запуск сервера
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
