// AlarmBanner.jsx
import React, { useEffect, useRef } from "react";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";

export const AlarmBanner = ({ cameraId }) => {
  const audioRef = useRef();
  const { alarms, stopAlarm } = useWebSocket();
  const active = alarms.includes(cameraId);

  useEffect(() => {
    if (active) audioRef.current?.play();
    else {
      audioRef.current?.pause();
      audioRef.current.currentTime = 0;
    }
  }, [active]);

  if (!active) return null;

  const handleStop = async () => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch("http://localhost:8000/alarm/stop", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ cam: cameraId }),
      });
      if (!res.ok) throw new Error("Не удалось остановить тревогу");
      stopAlarm(cameraId);  // теперь сбрасываем локальное состояние
    } catch (e) {
      console.error(e);
      alert(e.message);
    }
  };

  return (
    <div className="bg-red-600 text-white p-4 mb-4 rounded shadow-lg flex justify-between items-center">
      <span>Тревога! Обнаружение на камере {cameraId}!</span>
      <button onClick={handleStop} className="bg-white text-red-600 px-3 py-1 rounded">
        Остановить
      </button>
      <audio ref={audioRef} src="/alarm.wav" loop />
    </div>
  );
};
