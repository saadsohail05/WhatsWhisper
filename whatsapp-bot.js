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
    let messageCount = 0;  // Track total messages received

    // Message event listener
    client.onMessage(async message => {
        // Increment and log message details
        messageCount++;
        const senderNumber = message.from.split('@')[0];
        console.log('\n==================================');
        console.log(`📨 Message #${messageCount}`);
        console.log(`📱 From: +${senderNumber}`);
        console.log(`⏰ Time: ${new Date().toLocaleString()}`);

        // Handle only private messages, ignore group messages
        if (!message.isGroupMsg) {
            // Check if message is an audio message
            if (message.mimetype?.startsWith("audio")) {
                try {
                    console.log('🎵 Processing voice message...');
                    
                    // Extract audio from message
                    const buffer = await client.decryptFile(message);
                    
                    // Prepare audio data for API
                    const formData = new FormData();
                    formData.append("audio", buffer, {
                        filename: 'audio.ogg',
                        contentType: message.mimetype
                    });

                    // Send to FastAPI server for transcription
                    const response = await axios.post("http://localhost:5000/transcribe", 
                        formData, 
                        { headers: formData.getHeaders() }
                    );

                    // Log success and send transcription back to user
                    console.log('✅ Successfully transcribed');
                    console.log(`📤 Sending response to +${senderNumber}`);
                    await client.sendText(message.from, `📝 ${response.data.transcript}`);
                    
                } catch (error) {
                    // Handle and log any errors
                    console.error(`❌ Error for +${senderNumber}:`, error.message);
                    await client.sendText(message.from, "⚠️ Error transcribing the audio.");
                }
            } else {
                // Handle non-audio messages
                console.log('⚠️ Received non-audio message');
                await client.sendText(message.from, 
                    "🎤 Please send voice messages only. Text or other types of messages are not supported."
                );
            }
        }
        console.log('==================================\n');
    });
}
