// Select the chatbot container and buttons
var chatbotContainer = document.getElementById('chatbot-container');
var openButton = document.getElementById('open-chatbot-button');
var closeButton = document.getElementById('close-chatbot-button');

// Function to open the chatbot and hide the open button
function openChatbot() {
    chatbotContainer.style.display = 'block';
    openButton.style.display = 'none';
}

// Function to close the chatbot and show the open button
function closeChatbot() {
    chatbotContainer.style.display = 'none';
    openButton.style.display = 'block';
}

// Event listener to open the chatbot when the open button is clicked
openButton.addEventListener('click', openChatbot);

// Event listener to close the chatbot when the close button is clicked
closeButton.addEventListener('click', closeChatbot);
