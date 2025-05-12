import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";
import Header from "../Components/Header";
import Footer from "../Components/Footer";
import { AlarmBanner } from "../Components/AlarmBanner";

export default function SingleCamera({ onLogout }) {
  const { id } = useParams();
  const cam = Number(id) || 1;
  const navigate = useNavigate();
  const { alertMap, clearTrack, alarms, stopAlarm } = useWebSocket();

  const trackIds = alertMap[cam] || [];
  const latestTrackId = trackIds[trackIds.length - 1] || null;
  const showValidation = latestTrackId !== null;

  const [confirmed, setConfirmed] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isLive, setIsLive] = useState(true);

  const sendValidation = async (decision) => {
    if (!latestTrackId) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cam,
          track_id: latestTrackId,
          validated: decision,
          comment: decision
            ? "Подтверждено оператором"
            : "Отклонено оператором",
          decision_source: "operator",
        }),
      });
      if (!res.ok) throw new Error("Ошибка при сохранении");
      setConfirmed(decision);
      clearTrack(cam, latestTrackId);
      stopAlarm(cam); // остановим звук и баннер
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const streamUrl = isLive
    ? `http://localhost:8000/video-feed?cam=${cam}`
    : `http://localhost:8000/replay?cam=${cam}`;

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <Header onLogout={onLogout} />

      {/* Баннер тревоги для этой камеры */}
      {alarms.includes(cam) && (
        <AlarmBanner cameraId={cam} onStop={() => stopAlarm(cam)} />
      )}

      <main className="flex-grow px-4 py-6 max-w-[1280px] mx-auto w-full">
        <div className="flex gap-3 mb-4">
          <button
            onClick={() => navigate(-1)}
            className="bg-blue-500 px-4 py-2 rounded text-white"
          >
            Назад
          </button>
          {!isLive ? (
            <button
              onClick={() => setIsLive(true)}
              className="bg-green-600 px-4 py-2 rounded text-white"
            >
              В прямой эфир
            </button>
          ) : (
            <button
              onClick={() => setIsLive(false)}
              className="bg-yellow-500 px-4 py-2 rounded text-white"
            >
              Показать последние 60 секунд
            </button>
          )}
        </div>

        <h1 className="text-xl mb-4">Камера №{cam}</h1>

        <div className="w-full aspect-[16/9] bg-black rounded overflow-hidden">
          <img
            src={streamUrl}
            alt={`Камера ${cam}`}
            className="w-full h-full object-contain"
          />
        </div>

        {showValidation && confirmed === null && (
          <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-white p-4 rounded shadow-lg z-50 text-black">
            <p className="mb-2 text-red-600">
              Обнаружен объект (ID: {latestTrackId})
            </p>
            <button
              onClick={() => sendValidation(true)}
              disabled={loading}
              className="bg-green-500 text-white px-3 py-1 mr-2 rounded"
            >
              Подтвердить
            </button>
            <button
              onClick={() => sendValidation(false)}
              disabled={loading}
              className="bg-gray-500 text-white px-3 py-1 rounded"
            >
              Отклонить
            </button>
          </div>
        )}

        {confirmed !== null && (
          <p className="mt-4 text-green-400">
            Вы {confirmed ? "подтвердили" : "отклонили"} обнаружение
          </p>
        )}
        {error && <p className="mt-4 text-red-500">Ошибка: {error}</p>}
      </main>

      <Footer />
    </div>
  );
}
