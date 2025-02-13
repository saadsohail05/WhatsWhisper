from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi import HTTPException
# import whisper  # Commented out as we're using Groq instead
import os
from Whisper_groq import client  # Import the configured Groq client
from zipenhancer_speechenhancement import enhance_audio
from fastapi.responses import Response

# Initializing FastAPI application  
app = FastAPI()

# Configuring upload directory for temporary file storage
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Whisper model initialization commented out
# model = whisper.load_model("small")

@app.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    enhance: bool = Form(default=False)
):

    # Log new request details
    print("\n=== New Transcription Request ===")
    print(f"📁 File: {audio.filename}")
    
    # Read the file content
    file_content = await audio.read()
    print(f"📊 Size: {len(file_content)} bytes")
    print(f"🎵 Enhancement requested: {enhance}")
    
    # Generate temporary file path
    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    enhanced_path = os.path.join(UPLOAD_FOLDER, "enhanced_" + audio.filename)
    
    try:
        # Save the file content
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # Apply enhancement if requested
        processing_path = file_path
        if enhance:
            print("✨ Enhancing audio...")
            enhance_audio(file_path, enhanced_path)
            processing_path = enhanced_path

        # Processing audio with Groq's Whisper API
        print("🔄 Processing audio...")
        with open(processing_path, "rb") as file:
            result = client.audio.transcriptions.create(
                file=(processing_path, file.read()),
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
            "detected_language": "en",
            "enhanced": enhance
        }
    
    except Exception as e:
        # Handle and log any errors
        print(f"❌ Error: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e
    
    finally:
        # Cleaning up temporary files
        for path in [file_path, enhanced_path]:
            if os.path.exists(path):
                os.remove(path)

@app.post("/enhance")
async def enhance_only(audio: UploadFile = File(...)):
    print("\n=== New Enhancement Request ===")
    print(f"📁 File: {audio.filename}")
    
    file_path = os.path.join(UPLOAD_FOLDER, f"original{os.path.splitext(audio.filename)[1]}")
    enhanced_path = os.path.join(UPLOAD_FOLDER, "enhanced.mp3")
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await audio.read())
        
        print("✨ Enhancing audio...")
        success = enhance_audio(file_path, enhanced_path)
        
        if not success or not os.path.exists(enhanced_path):
            raise HTTPException(status_code=500, detail="Enhancement failed")
        
        # Stream the file back
        return FileResponse(
            enhanced_path,
            media_type="audio/mpeg",
            filename="enhanced_audio.mp3"
        )
    
    except Exception as e:
        print(f"Error in enhance_only: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up the original file
        if os.path.exists(file_path):
            os.remove(file_path)
        # Let FileResponse handle the enhanced file cleanup

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
