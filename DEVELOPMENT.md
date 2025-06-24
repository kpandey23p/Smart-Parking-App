# 🛠️ Smart Parking System - Development Guide

## Architecture Overview

The Smart Parking System uses a multi-agent architecture with the following components:

### Backend (Python/Flask)
- **VisionAgent**: Simulates computer vision for vehicle detection
- **PredictionAgent**: Handles occupancy prediction using time series analysis
- **PricingAgent**: Implements dynamic pricing based on demand
- **CoordinatorAgent**: Orchestrates all agents and manages the main pipeline

### Database Models
- **ParkingSpot**: Individual parking spaces
- **ParkingHistory**: Historical occupancy data
- **ParkingLot**: Parking lot information and pricing

### Mobile App (React Native/Expo)
- **Dashboard**: Real-time parking status
- **Find Parking**: AI-powered spot recommendations
- **Analytics**: Pricing trends and insights

## 🔄 Development Workflow

### 1. Setting Up Development Environment

```powershell
# Clone/setup project
git clone <your-repo> # or use existing files
cd "parking system"

# Setup backend
.\setup.ps1

# Setup mobile app
npm install
npm install -g expo-cli
```

### 2. Running in Development Mode

```powershell
# Terminal 1: Backend
.\start.ps1

# Terminal 2: Mobile App (optional)
npm start
```

### 3. Testing Changes

```powershell
# Run API tests
python test_system.py

# Run unit tests
pytest

# Test specific components
python -c "from smart_parking_backend import *; coordinator.process_parking_update()"
```

## 🧩 Key Components to Customize

### 1. Vision Agent (Computer Vision)

**Current**: Simulated detection with random patterns
**Upgrade to**: Real camera integration

```python
# In VisionAgent.detect_vehicles_simulation()
# Replace simulation with:
def detect_vehicles_real(self, camera_feed):
    # Load YOLO model
    model = YOLO('yolov8n.pt')
    
    # Process camera frame
    results = model(camera_feed)
    
    # Extract vehicle detections
    vehicles = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            if box.cls == 2:  # Car class in COCO dataset
                vehicles.append({
                    'bbox': box.xyxy.tolist(),
                    'confidence': box.conf.item()
                })
    
    return vehicles
```

### 2. Prediction Agent (Machine Learning)

**Current**: Simple time-based patterns
**Upgrade to**: Advanced ML models

```python
# Add to PredictionAgent
def train_prediction_model(self):
    from sklearn.ensemble import RandomForestRegressor
    
    # Get historical data
    history = ParkingHistory.query.all()
    
    # Feature engineering
    features = []  # time, day_of_week, weather, events, etc.
    targets = []   # occupancy_rate
    
    # Train model
    self.model = RandomForestRegressor()
    self.model.fit(features, targets)
```

### 3. Pricing Agent (Business Logic)

**Current**: Simple occupancy-based pricing
**Upgrade to**: Advanced pricing strategies

```python
# Enhanced pricing algorithm
def calculate_advanced_pricing(self, lot_id):
    # Consider multiple factors:
    # - Current occupancy
    # - Historical demand patterns
    # - Weather conditions
    # - Local events
    # - Competition pricing
    # - Revenue optimization
    
    factors = {
        'occupancy_multiplier': self.get_occupancy_multiplier(),
        'demand_multiplier': self.get_demand_multiplier(),
        'event_multiplier': self.get_event_multiplier(),
        'weather_multiplier': self.get_weather_multiplier()
    }
    
    final_price = base_price * reduce(mul, factors.values())
    return final_price
```

### 4. Mobile App Customization

**UI Themes**: Modify styles in `smart_parking_mobile.js`
**Features**: Add new screens and functionality
**Integration**: Connect with additional APIs

## 📊 Database Schema Extensions

### Add New Tables

```python
class ParkingReservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    precipitation = db.Column(db.Float)
    conditions = db.Column(db.String(50))

class EventSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    expected_attendance = db.Column(db.Integer)
```

## 🚀 Production Deployment

### 1. Environment Configuration

```bash
# Production .env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/parking
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
```

### 2. Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/parking
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: parking
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
```

### 3. Performance Optimization

- **Caching**: Add Redis for API response caching
- **Database**: Use PostgreSQL for production
- **Load Balancing**: Use nginx for multiple backend instances
- **Monitoring**: Add application monitoring (Prometheus, Grafana)

## 🔍 Monitoring and Analytics

### 1. Application Metrics

```python
# Add to backend
from prometheus_client import Counter, Histogram, generate_latest

api_requests = Counter('api_requests_total', 'Total API requests')
response_time = Histogram('response_time_seconds', 'Response time')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    api_requests.inc()
    response_time.observe(time.time() - request.start_time)
    return response
```

### 2. Business Analytics

```python
# Analytics endpoints
@app.route('/api/analytics/occupancy-trends')
def occupancy_trends():
    # Return hourly/daily/weekly occupancy patterns
    
@app.route('/api/analytics/revenue')
def revenue_analytics():
    # Return pricing and revenue data
    
@app.route('/api/analytics/user-behavior')
def user_behavior():
    # Return user parking patterns
```

## 🧪 Testing Strategy

### 1. Unit Tests

```python
# test_agents.py
def test_vision_agent():
    agent = VisionAgent()
    spots = [{'id': 1, 'coordinates': '[0,0,100,100]'}]
    results = agent.detect_vehicles_simulation(spots)
    assert len(results) == 1
    assert 'occupied' in results[0]

def test_pricing_agent():
    agent = PricingAgent()
    # Create test lot
    price = agent.calculate_dynamic_price(1)
    assert isinstance(price, float)
    assert price > 0
```

### 2. Integration Tests

```python
# test_api.py
def test_full_update_cycle():
    # Test complete update pipeline
    response = client.post('/api/update')
    assert response.status_code == 200
    
    # Verify database changes
    spots = ParkingSpot.query.all()
    assert len(spots) > 0
```

### 3. Load Testing

```python
# load_test.py
import asyncio
import aiohttp

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.get('http://localhost:5000/api/status')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        success_count = sum(1 for r in responses if r.status == 200)
        print(f"Success rate: {success_count}/100")
```

## 🎯 Next Steps for Production

1. **Authentication & Authorization**
2. **Payment Integration**
3. **Real Camera Integration**
4. **Mobile Push Notifications**
5. **Advanced Analytics Dashboard**
6. **Multi-location Support**
7. **API Rate Limiting**
8. **Data Backup & Recovery**

## 📚 Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **React Native Docs**: https://reactnative.dev/
- **OpenCV Python**: https://opencv-python-tutroals.readthedocs.io/
- **YOLO Documentation**: https://docs.ultralytics.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
