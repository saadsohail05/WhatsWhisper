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
                        `📅 *!schedule* - Schedule tasks from voice message\n` +
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

                if (messageContent === '!schedule') {
                    userStates.set(message.from, {
                        awaiting_audio: true,
                        schedule: true
                    });
                    await client.sendText(message.from, "🗣️ Send a voice message with your tasks!");
                    return;
                }
            }

            // Only process audio if user has requested transcription
            if (message.mimetype?.startsWith("audio") && userStates.get(message.from)?.awaiting_audio) {
                try {
                    const userState = userStates.get(message.from);
                    const buffer = Buffer.from(await client.decryptFile(message));
                    
                    // Save audio to temp file first
                    const tempPath = './temp_audio.ogg';
                    fs.writeFileSync(tempPath, buffer);
                    
                    const formData = new FormData();
                    formData.append("audio", fs.createReadStream(tempPath));

                    if (userState.schedule) {
                        try {
                            await client.sendText(message.from, "🎯 Processing your scheduling request...");
                            
                            // First get the transcription
                            const transcriptionResponse = await axios.post(
                                "http://localhost:5000/transcribe", 
                                formData
                            );

                            // Send the text for task scheduling with proper JSON content type
                            const scheduleResponse = await axios.post(
                                "http://localhost:5000/schedule_tasks",
                                { text: transcriptionResponse.data.transcript },
                                { headers: { 'Content-Type': 'application/json' } }
                            );

                            // Send back the scheduling results
                            await client.sendText(message.from, 
                                "📅 Task Scheduling Results:\n\n" + scheduleResponse.data.summary
                            );
                        } catch (error) {
                            console.error('Scheduling error:', error);
                            await client.sendText(message.from, "⚠️ Error scheduling tasks. Please try again.");
                        }
                    } else if (userState.enhance_only) {
                        try {
                            await client.sendText(message.from, "✨ Enhancing your audio...");
                            const response = await axios.post("http://localhost:5000/enhance", 
                                formData, 
                                { responseType: 'arraybuffer' }
                            );
                            
                            // Save the enhanced audio temporarily
                            const tempFilePath = './enhanced_audio.mp3';
                            fs.writeFileSync(tempFilePath, Buffer.from(response.data));
                            
                            // Send the audio file directly
                            await client.sendFile(
                                message.from,
                                tempFilePath,
                                'enhanced_audio.mp3',
                                'Here is your enhanced audio'
                            );
                            
                            // Clean up
                            fs.unlinkSync(tempFilePath);
                        } catch (error) {
                            console.error('Enhancement error:', error);
                            await client.sendText(message.from, "⚠️ Error enhancing the audio. Please try again.");
                        }
                    } else {
                        if (userState.enhance) {
                            formData.append("enhance", "true");
                        }

                        const response = await axios.post(
                            "http://localhost:5000/transcribe", 
                            formData
                        );

                        const enhancedPrefix = response.data.enhanced ? "✨ Enhanced and transcribed:\n" : "";
                        await client.sendText(message.from, `${enhancedPrefix}📝 ${response.data.transcript}`);
                    }

                    // Clean up temp file
                    fs.unlinkSync(tempPath);

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
