import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import CaseViewer from "./pages/CaseViewer";
import Login from "./pages/Login";
import ProtectedRoute from "./ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
      <Route path="/login" element={<Login />} />
      <Route
            path="/case/:filename"
            element={
              <ProtectedRoute>
                <CaseViewer />
              </ProtectedRoute>
            }
          />
    </Routes>
  );
}