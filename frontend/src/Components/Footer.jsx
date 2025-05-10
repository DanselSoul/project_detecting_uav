// Components/Footer.jsx
import React from "react";
import { useAuth } from "../auth/useAuth";

export default function Footer() {
  const { username } = useAuth();

  return (
    <footer className="bg-gray-800 text-gray-300 px-6 py-3 text-sm text-center">
      <p>Вы вошли как: <span className="text-white font-medium">{username || "неизвестный пользователь"}</span></p>
    </footer>
  );
}
