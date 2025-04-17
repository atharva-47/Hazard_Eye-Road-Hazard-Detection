import { useEffect, useRef, useState } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './LiveMode.css';
import HazardNotifier from './HazardNotifier';
import NearbyHazardNotifier from './NearbyHazardNotifier';
import EmergencyBrakeNotifier from './EmergencyBrakeNotifier';

export default function LiveMode() {
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const alertRef = useRef(null);
  const cooldownRef = useRef(null);
  const alertSoundRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [hazardDetected, setHazardDetected] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [hazardDistances, setHazardDistances] = useState([]);
  const [driverLaneHazardCount, setDriverLaneHazardCount] = useState(0);

  // Initialize alert sound
  useEffect(() => {
    alertSoundRef.current = new Audio('/alert.mp3');
    alertSoundRef.current.loop = true;
    
    return () => {
      if (alertSoundRef.current) {
        alertSoundRef.current.pause();
        alertSoundRef.current = null;
      }
    };
  }, []);

  // Get current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.watchPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          console.error("Error getting location:", error);
          toast.warning("Location access is needed for hazard reporting");
        }
      );
    } else {
      toast.warning("Geolocation is not supported by this browser");
    }
  }, []);

  const connectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsURL = window.location.origin.replace(/^http/, 'ws') + '/ws';
    wsRef.current = new WebSocket(wsURL);

    wsRef.current.onopen = () => {
      setIsConnected(true);
    };

    wsRef.current.onmessage = (e) => {
      if (typeof e.data === 'string') {
        try {
          const parsedData = JSON.parse(e.data);
          const driverLaneHazardCount = parsedData.driver_lane_hazard_count;
          const hazardDistances = parsedData.hazard_distances || [];
          setHazardDetected({ type: parsedData.hazard_type });
          setDriverLaneHazardCount(driverLaneHazardCount);
          setHazardDistances(hazardDistances);
    
          if (driverLaneHazardCount > 0) {
            if (!alertRef.current) {
              alertRef.current = toast.warning(`⚠️ Road Hazard Detected in Your Lane! \n
                Reducing Speed ......
                `, {
                autoClose: false,
                closeOnClick: false,
                draggable: false,
                onOpen: () => {
                  if (alertSoundRef.current) {
                    alertSoundRef.current.play().catch(err => console.error("Error playing sound:", err));
                  }
                },
                onClose: () => {
                  if (alertSoundRef.current) {
                    alertSoundRef.current.pause();
                    alertSoundRef.current.currentTime = 0;
                  }
                }
              });
            }
            if (cooldownRef.current) {
              clearTimeout(cooldownRef.current);
              cooldownRef.current = null;
            }
          } else {
            if (!cooldownRef.current) {
              cooldownRef.current = setTimeout(() => {
                if (alertRef.current) {
                  toast.dismiss(alertRef.current);
                  alertRef.current = null;
                  if (alertSoundRef.current) {
                    alertSoundRef.current.pause();
                    alertSoundRef.current.currentTime = 0;
                  }
                }
                cooldownRef.current = null;
              }, 3000);
            }
          }
        } catch (err) {
          console.error("WebSocket JSON Error:", err);
        }
      } else if (e.data instanceof Blob) {
        const url = URL.createObjectURL(e.data);
        let processedImg = document.getElementById('processed-feed');
        if (!processedImg) {
          processedImg = document.createElement('img');
          processedImg.id = 'processed-feed';
          processedImg.className = 'processed-feed';
          videoRef.current.after(processedImg);
        }
        
        if (processedImg.src) {
          URL.revokeObjectURL(processedImg.src);
        }
        processedImg.src = url;
      }
    };

    wsRef.current.onerror = () => {
      console.error("WebSocket error. Attempting to reconnect...");
      setIsConnected(false);
    };

    wsRef.current.onclose = () => {
      console.warn("WebSocket closed. Reconnecting in 3 seconds...");
      setIsConnected(false);
      setTimeout(connectWebSocket, 3000);
    };
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      const processedImg = document.getElementById('processed-feed');
      if (processedImg) {
        if (processedImg.src) {
          URL.revokeObjectURL(processedImg.src);
        }
        processedImg.remove();
      }
    };
  }, []);

  const handleNotificationSent = (hazard, response) => {
    if (response.success) {
      toast.success(`Hazard reported to authorities (ID: ${response.report_id.substring(0, 8)})`);
    }
  };

  return (
    <div className="live-container">
      <h1>Live Road Hazard Detection</h1>
      
      <div className="camera-status">
        Backend Camera (YOLO Detection Active)
      </div>

      <div className="content-grid">
        <div className="feed-column">
          <div className="video-container">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className="live-feed"
            />
          </div>
        </div>

        <div className="map-column">
          <iframe
            src="/Map.html"
            title="Road Hazard Map"
            className="map-iframe"
            allowFullScreen
          />
        </div>
      </div>

      <HazardNotifier 
        isConnected={isConnected}
        hazardDetected={hazardDetected}
        currentLocation={currentLocation}
        onNotificationSent={handleNotificationSent}
      />

      {/* NearbyHazardNotifier now handles pothole notifications */}
      <NearbyHazardNotifier currentLocation={currentLocation} />

      <EmergencyBrakeNotifier 
        hazardDistances={hazardDistances}
        driverLaneHazardCount={driverLaneHazardCount}
      />
      
      <ToastContainer />
    </div>
  );
}