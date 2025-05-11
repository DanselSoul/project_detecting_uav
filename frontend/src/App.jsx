import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useAuth } from "./auth/useAuth";
import Login from "./auth/Login";
import ProtectedRoute from "./auth/ProtectedRoute";
import MainStream from "./Pages/MainStream";
import SingleCamera from "./Pages/SingleCamera";

export default function App() {
  const { token, login, logout } = useAuth();

  return (
    <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login onLogin={login} />} />
          <Route
            path="/"
            element={
              <ProtectedRoute token={token}>
                <MainStream onLogout={logout} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/camera/:id"
            element={
              <ProtectedRoute token={token}>
                <SingleCamera />
              </ProtectedRoute>
            }
          />
        </Routes>
    </BrowserRouter>
  );
}
