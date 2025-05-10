import React from "react";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";
import Header from "../Components/Header";
import Footer from "../Components/Footer";
import NotificationPanel from "../Components/NotificationPanel";

const cameras = [1, 2, 3, 4].map((i) => ({
  id: i,
  name: `Камера ${i}`,
  src: `http://localhost:8000/video-feed?cam=${i}`,
}));

export default function MainStream({ onLogout }) {
  const navigate = useNavigate();
  const { alertMap } = useWebSocket();

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <Header onLogout={onLogout} />

      <main className="flex-grow px-4 py-6 max-w-[1080px] mx-auto w-full">
        <h1 className="text-2xl font-bold mb-6">Потоки с камер</h1>
        <div className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(500px,1fr))]">
          {cameras.map((cam) => (
            <div
              key={cam.id}
              onClick={() => navigate(`/camera/${cam.id}`)}
              className={`cursor-pointer rounded-lg overflow-hidden transition border-4 ${
                alertMap[cam.id]?.length ? "border-red-600" : "border-gray-700"
              }`}
            >
              <div className="aspect-[16/9] bg-black">
                <img
                  src={cam.src}
                  alt={cam.name}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="p-3 text-center bg-gray-800">{cam.name}</div>
            </div>
          ))}
        </div>
      </main>
      <NotificationPanel />
      <Footer />
    </div>
  );
}
