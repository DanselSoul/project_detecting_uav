import React, { useState } from "react";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";
import { useNavigate } from "react-router-dom";

export default function NotificationPanel() {
  const { alertMap, clearTrack } = useWebSocket();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const entries = Object.entries(alertMap).filter(([_, ids]) => ids.length);
  const totalCount = entries.reduce((acc, [_, ids]) => acc + ids.length, 0);

  const handleValidate = async (cam, trackId, validated) => {
    const message = validated
      ? "Вы уверены, что хотите подтвердить обнаружение?"
      : "Вы уверены, что хотите отклонить обнаружение?";

    if (!window.confirm(message)) return;

    try {
      const res = await fetch("http://localhost:8000/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cam,
          track_id: trackId,
          validated,
          comment: validated ? "Подтверждено из панели" : "Отклонено из панели",
          decision_source: "notification_panel",
        }),
      });

      if (res.ok) {
        clearTrack(cam, trackId); // убрать из UI
      } else {
        alert("Ошибка при подтверждении");
      }
    } catch (e) {
      alert("Сервер недоступен");
    }
  };

  return (
    <div className="fixed bottom-20 right-6 z-50">
      <button
        onClick={() => setOpen(!open)}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow-lg"
      >
        {open ? "Скрыть уведомления" : `Уведомления (${totalCount})`}
      </button>

      {open && (
        <div className="mt-2 w-96 max-h-64 overflow-y-auto bg-white text-black rounded shadow-xl border border-gray-300">
          <div className="p-3 font-bold border-b">Неподтверждённые события</div>
          {totalCount === 0 ? (
            <div className="p-3 text-gray-500">Нет новых уведомлений</div>
          ) : (
            entries.map(([camId, trackIds]) =>
              trackIds.map((tid) => (
                <div
                  key={`${camId}-${tid}`}
                  className="flex items-center justify-between px-4 py-2 hover:bg-gray-100 border-b text-sm"
                >
                  <span
                    className="cursor-pointer text-blue-700 underline"
                    onClick={() => navigate(`/camera/${camId}`)}
                  >
                    Камера {camId}: Объект {tid}
                  </span>

                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleValidate(Number(camId), tid, true)}
                      className="text-green-600 hover:text-green-800"
                      title="Подтвердить"
                    >
                      ✔
                    </button>
                    <button
                      onClick={() => handleValidate(Number(camId), tid, false)}
                      className="text-red-600 hover:text-red-800"
                      title="Отклонить"
                    >
                      ✖
                    </button>
                  </div>
                </div>
              ))
            )
          )}
        </div>
      )}
    </div>
  );
}
