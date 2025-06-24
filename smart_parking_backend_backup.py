# Smart Parking System - Backend API
# Optimized for student hardware with minimal resource requirements

from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import cv2
import numpy as np
import json
import threading
import time
from datetime import datetime, timedelta
import random
import os
from dataclasses import dataclass
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///parking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Optional AI Configuration
ENABLE_AI_FEATURES = os.getenv('ENABLE_AI_FEATURES', 'false').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:5000')
SITE_NAME = os.getenv('SITE_NAME', 'Smart Parking System')

# Initialize OpenAI/OpenRouter client
openai_client = None
if ENABLE_AI_FEATURES and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(
            base_url=OPENAI_BASE_URL,
            api_key=OPENAI_API_KEY,
        )
        
        # Determine which service we're using
        if 'openrouter.ai' in OPENAI_BASE_URL:
            print(f"🤖 OpenRouter integration enabled with model: {OPENAI_MODEL}")
        else:
            print(f"🤖 OpenAI integration enabled with model: {OPENAI_MODEL}")
            
    except ImportError:
        print("⚠️  OpenAI requested but not installed. Run: pip install openai")
        ENABLE_AI_FEATURES = False
else:
    print("🎯 Running in simulation mode (no AI integration)")

db = SQLAlchemy(app)
CORS(app)

# Database Models
class ParkingArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    x_position = db.Column(db.Float, nullable=False)  # X position on map (percentage)
    y_position = db.Column(db.Float, nullable=False)  # Y position on map (percentage)
    width = db.Column(db.Float, nullable=False)       # Width on map (percentage)
    height = db.Column(db.Float, nullable=False)      # Height on map (percentage)

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), unique=True, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    coordinates = db.Column(db.String(100))  # JSON string of coordinates
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    area_id = db.Column(db.Integer, db.ForeignKey('parking_area.id'), nullable=True)
    
class ParkingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    occupied = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer)  # Duration in minutes

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Float, default=2.0)  # Base price per hour
    current_price = db.Column(db.Float, default=2.0)

# Agentic Framework Components
@dataclass
class AgentMessage:
    agent_id: str
    message_type: str
    data: Dict
    timestamp: datetime

class BaseAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.is_active = True
        
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        pass

class VisionAgent(BaseAgent):
    """Simulates computer vision processing for parking spot detection"""
    
    def __init__(self):
        super().__init__("vision_agent")
        self.confidence_threshold = 0.7
        
    def detect_vehicles_simulation(self, spot_coords: List[Dict]) -> List[Dict]:
        """Simulates vehicle detection - in real implementation, this would use YOLO"""
        results = []
        for spot in spot_coords:
            # Simulate detection with random but realistic patterns
            occupied_probability = self._calculate_occupancy_probability()
            is_occupied = random.random() < occupied_probability
            confidence = random.uniform(0.75, 0.95) if is_occupied else random.uniform(0.8, 0.98)
            
            results.append({
                'spot_id': spot['id'],
                'occupied': is_occupied,
                'confidence': confidence,
                'bbox': spot.get('coordinates', [0, 0, 100, 100])  # Bounding box
            })
        return results
    
    def _calculate_occupancy_probability(self) -> float:
        """Calculate occupancy probability based on time patterns"""
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            return 0.7
        elif 18 <= current_hour <= 22:  # Evening
            return 0.5
        else:  # Night/early morning
            return 0.2

class PredictionAgent(BaseAgent):
    """Handles occupancy prediction using simple time series analysis"""
    
    def __init__(self):
        super().__init__("prediction_agent")
        
    def predict_availability(self, spot_id: int, hours_ahead: int = 1) -> Dict:
        """Predict parking availability for next few hours"""
        if ENABLE_AI_FEATURES:
            return self._ai_prediction(spot_id, hours_ahead)
        else:
            return self._simple_prediction(spot_id, hours_ahead)
    
    def _simple_prediction(self, spot_id: int, hours_ahead: int) -> Dict:
        """Simple time-based prediction (current implementation)"""
        history = ParkingHistory.query.filter_by(spot_id=spot_id).order_by(
            ParkingHistory.timestamp.desc()).limit(50).all()
        
        if not history:
            return {'predicted_available': True, 'confidence': 0.5}
            
        # Simple pattern analysis
        current_hour = datetime.now().hour
        same_hour_history = [h for h in history if h.timestamp.hour == current_hour]
        
        if same_hour_history:
            avg_occupancy = sum(1 for h in same_hour_history if h.occupied) / len(same_hour_history)
            return {
                'predicted_available': avg_occupancy < 0.5,
                'confidence': min(0.9, len(same_hour_history) / 10),
                'occupancy_rate': avg_occupancy
            }
        
        return {'predicted_available': True, 'confidence': 0.3}
    
    def _ai_prediction(self, spot_id: int, hours_ahead: int) -> Dict:
        """Advanced AI-powered prediction (requires OpenAI API key)"""
        global openai_client
        
        if not openai_client:
            return self._simple_prediction(spot_id, hours_ahead)
            
        try:
            # Get historical data
            history = ParkingHistory.query.filter_by(spot_id=spot_id).order_by(
                ParkingHistory.timestamp.desc()).limit(100).all()
            
            # Prepare context for AI
            current_time = datetime.now()
            context = {
                'current_hour': current_time.hour,
                'day_of_week': current_time.weekday(),
                'recent_pattern': [h.occupied for h in history[:20]],
                'spot_id': spot_id
            }
            
            prompt = f"""
            Based on this parking data for spot {spot_id}:
            - Current time: {current_time.strftime('%H:%M on %A')}
            - Recent occupancy pattern: {context['recent_pattern']}
            
            Predict if this spot will be available in {hours_ahead} hour(s).
            Return only a JSON object with: predicted_available (boolean), confidence (0-1), reasoning (string)
            """
            
            # Prepare extra headers for OpenRouter
            extra_headers = {}
            if 'openrouter.ai' in OPENAI_BASE_URL:
                extra_headers["HTTP-Referer"] = SITE_URL
                extra_headers["X-Title"] = SITE_NAME
            
            completion = openai_client.chat.completions.create(
                extra_headers=extra_headers,
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant for a smart parking system. Analyze parking data and provide predictions in JSON format."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            response_content = completion.choices[0].message.content
            print(f"🤖 AI Response: {response_content}")  # Debug line
            
            if not response_content or response_content.strip() == "":
                print("⚠️ Empty AI response, falling back")
                return self._simple_prediction(spot_id, hours_ahead)
            
            # Extract JSON from markdown code blocks if present
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'(\{[^}]*"predicted_available"[^}]*\})', response_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_content.strip()
            
            result = json.loads(json_str)
            result['ai_powered'] = True
            result['model'] = OPENAI_MODEL
            return result
            
        except Exception as e:
            print(f"AI prediction failed: {e}, falling back to simple prediction")
            return self._simple_prediction(spot_id, hours_ahead)

class PricingAgent(BaseAgent):
    """Dynamic pricing based on demand and occupancy"""
    
    def __init__(self):
        super().__init__("pricing_agent")
        
    def calculate_dynamic_price(self, lot_id: int) -> float:
        """Calculate dynamic pricing based on occupancy and demand"""
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return 2.0
            
        occupancy_rate = (lot.total_spots - lot.available_spots) / lot.total_spots
        base_price = lot.base_price
        
        # Dynamic pricing algorithm
        if occupancy_rate > 0.8:  # High demand
            multiplier = 1.5
        elif occupancy_rate > 0.6:  # Medium demand
            multiplier = 1.2
        elif occupancy_rate < 0.3:  # Low demand - incentivize parking
            multiplier = 0.8
        else:
            multiplier = 1.0
            
        # Time-based adjustments
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Peak hours
            multiplier *= 1.1
            
        new_price = round(base_price * multiplier, 2)
        
        # Update lot price
        lot.current_price = new_price
        db.session.commit()
        
        return new_price

class CoordinatorAgent(BaseAgent):
    """Main coordinator that orchestrates all other agents"""
    
    def __init__(self):
        super().__init__("coordinator")
        self.vision_agent = VisionAgent()
        self.prediction_agent = PredictionAgent()
        self.pricing_agent = PricingAgent()
        
    def process_parking_update(self) -> Dict:
        """Main processing pipeline"""
        # Get all parking spots
        spots = ParkingSpot.query.all()
        spot_coords = [{'id': s.id, 'coordinates': s.coordinates, 'area_id': s.area_id} for s in spots]
        
        # Vision processing
        detections = self.vision_agent.detect_vehicles_simulation(spot_coords)
        
        # Update database
        updates = []
        for detection in detections:
            spot = ParkingSpot.query.get(detection['spot_id'])
            if spot and spot.is_occupied != detection['occupied']:
                spot.is_occupied = detection['occupied']
                spot.last_updated = datetime.utcnow()
                
                # Record history
                history = ParkingHistory(
                    spot_id=spot.id,
                    occupied=detection['occupied'],
                    timestamp=datetime.utcnow()
                )
                db.session.add(history)
                updates.append({
                    'spot_id': spot.id,
                    'spot_number': spot.spot_number,
                    'occupied': detection['occupied'],
                    'confidence': detection['confidence'],
                    'area_id': spot.area_id
                })
        
        # Update lot availability
        lot = ParkingLot.query.first()
        if lot:
            available = sum(1 for s in spots if not s.is_occupied)
            lot.available_spots = available
            
            # Update pricing
            new_price = self.pricing_agent.calculate_dynamic_price(lot.id)
        
        db.session.commit()
        
        return {
            'updates': updates,
            'total_available': available if lot else 0,
            'current_price': new_price if lot else 2.0,
            'timestamp': datetime.utcnow().isoformat()
        }

# Initialize coordinator
coordinator = CoordinatorAgent()

# API Routes
@app.route('/')
def dashboard():
    """Simple web dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Parking Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .parking-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 10px; }
            .parking-spot { width: 80px; height: 40px; border: 2px solid #ddd; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
            .occupied { background-color: #e74c3c; color: white; }
            .available { background-color: #27ae60; color: white; }
            .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #2980b9; }
            .ai-prediction { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .prediction-form { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }
            .prediction-input { padding: 10px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
            .prediction-result { background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 15px; margin-top: 15px; }
            .confidence-bar { height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }
            .confidence-fill { height: 100%; background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60); transition: width 0.3s ease; }
            .reasoning { background: #fff; border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; font-style: italic; }
            .ai-badge { background: #9b59b6; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px; }
        </style>
        <script>
            function refreshData() {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('available-count').textContent = data.available_spots;
                        document.getElementById('occupancy-rate').textContent = Math.round(data.occupancy_rate * 100) + '%';
                        document.getElementById('current-price').textContent = '$' + data.current_price.toFixed(2);
                        updateParkingGrid(data.spots);
                    });
            }
            
            function updateParkingGrid(spots) {
                const grid = document.getElementById('parking-grid');
                grid.innerHTML = '';
                spots.forEach(spot => {
                    const div = document.createElement('div');
                    div.className = 'parking-spot ' + (spot.is_occupied ? 'occupied' : 'available');
                    div.textContent = spot.spot_number;
                    div.title = spot.is_occupied ? 'Occupied' : 'Available';
                    grid.appendChild(div);
                });
            }
            
            function updateSystem() {
                fetch('/api/update', {method: 'POST'})
                    .then(() => refreshData());
            }
            
            function predictSpot() {
                const spotInput = document.getElementById('spot-input');
                const spotId = spotInput.value.trim();
                
                if (!spotId) {
                    alert('Please enter a spot number');
                    return;
                }
                
                const resultDiv = document.getElementById('prediction-result');
                resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;">🤖 AI analyzing patterns...</div>';
                resultDiv.style.display = 'block';
                
                fetch(`/api/predict-by-number/${spotId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            resultDiv.innerHTML = `<div style="color: #e74c3c;">❌ ${data.error}</div>`;
                            return;
                        }
                        
                        const available = data.predicted_available;
                        const confidence = Math.round(data.confidence * 100);
                        const reasoning = data.reasoning || 'No reasoning provided';
                        const aiPowered = data.ai_powered;
                        const model = data.model;
                        
                        resultDiv.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4>Prediction for Spot ${spotId}</h4>
                                ${aiPowered ? `<span class="ai-badge">🤖 AI-Powered</span>` : '<span class="ai-badge" style="background: #95a5a6;">📊 Mathematical</span>'}
                            </div>
                            <div style="font-size: 18px; margin: 10px 0;">
                                <strong>Status:</strong> 
                                <span style="color: ${available ? '#27ae60' : '#e74c3c'};">
                                    ${available ? '✅ Likely Available' : '❌ Likely Occupied'}
                                </span>
                            </div>
                            <div>
                                <strong>Confidence:</strong> ${confidence}%
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${confidence}%;"></div>
                                </div>
                            </div>
                            ${reasoning ? `<div class="reasoning">"${reasoning}"</div>` : ''}
                            ${model ? `<div style="font-size: 12px; color: #7f8c8d; margin-top: 10px;">Model: ${model}</div>` : ''}
                        `;
                    })
                    .catch(error => {
                        resultDiv.innerHTML = `<div style="color: #e74c3c;">❌ Error: ${error.message}</div>`;
                    });
            }
            
            function refreshData() {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('available-count').textContent = data.available_spots;
                    });
                    
                    tileLayer.on('load', function() {
                        console.log('✅ Map tiles loaded successfully');
                        document.getElementById('map-status').innerHTML = '✅ Map loaded successfully!';
                        setTimeout(() => {
                            document.getElementById('map-status').style.display = 'none';
                        }, 2000);
                    });
                    
                    tileLayer.on('tileerror', function(e) {
                        console.warn('⚠️ Tile load error:', e);
                        document.getElementById('map-status').innerHTML = '⚠️ Some map tiles failed to load, but map should still work.';
                    });
                    
                    tileLayer.addTo(cityMap);
                    
                    console.log('🎯 Map initialized successfully, loading parking areas...');
                    document.getElementById('map-status').innerHTML = '🎯 Loading parking areas...';
                    
                    // Load and display parking areas
                    updateSatelliteMap();
                } catch (error) {
                    console.error('❌ Error initializing map:', error);
                    document.getElementById('map-status').innerHTML = '❌ Map failed to load. <button onclick="initializeCityMap()" style="background: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Retry</button>';
                    document.getElementById('real-city-map').innerHTML = '<div style="padding: 20px; text-align: center; color: #e74c3c; background: #fff; border: 2px dashed #e74c3c; border-radius: 8px;"><h4>Map Loading Failed</h4><p>Error: ' + error.message + '</p><p>Please check your internet connection and try again.</p></div>';
                }
            }
            
            function updateSatelliteMap() {
                console.log('🔄 Updating satellite map data...');
                
                fetch('/api/city-map')
                    .then(response => {
                        console.log('📡 API response received:', response.status);
                        return response.json();
                    })
                    .then(data => {
                        console.log('📊 Map data loaded:', data);
                        
                        // Clear existing markers
                        parkingMarkers.forEach(marker => cityMap.removeLayer(marker));
                        parkingMarkers = [];
                        
                        // Center map if we have areas
                        if (data.areas.length > 0 && data.center) {
                            console.log('📍 Centering map on:', data.center);
                            cityMap.setView([data.center.latitude, data.center.longitude], data.zoom);
                        }
                        
                        console.log(`🏢 Processing ${data.areas.length} parking areas...`);
                        
                        // Add markers for each parking area
                        data.areas.forEach((area, index) => {
                            console.log(`📍 Processing area ${index + 1}: ${area.name} at [${area.latitude}, ${area.longitude}]`);
                            
                            if (area.latitude && area.longitude) {
                                const availableSpots = area.available;
                                const totalSpots = area.total;
                                const occupancyRate = totalSpots > 0 ? (totalSpots - availableSpots) / totalSpots : 0;
                                
                                // Determine marker style based on availability
                                let markerClass = 'mixed';
                                if (occupancyRate === 0) markerClass = 'available';
                                else if (occupancyRate === 1) markerClass = 'occupied';
                                
                                console.log(`🎯 Creating ${markerClass} marker for ${area.name} (${availableSpots}/${totalSpots} available)`);
                                
                                // Create custom marker
                                const markerIcon = L.divIcon({
                                    className: `parking-marker ${markerClass}`,
                                    html: `<div class="marker-content ${markerClass}">${availableSpots}</div>`,
                                    iconSize: [40, 40],
                                    iconAnchor: [20, 20],
                                    popupAnchor: [0, -20]
                                });
                                
                                // Create marker
                                const marker = L.marker([area.latitude, area.longitude], { icon: markerIcon });
                                
                                // Create popup content with spot details
                                const spotsHtml = area.spots.map(spot => 
                                    `<div class="popup-spot">
                                        <span>Spot ${spot.spot_number}</span>
                                        <div>
                                            <span class="spot-status ${spot.is_occupied ? 'occupied' : 'available'}">
                                                ${spot.is_occupied ? 'Occupied' : 'Available'}
                                            </span>
                                            <button class="predict-btn" onclick="predictSpotFromMap('${spot.spot_number}')">Predict</button>
                                        </div>
                                    </div>`
                                ).join('');
                                
                                const popupContent = `
                                    <div class="popup-area">
                                        <h4>${area.name}</h4>
                                        <p style="margin: 5px 0; color: #7f8c8d; font-size: 13px;">${area.description}</p>
                                        <div class="popup-stats">
                                            <div class="popup-stat">
                                                <div class="number">${availableSpots}</div>
                                                <div>Available</div>
                                            </div>
                                            <div class="popup-stat">
                                                <div class="number">${totalSpots}</div>
                                                <div>Total</div>
                                            </div>
                                            <div class="popup-stat">
                                                <div class="number">${Math.round(occupancyRate * 100)}%</div>
                                                <div>Occupied</div>
                                            </div>
                                        </div>
                                        <div style="max-height: 150px; overflow-y: auto; border-top: 1px solid #eee; padding-top: 10px;">
                                            ${spotsHtml}
                                        </div>
                                    </div>
                                `;
                                
                                marker.bindPopup(popupContent, { maxWidth: 300 });
                                marker.addTo(cityMap);
                                parkingMarkers.push(marker);
                                
                                console.log(`✅ Added marker for ${area.name}`);
                            } else {
                                console.warn(`⚠️ Skipping ${area.name} - missing coordinates`);
                            }
                        });
                        
                        console.log(`✅ Map update complete! Added ${parkingMarkers.length} markers`);
                    })
                    .catch(error => {
                        console.error('❌ Error loading map data:', error);
                        document.getElementById('real-city-map').innerHTML = '<div style="padding: 20px; text-align: center; color: #e74c3c;">Failed to load parking data. Check console for details.</div>';
                    });
            }
            
            function createFallbackMap() {
                console.log('🔄 Creating fallback CSS-based map...');
                const mapElement = document.getElementById('real-city-map');
                const statusElement = document.getElementById('map-status');
                
                statusElement.innerHTML = '⚠️ Using fallback map (Leaflet unavailable)';
                
                // Create a simple CSS-based city map
                mapElement.innerHTML = `
                    <div style="position: relative; width: 100%; height: 100%; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); border-radius: 8px; overflow: hidden;">
                        <div style="position: absolute; top: 10px; left: 10px; right: 10px; bottom: 10px; background: #f0f8ff; border-radius: 4px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                            <h3 style="text-align: center; margin: 20px 0; color: #2c3e50;">🏙️ Smart City Parking Network</h3>
                            <div id="fallback-areas" style="padding: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; max-height: 400px; overflow-y: auto;">
                                <!-- Areas will be populated here -->
                            </div>
                        </div>
                    </div>
                `;
                
                // Load and display parking areas in fallback mode
                loadFallbackAreas();
            }
            
            function loadFallbackAreas() {
                fetch('/api/city-map')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('fallback-areas');
                        if (!container) return;
                        
                        container.innerHTML = '';
                        
                        data.areas.forEach(area => {
                            const availableSpots = area.available;
                            const totalSpots = area.total;
                            const occupancyRate = totalSpots > 0 ? (totalSpots - availableSpots) / totalSpots : 0;
                            
                            let colorClass = 'available';
                            let bgColor = '#d5f4e6';
                            let borderColor = '#27ae60';
                            
                            if (occupancyRate > 0.8) {
                                colorClass = 'occupied';
                                bgColor = '#fadbd8';
                                borderColor = '#e74c3c';
                            } else if (occupancyRate > 0.2) {
                                colorClass = 'mixed';
                                bgColor = '#fef9e7';
                                borderColor = '#f39c12';
                            }
                            
                            const areaCard = document.createElement('div');
                            areaCard.style.cssText = `
                                background: ${bgColor};
                                border: 2px solid ${borderColor};
                                border-radius: 8px;
                                padding: 15px;
                                cursor: pointer;
                                transition: transform 0.2s ease;
                            `;
                            
                            areaCard.innerHTML = `
                                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">${area.name}</h4>
                                <p style="margin: 0 0 10px 0; font-size: 12px; color: #7f8c8d;">${area.description}</p>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: ${borderColor};">${availableSpots}</div>
                                    <div style="text-align: right; font-size: 12px; color: #7f8c8d;">
                                        <div>Available</div>
                                        <div>${totalSpots} Total</div>
                                    </div>
                                </div>
                                <div style="margin-top: 10px; font-size: 11px; color: #7f8c8d;">
                                    ${Math.round(occupancyRate * 100)}% Occupied
                                </div>
                            `;
                            
                            areaCard.onmouseover = () => areaCard.style.transform = 'scale(1.05)';
                            areaCard.onmouseout = () => areaCard.style.transform = 'scale(1)';
                            areaCard.onclick = () => showFallbackAreaDetails(area);
                            
                            container.appendChild(areaCard);
                        });
                        
                        console.log(`✅ Fallback map loaded with ${data.areas.length} areas`);
                    })
                    .catch(error => {
                        console.error('❌ Error loading fallback areas:', error);
                    });
            }
            
            function showFallbackAreaDetails(area) {
                alert(`🏢 ${area.name}\n\n📍 ${area.description}\n📊 Available: ${area.available}/${area.total} spots\n🔢 Occupancy: ${Math.round((area.total - area.available) / area.total * 100)}%\n\n💡 Click "Predict" buttons in the main interface to get AI predictions for specific spots!`);
            }
                document.getElementById('spot-input').value = spotNumber;
                // Close all popups
                cityMap.closePopup();
                // Scroll to prediction form
                document.querySelector('.ai-prediction').scrollIntoView({ behavior: 'smooth' });
                // Trigger prediction after a brief delay
                setTimeout(() => {
                    predictSpot();
                }, 500);
            }
            
            // Auto-refresh every 10 seconds
            setInterval(refreshData, 10000);
            setInterval(updateSatelliteMap, 30000); // Update satellite map every 30 seconds
            
            // Add debugging information
            console.log('🔧 Script loaded, setting up page...');
            document.addEventListener('DOMContentLoaded', function() {
                console.log('📄 DOM Content Loaded');
            });
            
            window.onload = function() {
                console.log('🚀 Page loaded, starting initialization...');
                
                // Check if required elements exist
                const mapElement = document.getElementById('real-city-map');
                const statusElement = document.getElementById('map-status');
                
                if (!mapElement) {
                    console.error('❌ Map container element not found!');
                    return;
                }
                
                if (!statusElement) {
                    console.error('❌ Status element not found!');
                    return;
                }
                
                console.log('✅ Required DOM elements found');
                
                // Check if Leaflet is loaded
                if (typeof L === 'undefined') {
                    console.error('❌ Leaflet library not loaded!');
                    statusElement.innerHTML = '❌ Leaflet library failed to load. Using fallback map...';
                    setTimeout(() => {
                        createFallbackMap();
                    }, 500);
                    return;
                }
                
                console.log('✅ Leaflet library loaded successfully, version: ' + L.version);
                refreshData();
                
                // Add a small delay to ensure DOM is ready
                setTimeout(() => {
                    initializeCityMap(); // Initialize the satellite map
                }, 100);
            }
            
            // Allow Enter key to trigger prediction
            function handleEnterKey(event) {
                if (event.key === 'Enter') {
                    predictSpot();
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 Smart Parking System</h1>
                <p>AI-Powered Parking Management with Agentic Framework</p>
            </div>
            
            <div class="ai-prediction">
                <h3>🤖 AI Spot Prediction</h3>
                <p>Enter a spot number to get AI-powered availability prediction with reasoning</p>
                <div class="prediction-form">
                    <input type="text" id="spot-input" class="prediction-input" placeholder="e.g., A01, B05, 1, 15" onkeypress="handleEnterKey(event)">
                    <button class="btn" onclick="predictSpot()">🔮 Predict Availability</button>
                </div>
                <div id="prediction-result" class="prediction-result" style="display: none;"></div>
            </div>
            
            <div class="city-map">
                <h3>🛰️ Real-Time Satellite Map</h3>
                <p>Interactive satellite map showing parking areas across the city. Click markers to view details.</p>
                <div id="map-status" style="padding: 10px; background: #e3f2fd; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
                    🔄 Loading map...
                </div>
                <div id="real-city-map" class="map-container"></div>
                <div class="legend">
                    <div class="legend-item">
                        <div style="width: 16px; height: 16px; border-radius: 50%; background: #27ae60; border: 2px solid #27ae60;"></div>
                        <span>Fully Available</span>
                    </div>
                    <div class="legend-item">
                        <div style="width: 16px; height: 16px; border-radius: 50%; background: #f39c12; border: 2px solid #f39c12;"></div>
                        <span>Partially Available</span>
                    </div>
                    <div class="legend-item">
                        <div style="width: 16px; height: 16px; border-radius: 50%; background: #e74c3c; border: 2px solid #e74c3c;"></div>
                        <span>Fully Occupied</span>
                    </div>
                    <div class="legend-item">
                        <span>💡 Numbers show available spots</span>
                    </div>
                    <div class="legend-item">
                        <button onclick="initializeCityMap()" style="background: #3498db; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">🔄 Reload Map</button>
                    </div>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Available Spots</h3>
                    <h2 id="available-count">-</h2>
                </div>
                <div class="stat-card">
                    <h3>Occupancy Rate</h3>
                    <h2 id="occupancy-rate">-</h2>
                </div>
                <div class="stat-card">
                    <h3>Current Price</h3>
                    <h2 id="current-price">-</h2>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3>Parking Layout</h3>
                <button class="btn" onclick="updateSystem()">Update Detection</button>
                <button class="btn" onclick="refreshData()">Refresh</button>
                <div id="parking-grid" class="parking-grid"></div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/test-map')
def test_map():
    """Simple test map to debug Leaflet issues"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Map Test</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body { margin: 20px; font-family: Arial, sans-serif; }
            #map { height: 400px; width: 100%; border: 2px solid #ccc; }
            .status { padding: 10px; background: #f0f0f0; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>🗺️ Leaflet Map Test</h1>
        <div id="status" class="status">Starting...</div>
        <div id="map"></div>
        
        <script>
            function log(message) {
                console.log(message);
                document.getElementById('status').innerHTML += '<br>' + message;
            }
            
            log('🚀 Script started');
            
            // Test if Leaflet is loaded
            if (typeof L === 'undefined') {
                log('❌ Leaflet not loaded!');
            } else {
                log('✅ Leaflet loaded: ' + L.version);
                
                try {
                    log('📍 Creating map...');
                    var map = L.map('map').setView([40.7128, -74.0060], 13);
                    
                    log('🗺️ Adding tiles...');
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap contributors'
                    }).addTo(map);
                    
                    log('📍 Adding marker...');
                    L.marker([40.7128, -74.0060]).addTo(map)
                        .bindPopup('Test Location')
                        .openPopup();
                    
                    log('✅ Map created successfully!');
                } catch (error) {
                    log('❌ Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/api/status')
def get_status():
    """Get current parking lot status"""
    lot = ParkingLot.query.first()
    spots = ParkingSpot.query.all()
    areas = ParkingArea.query.all()
    
    if not lot:
        return jsonify({'error': 'No parking lot found'}), 404
    
    # Calculate area statistics
    area_stats = []
    for area in areas:
        area_spots = [s for s in spots if s.area_id == area.id]
        area_stats.append({
            'name': area.name,
            'total': len(area_spots),
            'available': sum(1 for s in area_spots if not s.is_occupied),
            'occupancy_rate': (sum(1 for s in area_spots if s.is_occupied) / len(area_spots)) if area_spots else 0
        })
        
    return jsonify({
        'lot_name': lot.name,
        'total_spots': lot.total_spots,
        'available_spots': lot.available_spots,
        'occupancy_rate': (lot.total_spots - lot.available_spots) / lot.total_spots,
        'current_price': lot.current_price,
        'base_price': lot.base_price,
        'area_stats': area_stats,
        'spots': [{
            'id': s.id,
            'spot_number': s.spot_number,
            'is_occupied': s.is_occupied,
            'area_id': s.area_id,
            'last_updated': s.last_updated.isoformat() if s.last_updated else None
        } for s in spots]
    })

@app.route('/api/update', methods=['POST'])
def update_parking():
    """Trigger parking detection update"""
    result = coordinator.process_parking_update()
    return jsonify(result)

@app.route('/api/predict/<int:spot_id>')
def predict_availability(spot_id):
    """Predict availability for a specific spot"""
    prediction = coordinator.prediction_agent.predict_availability(spot_id)
    return jsonify(prediction)

@app.route('/api/predict-by-number/<spot_number>')
def predict_availability_by_number(spot_number):
    """Predict availability for a specific spot by spot number (e.g., A01, B05)"""
    # Find spot by spot number or ID
    spot = None
    
    # Try to find by spot number first
    spot = ParkingSpot.query.filter_by(spot_number=spot_number.upper()).first()
    
    # If not found, try to find by ID if the input is numeric
    if not spot and spot_number.isdigit():
        spot = ParkingSpot.query.get(int(spot_number))
    
    if not spot:
        return jsonify({
            'error': f'Spot "{spot_number}" not found. Available spots: {[s.spot_number for s in ParkingSpot.query.all()]}'
        }), 404
    
    prediction = coordinator.prediction_agent.predict_availability(spot.id)
    prediction['spot_number'] = spot.spot_number
    prediction['spot_id'] = spot.id
    
    return jsonify(prediction)

@app.route('/test-map')
def test_map():
    """Simple map test page"""
    with open('map_test.html', 'r') as f:
        return f.read()

@app.route('/api/city-map')
def get_city_map():
    """Get city map data with parking areas and spots"""
    areas = ParkingArea.query.all()
    
    city_data = {
        'areas': [],
        'center': {
            'latitude': 40.7128,  # Default center coordinates
            'longitude': -74.0060
        },
        'zoom': 14
    }
    
    for area in areas:
        # Get spots in this area
        spots = ParkingSpot.query.filter_by(area_id=area.id).all()
        
        area_data = {
            'id': area.id,
            'name': area.name,
            'description': area.description,
            # Legacy percentage positions (for backward compatibility)
            'x': area.x_position,
            'y': area.y_position,
            'width': area.width,
            'height': area.height,
            # New geographic coordinates
            'latitude': area.latitude,
            'longitude': area.longitude,
            'zoom_level': area.zoom_level,
            'total': len(spots),
            'available': sum(1 for s in spots if not s.is_occupied),
            'spots': [{
                'id': s.id,
                'spot_number': s.spot_number,
                'is_occupied': s.is_occupied,
                'last_updated': s.last_updated.isoformat() if s.last_updated else None
            } for s in spots]
        }
        
        city_data['areas'].append(area_data)
    
    return jsonify(city_data)

@app.route('/api/find-parking')
def find_parking():
    """Find best available parking spot"""
    destination = request.args.get('destination', 'main_entrance')
    
    available_spots = ParkingSpot.query.filter_by(is_occupied=False).all()
    
    if not available_spots:
        return jsonify({'message': 'No available spots', 'spots': []})
    
    # Simple scoring based on spot number (simulate distance)
    scored_spots = []
    for spot in available_spots:
        # Get prediction for this spot
        prediction = coordinator.prediction_agent.predict_availability(spot.id, 1)
        
        # Simple scoring algorithm
        score = prediction['confidence'] * 10
        if 'A' in spot.spot_number:  # Simulate closer spots
            score += 5
            
        scored_spots.append({
            'spot': {
                'id': spot.id,
                'spot_number': spot.spot_number,
                'coordinates': spot.coordinates
            },
            'score': score,
            'prediction': prediction
        })
    
    # Sort by score
    scored_spots.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'recommended_spots': scored_spots[:3],
        'total_available': len(available_spots)
    })

@app.route('/api/pricing/history')
def pricing_history():
    """Get pricing history"""
    lot = ParkingLot.query.first()
    if not lot:
        return jsonify({'error': 'No lot found'}), 404
        
    # Simulate pricing history
    history = []
    for i in range(24):
        hour = (datetime.now().hour - i) % 24
        occupancy = random.uniform(0.2, 0.9)
        multiplier = 1.5 if occupancy > 0.8 else 1.2 if occupancy > 0.6 else 0.8 if occupancy < 0.3 else 1.0
        price = round(lot.base_price * multiplier, 2)
        
        history.append({
            'hour': hour,
            'price': price,
            'occupancy_rate': occupancy
        })
    
    return jsonify({'pricing_history': history})

def initialize_database():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create parking lot if doesn't exist
        if not ParkingLot.query.first():
            lot = ParkingLot(
                name="Smart City Parking Network",
                total_spots=50,
                available_spots=50,
                base_price=2.0,
                current_price=2.0
            )
            db.session.add(lot)
        
        # Create parking areas if don't exist
        if not ParkingArea.query.first():
            # Sample city coordinates (using a fictional city layout with realistic coordinates)
            # These coordinates represent different districts in a typical mid-sized city
            areas = [
                ParkingArea(name="Downtown Mall", description="Shopping center parking", 
                           x_position=5, y_position=5, width=20, height=15,
                           latitude=40.7128, longitude=-74.0060),  # NYC-style coordinates
                ParkingArea(name="City Hospital", description="Medical center parking", 
                           x_position=30, y_position=10, width=18, height=12,
                           latitude=40.7134, longitude=-74.0055),
                ParkingArea(name="University Campus", description="Student & faculty parking", 
                           x_position=55, y_position=8, width=22, height=14,
                           latitude=40.7140, longitude=-74.0048),
                ParkingArea(name="Business District", description="Office complex parking", 
                           x_position=80, y_position=12, width=15, height=10,
                           latitude=40.7145, longitude=-74.0040),
                ParkingArea(name="Residential Zone A", description="Apartment complex parking", 
                           x_position=8, y_position=35, width=16, height=12,
                           latitude=40.7120, longitude=-74.0065),
                ParkingArea(name="Tech Park", description="Technology companies parking", 
                           x_position=35, y_position=40, width=20, height=15,
                           latitude=40.7125, longitude=-74.0052),
                ParkingArea(name="Sports Complex", description="Stadium & gym parking", 
                           x_position=65, y_position=38, width=18, height=13,
                           latitude=40.7135, longitude=-74.0042),
                ParkingArea(name="Airport Terminal", description="Airport long-term parking", 
                           x_position=10, y_position=65, width=25, height=20,
                           latitude=40.7110, longitude=-74.0070),
                ParkingArea(name="Train Station", description="Public transit parking", 
                           x_position=45, y_position=70, width=20, height=15,
                           latitude=40.7115, longitude=-74.0045),
                ParkingArea(name="Beach Resort", description="Tourist area parking", 
                           x_position=75, y_position=68, width=18, height=16,
                           latitude=40.7105, longitude=-74.0035)
            ]
            db.session.add_all(areas)
            db.session.commit()
        
        # Create parking spots if don't exist
        if not ParkingSpot.query.first():
            areas = ParkingArea.query.all()
            spots = []
            spot_counter = 1
            
            for area in areas:
                # Determine number of spots per area based on area type
                if "Airport" in area.name or "Stadium" in area.name:
                    spot_count = 8  # Large areas
                elif "Hospital" in area.name or "University" in area.name:
                    spot_count = 6  # Medium areas
                else:
                    spot_count = 4  # Smaller areas
                
                for i in range(spot_count):
                    # Create spot number based on area
                    area_code = ''.join([c for c in area.name if c.isupper()])[:2]
                    if len(area_code) < 2:
                        area_code = area.name[:2].upper()
                    
                    spot = ParkingSpot(
                        spot_number=f"{area_code}{i+1:02d}",
                        coordinates=f"[{area.x_position + i*2}, {area.y_position + 2}, {area.x_position + i*2 + 1.5}, {area.y_position + 4}]",
                        is_occupied=random.choice([True, False]),
                        area_id=area.id
                    )
                    spots.append(spot)
            
            db.session.add_all(spots)
        
        # Update lot total spots
        lot = ParkingLot.query.first()
        if lot:
            total_spots = ParkingSpot.query.count()
            available_spots = ParkingSpot.query.filter_by(is_occupied=False).count()
            lot.total_spots = total_spots
            lot.available_spots = available_spots
        
        db.session.commit()
        print("Database initialized with city map and sample data!")

def background_updates():
    """Background thread for simulating real-time updates"""
    while True:
        time.sleep(30)  # Update every 30 seconds
        try:
            with app.app_context():
                coordinator.process_parking_update()
        except Exception as e:
            print(f"Background update error: {e}")

if __name__ == '__main__':
    initialize_database()
    
    # Start background update thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    print("🚗 Smart Parking System Starting...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔧 API documentation at: http://localhost:5000/api/status")
    
    app.run(debug=True, host='0.0.0.0', port=5000)