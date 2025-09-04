"""
Vision Processing Module

This module provides computer vision capabilities for the AI NPC system,
including object detection, face recognition, and environment analysis.
"""

import asyncio
import logging
import json
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum, auto
import cv2
import mss
from PIL import Image

logger = logging.getLogger(__name__)

class VisionBackend(Enum):
    """Available computer vision backends."""
    OPENCV = auto()
    YOLO = auto()
    TENSORFLOW = auto()
    TORCHVISION = auto()
    MEDIAPIPE = auto()

@dataclass
class VisionConfig:
    """Configuration for vision processing."""
    backend: VisionBackend = VisionBackend.OPENCV
    model_path: Optional[str] = None
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    frame_width: int = 640
    frame_height: int = 480
    frame_rate: int = 30
    device: str = "cpu"  # or "cuda" for GPU
    classes: List[str] = field(default_factory=list)
    api_keys: Dict[str, str] = field(default_factory=dict)

@dataclass
class Detection:
    """Represents a detected object."""
    label: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # x, y, width, height
    class_id: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

class VisionProcessor:
    """Handles computer vision tasks for the AI NPC."""
    
    def __init__(self, config: Optional[VisionConfig] = None):
        """Initialize the vision processor."""
        self.config = config or VisionConfig()
        self.model = None
        self.sct = mss.mss()
        self.is_processing = False
        self._callbacks = []
        self._stop_processing = False
        
        # Initialize the selected backend
        self._init_backend()
    
    def _init_backend(self):
        """Initialize the selected computer vision backend."""
        try:
            if self.config.backend == VisionBackend.OPENCV:
                self._init_opencv()
            elif self.config.backend == VisionBackend.YOLO:
                self._init_yolo()
            elif self.config.backend == VisionBackend.TENSORFLOW:
                self._init_tensorflow()
            elif self.config.backend == VisionBackend.TORCHVISION:
                self._init_torchvision()
            elif self.config.backend == VisionBackend.MEDIAPIPE:
                self._init_mediapipe()
            else:
                logger.warning(f"Unsupported vision backend: {self.config.backend}")
        except ImportError as e:
            logger.error(f"Failed to initialize vision backend: {e}")
            raise
    
    def _init_opencv(self):
        """Initialize OpenCV-based object detection."""
        try:
            # Check if we have a custom model
            if self.config.model_path and self.config.model_path.endswith(('.pb', '.pbtxt')):
                # Load a TensorFlow model
                self.model = cv2.dnn_DetectionModel(
                    self.config.model_path + '.pb',
                    self.config.model_path + '.pbtxt'
                )
                self.model.setInputSize(self.config.frame_width, self.config.frame_height)
                self.model.setInputScale(1.0 / 127.5)
                self.model.setInputMean((127.5, 127.5, 127.5))
                self.model.setInputSwapRB(True)
            else:
                # Use a pre-trained model
                model_file = self.config.model_path or "frozen_inference_graph.pb"
                config_file = (self.config.model_path or "ssd_mobilenet_v3_large_coco_2020_01_14") + ".pbtxt"
                
                if not os.path.exists(model_file) or not os.path.exists(config_file):
                    logger.warning("Model files not found, using default COCO model")
                    # Try to download the model if not found
                    import urllib.request
                    import os
                    
                    base_url = "https://github.com/opencv/opencv_extra/raw/master/testdata/dnn/"
                    if not os.path.exists(model_file):
                        urllib.request.urlretrieve(
                            base_url + "frozen_inference_graph.pb",
                            "frozen_inference_graph.pb"
                        )
                    if not os.path.exists(config_file):
                        urllib.request.urlretrieve(
                            base_url + "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt",
                            "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
                        )
                
                self.model = cv2.dnn_DetectionModel(
                    "frozen_inference_graph.pb",
                    "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
                )
                
                # Load COCO class names
                classes_file = "coco.names"
                if not os.path.exists(classes_file):
                    urllib.request.urlretrieve(
                        "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names",
                        classes_file
                    )
                
                with open(classes_file, 'rt') as f:
                    self.config.classes = f.read().rstrip('\n').split('\n')
                
                # Set model parameters
                self.model.setInputSize(320, 320)
                self.model.setInputScale(1.0 / 127.5)
                self.model.setInputMean((127.5, 127.5, 127.5))
                self.model.setInputSwapRB(True)
            
            logger.info("Initialized OpenCV vision backend")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenCV backend: {e}")
            raise
    
    def _init_yolo(self):
        """Initialize YOLO-based object detection."""
        try:
            import torch
            from models.experimental import attempt_load
            from utils.general import non_max_suppression, scale_coords
            from utils.torch_utils import select_device
            
            # Select device
            self.device = select_device(self.config.device)
            
            # Load model
            model_path = self.config.model_path or 'yolov5s.pt'
            self.model = attempt_load(model_path, map_location=self.device)
            self.stride = int(self.model.stride.max())  # model stride
            
            # Get class names
            if hasattr(self.model, 'module'):
                self.names = self.model.module.names
            else:
                self.names = self.model.names
            
            logger.info("Initialized YOLO vision backend")
            
        except ImportError as e:
            logger.error("YOLOv5 not available. Install with: pip install -r requirements.txt")
            raise
    
    def _init_tensorflow(self):
        """Initialize TensorFlow-based object detection."""
        try:
            import tensorflow as tf
            from object_detection.utils import label_map_util
            from object_detection.utils import config_util
            from object_detection.builders import model_builder
            
            # Load pipeline config and build a detection model
            configs = config_util.get_configs_from_pipeline_file(self.config.model_path + ".config")
            self.model = model_builder.build(model_config=configs['model'], is_training=False)
            
            # Restore checkpoint
            ckpt = tf.compat.v2.train.Checkpoint(model=self.model)
            ckpt.restore(self.config.model_path + "/ckpt-0").expect_partial()
            
            # Load label map
            label_map = label_map_util.load_labelmap(self.config.model_path + "/label_map.pbtxt")
            categories = label_map_util.convert_label_map_to_categories(
                label_map, max_num_classes=label_map_util.get_max_label_map_index(label_map))
            self.category_index = label_map_util.create_category_index(categories)
            
            logger.info("Initialized TensorFlow vision backend")
            
        except ImportError as e:
            logger.error("TensorFlow Object Detection API not available. Install with: pip install tensorflow")
            raise
    
    def _init_torchvision(self):
        """Initialize TorchVision-based object detection."""
        try:
            import torch
            import torchvision
            from torchvision.models.detection import fasterrcnn_resnet50_fpn
            from torchvision import transforms
            
            # Load a pre-trained model
            self.model = fasterrcnn_resnet50_fpn(pretrained=True)
            self.model.eval()
            
            # Define the image transformation
            self.transform = transforms.Compose([
                transforms.ToTensor(),
            ])
            
            # Load COCO class names
            self.coco_names = [
                '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
                'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
                'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
                'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
                'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
                'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
                'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
                'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
                'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
                'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
            ]
            
            logger.info("Initialized TorchVision vision backend")
            
        except ImportError as e:
            logger.error("TorchVision not available. Install with: pip install torch torchvision")
            raise
    
    def _init_mediapipe(self):
        """Initialize MediaPipe for face, hand, and pose detection."""
        try:
            import mediapipe as mp
            
            # Initialize MediaPipe solutions
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_hands = mp.solutions.hands
            self.mp_pose = mp.solutions.pose
            self.mp_holistic = mp.solutions.holistic
            
            # Create instances
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 0 for short-range, 1 for full-range
                min_detection_confidence=0.5
            )
            
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.holistic = self.mp_holistic.Holistic(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            logger.info("Initialized MediaPipe vision backend")
            
        except ImportError as e:
            logger.error("MediaPipe not available. Install with: pip install mediapipe")
            raise
    
    async def capture_screen(self) -> np.ndarray:
        """Capture the screen as a numpy array."""
        try:
            # Get the screen size
            monitor = self.sct.monitors[1]  # Primary monitor
            
            # Capture the screen
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Convert from BGRA to BGR (remove alpha channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Resize if needed
            if img.shape[1] != self.config.frame_width or img.shape[0] != self.config.frame_height:
                img = cv2.resize(img, (self.config.frame_width, self.config.frame_height))
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return np.zeros((self.config.frame_height, self.config.frame_width, 3), dtype=np.uint8)
    
    async def process_frame(self, frame: np.ndarray) -> List[Detection]:
        """Process a single frame and return detections."""
        if self.config.backend == VisionBackend.OPENCV:
            return await self._process_opencv(frame)
        elif self.config.backend == VisionBackend.YOLO:
            return await self._process_yolo(frame)
        elif self.config.backend == VisionBackend.TENSORFLOW:
            return await self._process_tensorflow(frame)
        elif self.config.backend == VisionBackend.TORCHVISION:
            return await self._process_torchvision(frame)
        elif self.config.backend == VisionBackend.MEDIAPIPE:
            return await self._process_mediapipe(frame)
        else:
            logger.warning(f"Unsupported vision backend: {self.config.backend}")
            return []
    
    async def _process_opencv(self, frame: np.ndarray) -> List[Detection]:
        """Process a frame using OpenCV."""
        if self.model is None:
            return []
        
        try:
            # Run detection
            class_ids, confidences, boxes = self.model.detect(
                frame, 
                confThreshold=self.config.confidence_threshold,
                nmsThreshold=self.config.nms_threshold
            )
            
            # Convert to detections
            detections = []
            if len(class_ids) > 0:
                for i in range(len(class_ids)):
                    class_id = int(class_ids[i])
                    confidence = float(confidences[i])
                    box = boxes[i].tolist()
                    
                    # Get class name
                    label = self.config.classes[class_id] if class_id < len(self.config.classes) else str(class_id)
                    
                    detections.append(Detection(
                        label=label,
                        confidence=confidence,
                        bbox=box,
                        class_id=class_id
                    ))
            
            return detections
            
        except Exception as e:
            logger.error(f"OpenCV detection failed: {e}")
            return []
    
    async def _process_yolo(self, frame: np.ndarray) -> List[Detection]:
        """Process a frame using YOLO."""
        if self.model is None:
            return []
        
        try:
            import torch
            from utils.general import non_max_suppression, scale_coords
            
            # Prepare the image
            img = cv2.resize(frame, (640, 640))
            img = img.transpose(2, 0, 1)  # HWC to CHW
            img = np.ascontiguousarray(img)
            img = torch.from_numpy(img).to(self.device)
            img = img.float() / 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            
            # Run inference
            with torch.no_grad():
                pred = self.model(img)[0]
            
            # Apply NMS
            pred = non_max_suppression(pred, self.config.confidence_threshold, self.config.nms_threshold)
            
            # Process detections
            detections = []
            for i, det in enumerate(pred):  # detections per image
                if det is not None and len(det):
                    # Rescale boxes from img_size to frame size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                    
                    # Convert to Detection objects
                    for *xyxy, conf, cls in reversed(det):
                        x1, y1, x2, y2 = map(int, xyxy)
                        w = x2 - x1
                        h = y2 - y1
                        
                        detections.append(Detection(
                            label=self.names[int(cls)],
                            confidence=float(conf),
                            bbox=(x1, y1, w, h),
                            class_id=int(cls)
                        ))
            
            return detections
            
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            return []
    
    async def _process_tensorflow(self, frame: np.ndarray) -> List[Detection]:
        """Process a frame using TensorFlow Object Detection API."""
        if self.model is None:
            return []
        
        try:
            import tensorflow as tf
            
            # Convert frame to tensor
            input_tensor = tf.convert_to_tensor(frame)
            input_tensor = input_tensor[tf.newaxis, ...]
            
            # Run inference
            detections = self.model(input_tensor)
            
            # Process detections
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy() 
                         for key, value in detections.items()}
            detections['num_detections'] = num_detections
            
            # Filter by confidence
            mask = detections['detection_scores'] >= self.config.confidence_threshold
            boxes = detections['detection_boxes'][mask]
            scores = detections['detection_scores'][mask]
            classes = detections['detection_classes'][mask].astype(np.int32)
            
            # Convert to Detection objects
            result = []
            height, width = frame.shape[:2]
            
            for i in range(len(boxes)):
                y1, x1, y2, x2 = boxes[i]
                
                # Convert from normalized coordinates to pixel coordinates
                x1 = int(x1 * width)
                y1 = int(y1 * height)
                w = int((x2 - x1) * width)
                h = int((y2 - y1) * height)
                
                # Get class name
                class_id = int(classes[i])
                label = self.category_index[class_id]['name'] if class_id in self.category_index else str(class_id)
                
                result.append(Detection(
                    label=label,
                    confidence=float(scores[i]),
                    bbox=(x1, y1, w, h),
                    class_id=class_id
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"TensorFlow detection failed: {e}")
            return []
    
    async def _process_torchvision(self, frame: np.ndarray) -> List[Detection]:
        """Process a frame using TorchVision."""
        if self.model is None:
            return []
        
        try:
            import torch
            
            # Convert frame to tensor
            img_tensor = self.transform(frame)
            img_tensor = img_tensor.unsqueeze(0)
            
            # Run inference
            with torch.no_grad():
                predictions = self.model(img_tensor)
            
            # Process predictions
            detections = []
            for pred in predictions:
                for i in range(len(pred['boxes'])):
                    if pred['scores'][i] >= self.config.confidence_threshold:
                        box = pred['boxes'][i].tolist()
                        x1, y1, x2, y2 = map(int, box)
                        
                        detections.append(Detection(
                            label=self.coco_names[pred['labels'][i]],
                            confidence=float(pred['scores'][i]),
                            bbox=(x1, y1, x2 - x1, y2 - y1),
                            class_id=int(pred['labels'][i])
                        ))
            
            return detections
            
        except Exception as e:
            logger.error(f"TorchVision detection failed: {e}")
            return []
    
    async def _process_mediapipe(self, frame: np.ndarray) -> List[Detection]:
        """Process a frame using MediaPipe."""
        try:
            import mediapipe as mp
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_results = self.face_detection.process(rgb_frame)
            
            # Detect hands
            hand_results = self.hands.process(rgb_frame)
            
            # Detect pose
            pose_results = self.pose.process(rgb_frame)
            
            # Process detections
            detections = []
            
            # Add face detections
            if face_results.detections:
                for detection in face_results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x = int(bbox.xmin * frame.shape[1])
                    y = int(bbox.ymin * frame.shape[0])
                    w = int(bbox.width * frame.shape[1])
                    h = int(bbox.height * frame.shape[0])
                    
                    detections.append(Detection(
                        label="face",
                        confidence=detection.score[0],
                        bbox=(x, y, w, h),
                        class_id=0,
                        extra={
                            'keypoints': [(kp.x * frame.shape[1], kp.y * frame.shape[0]) 
                                        for kp in detection.location_data.relative_keypoints]
                        }
                    ))
            
            # Add hand detections
            if hand_results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                    # Get bounding box
                    landmarks = np.array([(lm.x * frame.shape[1], lm.y * frame.shape[0]) 
                                        for lm in hand_landmarks.landmark])
                    x, y = landmarks.min(axis=0).astype(int)
                    w, h = (landmarks.max(axis=0) - landmarks.min(axis=0)).astype(int)
                    
                    # Determine handedness
                    handedness = "left"
                    if hand_results.multi_handedness:
                        handedness = hand_results.multi_handedness[i].classification[0].label.lower()
                    
                    detections.append(Detection(
                        label=f"{handedness}_hand",
                        confidence=1.0,  # MediaPipe doesn't provide confidence for hands
                        bbox=(x, y, w, h),
                        class_id=1 if handedness == "left" else 2,
                        extra={
                            'landmarks': landmarks,
                            'handedness': handedness
                        }
                    ))
            
            # Add pose detections
            if pose_results.pose_landmarks:
                landmarks = np.array([(lm.x * frame.shape[1], lm.y * frame.shape[0])
                                    for lm in pose_results.pose_landmarks.landmark])
                
                # Get bounding box
                if len(landmarks) > 0:
                    x, y = landmarks.min(axis=0).astype(int)
                    w, h = (landmarks.max(axis=0) - landmarks.min(axis=0)).astype(int)
                    
                    detections.append(Detection(
                        label="pose",
                        confidence=1.0,  # MediaPipe doesn't provide confidence for pose
                        bbox=(x, y, w, h),
                        class_id=3,
                        extra={
                            'landmarks': landmarks
                        }
                    ))
            
            return detections
            
        except Exception as e:
            logger.error(f"MediaPipe detection failed: {e}")
            return []
    
    async def start_processing(self, callback: Optional[Callable[[List[Detection], np.ndarray], None]] = None):
        """Start continuous processing of frames."""
        if self.is_processing:
            logger.warning("Already processing frames")
            return
        
        if callback:
            self._callbacks.append(callback)
        
        self.is_processing = True
        self._stop_processing = False
        
        # Start the processing loop in a background task
        asyncio.create_task(self._processing_loop())
    
    async def stop_processing(self):
        """Stop processing frames."""
        self._stop_processing = True
        self.is_processing = False
    
    async def _processing_loop(self):
        """Background task that continuously processes frames."""
        try:
            while not self._stop_processing:
                # Capture a frame
                frame = await self.capture_screen()
                
                # Process the frame
                detections = await self.process_frame(frame)
                
                # Call callbacks
                if self._callbacks:
                    for callback in self._callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(detections, frame)
                            else:
                                callback(detections, frame)
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
                
                # Limit frame rate
                await asyncio.sleep(1.0 / self.config.frame_rate)
                
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
        finally:
            self.is_processing = False
            logger.info("Stopped processing frames")
    
    def add_callback(self, callback: Callable[[List[Detection], np.ndarray], None]):
        """Add a callback function to be called with each processed frame."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[List[Detection], np.ndarray], None]):
        """Remove a callback function."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.stop_processing()
        
        # Clean up MediaPipe resources
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
        if hasattr(self, 'hands'):
            self.hands.close()
        if hasattr(self, 'pose'):
            self.pose.close()
        if hasattr(self, 'holistic'):
            self.holistic.close()

# Example usage
if __name__ == "__main__":
    import asyncio
    import cv2
    
    async def main():
        # Create a vision processor with default settings
        config = VisionConfig(
            backend=VisionBackend.OPENCV,
            confidence_threshold=0.5
        )
        
        async with VisionProcessor(config) as vision:
            # Define a callback to display detections
            def display_detections(detections, frame):
                # Draw detections on the frame
                for detection in detections:
                    x, y, w, h = map(int, detection.bbox)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"{detection.label} {detection.confidence:.2f}",
                              (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Display the frame
                cv2.imshow("Vision Processing", frame)
                cv2.waitKey(1)  # Needed to update the window
            
            # Start processing with the display callback
            await vision.start_processing(display_detections)
            
            # Run for 30 seconds
            logger.info("Running vision processing for 30 seconds...")
            await asyncio.sleep(30)
            
            # Stop processing
            await vision.stop_processing()
            cv2.destroyAllWindows()
    
    asyncio.run(main())
