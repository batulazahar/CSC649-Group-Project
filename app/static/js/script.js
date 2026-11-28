
// ==========================================
// 1. GET HTML ELEMENTS
// ==========================================

const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");
const historySearch = document.getElementById("historySearch");

// ==========================================
// CHAT HISTORY
// ==========================================

const currentUserEmail =
    window.currentUserEmail || "guest";

const STORAGE_KEY =
    `travelMateHistory_${currentUserEmail}`;

let chatHistory = JSON.parse(

    localStorage.getItem(
        STORAGE_KEY
    )

) || [];

let currentConversation = {
    id: Date.now(),
    title: "New Conversation",
    messages: [],
    pinned: false
};

let conversationSearch = "";


// ==========================================
// 2. FORMAT INLINE MARKDOWN SAFELY
// ==========================================

function formatInlineText(text, container) {

    // Supports **bold** and `inline code`
    const pattern = /(\*\*.*?\*\*|`.*?`)/g;

    let lastIndex = 0;
    let match;

    while ((match = pattern.exec(text)) !== null) {

        // Add normal text
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

    // Add remaining text
    container.appendChild(
        document.createTextNode(text.substring(lastIndex))
    );
}


// ==========================================
// 3. FORMAT CHATBOT MARKDOWN RESPONSES
// ==========================================

function renderMarkdown(container, text) {

    const lines = String(text).split("\n");

    let paragraph = [];
    let currentList = null;

    function flushParagraph() {

    if (paragraph.length === 0) return;

    const p = document.createElement("p");

    paragraph.forEach((line, index) => {

        if (index > 0) {
            p.appendChild(document.createElement("br"));
        }

        formatInlineText(line, p);

    });

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
        const numberedMatch = trimmed.match(/^(\d+)[.)]\s+(.+)$/);

        if (bulletMatch || numberedMatch) {

            flushParagraph();

            const listType = bulletMatch ? "ul" : "ol";

            if (!currentList ||
                currentList.tagName.toLowerCase() !== listType) {

                flushList();

                currentList = document.createElement(listType);
            }

            const li = document.createElement("li");

            formatInlineText(
                bulletMatch ? bulletMatch[1] : numberedMatch[2],
                li
            );

            if (numberedMatch) {
                li.value = Number(numberedMatch[1]);
            }

currentList.appendChild(li);

            return;
        }

        // Normal paragraph
        flushList();

        paragraph.push(trimmed);

    });

    flushParagraph();
    flushList();
}


// ==========================================
// 4. DISPLAY CHAT MESSAGE
// ==========================================

function displayMessage(message, sender) {

    // Remove welcome screen
    const welcomeMessage = document.querySelector(".welcome-message");

    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Create message container
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    // Create message content
    const messageContent = document.createElement("div");

    messageContent.classList.add("message-content");

    // Format AI response
    if (sender === "bot-message") {

        renderMarkdown(messageContent, message);

    } else {

        messageContent.textContent = message;

    }

    messageDiv.appendChild(messageContent);

    // Add message to chat
    chatMessages.appendChild(messageDiv);

    // Scroll to latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}


// ==========================================
// 5. TYPING INDICATOR
// ==========================================

function showTypingIndicator() {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", "bot-message");
    messageDiv.classList.add("typing-message");

    messageDiv.setAttribute("role", "status");

    const content = document.createElement("div");

    content.classList.add("message-content", "typing-indicator");
    content.setAttribute("aria-hidden", "true");

    // Create three animated dots
    for (let i = 0; i < 3; i++) {

        const dot = document.createElement("span");

        content.appendChild(dot);
    }

    // Dynamic loading messages
    const loadingTexts = [
        "TravelMate AI is thinking...",
        "Working on your request...",
        "Preparing your travel assistance...",
        "Generating your response...",
        "Thank you for your patience..."
    ];

    let textIndex = 0;

    // Create typing status text
    const typingText = document.createElement("div");

    typingText.classList.add("typing-text");

    typingText.textContent = loadingTexts[textIndex];

    // Change loading text every 2.5 seconds
    const typingInterval = setInterval(() => {

        if (textIndex < loadingTexts.length - 1) {

            textIndex++;

            typingText.textContent = loadingTexts[textIndex];

        } else {

            clearInterval(typingInterval);

        }

    }, 2500);

    // Store interval for cleanup
    messageDiv.typingInterval = typingInterval;

    // Add animation and text
    messageDiv.appendChild(content);
    messageDiv.appendChild(typingText);

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}


// ==========================================
// 6. SEND MESSAGE TO FLASK
// ==========================================

async function sendMessage(messageOverride = null) {

    const message = (
        typeof messageOverride === "string"
            ? messageOverride
            : userInput.value
    ).trim();

    // Prevent empty messages
    if (!message || sendButton.disabled) {
        return;
    }

    // Display user's message
    displayMessage(message, "user-message");

    currentConversation.messages.push({
        sender: "user",
        text: message
    });

    saveConversation();

    if (
        currentConversation.title === "New Conversation"
    ) {
        currentConversation.title =
            message.substring(0, 30) +
            (message.length > 30 ? "..." : "");
    }

    // Clear input
    userInput.value = "";

    // Disable button while waiting
    sendButton.disabled = true;

    // Show typing animation
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

        const data = await response.json();

        // Remove typing indicator
        clearInterval(loadingMessage.typingInterval);
        loadingMessage.remove();

        // Check API response
        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );

        }

        // Display AI response
        if (data.response) {

            displayMessage(
                data.response,
                "bot-message"
            );

            currentConversation.messages.push({
                sender: "bot",
                text: data.response
            });

            saveConversation();

        } else {

            throw new Error("The chatbot returned an empty response.");

        }

    } catch (error) {

        loadingMessage.remove();

        displayMessage(
            "Sorry, something went wrong: " + error.message,
            "bot-message"
        );

        console.error("Chatbot Error:", error);

    } finally {

        // Enable button again
        sendButton.disabled = false;

        userInput.focus();

    }

}


// ==========================================
// 7. SEND BUTTON EVENT
// ==========================================

sendButton.addEventListener("click", function () {

    sendMessage();

});


// ==========================================
// 8. ENTER KEY EVENT
// ==========================================

userInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

});


// ==========================================
// 9. CLICKABLE SUGGESTION CARDS
// ==========================================

const suggestionCards = document.querySelectorAll(
    ".suggestion-card"
);

const suggestionPrompts = [

    "Help me plan a travel budget for my next trip.",

    "I want to record and track my daily travel expenses.",

    "Help me monitor my travel spending and remaining budget.",

    "Convert a foreign currency into Malaysian Ringgit (MYR)."

];

suggestionCards.forEach((card, index) => {

    card.addEventListener("click", function () {

        if (suggestionPrompts[index]) {

            sendMessage(suggestionPrompts[index]);

        }

    });

});


// ==========================================
// 9. NEW CHAT BUTTON
// ==========================================

const newChatButton = document.querySelector(".new-chat-btn");

if (newChatButton) {

    newChatButton.addEventListener("click", function () {

        chatMessages.innerHTML = "";

        currentConversation = {
            id: Date.now(),
            title: "New Conversation",
            messages: [],
            pinned: false
        };

        renderConversationList();

    });

}

// ==========================================
// 10. SAVE CONVERSATIONS
// ==========================================
function saveConversation() {

    const index = chatHistory.findIndex(
        chat => chat.id === currentConversation.id
    );

    if (index === -1) {
        chatHistory.unshift(currentConversation);
    } else {
        chatHistory[index] = currentConversation;
    }

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chatHistory)
    );

    renderConversationList();
}


/* ==========================================
   11. RESIZABLE + COLLAPSIBLE SIDEBAR
========================================== */

const sidebar = document.querySelector(".sidebar");
const sidebarResizer = document.getElementById("sidebarResizer");
const sidebarToggle = document.getElementById("sidebarToggle");

const DEFAULT_SIDEBAR_WIDTH = 280;
const MIN_SIDEBAR_WIDTH = 180;
const MAX_SIDEBAR_WIDTH = 520;

let isResizing = false;

// ==========================
// COLLAPSE / EXPAND
// ==========================

sidebarToggle.addEventListener("click", function(event) {

    event.stopPropagation();

    sidebar.classList.toggle("collapsed");

    const collapsed =
        sidebar.classList.contains("collapsed");

    sidebarToggle.textContent =
        collapsed ? "▶" : "◀";

    localStorage.setItem(
        "travelMateSidebarCollapsed",
        collapsed
    );

});

// ==========================
// LOAD SIDEBAR WIDTH
// ==========================

function loadSidebarWidth() {

    const savedWidth = Number(
        localStorage.getItem(
            "travelMateSidebarWidth"
        )
    );

    const width =
        Number.isFinite(savedWidth) &&
            savedWidth >= MIN_SIDEBAR_WIDTH &&
            savedWidth <= MAX_SIDEBAR_WIDTH
            ? savedWidth
            : DEFAULT_SIDEBAR_WIDTH;

    document.documentElement.style.setProperty(
        "--sidebar-width",
        `${width}px`
    );

}

// ==========================
// LOAD COLLAPSED STATE
// ==========================

function loadSidebarState() {

    const collapsed =
        localStorage.getItem(
            "travelMateSidebarCollapsed"
        );

    if (collapsed === "true") {

        sidebar.classList.add("collapsed");

        sidebarToggle.textContent = "▶";

    } else {

        sidebarToggle.textContent = "◀";

    }
}

// ==========================
// START RESIZING
// ==========================

sidebarResizer.addEventListener(
    "pointerdown",
    function(event) {

        // Ignore drag if arrow button clicked

        if (
            event.target === sidebarToggle
        ) {
            return;
        }

        // Don't resize when collapsed

        if (
            sidebar.classList.contains(
                "collapsed"
            )
        ) {
            return;
        }

        if (window.innerWidth <= 550) {
            return;
        }

        isResizing = true;

        sidebarResizer.classList.add(
            "dragging"
        );

        document.body.classList.add(
            "sidebar-resizing"
        );

        sidebarResizer.setPointerCapture(
            event.pointerId
        );

        event.preventDefault();

    }
);

// ==========================
// RESIZE SIDEBAR
// ==========================

function resizeSidebar(event) {

    if (!isResizing) return;

    const newWidth = Math.min(
        MAX_SIDEBAR_WIDTH,
        Math.max(
            MIN_SIDEBAR_WIDTH,
            event.clientX
        )
    );

    document.documentElement.style.setProperty(
        "--sidebar-width",
        `${newWidth}px`
    );

    localStorage.setItem(
        "travelMateSidebarWidth",
        newWidth
    );

}

sidebarResizer.addEventListener(
    "pointermove",
    resizeSidebar
);

// ==========================
// STOP RESIZING
// ==========================

function stopResizing() {

    isResizing = false;

    sidebarResizer.classList.remove(
        "dragging"
    );

    document.body.classList.remove(
        "sidebar-resizing"
    );

}

sidebarResizer.addEventListener(
    "pointerup",
    stopResizing
);

sidebarResizer.addEventListener(
    "pointercancel",
    stopResizing
);

// ==========================
// DOUBLE CLICK = RESET WIDTH
// ==========================

sidebarResizer.addEventListener(
    "dblclick",
    function() {

        document.documentElement.style.setProperty(
            "--sidebar-width",
            `${DEFAULT_SIDEBAR_WIDTH}px`
        );

        localStorage.setItem(
            "travelMateSidebarWidth",
            DEFAULT_SIDEBAR_WIDTH
        );

    }
);

// ==========================
// KEYBOARD CONTROLS
// ==========================

sidebarResizer.addEventListener(
    "keydown",
    function(event) {

        let width = parseInt(
            getComputedStyle(
                sidebar
            ).width
        );

        if (event.key === "ArrowRight") {

            width += 10;

        } else if (
            event.key === "ArrowLeft"
        ) {

            width -= 10;

        } else if (
            event.key === "Home"
        ) {

            width =
                MIN_SIDEBAR_WIDTH;

        } else if (
            event.key === "End"
        ) {

            width =
                MAX_SIDEBAR_WIDTH;

        } else {

            return;

        }

        event.preventDefault();

        width = Math.min(
            MAX_SIDEBAR_WIDTH,
            Math.max(
                MIN_SIDEBAR_WIDTH,
                width
            )
        );

        document.documentElement.style.setProperty(
            "--sidebar-width",
            `${width}px`
        );

        localStorage.setItem(
            "travelMateSidebarWidth",
            width
        );

    }
);

// ==========================
// INITIALIZE
// ==========================

loadSidebarWidth();
loadSidebarState();

// ==========================================
// 12. DISPLAY CONVERSATION LIST
// ==========================================


function renderConversationList() {

    const list = document.getElementById("conversationList");
    const empty = document.getElementById("historyEmpty");

    if (!list || !empty) return;

    list.innerHTML = "";

    empty.style.display = "none";

    const filteredChats =
        chatHistory.filter(chat => {

            if (!conversationSearch) {
                return true;
            }

            const title =
                (chat.title || "")
                    .toLowerCase();

            const messageContent =
                chat.messages
                    .map(msg => msg.text)
                    .join(" ")
                    .toLowerCase();

            return (
                title.includes(conversationSearch) ||
                messageContent.includes(conversationSearch)
            );

        });

    const sortedChats =
        [...filteredChats].sort((a, b) => {

            if (a.pinned && !b.pinned) return -1;
            if (!a.pinned && b.pinned) return 1;

            return b.id - a.id;

        });

    if (sortedChats.length === 0) {
        empty.style.display = "block";

        empty.innerHTML =
            conversationSearch
                ? `
            <span>🔍</span>
            <p>No matching conversations found</p>
          `
                : `
            <span>💬</span>
            <p>No conversations yet</p>
          `;
        return;
    }

    sortedChats.forEach(chat => {

        const item = document.createElement("div");

        // Match the existing CSS class
        item.className = "history-item";

        if (String(chat.id) === String(currentConversation.id)) {
            item.classList.add("active");
        }

        if (chat.pinned) {
            item.classList.add("pinned");
        }

        // Conversation title
        const title = document.createElement("span");
        title.className = "history-title";
        title.textContent = chat.title || "Untitled Conversation";
        title.title = chat.title || "Untitled Conversation";

        // Action buttons
        const actions = document.createElement("div");
        actions.className = "history-actions";

        const pinButton = document.createElement("button");
        pinButton.className = "pin-btn";
        pinButton.dataset.id = chat.id;
        pinButton.type = "button";
        pinButton.title = chat.pinned ? "Unpin conversation" : "Pin conversation";
        pinButton.setAttribute("aria-label", pinButton.title);
        pinButton.textContent = chat.pinned ? "📌" : "📍";

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.dataset.id = chat.id;
        deleteButton.type = "button";
        deleteButton.title = "Delete conversation";
        deleteButton.setAttribute("aria-label", "Delete conversation");
        deleteButton.textContent = "🗑";

        actions.appendChild(pinButton);
        actions.appendChild(deleteButton);

        item.appendChild(title);
        item.appendChild(actions);

        item.addEventListener("click", () => {
            loadConversation(chat.id);
        });

        list.appendChild(item);

    });

    attachDeleteEvents();
    attachPinEvents();
}



// ==========================================
// 13. REOPEN PREVIOUS CONVERSATIONS
// ==========================================
function loadConversation(id) {

    const chat =
        chatHistory.find(
            c => String(c.id) === String(id)
        );

    if (!chat) return;

    currentConversation = chat;

    chatMessages.innerHTML = "";

    chat.messages.forEach(msg => {

        displayMessage(
            msg.text,
            msg.sender === "user"
                ? "user-message"
                : "bot-message"
        );

    });

    renderConversationList();
}

// ==========================================
// 14. DELETE CONVERSATIONS
// ==========================================

// Store conversation waiting to be deleted
let deleteConversationId = null;

// Modal elements
const deleteModal =
    document.getElementById("deleteModal");

const confirmDelete =
    document.getElementById("confirmDelete");

const cancelDelete =
    document.getElementById("cancelDelete");

// Open delete confirmation modal
function showDeleteModal(id) {

    deleteConversationId = id;

    deleteModal.classList.remove("hidden");
}

// Close modal
function closeDeleteModal() {

    deleteModal.classList.add("hidden");

    deleteConversationId = null;
}

// Confirm delete button
confirmDelete.addEventListener("click", function () {

    if (!deleteConversationId) return;

    chatHistory = chatHistory.filter(
        chat => String(chat.id) !== String(deleteConversationId)
    );

    // If current chat was deleted,
    // create a fresh conversation
    if (
        String(currentConversation.id) ===
        String(deleteConversationId)
    ) {

        chatMessages.innerHTML = "";

        currentConversation = {
            id: Date.now(),
            title: "New Conversation",
            messages: [],
            pinned: false
        };
    }

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chatHistory)
    );

    renderConversationList();

    closeDeleteModal();
});

// Cancel button
cancelDelete.addEventListener("click", function () {

    closeDeleteModal();
});

// Close when clicking outside modal
deleteModal.addEventListener("click", function (event) {

    if (event.target === deleteModal) {

        closeDeleteModal();

    }

});

// Attach delete button events to conversation list
function attachDeleteEvents() {

    document
        .querySelectorAll(".delete-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    showDeleteModal(
                        this.dataset.id
                    );

                }
            );

        });

}

// ==========================================
// 15. PIN MESSAGES
// ==========================================
function togglePin(id) {

    const chat = chatHistory.find(
        c => String(c.id) === String(id)
    );

    if (!chat) return;

    chat.pinned = !chat.pinned;

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chatHistory)
    );

    renderConversationList();
}

//ATTACH PIN BUTTON EVENTS TO CONVERSATION LIST
function attachPinEvents() {

    document
        .querySelectorAll(".pin-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    togglePin(
                        this.dataset.id
                    );

                }
            );

        });

}
// ==========================================
// 16. APPEARANCE SETTINGS
// ==========================================

const settingsButton = document.getElementById("settingsButton");
const settingsPanel = document.getElementById("settingsPanel");
const closeSettings = document.getElementById("closeSettings");
const resetSettings = document.getElementById("resetSettings");

const themeOptions = document.querySelectorAll(".theme-option");
const colourOptions = document.querySelectorAll(".colour-option");
const bubbleOptions = document.querySelectorAll(".bubble-option");

const defaultAppearance = {
    theme: "light",
    colour: "#6556CC",
    bubble: "rounded"
};

let appearance = { ...defaultAppearance };

// Open Appearance Settings

settingsButton.addEventListener("click", () => {

    settingsPanel.showModal();

});


// Close Appearance Settings

closeSettings.addEventListener("click", () => {

    settingsPanel.close();

});


// Close when clicking outside the panel

settingsPanel.addEventListener("click", (event) => {

    if (event.target === settingsPanel) {

        const rect = settingsPanel.getBoundingClientRect();

        if (
            event.clientX < rect.left ||
            event.clientX > rect.right ||
            event.clientY < rect.top ||
            event.clientY > rect.bottom
        ) {
            settingsPanel.close();
        }

    }

});

// Choose readable text colour

function getBubbleTextColour(hex) {

    const rgb = hex.replace("#", "")
        .match(/.{2}/g)
        .map(value => parseInt(value, 16) / 255)
        .map(value =>
            value <= 0.04045
                ? value / 12.92
                : Math.pow((value + 0.055) / 1.055, 2.4)
        );

    const luminance =
        0.2126 * rgb[0] +
        0.7152 * rgb[1] +
        0.0722 * rgb[2];

    const whiteContrast = 1.05 / (luminance + 0.05);
    const blackContrast = (luminance + 0.05) / 0.05;

    return whiteContrast >= blackContrast
        ? "#FFFFFF"
        : "#000000";
}

// Apply Appearance Settings

function applyAppearance() {

    document.body.dataset.theme = appearance.theme;

    document.body.dataset.bubble = appearance.bubble;

    document.documentElement.style.setProperty(
        "--user-bubble",
        appearance.colour
    );

    document.documentElement.style.setProperty(
        "--user-bubble-text",
        getBubbleTextColour(appearance.colour)
    );

    // Highlight selected theme

    themeOptions.forEach(button => {

        const selected =
            button.dataset.theme === appearance.theme;

        button.classList.toggle("active", selected);

        button.setAttribute("aria-pressed", selected);

    });

    // Highlight selected colour

    colourOptions.forEach(button => {

        const selected =
            button.dataset.colour === appearance.colour;

        button.classList.toggle("active", selected);

        button.setAttribute("aria-pressed", selected);

    });

    // Highlight selected bubble style

    bubbleOptions.forEach(button => {

        const selected =
            button.dataset.bubble === appearance.bubble;

        button.classList.toggle("active", selected);

        button.setAttribute("aria-pressed", selected);

    });

}
// Save Appearance Settings

function saveAppearance() {

    try {

        localStorage.setItem(
            "travelMateAppearance",
            JSON.stringify(appearance)
        );

    } catch (error) {

        console.warn("Unable to save appearance:", error);

    }

}


// Load Appearance Settings

function loadAppearance() {

    try {

        const saved = JSON.parse(
            localStorage.getItem("travelMateAppearance")
        );

        if (saved) {

            if (["light", "dark"].includes(saved.theme)) {
                appearance.theme = saved.theme;
            }

            if (
                Array.from(colourOptions).some(
                    button => button.dataset.colour === saved.colour
                )
            ) {
                appearance.colour = saved.colour;
            }

            if (
                Array.from(bubbleOptions).some(
                    button => button.dataset.bubble === saved.bubble
                )
            ) {
                appearance.bubble = saved.bubble;
            }

        }

    } catch (error) {

        console.warn("Unable to load appearance:", error);

    }

    applyAppearance();

}

// Theme Selection

themeOptions.forEach(button => {

    button.addEventListener("click", () => {

        appearance.theme = button.dataset.theme;

        applyAppearance();
        saveAppearance();

    });

});


// Colour Selection

colourOptions.forEach(button => {

    button.addEventListener("click", () => {

        appearance.colour = button.dataset.colour;

        applyAppearance();
        saveAppearance();

    });

});


// Bubble Style Selection

bubbleOptions.forEach(button => {

    button.addEventListener("click", () => {

        appearance.bubble = button.dataset.bubble;

        applyAppearance();
        saveAppearance();

    });

});


// Reset Appearance Settings

resetSettings.addEventListener("click", () => {

    appearance = { ...defaultAppearance };

    applyAppearance();
    saveAppearance();

});


// Initialize Appearance Settings

loadAppearance();
renderConversationList();

// ==========================================
// 12. WORKSPACE NAVIGATION
// ==========================================

const workspaceItems =
    document.querySelectorAll(
        ".workspace-nav .nav-item"
    );

workspaceItems.forEach((item) => {

    item.addEventListener("click", () => {

        workspaceItems.forEach((nav) => {

            nav.classList.remove("active");
            nav.removeAttribute("aria-current");

        });

        item.classList.add("active");
        item.setAttribute("aria-current", "true");

        const prompt = item.dataset.prompt;

        if (prompt) {

            userInput.value = prompt;

            userInput.dispatchEvent(
                new Event("input", { bubbles: true })
            );

        }

        userInput.focus();

    });

});
// ==========================================
// 13. SIDEBAR QUICK SETTINGS
// ==========================================

const sidebarSettingsButton =
    document.getElementById("sidebarSettingsButton");

sidebarSettingsButton.addEventListener("click", () => {

    document.getElementById("settingsButton").click();

});

const quickThemeButton =
    document.getElementById("quickThemeButton");

const quickThemeIcon =
    document.getElementById("quickThemeIcon");

const quickThemeText =
    document.getElementById("quickThemeText");


// Update Theme Button

function updateQuickThemeButton() {

    const isDark =
        document.body.dataset.theme === "dark";

    quickThemeIcon.textContent =
        isDark ? "☀" : "☾";

    quickThemeText.textContent =
        isDark ? "Light Mode" : "Dark Mode";

    quickThemeButton.setAttribute(
        "aria-label",
        isDark
            ? "Switch to light mode"
            : "Switch to dark mode"
    );

}


// Switch Theme Using Existing Settings

quickThemeButton.addEventListener("click", () => {

    const isDark =
        document.body.dataset.theme === "dark";

    const nextTheme =
        isDark ? "light" : "dark";

    const themeOption =
        document.querySelector(
            `.theme-option[data-theme="${nextTheme}"]`
        );

    if (themeOption) {

        themeOption.click();

    }

    updateQuickThemeButton();

});


// Synchronize With Appearance Settings

const sidebarThemeObserver =
    new MutationObserver(updateQuickThemeButton);

sidebarThemeObserver.observe(document.body, {

    attributes: true,

    attributeFilter: ["data-theme"]

});

updateQuickThemeButton();

// search history functionality

if (historySearch) {

    historySearch.addEventListener(
        "input",
        function () {

            conversationSearch =
                this.value
                    .trim()
                    .toLowerCase();

            renderConversationList();

        }
    );

}

const loginButton =
    document.getElementById("loginButton");

if (loginButton) {

    loginButton.addEventListener(
        "click",
        () => {

            window.location.href =
                "/login";

        }
    );

}