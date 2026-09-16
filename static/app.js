const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("chat-messages");

let currentAudio = null;


async function sendMessage() {

    const text = input.value.trim();

    if (!text) {
        return;
    }

    // Show user's message
    addMessage(text, "user");

    input.value = "";
    sendButton.disabled = true;

    try {

        console.log("Sending message to Pixel...");

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text
            })
        });

        if (!response.ok) {
            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        const data = await response.json();

        console.log("Pixel response:", data);

        // Display Pixel's response
        addMessage(
            data.response,
            "pixel"
        );

        // Play Pixel's voice
        if (data.audio) {

            console.log(
                "Playing Pixel audio:",
                data.audio
            );

            playAudio(data.audio);

        }

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        addMessage(
            "Error talking to Pixel. Check the terminal.",
            "pixel"
        );

    }

    sendButton.disabled = false;
    input.focus();

    scrollToBottom();
}


function playAudio(audioUrl) {

    // Stop previous audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }

    // Create new audio player
    currentAudio = new Audio(audioUrl);

    currentAudio.volume = 1.0;

    currentAudio.play()
        .then(() => {

            console.log(
                "Pixel audio started."
            );

        })
        .catch(error => {

            console.error(
                "Audio playback failed:",
                error
            );

        });
}


function addMessage(text, sender) {

    const message =
        document.createElement("div");

    message.classList.add(
        "message",
        sender
    );

    const bubble =
        document.createElement("div");

    bubble.classList.add(
        "bubble"
    );

    bubble.textContent = text;

    message.appendChild(
        bubble
    );

    messages.appendChild(
        message
    );

    scrollToBottom();
}


sendButton.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


function scrollToBottom() {

    messages.scrollTop =
        messages.scrollHeight;

}
