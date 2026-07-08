const chatInput = document.querySelector(".chat-input input");
const chatButton = document.querySelector(".chat-input button");
const chatBody = document.querySelector(".chat-body");

function addMessage(text, type) {
  const message = document.createElement("div");
  message.classList.add("msg", type);
  message.textContent = text;
  chatBody.appendChild(message);
}

chatButton.addEventListener("click", () => {
  const userMessage = chatInput.value.trim();

  if (!userMessage) return;

  addMessage(userMessage, "msg-user");

  chatInput.value = "";

  setTimeout(() => {
    addMessage(
      "Thanks! In the final version, our AI will return personalized local recommendations here.",
      "msg-bot"
    );
  }, 600);
});