import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pymongo import MongoClient
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = mongo_client["road_hazards"]
hazard_reports = db["hazard_reports"]

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
AUTHORITY_EMAIL = os.getenv("AUTHORITY_EMAIL", "local.authority@example.com")

# Create router
router = APIRouter()

# Update the model at the top of the file
class HazardNotification(BaseModel):
    location: Dict[str, float]
    timestamp: datetime
    type: str
    severity: str
    image_url: Optional[str] = None
    hazard_count: Optional[int] = 1

# Modify the send_email_to_authority function to be asynchronous
async def send_email_to_authority(notification, report_id, nearby_count):
    """Send email notification to the authority about a hazard"""
    try:
        # Create a background task for sending the email
        asyncio.create_task(_send_email_async(notification, report_id, nearby_count))
        return True
    except Exception as e:
        print(f"Error scheduling email: {str(e)}")
        return False

# Create a new function that actually sends the email
async def _send_email_async(notification, report_id, nearby_count):
    """Asynchronously send email notification to the authority"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Email configuration
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", "587"))
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        authority_email = os.getenv("AUTHORITY_EMAIL")
        sender_email = os.getenv("SENDER_EMAIL")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = authority_email
        msg['Subject'] = f"Road Hazard Alert: {notification.type.capitalize()} Detected"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Road Hazard Alert</h2>
            <p><strong>Type:</strong> {notification.type.capitalize()}</p>
            <p><strong>Severity:</strong> {notification.severity}</p>
            <p><strong>Location:</strong> Lat: {notification.location['lat']}, Lng: {notification.location['lng']}</p>
            <p><strong>Time Detected:</strong> {notification.timestamp}</p>
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Nearby Reports:</strong> {nearby_count} similar hazards reported in this area in the last 30 days</p>
            <p>Please take appropriate action to address this road hazard.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Add image if available
        if notification.image_url:
            img_data = requests.get(notification.image_url).content
            image = MIMEImage(img_data)
            image.add_header('Content-ID', '<image1>')
            msg.attach(image)
        
        # Connect to server and send email
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: _send_smtp_email(
            email_host, email_port, email_user, email_password, 
            sender_email, authority_email, msg.as_string()
        ))
        
        print(f"Email notification sent for hazard report {report_id}")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        return False

def _send_smtp_email(host, port, user, password, sender, recipient, message):
    """Send email via SMTP - runs in executor to avoid blocking"""
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, recipient, message)

# Modify the send_hazard_notification endpoint to use the async email function
@router.post("/hazard-notification")
async def send_hazard_notification(notification: HazardNotification = Body(...)):
    try:
        # Only process pothole notifications (class 0)
        if notification.type.lower() != "pothole":
            return {"success": False, "message": "Only pothole hazards are reported to authorities"}
            
        # Check if we've already reported a hazard at this location
        # Using approximately 100 meter radius (0.001 degrees ≈ 111 meters)
        existing_report = hazard_reports.find_one({
            "location.lat": {"$gte": notification.location["lat"] - 0.001, "$lte": notification.location["lat"] + 0.001},
            "location.lng": {"$gte": notification.location["lng"] - 0.001, "$lte": notification.location["lng"] + 0.001},
        })
        
        # Count nearby hazards in a slightly larger area (500m radius)
        nearby_count = hazard_reports.count_documents({
            "location.lat": {"$gte": notification.location["lat"] - 0.005, "$lte": notification.location["lat"] + 0.005},
            "location.lng": {"$gte": notification.location["lng"] - 0.005, "$lte": notification.location["lng"] + 0.005},
            "timestamp": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)}
        })
        
        if existing_report:
            # If the report is less than 7 days old, don't send a new notification
            report_time = existing_report.get("timestamp", datetime.min)
            if isinstance(report_time, str):
                report_time = datetime.fromisoformat(report_time.replace('Z', '+00:00'))
            
            days_difference = (datetime.now() - report_time).days
            if days_difference < 7:
                return {"success": False, "message": "Recent report exists for this location"}
        
        # Store in MongoDB
        report_id = hazard_reports.insert_one({
            "location": notification.location,
            "timestamp": notification.timestamp,
            "type": notification.type,
            "severity": notification.severity,
            "image_url": notification.image_url,
            "status": "reported",
            "hazard_count": notification.hazard_count if hasattr(notification, 'hazard_count') else 1
        }).inserted_id
        
        # Send email notification with nearby count - now async
        await send_email_to_authority(notification, str(report_id), nearby_count)
        
        return {"success": True, "report_id": str(report_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process notification: {str(e)}")

@router.get("/hazard-reports")
async def get_hazard_reports():
    """Get all hazard reports from the database"""
    try:
        # Fetch all reports, sort by timestamp descending (newest first)
        reports = list(hazard_reports.find({}, {'_id': 0}).sort('timestamp', -1))
        
        # Convert ObjectId to string for JSON serialization
        for report in reports:
            if '_id' in report:
                report['_id'] = str(report['_id'])
            
            # Ensure timestamp is serializable
            if 'timestamp' in report and isinstance(report['timestamp'], datetime):
                report['timestamp'] = report['timestamp'].isoformat()
        
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hazard reports: {str(e)}")

@router.delete("/cleanup-resolved-hazards")
async def cleanup_resolved_hazards():
    """Remove hazard reports that are older than 7 days and have no recent reports in the same location"""
    try:
        # Get the cutoff date (7 days ago)
        cutoff_date = datetime.now() - timedelta(days=7)
        
        # Find all reports older than 7 days
        old_reports = list(hazard_reports.find({
            "timestamp": {"$lt": cutoff_date}
        }))
        
        removed_count = 0
        
        for report in old_reports:
            # For each old report, check if there's a newer report within 100m
            has_newer_report = hazard_reports.find_one({
                "location.lat": {"$gte": report["location"]["lat"] - 0.001, "$lte": report["location"]["lat"] + 0.001},
                "location.lng": {"$gte": report["location"]["lng"] - 0.001, "$lte": report["location"]["lng"] + 0.001},
                "timestamp": {"$gte": cutoff_date}
            })
            
            # If no newer report exists, remove this old report
            if not has_newer_report:
                hazard_reports.delete_one({"_id": report["_id"]})
                removed_count += 1
        
        return {
            "success": True, 
            "message": f"Removed {removed_count} resolved hazards",
            "removed_count": removed_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup resolved hazards: {str(e)}")

# Also add a specific endpoint to delete a single hazard by ID
@router.delete("/hazard-reports/{report_id}")
async def delete_hazard_report(report_id: str):
    """Delete a specific hazard report by ID"""
    try:
        from bson.objectid import ObjectId
        
        # Convert string ID to MongoDB ObjectId
        result = hazard_reports.delete_one({"_id": ObjectId(report_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Hazard report with ID {report_id} not found")
        
        return {"success": True, "message": f"Hazard report {report_id} deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete hazard report: {str(e)}")