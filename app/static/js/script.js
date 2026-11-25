
// ==========================================
// 1. GET HTML ELEMENTS
// ==========================================

const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");


// ==========================================
// 2. DISPLAY CHAT MESSAGE
// ==========================================

function displayMessage(message, sender) {

    // Remove welcome message
    const welcomeMessage = document.querySelector(".welcome-message");

    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Create message container
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    // Create message text
    const messageText = document.createElement("p");

    messageText.textContent = message;

    messageDiv.appendChild(messageText);

    // Add message to chat area
    chatMessages.appendChild(messageDiv);

    // Scroll to latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;

}


// ==========================================
// 3. SEND MESSAGE TO FLASK
// ==========================================

async function sendMessage() {

    const message = userInput.value.trim();

    // Check empty message
    if (message === "") {
        return;
    }

    // Display user's message
    displayMessage(message, "user-message");

    // Clear input
    userInput.value = "";

    // Disable button while waiting
    sendButton.disabled = true;

    // Display loading message
    displayMessage("Thinking...", "bot-message");

    const loadingMessage = chatMessages.lastElementChild;

    try {

        // Send message to Flask API
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

        // Remove loading message
        loadingMessage.remove();

        // Check API response
        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );

        }

        // Display chatbot response
        displayMessage(data.response, "bot-message");

    } catch (error) {

        // Remove loading message
        loadingMessage.remove();

        displayMessage(
            "Sorry, something went wrong: " + error.message,
            "bot-message"
        );

    } finally {

        // Enable button again
        sendButton.disabled = false;

        userInput.focus();

    }

}


// ==========================================
// 4. SEND BUTTON EVENT
// ==========================================

sendButton.addEventListener("click", sendMessage);


// ==========================================
// 5. ENTER KEY EVENT
// ==========================================

userInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        sendMessage();

    }

});
