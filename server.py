from fastapi import FastAPI, File, UploadFile
# import whisper  # Commented out as we're using Groq instead
import os
from Whisper_groq import client  # Import the configured Groq client

# Initializing FastAPI application  
app = FastAPI()

# Configuring upload directory for temporary file storage
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Whisper model initialization commented out
# model = whisper.load_model("small")

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):

    # Log new request details
    print("\n=== New Transcription Request ===")
    print(f"📁 File: {audio.filename}")
    print(f"📊 Size: {len(await audio.read())} bytes")
    await audio.seek(0)  # Reset file pointer after reading
    
    # Generate temporary file path
    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    
    try:
        # Saving uploaded audio to temporary file
        with open(file_path, "wb") as buffer:
            buffer.write(await audio.read())

        # Processing audio with Groq's Whisper API
        print("🔄 Processing audio...")
        with open(file_path, "rb") as file:
            result = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                temperature=0.0
            )
        # result = model.transcribe(
        #     file_path,
        #     task="transcribe",
        #     fp16=False  
        # )
        # Logging success and return results
        print("📝 Transcription complete")
        
        return {
            "transcript": result.text,
            "detected_language": "en"
        }
    
    except Exception as e:
        # Handle and log any errors
        print(f"❌ Error: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e
    
    finally:
        # Cleaning up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
