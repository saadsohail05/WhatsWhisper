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
                
                // Add help command
                if (messageContent === '!commands' || messageContent === '!help') {
                    const helpMessage = `🤖 *Available Commands:*\n\n` +
                        `📝 *!transcribe* - Transcribe an audio message\n` +
                        `✨ *!transcribe -e* - Enhance and transcribe an audio message\n` +
                        `🎵 *!enhance* - Enhance audio quality only\n` +
                        `❓ *!commands* or *!help* - Show this help message`;
                    
                    await client.sendText(message.from, helpMessage);
                    return;
                }

                if (messageContent === '!enhance') {
                    userStates.set(message.from, {
                        awaiting_audio: true,
                        enhance_only: true
                    });
                    await client.sendText(message.from, "🎵 Send an audio message and I'll enhance its quality!");
                    return;
                }

                if (messageContent === '!transcribe' || messageContent === '!transcribe -e') {
                    const enhanceAudio = messageContent.includes('-e');
                    userStates.set(message.from, {
                        awaiting_audio: true,
                        enhance: enhanceAudio
                    });
                    
                    const responseText = enhanceAudio 
                        ? "🎤 Send any voice message and I'll enhance and transcribe it!"
                        : "🎤 Send any voice message and I'll transcribe it for you!";
                    
                    await client.sendText(message.from, responseText);
                    return;
                }
            }

            // Only process audio if user has requested transcription
            if (message.mimetype?.startsWith("audio") && userStates.get(message.from)?.awaiting_audio) {
                try {
                    const userState = userStates.get(message.from);
                    const buffer = await client.decryptFile(message);
                    const formData = new FormData();
                    formData.append("audio", buffer, {
                        filename: 'audio.ogg',
                        contentType: message.mimetype
                    });

                    if (userState.enhance_only) {
                        try {
                            await client.sendText(message.from, "✨ Enhancing your audio...");
                            const response = await axios.post("http://localhost:5000/enhance", 
                                formData, 
                                { 
                                    headers: formData.getHeaders(),
                                    responseType: 'arraybuffer'
                                }
                            );
                            
                            // Save the enhanced audio temporarily
                            const tempFilePath = './enhanced_audio.mp3';
                            fs.writeFileSync(tempFilePath, Buffer.from(response.data));
                            
                            // Send the enhanced audio file
                            await client.sendVoiceBase64(
                                message.from,
                                response.data.toString('base64'),
                                'enhanced_audio'
                            );
                            
                            // Clean up the temporary file
                            fs.unlinkSync(tempFilePath);
                            
                            await client.sendText(message.from, "✨ Here's your enhanced audio!");
                        } catch (error) {
                            console.error('Enhancement error:', error);
                            await client.sendText(message.from, "⚠️ Error enhancing the audio. Please try again.");
                        }
                    } else {
                        formData.append("enhance", userState.enhance);

                        const response = await axios.post("http://localhost:5000/transcribe", 
                            formData, 
                            { headers: formData.getHeaders() }
                        );

                        const enhancedPrefix = response.data.enhanced ? "✨ Enhanced and transcribed:\n" : "";
                        await client.sendText(message.from, `${enhancedPrefix}📝 ${response.data.transcript}`);
                    }
                } catch (error) {
                    console.error('Processing error:', error.message);
                    await client.sendText(message.from, "⚠️ Error processing the audio.");
                } finally {
                    userStates.delete(message.from);
                }
            }
        }
    });
}
