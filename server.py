from fastapi import FastAPI, File, UploadFile
import whisper
import os

# Initializing FastAPI application  
app = FastAPI()

# Configuring upload directory for temporary file storage
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initializing Whisper for speech recognition
model = whisper.load_model("small")

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

        # Processing audio with Whisper model
        print("🔄 Processing audio...")
        result = model.transcribe(
            file_path,
            task="transcribe",
            fp16=False  
        )
        
        # Loging success and return results
        print(f"✅ Language detected: {result['language']}")
        print(f"📝 Transcription complete")
        
        return {
            "transcript": result["text"],
            "detected_language": result["language"]
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
        print("=== Request Complete ===\n")

# Starting server when run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
