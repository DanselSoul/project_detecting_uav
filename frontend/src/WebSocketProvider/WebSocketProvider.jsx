import React, { createContext, useContext, useEffect, useRef, useState } from "react";

const WebSocketContext = createContext();
export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [alertMap, setAlertMap] = useState({});
  const [alarms, setAlarms] = useState(new Set());
  const ws = useRef(null);
  const isConnected = useRef(false);

  const connectWebSocket = () => {
    if (isConnected.current) return;

    console.log("[WebSocket] Connecting...");
    ws.current = new WebSocket("ws://localhost:8000/ws/alerts");
    isConnected.current = true;

    ws.current.onopen = () => {
      console.log("[WebSocket] Connected");
    };

    ws.current.onmessage = (event) => {
      const data = event.data;
      console.log("[WebSocket] Received:", data);

      if (data.startsWith("camera ")) {
        const match = data.match(/camera (\d+): track (\d+)/);
        if (match) {
          const cam = parseInt(match[1], 10);
          const trackId = parseInt(match[2], 10);

          setAlertMap((prev) => {
            const updated = structuredClone(prev);
            if (!updated[cam]) updated[cam] = [];
            if (!updated[cam].includes(trackId)) {
              updated[cam].push(trackId);
            }
            return updated;
          });
        }
      } else if (data.startsWith("alarm_start")) {
        const match = data.match(/camera (\d+)/);
        if (match) {
          const cam = parseInt(match[1], 10);
          console.log("[WebSocket] Parsed alarm_start for cam", cam);
          setAlarms((prev) => new Set(prev).add(cam));
        }
      } else if (data.startsWith("alarm_stop")) {
        const match = data.match(/camera (\d+)/);
        if (match) {
          const cam = parseInt(match[1], 10);
          console.log("[WebSocket] Parsed alarm_stop for cam", cam);
          setAlarms((prev) => {
            const next = new Set(prev);
            next.delete(cam);
            return next;
          });
        }
      }
    };

    ws.current.onclose = () => {
      console.warn("[WebSocket] Disconnected. Reconnecting in 1s...");
      isConnected.current = false;
      setTimeout(connectWebSocket, 1000);
    };

    ws.current.onerror = (err) => {
      console.error("[WebSocket] Error:", err);
      ws.current.close();
    };
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      ws.current?.close();
      isConnected.current = false;
    };
  }, []);

  const clearTrack = (camId, trackId) => {
    setAlertMap((prev) => {
      const updated = { ...prev };
      if (updated[camId]) {
        updated[camId] = updated[camId].filter((tid) => tid !== trackId);
        if (updated[camId].length === 0) {
          delete updated[camId];
        }
      }
      return updated;
    });
  };

  const stopAlarm = (camId) => {
    setAlarms((prev) => {
      const next = new Set(prev);
      next.delete(camId);
      return next;
    });
  };

  return (
    <WebSocketContext.Provider
      value={{ alertMap, alarms: Array.from(alarms), clearTrack, stopAlarm }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
