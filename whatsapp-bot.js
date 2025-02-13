// Required dependencies
const venom = require('venom-bot');
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

// Reset function: Clears existing WhatsApp session
function resetSession() {
    const tokensPath = './tokens';
    if (fs.existsSync(tokensPath)) {
        fs.rmSync(tokensPath, { recursive: true, force: true });
        console.log('🔄 Session reset! Start the bot again to scan new QR code.');
        process.exit(0);
    }
}

// Checks for reset command
if (process.argv.includes('--reset')) {
    resetSession();
}

// Initializes directory needed 
['./tokens'].forEach(dir => {  
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

// Configures and initializes WhatsApp bot
// Using venom-bot for WhatsApp Web automation
venom
    .create({
        session: 'whatsapp-session',    // Session name
        multidevice: true,              // Enable multi-device support
        folderNameToken: 'tokens',      // Token storage location
        createPathFileToken: true,      // Create token path if doesn't exist
        headless: true,                 // Run in headless mode
        useChrome: false,               // Using Chromium instead of Chrome
        debug: false,                   // Disable debug logs
        logQR: true                     // Show QR in console
    })
    .then((client) => start(client))
    .catch((error) => {
        console.error('Error creating client:', error);
    });

// Main bot function that handles all message events
function start(client) {
    console.log("🤖 WhatsApp Bot Started...");
    const userStates = new Map();

    // Message event listener
    client.onMessage(async message => {
        // Handle only private messages, ignore group messages
        if (!message.isGroupMsg) {
            // Check if message has a body before processing commands
            if (message.body) {
                const messageContent = message.body.toLowerCase();
                if (messageContent === '!transcribe') {
                    userStates.set(message.from, 'awaiting_audio');
                    await client.sendText(message.from, 
                        "🎤 Send any voice message and I'll transcribe it for you!"
                    );
                    return;
                }
            }

            // Only process audio if user has requested transcription
            if (message.mimetype?.startsWith("audio") && userStates.get(message.from)) {
                try {
                    const buffer = await client.decryptFile(message);
                    const formData = new FormData();
                    formData.append("audio", buffer, {
                        filename: 'audio.ogg',
                        contentType: message.mimetype
                    });

                    const response = await axios.post("http://localhost:5000/transcribe", 
                        formData, 
                        { headers: formData.getHeaders() }
                    );

                    await client.sendText(message.from, `📝 ${response.data.transcript}`);
                } catch (error) {
                    console.error('Transcription error:', error.message);
                    await client.sendText(message.from, "⚠️ Error transcribing the audio.");
                } finally {
                    userStates.delete(message.from);
                }
            }
        }
    });
}
