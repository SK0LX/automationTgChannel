// Функция для редактирования поста
function editPost(postId, currentContent) {
    // Создание модального окна
    const modal = document.createElement('div');
    modal.className = 'modal';

    modal.innerHTML = `
        <div class="modal-content">
            <textarea id="edit-content">${currentContent}</textarea>
            <div class="modal-buttons">
                <button onclick="savePost(${postId})">💾 Save</button>
                <button onclick="closeModal()">❌ Cancel</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Добавляем класс размытия только для фона
    document.querySelector('.container').classList.add('blurred');
}

// Функция для сохранения изменений
async function savePost(postId) {
    const newContent = document.getElementById('edit-content').value;
   
    const response = await fetch(`/posts/edit/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: newContent }),
    });

    if (response.ok) {
        alert('Post updated successfully!');
        closeModal();
        // Обновляем контент поста на странице
        const postDiv = document.querySelector(`[data-post-id="${postId}"]`);
        postDiv.querySelector('p').innerHTML = `${newContent} <a href="${postDiv.querySelector('a').href}" target="_blank">Source</a>`;
    } else {
        alert('Failed to update post.');
    }
}

// Функция для закрытия модального окна
function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
        document.querySelector('.container').classList.remove('blurred');
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const topicSelect = document.getElementById('topic');
    const topicNameSpan = document.getElementById('topic-name');
    const postsList = document.getElementById('posts-list');
    const sitesList = document.getElementById('sites-list');
    const promptsList = document.getElementById('prompts-list');
    const newSiteInput = document.getElementById('new-site');
    const addSiteButton = document.getElementById('add-site-button');
    const newPromptInput = document.getElementById('new-prompt');
    const addPromptButton = document.getElementById('add-prompt-button');
    const siteSelect = document.getElementById('site');
    const newTopicInput = document.getElementById('new-topic');
    const addTopicButton = document.getElementById('add-topic-button');

    // Элементы для Telegram-канала
    const tgChannelInput = document.getElementById('tg-channel-id');
    const tgChannelNameInput = document.getElementById('tg-channel-name');
    const addTgChannelButton = document.getElementById('add-tg-channel-button');

    const modal = document.getElementById('edit-modal');
    const modalContent = document.getElementById('edit-post-content');
    const saveButton = document.getElementById('save-post-button');
    const cancelButton = document.getElementById('cancel-edit-button');
    let currentPostId = null;

    





    // Подгружаем топики
    const topicsResponse = await fetch('/topics');
    const topics = await topicsResponse.json();
    topics.forEach(topic => {
        const option = document.createElement('option');
        option.value = topic.id;
        option.textContent = topic.name;
        topicSelect.appendChild(option);
    });

    // Обработчик загрузки постов
    document.getElementById('topic-form').onsubmit = async (e) => {
        e.preventDefault();
        const topicId = topicSelect.value;
        topicNameSpan.textContent = topicSelect.options[topicSelect.selectedIndex].text;

        // Получаем канал для выбранного топика
        const tgChannelResponse = await fetch(`/tg-channel/${topicId}`);
        if (tgChannelResponse.ok) {
            const tgChannelData = await tgChannelResponse.json();
            tgChannelNameInput.value = tgChannelData.channel_name;
            tgChannelInput.value = tgChannelData.channel_id;
        } else {
            tgChannelNameInput.value = '';
            tgChannelInput.value = '';
        }

        // Показываем поле и кнопку для Telegram-канала
        tgChannelInput.style.display = 'block';
        tgChannelNameInput.style.display = 'block';
        addTgChannelButton.style.display = 'block';

        // Получаем посты для выбранного топика
        const postsResponse = await fetch('/admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topicId })
        });
        const posts = await postsResponse.json();
        postsList.innerHTML = '';

        posts.forEach(post => {
            const postDiv = document.createElement('div');
            postDiv.className = 'post-container';
            postDiv.setAttribute('data-post-id', post.id); // Установка атрибута data-post-id
            postDiv.innerHTML = `
                <p>${post.content} <a href="${post.source}" target="_blank">Source</a></p>
                <div class="post-buttons">
                    <button onclick="postAction(${post.id}, 'accept')">✅</button>
                    <button onclick="postAction(${post.id}, 'reject')">⛔</button>
                    <button onclick="editPost(${post.id}, '${post.content}')">✏️</button>
                </div>
            `;
            postsList.appendChild(postDiv);
        });


        // Получаем сайты и промты для выбранного топика
        const sitesResponse = await fetch(`/sites/${topicId}`);
        const sites = await sitesResponse.json();
        sitesList.innerHTML = sites.map(site => `<p>${site.site_url}</p>`).join('');
        sitesList.style.display = 'block'; 
        newSiteInput.style.display = 'block';
        addSiteButton.style.display = 'block';
        
        const promptsResponse = await fetch(`/prompts/${topicId}`);
        const prompts = await promptsResponse.json();
        promptsList.innerHTML = prompts.map(prompt => `<p>${prompt.prompt_text}</p>`).join('');
        promptsList.style.display = 'block'; 
        newPromptInput.style.display = 'block';
        addPromptButton.style.display = 'block';

        // Обновляем выбор сайта
        siteSelect.innerHTML = '';
        sites.forEach(site => {
            const option = document.createElement('option');
            option.value = site.id;
            option.textContent = site.site_url;
            siteSelect.appendChild(option);
        });

        // Скрываем/отображаем секции работы с промптами
        document.getElementById('prompts-management').style.display = sites.length > 0 ? 'block' : 'none';
    };

    // Обработчик загрузки промптов для выбранного сайта
    document.getElementById('site-select-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const siteId = siteSelect.value;
        if (!siteId) {
            alert('Please select a site.');
            return;
        }

        const response = await fetch(`/get-prompts?site=${siteId}`);
        const prompts = await response.json();

        promptsList.innerHTML = ''; // Очистка списка промптов
        prompts.forEach(prompt => {
            const promptItem = document.createElement('div');
            promptItem.textContent = prompt.prompt_text;
            promptsList.appendChild(promptItem);
        });

        document.getElementById('prompts-management').style.display = 'block';
    });

    // Добавление нового промпта
    addPromptButton.onclick = async () => {
        const siteId = siteSelect.value;
        const promptText = newPromptInput.value;

        if (!promptText || !siteId) {
            alert('Please enter a prompt and select a site.');
            return;
        }

        const response = await fetch('/add-prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ site: siteId, text: promptText })
        });

        if (response.ok) {
            alert('Prompt added successfully!');
            newPromptInput.value = '';
        } else {
            alert('Failed to add prompt.');
        }
    };


    addTgChannelButton.onclick = async () => {
        const tgChannelName = document.getElementById('tg-channel-name').value;
        const tgChannelId = document.getElementById('tg-channel-id').value;
        const topicId = topicSelect.value;

        if (!tgChannelName || !tgChannelId || !topicId) {
            alert('Please select a topic and enter both the Telegram Channel Name and ID');
            return;
        }

        await fetch('/tg-channels/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                channelName: tgChannelName,
                channelId: tgChannelId,
                topicId: topicId,
            }),
        });

        document.getElementById('tg-channel-name').value = '';
        document.getElementById('tg-channel-id').value = '';
    };


    // Обработчик добавления сайта
    addSiteButton.onclick = async () => {
        const newSite = newSiteInput.value;
        const topicId = topicSelect.value;
        if (!newSite || !topicId) {
            alert('Please select a topic and enter a site URL');
            return;
        }
        await fetch('/sites/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ site: newSite, topicId: topicId })
        });
        newSiteInput.value = '';
    };

    // Обработчик добавления нового топика
    addTopicButton.onclick = async () => {
        const newTopicName = newTopicInput.value;
        if (!newTopicName) {
            alert('Please enter a topic name');
            return;
        }
        await fetch('/topics/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newTopicName })
        });
        newTopicInput.value = '';
        // Обновление списка топиков
        const topicsResponse = await fetch('/topics');
        const topics = await topicsResponse.json();
        topicSelect.innerHTML = '';
        topics.forEach(topic => {
            const option = document.createElement('option');
            option.value = topic.id;
            option.textContent = topic.name;
            topicSelect.appendChild(option);
        });
    };
});

// Функция для выполнения действий с постами
async function postAction(postId, action) {
    const response = await fetch(`/posts/${postId}/${action}`, {
        method: 'POST',
    });

    if (response.ok) {
        // Если запрос успешен, удаляем пост из списка
        const postDiv = document.querySelector(`[data-post-id="${postId}"]`);
        if (postDiv) {
            postDiv.remove();
        }
    } else {
        const result = await response.text();
        alert(result);
    }
}