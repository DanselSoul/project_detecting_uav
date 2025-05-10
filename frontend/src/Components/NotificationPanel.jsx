import React, { useState } from "react";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";
import { useNavigate } from "react-router-dom";

export default function NotificationPanel() {
  const { alertMap } = useWebSocket();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const entries = Object.entries(alertMap).filter(([_, ids]) => ids.length);

  return (
    <div className="fixed bottom-20 right-6 z-50"> {/* ⬅️ смещено выше футера */}
      <button
        onClick={() => setOpen(!open)}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow-lg"
      >
        {open ? "Скрыть уведомления" : `Уведомления (${entries.length})`}
      </button>

      {open && (
        <div className="mt-2 w-80 max-h-64 overflow-y-auto bg-white text-black rounded shadow-xl border border-gray-300">
          <div className="p-3 font-bold border-b">Неподтверждённые события</div>
          {entries.length === 0 ? (
            <div className="p-3 text-gray-500">Нет новых уведомлений</div>
          ) : (
            entries.map(([camId, trackIds]) =>
              trackIds.map((tid) => (
                <div
                  key={`${camId}-${tid}`}
                  onClick={() => navigate(`/camera/${camId}`)}
                  className="cursor-pointer px-4 py-2 hover:bg-gray-100 border-b text-sm"
                >
                  Камера {camId}: Объект {tid}
                </div>
              ))
            )
          )}
        </div>
      )}
    </div>
  );
}
