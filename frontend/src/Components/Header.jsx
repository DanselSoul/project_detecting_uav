import React from "react";
import { useNavigate } from "react-router-dom";

export default function Header({ onLogout }) {
  const navigate = useNavigate();

  return (
    <header className="w-full bg-gray-800 text-white px-6 py-4 shadow-md">
      <div className="max-w-[1080px] mx-auto flex justify-between items-center">
        <div
          onClick={() => navigate("/")}
          className="cursor-pointer text-xl font-bold tracking-wide hover:text-purple-400 transition"
        >
          UAV Monitor
        </div>

        <button
          onClick={onLogout}
          className="bg-red-500 px-4 py-2 rounded hover:bg-red-600 transition"
        >
          Выйти
        </button>
      </div>
    </header>
  );
}
