import React, { createContext, useContext, useEffect, useRef, useState } from "react";

const WebSocketContext = createContext();
export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [alertMap, setAlertMap] = useState({});

  const ws = useRef(null);

  const connectWebSocket = () => {
    ws.current = new WebSocket("ws://localhost:8000/ws/alerts");

    ws.current.onmessage = (event) => {
      const match = event.data.match(/camera (\d+): track (\d+)/);
      if (!match) return;

      const cam = match[1];
      const trackId = parseInt(match[2]);

      setAlertMap((prev) => {
        const updated = { ...prev };
        if (!updated[cam]) updated[cam] = [];
        if (!updated[cam].includes(trackId)) {
          updated[cam].push(trackId);
        }
        return updated;
      });
    };

    ws.current.onclose = () => {
      setTimeout(connectWebSocket, 1000);
    };
  };

  useEffect(() => {
    connectWebSocket();
    return () => ws.current?.close();
  }, []);

  useEffect(() => {
    localStorage.setItem("alertMap", JSON.stringify(alertMap));
  }, [alertMap]);

  const clearTrack = (camId, trackId) => {
    setAlertMap((prev) => {
      const updated = { ...prev };
      updated[camId] = updated[camId]?.filter((tid) => tid !== trackId);
      if (!updated[camId]?.length) {
        delete updated[camId];
      }
      return updated;
    });
  };

  return (
    <WebSocketContext.Provider value={{ alertMap, clearTrack }}>
      {children}
    </WebSocketContext.Provider>
  );
};
