// components/AlarmBanner.jsx
import React, { useEffect, useRef } from "react";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";

export const AlarmBanner = ({ cameraId }) => {
  const audioRef = useRef();
  const { alarms, stopAlarm } = useWebSocket();
  const active = alarms.includes(cameraId);

  useEffect(() => {
    if (active) {
      audioRef.current?.play();
    } else {
      audioRef.current?.pause();
      audioRef.current.currentTime = 0;
    }
  }, [active]);

  if (!active) return null;
  return (
    <div className="bg-red-600 text-white p-4 mb-4 rounded shadow-lg flex justify-between items-center">
      <span>Тревога! Обнаружение на камере {cameraId}!</span>
      <button
        onClick={() => stopAlarm(cameraId)}
        className="bg-white text-red-600 px-3 py-1 rounded"
      >
        Остановить
      </button>
      {/* невидимый аудиоэлемент */}
      <audio ref={audioRef} src="/alarm.wav" loop />
    </div>
  );
};
