from fastapi import FastAPI, File, UploadFile, Form, Body
from fastapi.responses import FileResponse
from fastapi import HTTPException
import os
from Whisper_groq import client
from zipenhancer_speechenhancement import enhance_audio
from fastapi.responses import Response
from phi3_5 import client as phi_client, process_tasks
from googlecalendar import GoogleCalendarAPI
from datetime import datetime
import json
from pydantic import BaseModel

# Initializing FastAPI application  
app = FastAPI()

# Configuring upload directory for temporary file storage
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Whisper model initialization commented out
# model = whisper.load_model("small")

# Initialize Google Calendar API at startup
print("\n=== Initializing Google Calendar API ===")
try:
    calendar_api = GoogleCalendarAPI()
    print("✅ Google Calendar API initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Google Calendar API: {str(e)}")
    print("Please ensure credentials.json is in the correct location")
    raise

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

class TranscriptionRequest(BaseModel):
    text: str

@app.post("/schedule_tasks")
async def schedule_tasks(request: TranscriptionRequest):
    try:
        print("\n=== New Scheduling Request ===")
        print(f"📝 Input text: {request.text}")
        
        try:
            tasks = process_tasks(request.text)
            if not tasks:
                return {"status": "warning", "summary": "No tasks could be extracted from the input"}
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"AI model error: {str(e)}"
            )

        scheduled_tasks = []
        for task in tasks:
            print(f"\n🔍 Task Details:")
            print(f"📌 Title: {task['title']}")
            print(f"📅 Date: {task['date']}")
            print(f"⏰ Start: {task['start_time']}")
            print(f"⏰ End: {task['end_time']}")
            print(f"📝 Description: {task['description']}")
            
            start_datetime = datetime.strptime(f"{task['date']} {task['start_time']}", "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(f"{task['date']} {task['end_time']}", "%Y-%m-%d %H:%M")
            duration = int((end_time - start_datetime).total_seconds() / 60)
            print(f"⏱️ Duration: {duration} minutes")
            
            scheduled_tasks.append(f"✅ {task['title']} on {task['date']} at {task['start_time']}")

        summary = "\n".join(scheduled_tasks)
        print("\n=== Final Summary ===")
        print(summary)
        return {"status": "success", "summary": summary}
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
