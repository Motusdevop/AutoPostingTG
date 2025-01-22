import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Channels from "./pages/Channels";
import ChannelForm from "./pages/ChannelForm";
import Login from "./pages/Login";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Navigate to="/channels" replace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/channels"
            element={
              <ProtectedRoute>
                <Channels />
              </ProtectedRoute>
            }
          />
          <Route
            path="/channels/new"
            element={
              <ProtectedRoute>
                <ChannelForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/channels/:id/edit"
            element={
              <ProtectedRoute>
                <ChannelForm />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;