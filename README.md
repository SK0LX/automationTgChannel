
## **Architecture**

### **System Flow**  
```plaintext
[ Sources ] → [ Python Core ] → [ OpenRouter AI ] → [ PostgreSQL DB ]
                │                       │                  │
        ┌───────┴───────┐        ┌──────▼─────┐      ┌─────▼─────┐
        │ Web Admin     │        │ Content AI │      │ Telegram  │
        │ Panel         │        │ Filtering  │      │ Bot       │
        └───────┬───────┘        └──────▲─────┘      └─────▲─────┘
                │                          │                │
                └─────────[ Moderator Actions ]─────────────┘
                                Accept/Reject/Edit
```

---

## **Components**

1. **Python Core**  
   - **Parses content**  
   - Sends to **OpenRouter** for filtering  
   - Saves results to **PostgreSQL**  

2. **Web Admin Panel**  
   - Moderation: **Accept**, **Reject**, **Edit**  
   - Settings: Sources, prompts  

3. **Telegram Bot**  
   - Moderation interface via **commands/buttons**  

4. **PostgreSQL DB**  
   - Stores posts and statuses  

---

## **Tech Stack**

| Component          | Technology          |
|---------------------|---------------------|
| **Core**           | Python, OpenRouter API |
| **Web Panel**      | Node.js, Express, HTML/CSS/JS |
| **Bot**            | Python (aiogram)    |
| **Database**       | PostgreSQL          |

---

## **Flow**  
```plaintext
Sources → Core Parser → AI Filtering → Database → Moderation (Web/Bot) → Final Posts
```
