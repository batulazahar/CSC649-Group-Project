
// ==========================================
// 1. GET HTML ELEMENTS
// ==========================================

const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");
const historyList = document.getElementById("historyList");
const deleteModal = document.getElementById("deleteModal");
const deleteModalText = document.getElementById("deleteModalText");
const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

let pendingDeleteId = null;
const newChatButton = document.querySelector(".new-chat-btn");

const STORAGE_KEY = "travelmate-history";


// ==========================================
// 2. CHAT HISTORY DATA
// ==========================================

let chatHistory = [];

let currentConversation = createConversation();

function createConversation() {
    return {
        id: Date.now() + Math.random(),
        title: "New Chat",
        messages: []
    };
}


// ==========================================
// 3. SAVE AND LOAD HISTORY
// ==========================================

function saveHistory() {
    try {
        // Save the current conversation if it has messages
        if (currentConversation.messages.length > 0) {
            const index = chatHistory.findIndex(
                chat => chat.id === currentConversation.id
            );

            if (index !== -1) {
                chatHistory[index] = currentConversation;
            } else {
                chatHistory.unshift(currentConversation);
            }
        }

        localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(chatHistory)
        );

    } catch (error) {
        console.error("Unable to save chat history:", error);
    }
}

function loadHistory() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);

        if (saved) {
            const parsed = JSON.parse(saved);

            chatHistory = Array.isArray(parsed) ? parsed : [];
        }

    } catch (error) {
        console.error("Unable to load chat history:", error);
        chatHistory = [];
    }

    renderHistory();
}



// ==========================================
// 4. RENDER HISTORY SIDEBAR
// ==========================================


function renderHistory() {

    if (!historyList) return;

    historyList.innerHTML = "";

    // Show empty message
    if (chatHistory.length === 0) {

        const empty = document.createElement("div");
        empty.className = "history-empty";

        const icon = document.createElement("span");
        icon.textContent = "💬";

        const paragraph = document.createElement("p");
        paragraph.textContent = "No conversations yet";

        empty.append(icon, paragraph);

        historyList.appendChild(empty);

        return;
    }

    // Display saved conversations
    chatHistory.forEach(chat => {

        const item = document.createElement("div");

        item.className =
            "history-item" +
            (String(chat.id) === String(currentConversation.id)
                ? " active"
                : "");

        // Conversation title
        const title = document.createElement("span");

        title.className = "history-title";
        title.textContent = chat.title || "New Chat";

        // Delete button
        const deleteButton = document.createElement("button");

        deleteButton.className = "delete-chat";
        deleteButton.dataset.id = chat.id;
        deleteButton.textContent = "✕";
        deleteButton.type = "button";

        deleteButton.setAttribute(
            "aria-label",
            "Delete conversation"
        );

        // Open conversation
        item.addEventListener("click", function () {
            loadConversation(chat.id);
        });

        // Delete confirmation
        deleteButton.addEventListener("click", function (event) {

            event.stopPropagation();

            showDeleteModal(chat.id);

        });

        // IMPORTANT: Add elements into conversation item
        item.appendChild(title);
        item.appendChild(deleteButton);

        // Add conversation into sidebar
        historyList.appendChild(item);

    });
}


// ==========================================
// 5. LOAD PREVIOUS CONVERSATION
// ==========================================

function loadConversation(id) {

    const conversation = chatHistory.find(
        chat => String(chat.id) === String(id)
    );

    if (!conversation) return;

    // Save current conversation before switching
    saveHistory();

    currentConversation = conversation;

    chatMessages.innerHTML = "";

    conversation.messages.forEach(msg => {
        displayMessage(
            msg.content,
            msg.sender,
            false
        );
    });

    renderHistory();
}


// ==========================================
// 6. DELETE CONVERSATION
// ==========================================

function deleteConversation(id) {

    chatHistory = chatHistory.filter(
        chat => String(chat.id) !== String(id)
    );

    if (
        String(currentConversation.id) ===
        String(id)
    ) {

        currentConversation = {
            id: Date.now(),
            title: "New Chat",
            messages: []
        };

        chatMessages.innerHTML = "";
    }

    saveHistory();

    renderHistory();

    closeDeleteModal();
}

// Delete message history popup //
function showDeleteModal(id) {

    const conversation =
        chatHistory.find(
            chat => String(chat.id) === String(id)
        );

    if (!conversation) return;

    pendingDeleteId = id;

    deleteModalText.textContent =
        `Are you sure you want to delete "${conversation.title}"? This action cannot be undone.`;

    deleteModal.classList.add("show");
}

function closeDeleteModal() {

    pendingDeleteId = null;

    deleteModal.classList.remove("show");
}


// ==========================================
// DELETE MODAL BUTTON EVENTS
// ==========================================

// Cancel button
if (cancelDeleteBtn) {

    cancelDeleteBtn.addEventListener("click", function () {

        closeDeleteModal();

    });
}


// Confirm delete button
if (confirmDeleteBtn) {

    confirmDeleteBtn.addEventListener("click", function () {

        if (pendingDeleteId !== null) {

            deleteConversation(pendingDeleteId);

        }

    });
}


// ==========================================
// 7. FORMAT INLINE MARKDOWN
// ==========================================

function formatInlineText(text, container) {

    const pattern = /(\*\*.*?\*\*|`.*?`)/g;

    let lastIndex = 0;
    let match;

    while ((match = pattern.exec(text)) !== null) {

        container.appendChild(
            document.createTextNode(
                text.substring(lastIndex, match.index)
            )
        );

        const value = match[0];

        if (value.startsWith("**")) {

            const bold = document.createElement("strong");

            bold.textContent = value.slice(2, -2);

            container.appendChild(bold);

        } else {

            const code = document.createElement("code");

            code.textContent = value.slice(1, -1);

            container.appendChild(code);
        }

        lastIndex = pattern.lastIndex;
    }

    container.appendChild(
        document.createTextNode(text.substring(lastIndex))
    );
}


// ==========================================
// 8. MARKDOWN RENDERER
// ==========================================

function renderMarkdown(container, text) {

    const lines = String(text).split("\n");

    let paragraph = [];
    let currentList = null;

    function flushParagraph() {

        if (paragraph.length === 0) return;

        const p = document.createElement("p");

        formatInlineText(paragraph.join(" "), p);

        container.appendChild(p);

        paragraph = [];
    }

    function flushList() {

        if (currentList) {
            container.appendChild(currentList);
            currentList = null;
        }
    }

    lines.forEach(line => {

        const trimmed = line.trim();

        // Empty line
        if (!trimmed) {
            flushParagraph();
            flushList();
            return;
        }

        // Headings
        const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);

        if (headingMatch) {

            flushParagraph();
            flushList();

            const heading = document.createElement(
                "h" + headingMatch[1].length
            );

            formatInlineText(headingMatch[2], heading);

            container.appendChild(heading);

            return;
        }

        // Bullet points
        const bulletMatch = trimmed.match(/^[-*]\s+(.+)$/);

        // Numbered lists
        const numberedMatch = trimmed.match(/^\d+[.)]\s+(.+)$/);

        if (bulletMatch || numberedMatch) {

            flushParagraph();

            const listType = bulletMatch ? "ul" : "ol";

            if (
                !currentList ||
                currentList.tagName.toLowerCase() !== listType
            ) {
                flushList();
                currentList = document.createElement(listType);
            }

            const li = document.createElement("li");

            formatInlineText(
                bulletMatch ? bulletMatch[1] : numberedMatch[1],
                li
            );

            currentList.appendChild(li);

            return;
        }

        flushList();

        paragraph.push(trimmed);
    });

    flushParagraph();
    flushList();
}


// ==========================================
// 9. DISPLAY CHAT MESSAGE
// ==========================================

function displayMessage(message, sender, save = true) {

    // Remove welcome screen
    const welcomeMessage = document.querySelector(".welcome-message");

    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    const messageContent = document.createElement("div");

    messageContent.classList.add("message-content");

    if (sender === "bot-message") {
        renderMarkdown(messageContent, message);
    } else {
        messageContent.textContent = message;
    }

    messageDiv.appendChild(messageContent);

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Save message to conversation history
    if (save) {

        currentConversation.messages.push({
            content: message,
            sender: sender
        });

        // Use the first user message as the conversation title
        if (
            sender === "user-message" &&
            currentConversation.title === "New Chat"
        ) {
            currentConversation.title =
                message.length > 30
                    ? message.substring(0, 30) + "..."
                    : message;
        }

        saveHistory();
    }

    return messageDiv;
}


// ==========================================
// 10. TYPING INDICATOR
// ==========================================

function showTypingIndicator() {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add(
        "message",
        "bot-message",
        "typing-message"
    );

    const content = document.createElement("div");

    content.classList.add(
        "message-content",
        "typing-indicator"
    );

    for (let i = 0; i < 3; i++) {

        const dot = document.createElement("span");

        content.appendChild(dot);
    }

    messageDiv.appendChild(content);

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}


// ==========================================
// 11. SEND MESSAGE TO FLASK
// ==========================================

async function sendMessage(messageOverride = null) {

    if (!userInput || !sendButton || !chatMessages) return;

    const message = (
        typeof messageOverride === "string"
            ? messageOverride
            : userInput.value
    ).trim();

    // Prevent empty messages and multiple requests
    if (!message || sendButton.disabled) return;

    // Display user's message
    displayMessage(message, "user-message");

    // Clear input
    userInput.value = "";

    // Disable button
    sendButton.disabled = true;

    // Show typing indicator
    const loadingMessage = showTypingIndicator();

    try {

        // Send request to Flask backend
        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        });

        // Check response format
        const data = await response.json();

        // Remove typing indicator
        loadingMessage.remove();

        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );
        }

        // Display chatbot response
        if (data.response) {

            displayMessage(
                data.response,
                "bot-message"
            );

        } else {

            throw new Error(
                "The chatbot returned an empty response."
            );
        }

    } catch (error) {

        loadingMessage.remove();

        displayMessage(
            "Sorry, something went wrong: " + error.message,
            "bot-message"
        );

        console.error("Chatbot Error:", error);

    } finally {

        sendButton.disabled = false;

        userInput.focus();
    }
}


// ==========================================
// 12. SEND BUTTON EVENT
// ==========================================

if (sendButton) {

    sendButton.addEventListener("click", function () {
        sendMessage();
    });
}


// ==========================================
// 13. ENTER KEY EVENT
// ==========================================

if (userInput) {

    userInput.addEventListener("keydown", function (event) {

        if (event.key === "Enter" && !event.shiftKey) {

            event.preventDefault();

            sendMessage();
        }
    });
}


// ==========================================
// 14. CLICKABLE SUGGESTION CARDS
// ==========================================

const suggestionPrompts = [

    "Help me plan a travel budget for my next trip.",

    "I want to record and track my daily travel expenses.",

    "Help me monitor my travel spending and remaining budget.",

    "Convert a foreign currency into Malaysian Ringgit (MYR)."

];

const suggestionCards = document.querySelectorAll(
    ".suggestion-card"
);

suggestionCards.forEach((card, index) => {

    card.addEventListener("click", function () {

        if (suggestionPrompts[index]) {
            sendMessage(suggestionPrompts[index]);
        }

    });
});


// ==========================================
// 15. NEW CHAT BUTTON
// ==========================================

if (newChatButton) {

    newChatButton.addEventListener("click", function () {

        // Save existing conversation
        saveHistory();

        // Create a fresh conversation
        currentConversation = createConversation();

        // Clear chat display
        chatMessages.innerHTML = "";

        // Update sidebar
        renderHistory();

        // Focus on input
        if (userInput) {
            userInput.focus();
        }
    });
}


// ==========================================
// 16. INITIALIZE CHATBOT
// ==========================================

loadHistory();

