
# Telegram Post Publishing Bot

This is a Python script that periodically checks for accepted posts in a PostgreSQL database and sends them to corresponding Telegram channels using a Telegram bot. After successfully sending a post, it deletes the post from the database to avoid re-publishing.

## Requirements

- Python 3.x
- PostgreSQL Database
- Telegram Bot Token
- Required Python Packages:
  - `psycopg2` (for PostgreSQL interaction)
  - `python-telegram-bot` (for interacting with the Telegram API)
  - `python-dotenv` (for environment variable management)

## Setup

### 1. Install dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

Where `requirements.txt` contains the following:

```text
psycopg2
python-telegram-bot
python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory of the project and add your PostgreSQL and Telegram bot configuration:

```text
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DB=<your_postgres_db>
JWT_SECRET=<your_jwt_secret>
TELEGRAM_API_TOKEN=<your_telegram_bot_api_token>
```

### 3. Database Setup

Ensure that the PostgreSQL database is set up with the following tables:

```sql
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100),
    is_accepted BOOLEAN DEFAULT FALSE,
    topic_id INT REFERENCES topics(id)
);

CREATE TABLE telegram_channels (
    id SERIAL PRIMARY KEY,
    topic_id INT REFERENCES topics(id) ON DELETE CASCADE,
    channel_name VARCHAR(100) NOT NULL,
    channel_id VARCHAR(50) NOT NULL UNIQUE
);
```

### 4. Run the Script

To start the bot, run the following command:

```bash
python bot.py
```

The bot will start checking the `posts` table every 15 minutes. If it finds any posts marked as `is_accepted = true`, it will send the post content to the corresponding Telegram channel and delete the post from the database.

## How It Works

- The bot periodically checks for new posts with `is_accepted = true`.
- It looks up the appropriate Telegram channel for the `topic_id` of the post.
- If a valid channel is found, the post content is sent to the Telegram channel.
- After a successful send, the post is deleted from the database.
- If a post cannot be sent, it is not deleted, and the bot will retry in the next cycle.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
