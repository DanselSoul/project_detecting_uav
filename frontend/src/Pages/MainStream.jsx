import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";
import Header from "../Components/Header";
import Footer from "../Components/Footer";
import { AlarmBanner } from "../Components/AlarmBanner";
import NotificationPanel from "../Components/NotificationPanel";
import LatestDetectionsModal from "../Components/LatestDetectionsModal";

export default function MainStream({ onLogout }) {
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();
  const { alertMap, alarms, stopAlarm } = useWebSocket();

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <Header onLogout={onLogout} />

      {/* Кнопка для открытия модалки */}
      <div className="p-4 text-right max-w-[1080px] mx-auto w-full">
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded"
        >
          Показать последние обнаружения
        </button>
      </div>

      {/* Контролируемый модал LatestDetections */}
      <LatestDetectionsModal
        visible={showModal}
        onClose={() => setShowModal(false)}
      />

      <main className="flex-grow px-4 py-6 max-w-[1080px] mx-auto w-full">
        <h1 className="text-2xl font-bold mb-6">Потоки с камер</h1>

        {alarms.map((cam) => (
          <AlarmBanner
            key={`alarm-${cam}`}
            cameraId={cam}
            onStop={() => stopAlarm(cam)}
          />
        ))}

        <div className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(500px,1fr))]">
          {[1,2,3,4].map((i) => (
            <div
              key={i}
              onClick={() => navigate(`/camera/${i}`)}
              className={`cursor-pointer rounded-lg overflow-hidden transition border-4 ${
                alertMap[i]?.length ? "border-red-600" : "border-gray-700"
              }`}
            >
              <div className="aspect-[16/9] bg-black">
                <img
                  src={`http://localhost:8000/video-feed?cam=${i}`}
                  alt={`Камера ${i}`}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="p-3 text-center bg-gray-800">Камера {i}</div>
            </div>
          ))}
        </div>
      </main>

      <NotificationPanel />

      <Footer />
    </div>
  );
}
