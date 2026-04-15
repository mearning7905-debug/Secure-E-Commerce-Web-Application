// TOGGLE CHAT
function toggleChat() {
    const box = document.getElementById("chatbot-box");
    box.style.display = box.style.display === "flex" ? "none" : "flex";
}

// SEND MESSAGE
document.addEventListener("DOMContentLoaded", () => {

    const sendBtn = document.getElementById("send-btn");
    const input = document.getElementById("chat-input");

    if (!sendBtn) return;

    sendBtn.onclick = sendMessage;
    input.addEventListener("keypress", e => {
        if (e.key === "Enter") sendMessage();
    });

    function sendMessage() {
        const msg = input.value.trim();
        if (!msg) return;

        addMessage("You", msg);
        input.value = "";

        showTyping();

        setTimeout(() => {
            removeTyping();
            botReply(msg.toLowerCase());
        }, 1000);
    }
});

// ADD MESSAGE
function addMessage(sender, text) {
    const body = document.getElementById("chat-body");
    const div = document.createElement("div");
    div.classList.add("chat-message");

    if (sender === "You") {
        div.innerHTML = `<div class="user-msg">${text}</div>`;
    } else {
        div.innerHTML = `<div class="bot-msg">${text}</div>`;
    }

    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

// TYPING EFFECT
function showTyping() {
    const body = document.getElementById("chat-body");
    const typing = document.createElement("div");
    typing.id = "typing";
    typing.innerHTML = `<div class="bot-msg">SmartPay is typing...</div>`;
    body.appendChild(typing);
    body.scrollTop = body.scrollHeight;
}

function removeTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
}

// SMART BOT LOGIC
function botReply(message) {

    let reply = "Sorry 🤔 I didn’t understand that. Try asking about payment, OTP, fraud, price or transaction.";

    const greetings = ["hi", "hello", "hey"];
    const thanks = ["thank", "thanks"];
    const bye = ["bye", "goodbye"];

    // Greeting
    if (greetings.some(word => message.includes(word))) {
        reply = "Hello 👋 Welcome to SmartPay! How can I help you today?";
    }

    // OTP
    else if (message.includes("otp")) {
        reply = "🔐 OTP is valid for 30 seconds. Never share your OTP with anyone.";
    }

    // Fraud
    else if (message.includes("fraud") || message.includes("scam")) {
        reply = "🛡 Our AI system detects fraud using risk scoring & unusual activity tracking.";
    }

    // Blocked
    else if (message.includes("blocked") || message.includes("block")) {
        reply = "⚠ Your card may be blocked due to multiple failed OTP attempts.";
    }

    // Risk
    else if (message.includes("risk")) {
        reply = "📊 Risk score is calculated using amount, IP address & transaction behavior.";
    }

    // Transaction
    else if (message.includes("transaction")) {
        reply = "💳 Transaction ID is generated after successful OTP verification.";
    }

    // Price
    else if (message.includes("price")) {
        reply = "🛍 Product prices are displayed on the product page. Please check the details section.";
    }

    // Payment
    else if (message.includes("payment")) {
        reply = "💰 We support UPI, Credit Card, Debit Card and Net Banking.";
    }

    // Time
    else if (message.includes("time")) {
        const now = new Date();
        reply = "⏰ Current time is: " + now.toLocaleTimeString();
    }

    // Thanks
    else if (thanks.some(word => message.includes(word))) {
        reply = "You're welcome 😊 Happy to help!";
    }

    // Bye
    else if (bye.some(word => message.includes(word))) {
        reply = "Goodbye 👋 Have a great day!";
    }

    addMessage("Bot", reply);
}

// CLEAR CHAT
function clearChat() {
    document.getElementById("chat-body").innerHTML = "";
}