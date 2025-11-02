import os
import requests
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")


def get_zoom_access_token():
    """
    Get Zoom OAuth access token
    """
    if not all([ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET]):
        raise Exception("Zoom credentials not configured")
    
    # Encode credentials
    credentials = f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # Get token
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ZOOM_ACCOUNT_ID}"
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    
    return response.json()["access_token"]


def get_user_meetings(user_id="me", days_back=7):
    """
    Get list of meetings for a user
    """
    token = get_zoom_access_token()
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days_back)
    
    url = f"https://api.zoom.us/v2/users/{user_id}/recordings"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d")
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()


def get_meeting_transcript(meeting_id):
    """
    Get transcript for a specific meeting
    """
    token = get_zoom_access_token()
    
    # Get meeting recordings
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    # Find transcript file
    transcript_url = None
    for recording_file in data.get("recording_files", []):
        if recording_file.get("file_type") == "TRANSCRIPT":
            transcript_url = recording_file.get("download_url")
            break
    
    if not transcript_url:
        raise Exception("No transcript found for this meeting")
    
    # Download transcript
    transcript_response = requests.get(
        transcript_url,
        headers=headers
    )
    transcript_response.raise_for_status()
    
    return transcript_response.text


def list_recent_meetings_with_transcripts():
    """
    List recent meetings that have transcripts available
    """
    try:
        meetings_data = get_user_meetings()
        
        meetings_with_transcripts = []
        for meeting in meetings_data.get("meetings", []):
            # Check if meeting has transcript
            has_transcript = any(
                f.get("file_type") == "TRANSCRIPT" 
                for f in meeting.get("recording_files", [])
            )
            
            if has_transcript:
                meetings_with_transcripts.append({
                    "id": meeting.get("id"),
                    "uuid": meeting.get("uuid"),
                    "topic": meeting.get("topic"),
                    "start_time": meeting.get("start_time"),
                    "duration": meeting.get("duration"),
                    "participant_count": meeting.get("participant_count", 0)
                })
        
        return meetings_with_transcripts
    
    except Exception as e:
        print(f"Error fetching Zoom meetings: {e}")
        return []


def format_zoom_transcript(raw_transcript):
    """
    Format Zoom VTT transcript to readable text
    """
    # Zoom transcripts are in VTT format
    # Parse and format for readability
    
    lines = raw_transcript.split('\n')
    formatted_lines = []
    
    current_speaker = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        
        # Skip VTT headers and timestamps
        if line.startswith('WEBVTT') or '-->' in line or not line:
            continue
        
        # Check if line is a speaker name (usually ends with :)
        if ':' in line and len(line.split(':')[0]) < 30:
            # New speaker
            if current_speaker and current_text:
                formatted_lines.append(f"{current_speaker}: {' '.join(current_text)}")
            
            parts = line.split(':', 1)
            current_speaker = parts[0].strip()
            current_text = [parts[1].strip()] if len(parts) > 1 else []
        else:
            # Continue current speaker's text
            current_text.append(line)
    
    # Add last speaker
    if current_speaker and current_text:
        formatted_lines.append(f"{current_speaker}: {' '.join(current_text)}")
    
    return '\n\n'.join(formatted_lines)
