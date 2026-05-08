from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

# Import email service
from email_service import send_confirmation_email, send_reminder_email


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
# DB_NAME is set by Kubernetes in production, use default for local dev
db_name = os.environ.get('DB_NAME', 'test_database')
db = client[db_name]

# Initialize scheduler for reminder emails
scheduler = BackgroundScheduler()
scheduler.start()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Discount Settings Model - PER SERVICE
class ServiceDiscount(BaseModel):
    service_name: str  # e.g., "Tradicionalna tajlandska masaža - 60 min"
    discount_percentage: int = Field(default=0, ge=0, le=100)  # 0, 5, 10, 15, etc.

class AllDiscounts(BaseModel):
    discounts: dict  # service_name -> discount_percentage mapping

# Booking Models
class AppointmentBooking(BaseModel):
    client_first_name: str
    client_last_name: str
    client_phone: str
    client_email: str
    appointment_date: str
    start_time: str  # ISO datetime format
    service_id: str
    therapist_id: str = ""  # Empty string by default
    notes: Optional[str] = ""
    language: Optional[str] = "sr"  # Default to Serbian
    service_name: Optional[str] = ""  # For email display
    duration_type: Optional[int] = None  # For couples massage total duration
    duration: Optional[int] = None  # Service duration in minutes

# Couple Booking Model
# Snapshot model for service pricing
class ServiceSnapshot(BaseModel):
    service_id: str
    service_code: str
    original_price: float
    discount_percentage: float
    final_price: float
    duration: int

class CoupleBooking(BaseModel):
    client_first_name: str
    client_last_name: str
    client_phone: str
    client_email: Optional[str] = ""
    start_time: str  # ISO datetime format
    duration_type: int  # 60, 90, or 120 minutes per person
    person1_services: Optional[List[str]] = None  # DEPRECATED - use snapshots instead
    person2_services: Optional[List[str]] = None  # DEPRECATED - use snapshots instead
    discount_couples_massage: float = 0.0  # NO discount - already applied in frontend
    language: Optional[str] = "sr"  # Default to Serbian
    
    # NEW: Snapshot system (Variant 1)
    person1_snapshots: Optional[List[ServiceSnapshot]] = None  # Complete snapshot for person 1
    person2_snapshots: Optional[List[ServiceSnapshot]] = None  # Complete snapshot for person 2

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.get("/discounts")
async def get_all_discounts():
    """Get all service discounts"""
    try:
        settings = await db.settings.find_one({"_id": "service_discounts"})
        if settings and "discounts" in settings:
            return {"discounts": settings["discounts"]}
        else:
            # Default: no discounts
            return {"discounts": {}}
    except Exception as e:
        logger.error(f"Error fetching discounts: {e}")
        return {"discounts": {}}

@api_router.post("/discount/set")
async def set_service_discount(discount: ServiceDiscount):
    """Set discount for a specific service (0, 5, 10, 15)"""
    try:
        # Get current discounts
        settings = await db.settings.find_one({"_id": "service_discounts"})
        discounts = settings.get("discounts", {}) if settings else {}
        
        # Update discount for this service
        discounts[discount.service_name] = discount.discount_percentage
        
        # Save back to database
        await db.settings.update_one(
            {"_id": "service_discounts"},
            {"$set": {"discounts": discounts}},
            upsert=True
        )
        
        logger.info(f"✅ Discount for '{discount.service_name}' set to {discount.discount_percentage}%")
        return {"success": True, "service_name": discount.service_name, "discount_percentage": discount.discount_percentage}
    except Exception as e:
        logger.error(f"Error setting discount: {e}")
        raise HTTPException(status_code=500, detail="Failed to set discount")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# Health Check Endpoint
@api_router.get("/health")
async def health_check():
    """
    Health check endpoint - verifies local backend AND external booking API connectivity
    """
    booking_api_url = os.environ.get('BOOKING_API_URL', '')
    external_status = "unknown"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{booking_api_url}/api/services")
            external_status = "connected" if response.status_code == 200 else f"error:{response.status_code}"
    except Exception as e:
        external_status = f"error:{str(e)[:50]}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "booking_api": booking_api_url,
        "booking_api_status": external_status
    }

# Helper function to extract service code (base name without prefix and duration)
def extract_service_code(service_name: str) -> str:
    """
    Extract unique service code from service name.
    Examples:
    - "[PAROVI] Aroma terapija - 90 min" -> "Aroma terapija"
    - "Aroma terapija - 90 min" -> "Aroma terapija"
    - "Masaža stopala - 60 min" -> "Masaža stopala"
    """
    # Remove [PAROVI] prefix
    name = service_name.replace('[PAROVI]', '').strip()
    
    # Remove duration suffix (e.g., " - 60 min", " - 90 min")
    import re
    name = re.sub(r'\s*-\s*\d+\s*min\s*$', '', name, flags=re.IGNORECASE)
    
    return name.strip()

# Services Proxy Endpoint with Single Discount Logic
@api_router.get("/services")
async def get_services():
    """
    Proxy endpoint to fetch services from booking system with intelligent discount handling.
    
    BUSINESS LOGIC:
    - Each service gets ONLY ONE discount applied (highest available)
    - If same massage exists in multiple categories with different discounts, 
      the highest discount is selected
    - Backend calculates final price with discount
    - Frontend displays values from backend (no frontend calculations)
    """
    booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{booking_api_url}/api/services")
            response.raise_for_status()
            raw_services = response.json()
            
            # Group services by service_code to find highest discount
            services_by_code = {}
            for service in raw_services:
                service_code = extract_service_code(service['name'])
                
                if service_code not in services_by_code:
                    services_by_code[service_code] = []
                
                services_by_code[service_code].append(service)
            
            # Find highest discount for each service code
            max_discounts = {}
            for service_code, services in services_by_code.items():
                max_discount = max(s.get('discount_percentage', 0) for s in services)
                max_discounts[service_code] = max_discount
            
            # Apply highest discount to each service
            processed_services = []
            for service in raw_services:
                service_code = extract_service_code(service['name'])
                highest_discount = max_discounts.get(service_code, 0)
                
                # Add service_code to service for frontend reference
                service['service_code'] = service_code
                
                # Override discount with highest available
                service['discount_percentage'] = highest_discount
                
                # CRITICAL: DO NOT calculate discount - recepcija is source of truth!
                # Just pass through the values from booking system
                service['discounted_price'] = service['price']  # Recepcija već diskontovala
                service['original_price'] = service['price']  # Čuva vrednost kako je recepcija postavila
                
                processed_services.append(service)
            
            logger.info(f"✅ Processed {len(processed_services)} services with single discount logic")
            return processed_services
            
    except Exception as e:
        logger.error(f"Error fetching services from booking system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")

# NEW ENDPOINT: Couples Services Only
@api_router.get("/services/couples/list")
async def get_couples_services():
    """
    Returns ONLY couple services (services from "Kartica Masaza za parove" category).
    
    CRITICAL: This endpoint is used EXCLUSIVELY by "Masaža za parove" card on website.
    - Filters only services with category = "Kartica Masaza za parove"
    - Returns services with [PAROVI] prefix
    - Applies highest discount logic per service_code
    - NO mixing with single services
    """
    booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{booking_api_url}/api/services")
            response.raise_for_status()
            raw_services = response.json()
            
            # CRITICAL FILTER: Only "Kartica Masaza za parove" category (INDIVIDUAL [PAROVI] masaže za dropdown)
            couples_only = [s for s in raw_services if s.get('category') == 'Kartica Masaza za parove']
            
            logger.info(f"🔍 DEBUG - Total services from external API: {len(raw_services)}")
            logger.info(f"🔍 DEBUG - Categories in response: {set(s.get('category') for s in raw_services)}")
            logger.info(f"🔍 DEBUG - Filtered 'Kartica Masaza za parove': {len(couples_only)}")
            
            logger.info(f"🔍 Filtered couples services: {len(couples_only)} out of {len(raw_services)} total services")
            
            # Group by service_code to find highest discount (within couples category only)
            services_by_code = {}
            for service in couples_only:
                service_code = extract_service_code(service['name'])
                
                if service_code not in services_by_code:
                    services_by_code[service_code] = []
                
                services_by_code[service_code].append(service)
            
            # Find highest discount for each service code (within couples only)
            max_discounts = {}
            for service_code, services in services_by_code.items():
                max_discount = max(s.get('discount_percentage', 0) for s in services)
                max_discounts[service_code] = max_discount
            
            # Process couples services
            processed_services = []
            for service in couples_only:
                service_code = extract_service_code(service['name'])
                highest_discount = max_discounts.get(service_code, 0)
                
                # Add metadata
                service['service_code'] = service_code
                service['is_couple'] = True  # Mark as couple service
                service['discount_percentage'] = highest_discount
                
                # CRITICAL: Recepcija sends ALREADY DISCOUNTED prices!
                # service['price'] from recepcija = final price AFTER discount
                # We need to calculate ORIGINAL price back from discounted price
                final_price = service['price']  # This is AFTER discount from recepcija
                
                if highest_discount > 0:
                    # Calculate original price: original = final / (1 - discount/100)
                    original_price = final_price / (1 - highest_discount / 100)
                else:
                    original_price = final_price
                
                service['final_price'] = final_price  # Price AFTER discount (from recepcija)
                service['original_price'] = original_price  # Calculated ORIGINAL price
                service['discounted_price'] = final_price  # Same as final_price (for backwards compatibility)
                
                processed_services.append(service)
            
            logger.info(f"✅ Returning {len(processed_services)} COUPLES services (isolated from single)")
            return processed_services
            
    except Exception as e:
        logger.error(f"Error fetching couples services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch couples services: {str(e)}")

# NEW ENDPOINT: Couples Individual Services (for dropdown selection)
@api_router.get("/services/couples/individual")
async def get_couples_individual_services():
    """
    Returns INDIVIDUAL [PAROVI] masaže for dropdown selection.
    
    This endpoint provides services from "Kartica Masaza za parove" category
    which have [PAROVI] prefix and are used for Osoba 1 / Osoba 2 selection.
    """
    booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{booking_api_url}/api/services")
            response.raise_for_status()
            raw_services = response.json()
            
            # CRITICAL FILTER: Only "Kartica Masaza za parove" category
            individual_couples = [s for s in raw_services if s.get('category') == 'Kartica Masaza za parove']
            
            logger.info(f"✅ Returning {len(individual_couples)} INDIVIDUAL [PAROVI] services for dropdown")
            
            # Process and add metadata
            processed = []
            for service in individual_couples:
                # Use metadata if available (source of truth for prices)
                metadata = service.get('metadata', {})
                if metadata and 'original_price' in metadata and 'final_price' in metadata:
                    service['original_price'] = metadata['original_price']
                    service['final_price'] = metadata['final_price']
                else:
                    service['original_price'] = service['price']
                    service['final_price'] = service['price']
                
                processed.append(service)
            
            return processed
            
    except Exception as e:
        logger.error(f"Error fetching couples individual services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch couples individual services: {str(e)}")

# NEW ENDPOINT: Single Services Only
@api_router.get("/services/single/list")
async def get_single_services():
    """
    Returns ONLY single services (services from "Obicne masaze" category).
    
    Used for regular massage bookings.
    - Filters only services with category = "Obicne masaze"
    - NO couple services included
    """
    booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{booking_api_url}/api/services")
            response.raise_for_status()
            raw_services = response.json()
            
            # CRITICAL FILTER: Only "Obicne masaze" category
            single_only = [s for s in raw_services if s.get('category') == 'Obicne masaze']
            
            logger.info(f"🔍 Filtered single services: {len(single_only)} out of {len(raw_services)} total services")
            
            # Process single services
            processed_services = []
            for service in single_only:
                service_code = extract_service_code(service['name'])
                
                # Add metadata
                service['service_code'] = service_code
                service['is_couple'] = False  # Mark as single service
                
                # CRITICAL FIX: Eksterni API ima BUG - dodaje pogrešan final_price sa duplim popustom!
                # metadata.final_price je PRAVI source of truth!
                metadata = service.get('metadata', {})
                if metadata and 'original_price' in metadata and 'final_price' in metadata:
                    # PREPISI POGREŠAN final_price sa PRAVIM iz metadata
                    service['original_price'] = metadata['original_price']
                    service['final_price'] = metadata['final_price']  # OVERWRITE bug from external API!
                    service['discounted_price'] = metadata['final_price']  # Backwards compatibility
                    
                    # DODATNO: Log razliku između metadata i root-level final_price (ako postoji bug)
                    if 'final_price' in service and service['final_price'] != metadata['final_price']:
                        logger.warning(f"⚠️ FIXING double discount bug: {service['name']} - metadata.final_price={metadata['final_price']}, wrong root final_price was={service['final_price']}")
                        service['final_price'] = metadata['final_price']  # Force fix
                else:
                    # Fallback ako metadata ne postoji - koristi price vrednost
                    service['original_price'] = service['price']
                    service['final_price'] = service['price']
                    service['discounted_price'] = service['price']
                
                processed_services.append(service)
            
            logger.info(f"✅ Returning {len(processed_services)} SINGLE services")
            return processed_services
            
    except Exception as e:
        logger.error(f"Error fetching single services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch single services: {str(e)}")

# Booking Proxy Endpoint
@api_router.post("/book-appointment")
async def book_appointment(booking: AppointmentBooking, background_tasks: BackgroundTasks):
    """
    Proxy endpoint to forward booking requests to spa booking system
    Automatically rotates through web slot therapists to allow multiple simultaneous bookings
    Sends confirmation email immediately and schedules reminder 2h before appointment
    Special handling for "Masaža za parove" with custom duration and discounted price in notes
    """
    try:
        # Log the booking data for debugging
        logger.info(f"📌 BOOKING REQUEST - Service ID: {booking.service_id}, Service Name: {booking.service_name}, Client: {booking.client_first_name} {booking.client_last_name}, Time: {booking.start_time}, Language: {booking.language}")
        
        # Special handling for "Masaža za parove" - calculate total duration from notes
        is_couples_massage = "Masaža za parove" in (booking.service_name or "")
        couples_total_duration = None
        couples_final_price = None
        
        if is_couples_massage and booking.notes:
            # Extract total duration and final price from notes
            # Notes format includes "UKUPNA CENA SA POPUSTOM: X,XXX RSD"
            import re
            price_match = re.search(r'UKUPNA CENA SA POPUSTOM:\s*([\d,]+)\s*RSD', booking.notes)
            if price_match:
                couples_final_price = price_match.group(1).replace(',', '')
                logger.info(f"💰 Couples massage final price: {couples_final_price} RSD")
            
            # Calculate duration from notes (count massage durations)
            duration_matches = re.findall(r'\((\d+) min\)', booking.notes)
            if duration_matches:
                couples_total_duration = sum(int(d) for d in duration_matches)
                logger.info(f"⏱️ Couples massage total duration: {couples_total_duration} min")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
            
            # KRITIČNO: Terapeut NIJE OBAVEZAN - recepcionar će ga manuelno dodati u recepciji
            # NE pokušavaj da automatski dodeliš terapeuta!
            logger.info("📋 Booking WITHOUT therapist - manual assignment in reception")
            
            # Prepare booking payload
            booking_payload = booking.model_dump()
            
            # UVEK ukloni therapist_id - recepcionar će ga manuelno dodati
            if 'therapist_id' in booking_payload:
                logger.info("📋 Removing therapist_id from payload (manual assignment required)")
                booking_payload.pop('therapist_id', None)
            
            booking_result = None
            
            # For couples massage, enhance notes with total duration and final price info
            if is_couples_massage and couples_total_duration and couples_final_price:
                original_notes = booking_payload['notes']
                
                # OVERRIDE service_name to show actual total duration
                booking_payload['service_name'] = f"Masaža za parove - {couples_total_duration} min"
                
                # Set duration_type to total duration (120, 180, or 240)
                booking_payload['duration_type'] = couples_total_duration
                
                booking_payload['notes'] = (
                    f"⭐ MASAŽA ZA PAROVE - UKUPNO TRAJANJE: {couples_total_duration} min ⭐\n"
                    f"💰 FINALNA CENA SA POPUSTOM (-15%): {couples_final_price} RSD 💰\n\n"
                    f"DETALJI:\n{original_notes}"
                )
                logger.info(f"📝 Enhanced couples massage: service_name={booking_payload['service_name']}, duration_type={couples_total_duration}, price: {couples_final_price} RSD")
            
            # Send booking request WITHOUT therapist_id - manual assignment in reception
            logger.info(f"📤 Sending booking request WITHOUT therapist_id to {booking_api_url}/api/appointments")
            response = await client.post(
                f'{booking_api_url}/api/appointments',
                json=booking_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            # If booking succeeds
            if response.status_code in [200, 201]:
                logger.info(f"✅ Booking successful - therapist will be assigned manually in reception")
                booking_result = response.json()
            else:
                # Booking failed
                error_text = response.text
                logger.error(f"❌ Booking failed: {response.status_code} - {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Booking failed: {error_text}"
                )
            
            # Send confirmation email immediately (in background)
            background_tasks.add_task(
                send_confirmation_email,
                client_email=booking.client_email,
                client_name=f"{booking.client_first_name} {booking.client_last_name}",
                client_phone=booking.client_phone,
                service_name=booking.service_name or "Tretman",
                appointment_datetime=booking.start_time,
                language=booking.language or 'sr'
            )
            logger.info(f"📧 Confirmation email scheduled for {booking.client_email}")
            
            # Schedule reminder email 2 hours before appointment
            try:
                appointment_dt = datetime.fromisoformat(booking.start_time.replace('Z', ''))
                # Make appointment_dt timezone-aware if it's naive
                if appointment_dt.tzinfo is None:
                    appointment_dt = appointment_dt.replace(tzinfo=timezone.utc)
                
                reminder_time = appointment_dt - timedelta(hours=2)
                
                # Only schedule if reminder time is in the future
                now = datetime.now(timezone.utc)
                if reminder_time > now:
                    scheduler.add_job(
                        send_reminder_email,
                        trigger=DateTrigger(run_date=reminder_time),
                        args=[
                            booking.client_email,
                            f"{booking.client_first_name} {booking.client_last_name}",
                            booking.service_name or "Tretman",
                            booking.start_time,
                            booking.language or 'sr'
                        ],
                        id=f"reminder_{booking_result['id']}",
                        replace_existing=True
                    )
                    logger.info(f"⏰ Reminder email scheduled for {reminder_time} (2h before appointment)")
                else:
                    logger.info("⚠️ Appointment too soon - no reminder scheduled")
                    
            except Exception as e:
                logger.error(f"Failed to schedule reminder: {e}")
            
            return booking_result
            
    except httpx.RequestError as e:
        logger.error(f"Booking API request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Booking service unavailable"
        )
            
    except httpx.RequestError as e:
        logger.error(f"Booking API request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Booking service unavailable"
        )

# Couple Booking Endpoint
@api_router.post("/book-couple-appointment")
async def book_couple_appointment(booking: CoupleBooking, background_tasks: BackgroundTasks):
    """
    Proxy endpoint for couple massage bookings
    Forwards to booking system's /api/appointments/couple endpoint
    """
    try:
        logger.info(f"📌 COUPLE BOOKING REQUEST - Client: {booking.client_first_name} {booking.client_last_name}, Duration: {booking.duration_type}min per person")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get available therapists
            booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
            therapists_response = await client.get(f'{booking_api_url}/api/therapists')
            
            if therapists_response.status_code != 200:
                logger.error(f"Failed to get therapists: {therapists_response.status_code}")
                raise HTTPException(status_code=503, detail="Cannot access therapist list")
            
            therapists = therapists_response.json()
            # Support both "Web Slot" and "Web Rezervacije" therapist names
            web_slot_therapists = [t for t in therapists if (t.get('name', '').startswith('Web Slot') or t.get('name', '').startswith('Web Rezervacije')) and t.get('is_active', True)]
            
            if not web_slot_therapists:
                logger.error("No Web Slot or Web Rezervacije therapists found")
                raise HTTPException(status_code=500, detail="Web booking system not configured")
            
            logger.info(f"Found {len(web_slot_therapists)} web booking therapists")
            
            # Check if frontend sent snapshots (Variant 1)
            if booking.person1_snapshots and booking.person2_snapshots:
                logger.info("📸 Using snapshot from websajt (Variant 1)")
                
                # Calculate total from snapshots
                total_original = sum(s.original_price for s in booking.person1_snapshots) + sum(s.original_price for s in booking.person2_snapshots)
                total_final = sum(s.final_price for s in booking.person1_snapshots) + sum(s.final_price for s in booking.person2_snapshots)
                
                # CRITICAL: Discount is ALREADY applied in final_price!
                # We must send 0% to recepcija so it doesn't apply discount again!
                discount_percent = 0.0  # ALWAYS 0 when using snapshots - cene su već diskontovane!
                
                logger.info(f"💰 Snapshot prices - Original: {total_original} RSD, Final: {total_final} RSD")
                logger.info(f"⚠️  Sending discount_couples_massage: 0% (cene već diskontovane u snapshots)")
            else:
                logger.warning("⚙️ Websajt didn't send snapshot - using fallback with service IDs")
                discount_percent = booking.discount_couples_massage
            
            # Try each Web Slot therapist until one is available
            booking_result = None
            for therapist in web_slot_therapists:
                # Prepare booking payload for couple endpoint
                couple_payload = {
                    "client_first_name": booking.client_first_name,
                    "client_last_name": booking.client_last_name,
                    "client_phone": booking.client_phone,
                    "client_email": booking.client_email or None,
                    "therapist_id": therapist['id'],
                    "duration_type": booking.duration_type,
                    "person1_services": booking.person1_services,
                    "person2_services": booking.person2_services,
                    "start_time": booking.start_time,
                    "status": "scheduled",
                    "discount_couples_massage": discount_percent  # Use discount from snapshot or fallback
                }
                
                # Add snapshots if available (Variant 1)
                if booking.person1_snapshots and booking.person2_snapshots:
                    couple_payload["person1_snapshots"] = [s.dict() for s in booking.person1_snapshots]
                    couple_payload["person2_snapshots"] = [s.dict() for s in booking.person2_snapshots]
                
                logger.info(f"🔄 Trying {therapist['name']} (ID: {therapist['id']})")
                
                response = await client.post(
                    f'{booking_api_url}/api/appointments/couple',
                    json=couple_payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                # If booking succeeds
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Couple booking successful with {therapist['name']} (ID: {therapist['id']})")
                    booking_result = response.json()
                    break
                
                # If this therapist is not available, try the next one
                if response.status_code == 400:
                    error_text = response.text.lower()
                    if 'not available' in error_text or 'unavailable' in error_text:
                        logger.info(f"⚠️ {therapist['name']} not available, trying next...")
                        continue
                
                # For other errors, log and continue to next therapist
                logger.warning(f"Error with {therapist['name']}: {response.status_code} - {response.text}")
            
            # If no therapist is available
            if not booking_result:
                logger.error(f"❌ All web booking therapists busy for {booking.start_time}")
                raise HTTPException(
                    status_code=400,
                    detail="Svi termini su zauzeti za izabrano vreme. Molimo izaberite drugo vreme."
                )
            
            # Send confirmation email (construct detailed service name with massage choices)
            # Get COUPLES service names from our endpoint
            logger.info("📧 Preparing email - fetching couples services...")
            couples_services_response = await client.get(f'http://localhost:8001/api/services/couples/list')
            couples_services = couples_services_response.json() if couples_services_response.status_code == 200 else []
            
            # Create service name lookup from couples services
            service_names = {s['id']: s['name'] for s in couples_services}
            logger.info(f"📧 Loaded {len(service_names)} service names for email")
            
            # Build detailed service description with massage choices
            total_duration = booking.duration_type * 2
            service_display_name = f"Masaža za parove - Ukupno {total_duration} min\n\n"
            service_display_name += "Osoba 1:\n"
            for service_id in booking.person1_services:
                service_name = service_names.get(service_id, service_id)
                service_display_name += f"  • {service_name}\n"
            service_display_name += "\nOsoba 2:\n"
            for service_id in booking.person2_services:
                service_name = service_names.get(service_id, service_id)
                service_display_name += f"  • {service_name}\n"
            
            background_tasks.add_task(
                send_confirmation_email,
                client_email=booking.client_email or "",
                client_name=f"{booking.client_first_name} {booking.client_last_name}",
                client_phone=booking.client_phone,
                service_name=service_display_name,
                appointment_datetime=booking.start_time,
                language=booking.language or 'sr'
            )
            logger.info(f"📧 Confirmation email scheduled for {booking.client_email}")
            
            # Schedule reminder email 2 hours before appointment
            try:
                appointment_dt = datetime.fromisoformat(booking.start_time.replace('Z', ''))
                if appointment_dt.tzinfo is None:
                    appointment_dt = appointment_dt.replace(tzinfo=timezone.utc)
                
                reminder_time = appointment_dt - timedelta(hours=2)
                
                if reminder_time > datetime.now(timezone.utc):
                    scheduler.add_job(
                        send_reminder_email,
                        DateTrigger(run_date=reminder_time),
                        args=[
                            booking.client_email or "",
                            f"{booking.client_first_name} {booking.client_last_name}",
                            service_display_name,  # Removed client_phone - function doesn't use it
                            booking.start_time,
                            booking.language or 'sr'
                        ],
                        id=f"reminder_{booking_result['id']}",
                        replace_existing=True
                    )
                    logger.info(f"⏰ Reminder email scheduled for {reminder_time} (2h before appointment)")
                else:
                    logger.info("⚠️ Appointment too soon - no reminder scheduled")
                    
            except Exception as e:
                logger.error(f"Failed to schedule reminder: {e}")
            
            return booking_result
            
    except httpx.RequestError as e:
        logger.error(f"Couple booking API request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Booking service unavailable"
        )

# NEW LOGIC: /api/appointments endpoint for couples massage booking
@api_router.post("/appointments")
async def create_appointment(booking: AppointmentBooking, background_tasks: BackgroundTasks):
    """
    NEW LOGIC for couples massage booking:
    1. User selects Person 1 massage from dropdown (Tip A - individual [PAROVI] service)
    2. User selects Person 2 massage from dropdown (Tip A - individual [PAROVI] service)
    3. For booking, frontend should:
       - Calculate totalMinutes = person1.duration + person2.duration (e.g., 60+60=120)
       - Fetch couples packages from /api/services/couples/list
       - Find package matching that duration (e.g., "Masaža za parove - 120 min")
       - Send booking with THAT package's service_id (Tip B)
       - Include dropdown selections in notes field
    """
    try:
        logger.info(f"📌 NEW LOGIC APPOINTMENT REQUEST - Service ID: {booking.service_id}, Client: {booking.client_first_name} {booking.client_last_name}")
        
        # Check if this is a couples booking by looking at the notes field
        is_couples_booking = booking.notes and "COUPLES UI izbor:" in booking.notes
        
        if is_couples_booking:
            logger.info("🎯 COUPLES BOOKING DETECTED - Implementing NEW LOGIC")
            
            # Parse couples data from notes
            # Expected format: "COUPLES UI izbor: Osoba1=[PAROVI] Tradicionalna tajlandska masaža (60min); Osoba2=[PAROVI] Aroma terapija (60min)"
            import re
            
            # Extract person 1 and person 2 selections
            person1_match = re.search(r'Osoba1=(.+?)\s*\((\d+)min\)', booking.notes)
            person2_match = re.search(r'Osoba2=(.+?)\s*\((\d+)min\)', booking.notes)
            
            if person1_match and person2_match:
                person1_duration = int(person1_match.group(2))
                person2_duration = int(person2_match.group(2))
                totalMinutes = person1_duration + person2_duration
                
                logger.info(f"🔍 Parsed couples selection: Person1={person1_duration}min, Person2={person2_duration}min, totalMinutes={totalMinutes}")
                console_log = f"Found matching couples package with totalMinutes: {totalMinutes}"
                logger.info(console_log)
                
                # Fetch couples packages from /api/services/couples/list
                booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # Get couples packages
                    couples_response = await client.get(f"{booking_api_url}/api/services")
                    couples_response.raise_for_status()
                    all_services = couples_response.json()
                    
                    # Filter for couples packages (Tip B) - these are the packages, not individual services
                    couples_packages = [s for s in all_services if 
                                      s.get('category') == 'Masaza za parove' and 
                                      not s.get('name', '').startswith('[PAROVI]')]
                    
                    logger.info(f"📦 Found {len(couples_packages)} couples packages")
                    
                    # Find package matching totalMinutes
                    matching_package = None
                    for package in couples_packages:
                        # Extract duration from package name (e.g., "Masaža za parove - 120 min")
                        duration_match = re.search(r'(\d+)\s*min', package['name'])
                        if duration_match:
                            package_duration = int(duration_match.group(1))
                            if package_duration == totalMinutes:
                                matching_package = package
                                break
                    
                    if matching_package:
                        logger.info(f"✅ Found matching couples package: {matching_package['name']} (ID: {matching_package['id']})")
                        
                        # Update booking to use the couples package service_id (Tip B)
                        booking.service_id = matching_package['id']
                        booking.service_name = matching_package['name']
                        
                        console_log_final = f"Couples booking payload (FINAL): service_id={matching_package['id']}, notes={booking.notes}"
                        logger.info(console_log_final)
                    else:
                        logger.error(f"❌ No couples package found for totalMinutes: {totalMinutes}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"No couples package available for {totalMinutes} minutes duration"
                        )
        
        # Forward to external booking system
        booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prepare booking payload
            booking_payload = booking.model_dump()
            
            # Remove therapist_id - manual assignment in reception
            booking_payload.pop('therapist_id', None)
            
            logger.info(f"📤 Sending booking request to {booking_api_url}/api/appointments")
            response = await client.post(
                f'{booking_api_url}/api/appointments',
                json=booking_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Booking successful")
                booking_result = response.json()
                
                # Send confirmation email
                background_tasks.add_task(
                    send_confirmation_email,
                    client_email=booking.client_email,
                    client_name=f"{booking.client_first_name} {booking.client_last_name}",
                    client_phone=booking.client_phone,
                    service_name=booking.service_name or "Tretman",
                    appointment_datetime=booking.start_time,
                    language=booking.language or 'sr'
                )
                
                return booking_result
            else:
                error_text = response.text
                logger.error(f"❌ Booking failed: {response.status_code} - {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Booking failed: {error_text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Booking API request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Booking service unavailable"
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()