
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");

function sendMessage() {

    const message = userInput.value.trim();

    if (message === "") {
        return;
    }

    // Remove welcome message
    const welcome = document.querySelector(".welcome-message");

    if (welcome) {
        welcome.remove();
    }

    // Display user message
    const userMessage = document.createElement("div");
    userMessage.textContent = message;
    userMessage.style.cssText =
        "background:#5b5bd6;color:white;padding:12px 18px;" +
        "border-radius:12px;margin:15px 0 15px auto;" +
        "max-width:70%;width:fit-content;";

    chatMessages.appendChild(userMessage);

    // Temporary chatbot response
    const botMessage = document.createElement("div");
    botMessage.textContent = "Hello! This is a test response.";
    botMessage.style.cssText =
        "background:white;color:#333;padding:12px 18px;" +
        "border-radius:12px;margin:15px 0;max-width:70%;";

    chatMessages.appendChild(botMessage);

    // Clear input
    userInput.value = "";

    // Scroll to latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send button
sendButton.addEventListener("click", sendMessage);

// Press Enter to send
userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
