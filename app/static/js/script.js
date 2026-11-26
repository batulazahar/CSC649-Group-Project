
// ==========================================
// 1. GET HTML ELEMENTS
// ==========================================

const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");


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

        formatInlineText(
            paragraph.join(" "),
            p
        );

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

            if (!currentList ||
                currentList.tagName.toLowerCase() !== listType) {

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

    const content = document.createElement("div");

    content.classList.add("message-content", "typing-indicator");

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
// 10. NEW CHAT BUTTON
// ==========================================

const newChatButton = document.querySelector(".new-chat-btn");

if (newChatButton) {

    newChatButton.addEventListener("click", function () {

        // Reload the homepage to start a fresh conversation
        window.location.reload();

    });

}

// ==========================================
// 11. APPEARANCE SETTINGS
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