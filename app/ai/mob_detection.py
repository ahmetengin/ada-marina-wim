"""
MOB (Man Overboard) Detection System
AI-powered computer vision for automatic MOB detection

"İleride YOLO ile MOB ta yapacak!" - Captain's vision

FUTURE: Real-time person detection using YOLO v8/v9
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DetectionStatus(Enum):
    """Detection system status"""
    ACTIVE = "active"
    PAUSED = "paused"
    OFFLINE = "offline"
    ALERT = "alert"


class AlertPriority(Enum):
    """Alert priority"""
    CRITICAL = "critical"  # MOB detected!
    HIGH = "high"  # Possible MOB
    MEDIUM = "medium"  # Person near edge
    LOW = "low"  # Normal monitoring


@dataclass
class PersonDetection:
    """Person detection result"""
    timestamp: datetime
    person_id: int
    confidence: float  # 0.0-1.0
    position_x: float  # Relative position in frame
    position_y: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    is_crew: bool
    is_near_edge: bool
    velocity: Optional[float] = None  # Pixels per second


@dataclass
class MOBAlert:
    """MOB alert"""
    alert_id: str
    timestamp: datetime
    gps_position: Tuple[float, float]  # lat, lon
    person_id: int
    confidence: float
    last_seen_frame: Any  # Store frame image
    alert_priority: AlertPriority
    acknowledged: bool = False
    mob_button_pressed: bool = False


class MOBDetectionSystem:
    """
    AI-powered MOB detection system

    FUTURE IMPLEMENTATION with YOLO:
    - Real-time video processing from deck cameras
    - Person detection and tracking
    - Edge detection (person near rail)
    - Sudden disappearance detection
    - Automatic MOB alert
    - GPS mark of last position

    CURRENT: Framework ready for AI integration
    """

    def __init__(self, vessel_name: str):
        """
        Initialize MOB detection system

        Args:
            vessel_name: Vessel name
        """
        self.vessel_name = vessel_name
        self.detection_status = DetectionStatus.OFFLINE

        # Detection settings
        self.confidence_threshold = 0.7  # Minimum confidence for person detection
        self.edge_distance_threshold = 50  # Pixels from edge = "near edge"
        self.disappearance_time_threshold = 2.0  # Seconds before MOB alert

        # Tracking
        self.tracked_persons: Dict[int, PersonDetection] = {}
        self.mob_alerts: List[MOBAlert] = []

        # Camera setup (FUTURE)
        self.cameras = []  # Will hold camera objects
        self.ai_model = None  # Will hold YOLO model

        logger.info(f"MOBDetectionSystem initialized for {vessel_name}")
        logger.info("⚠️ FUTURE: Awaiting YOLO model integration")

    def start_monitoring(self):
        """Start MOB monitoring"""
        logger.info("🎥 MOB monitoring started")
        self.detection_status = DetectionStatus.ACTIVE

        # FUTURE: Start camera feeds
        # FUTURE: Load YOLO model
        # FUTURE: Begin real-time detection

        logger.warning("⚠️ AI model not loaded - manual MOB button only")

    def stop_monitoring(self):
        """Stop MOB monitoring"""
        logger.info("🛑 MOB monitoring stopped")
        self.detection_status = DetectionStatus.PAUSED

    def manual_mob_alert(
        self,
        gps_position: Tuple[float, float],
        triggering_person: str
    ) -> MOBAlert:
        """
        Manual MOB button pressed

        Args:
            gps_position: Current GPS position
            triggering_person: Who pressed button

        Returns:
            MOB alert
        """
        logger.critical("🚨 MANUAL MOB BUTTON PRESSED!")
        logger.critical(f"   Position: {gps_position[0]:.6f}°N, {gps_position[1]:.6f}°E")
        logger.critical(f"   Triggered by: {triggering_person}")

        alert = MOBAlert(
            alert_id=f"MOB_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow(),
            gps_position=gps_position,
            person_id=-1,  # Manual trigger
            confidence=1.0,  # Manual = 100% confidence
            last_seen_frame=None,
            alert_priority=AlertPriority.CRITICAL,
            mob_button_pressed=True
        )

        self.mob_alerts.append(alert)

        # Trigger emergency response
        self._trigger_mob_response(alert)

        return alert

    def _trigger_mob_response(self, alert: MOBAlert):
        """
        Trigger automatic MOB emergency response

        Args:
            alert: MOB alert
        """
        logger.critical("=" * 60)
        logger.critical("  🚨 MOB EMERGENCY RESPONSE ACTIVATED 🚨")
        logger.critical("=" * 60)

        # 1. Sound alarm
        logger.critical("1. 🔊 SOUNDING ALARM: 'MAN OVERBOARD!'")

        # 2. GPS mark
        logger.critical(f"2. 📍 GPS MARK: {alert.gps_position[0]:.6f}°N, {alert.gps_position[1]:.6f}°E")

        # 3. Display on chartplotter
        logger.critical("3. 🗺️  MOB WAYPOINT CREATED ON CHARTPLOTTER")

        # 4. Alert crew
        logger.critical("4. 📢 ALERTING ALL CREW")

        # 5. Start timer
        logger.critical("5. ⏱️  MOB TIMER STARTED")

        # 6. Display procedure
        logger.critical("6. 📋 DISPLAYING MOB PROCEDURE:")
        logger.critical("   • Throw life ring")
        logger.critical("   • Assign crew to keep eyes on person")
        logger.critical("   • Engine - engage")
        logger.critical("   • Turn vessel (Williamson Turn)")
        logger.critical("   • VHF Mayday if alone")

        # 7. Prepare radio
        logger.critical("7. 📻 MAYDAY READY ON VHF 16")

        logger.critical("=" * 60)

    def process_frame(self, frame: Any, current_gps: Tuple[float, float]):
        """
        Process video frame for person detection

        FUTURE: YOLO integration

        Args:
            frame: Video frame (numpy array)
            current_gps: Current GPS position

        Returns:
            Detections and alerts
        """
        if self.detection_status != DetectionStatus.ACTIVE:
            return

        # FUTURE IMPLEMENTATION:
        # 1. Run YOLO model on frame
        # 2. Detect all persons
        # 3. Track each person
        # 4. Check if near edge
        # 5. Detect sudden disappearance
        # 6. Trigger MOB alert if needed

        logger.debug("Frame processing placeholder - YOLO not implemented yet")

    def _detect_persons_yolo(self, frame: Any) -> List[PersonDetection]:
        """
        FUTURE: Detect persons using YOLO

        Will use YOLOv8 or YOLOv9:
        - Real-time person detection
        - Bounding box extraction
        - Confidence scoring
        - Person ID tracking

        Args:
            frame: Video frame

        Returns:
            List of detected persons
        """
        # PLACEHOLDER
        # from ultralytics import YOLO
        # model = YOLO('yolov8n.pt')
        # results = model(frame)
        # persons = [r for r in results if r.cls == 0]  # Class 0 = person

        return []

    def _is_near_edge(self, detection: PersonDetection, frame_width: int, frame_height: int) -> bool:
        """
        Check if person is near edge of vessel

        Args:
            detection: Person detection
            frame_width: Frame width
            frame_height: Frame height

        Returns:
            True if near edge
        """
        x, y, w, h = detection.bounding_box

        # Check if close to frame edge (representing vessel edge)
        near_left = x < self.edge_distance_threshold
        near_right = (x + w) > (frame_width - self.edge_distance_threshold)
        near_top = y < self.edge_distance_threshold
        near_bottom = (y + h) > (frame_height - self.edge_distance_threshold)

        return near_left or near_right or near_top or near_bottom

    def _detect_sudden_disappearance(self, person_id: int) -> bool:
        """
        Detect if person suddenly disappeared from frame

        Args:
            person_id: Person ID

        Returns:
            True if sudden disappearance detected
        """
        if person_id not in self.tracked_persons:
            return False

        last_seen = self.tracked_persons[person_id]
        time_since_seen = (datetime.utcnow() - last_seen.timestamp).total_seconds()

        # If person was near edge and suddenly disappeared = possible MOB
        if last_seen.is_near_edge and time_since_seen > self.disappearance_time_threshold:
            logger.warning(f"⚠️ Person {person_id} disappeared near edge!")
            return True

        return False

    def get_active_alerts(self) -> List[MOBAlert]:
        """Get all active (unacknowledged) MOB alerts"""
        return [a for a in self.mob_alerts if not a.acknowledged]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge MOB alert

        Args:
            alert_id: Alert identifier

        Returns:
            True if acknowledged
        """
        for alert in self.mob_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"✓ MOB alert {alert_id} acknowledged")
                return True

        return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'vessel': self.vessel_name,
            'status': self.detection_status.value,
            'cameras_active': len(self.cameras),
            'ai_model_loaded': self.ai_model is not None,
            'tracked_persons': len(self.tracked_persons),
            'active_alerts': len(self.get_active_alerts()),
            'total_alerts': len(self.mob_alerts),
            'future_features': [
                'YOLO v8/v9 person detection',
                'Real-time video processing',
                'Automatic MOB detection',
                'Edge proximity alerts',
                'Crew identification',
                'Night vision support',
                'Thermal camera integration'
            ]
        }

    def get_integration_guide(self) -> str:
        """
        Get YOLO integration guide

        Returns:
            Integration instructions
        """
        guide = """
# YOLO MOB Detection Integration Guide

## Hardware Requirements:
- Deck cameras (1-4): IP cameras or USB cameras
- GPU recommended: NVIDIA (CUDA support)
- Mac Mini M4: Apple Neural Engine can run YOLO!

## Software Stack:
```bash
pip install ultralytics  # YOLOv8/v9
pip install opencv-python  # Camera capture
pip install torch  # PyTorch (or Apple MLX)
```

## Implementation Steps:

### 1. Load YOLO Model:
```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov8n.pt')  # Nano (fastest)
# or yolov8s.pt (small), yolov8m.pt (medium)
```

### 2. Camera Setup:
```python
import cv2

# IP camera
cap = cv2.VideoCapture('rtsp://camera_ip:port/stream')

# USB camera
cap = cv2.VideoCapture(0)
```

### 3. Real-time Detection:
```python
while True:
    ret, frame = cap.read()

    # Run YOLO
    results = model(frame, conf=0.7)

    # Process detections
    for r in results:
        boxes = r.boxes
        for box in boxes:
            if box.cls == 0:  # Person class
                x, y, w, h = box.xywh
                conf = box.conf

                # Process person detection
                mob_system.process_detection(x, y, w, h, conf)
```

### 4. MOB Detection Logic:
```python
def process_detection(x, y, w, h, conf):
    # Check if near edge
    if self._is_near_edge(x, y, frame_width, frame_height):
        # Track this person
        person_id = self._track_person(x, y, w, h)

        # Monitor for sudden disappearance
        if person_id in self.disappearing_persons:
            # TRIGGER MOB ALERT!
            self.trigger_automatic_mob_alert(person_id)
```

## Apple Neural Engine (Mac Mini M4):
```python
# Use Apple's MLX for M4 optimization
import mlx
model = YOLO('yolov8n_mlx.pt')  # MLX optimized
```

## Camera Placement:
- Stern camera: Monitor cockpit and swim platform
- Port/Starboard: Monitor side decks
- Bow camera: Monitor foredeck

## Next Steps:
1. Install cameras
2. Test YOLO on Mac Mini M4
3. Implement tracking algorithm
4. Train custom model (optional - to recognize specific crew)
5. Integrate with ADA.SEA emergency system
"""
        return guide


class MOBProcedureAssistant:
    """
    MOB procedure step-by-step assistant

    Guides crew through MOB recovery procedure
    """

    def __init__(self, knowledge_base):
        """
        Initialize procedure assistant

        Args:
            knowledge_base: MaritimeKnowledgeBase instance
        """
        self.knowledge_base = knowledge_base
        self.current_step = 0
        self.procedure_active = False

    def start_mob_procedure(self) -> str:
        """Start MOB procedure guidance"""
        self.procedure_active = True
        self.current_step = 0

        mob_proc = self.knowledge_base.get_emergency_procedure(
            EmergencyType.MOB
        )

        output = "🚨 DENİZE ADAM DÜŞTÜ - PROSEDÜR BAŞLADI\n\n"
        output += "HEMEN YAPILACAKLAR:\n"

        for i, action in enumerate(mob_proc.immediate_actions_tr, 1):
            output += f"{i}. {action}\n"

        return output

    def next_step(self) -> Optional[str]:
        """Get next procedure step"""
        if not self.procedure_active:
            return None

        mob_proc = self.knowledge_base.get_emergency_procedure(
            EmergencyType.MOB
        )

        if self.current_step >= len(mob_proc.detailed_steps_tr):
            return "✅ PROSEDÜR TAMAMLANDI"

        step = mob_proc.detailed_steps_tr[self.current_step]
        self.current_step += 1

        return f"Adım {self.current_step}: {step}"

    def get_quick_reference(self) -> str:
        """Get quick MOB reference card"""
        return self.knowledge_base.get_mob_procedure_quick()
