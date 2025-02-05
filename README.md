# 🎤💬 WhatsWhisper

In today’s fast-paced world, voice messages have become a popular way to communicate—offering speed and ease when typing is cumbersome—but they also present challenges in noisy or public environments where listening is not feasible, and for users with hearing impairments. WhatsWhisper addresses these issues by automatically converting WhatsApp voice messages into text using OpenAI’s Whisper model, thereby making communication more accessible and convenient, regardless of the setting.

## 🚀 Features

- Voice message transcription
- Multi-language support
- Easy setup process
- Automatic session management

## 🏗️ System Architecture

<div align="center">
  <img src="media/diagram.png" alt="WhatsWhisper System Architecture">
</div>

The diagram above illustrates the flow of data in WhatsWhisper:
1. User sends a voice message via WhatsApp
2. WhatsApp Bot (venom-bot) receives the message
3. Voice message is processed and sent to FastAPI server
4. Whisper model transcribes the audio
5. Transcribed text is sent back to the user

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- npm
- FFmpeg

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saadsohail05/WhatsWhisper.git
   cd WhatsWhisper
   ```

2. Run the setup script:
   ```bash
   python setup.py
   ```

3. Start the FastAPI server:
   ```bash
   python server.py
   ```

4. In a new terminal, start the WhatsApp bot:
   ```bash
   node whatsapp-bot.js
   ```

5. Scan the QR code that appears in the terminal with your WhatsApp to connect.

## 🔄 Reset WhatsApp Session

To reset the WhatsApp session, you have two options:

1. Using the reset flag (recommended):
   ```bash
   node whatsapp-bot.js --reset
   ```

2. Manual reset:
   ```bash
   rm -rf tokens/
   node whatsapp-bot.js
   ```

After resetting, a new QR code will appear in the terminal. Scan it with WhatsApp to establish a new session.

## 📖 Usage

1. Send a voice message to your WhatsApp number.
2. The bot will automatically transcribe the voice message and send the text back to you.

## 🛠️ Troubleshooting

- If the bot is not responding, make sure the FastAPI server and WhatsApp bot are running.
- Ensure you have scanned the QR code to connect the bot to your WhatsApp.
- Check the logs for any error messages.

## 🙏 Acknowledgments

- [venom-bot](https://github.com/orkestral/venom) - Thanks to the venom-bot team for their excellent WhatsApp Web automation library that powers this project's WhatsApp integration.
- [OpenAI Whisper](https://github.com/openai/whisper) - For providing the speech recognition model.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
