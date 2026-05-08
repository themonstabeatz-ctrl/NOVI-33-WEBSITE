import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { API_BASE } from "./config/api";

// 🔐 LOG HARD LOCKED BACKEND ON APP START
console.log("🔐 LOCKED API_BASE =", API_BASE);

// ✅ FIX: Navigate with query params preserved
const NavigateWithParams = ({ to }) => {
  const location = useLocation();
  return <Navigate to={`${to}${location.search}`} replace />;
};
import { LanguageProvider } from "./context/LanguageContext";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Massage from "./pages/Massage";
import Spa from "./pages/Spa";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Gallery from "./pages/Gallery";
import Termini from "./pages/Termini";
import HeadSpa from "./pages/HeadSpa";
import { Toaster } from "./components/ui/sonner";
import BackendHealthCheck from "./components/BackendHealthCheck";
import ScrollManager from "./components/ScrollManager";

function App() {
  return (
    <div className="App">
      <BackendHealthCheck>
      <LanguageProvider>
        <BrowserRouter>
          <ScrollManager />
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="en" element={<Home lang="en" />} />
              <Route path="massage" element={<Massage />} />
              <Route path="masaze" element={<Massage />} />
              <Route path="spa" element={<Spa />} />
              <Route path="about" element={<About />} />
              <Route path="o-nama" element={<About />} />
              <Route path="contact" element={<Contact />} />
              {/* REMOVED: <Route path="booking" element={<Contact />} /> */}
              <Route path="galerija" element={<Gallery />} />
              <Route path="gallery" element={<Gallery />} />
              <Route path="termini" element={<Termini />} />
              <Route path="appointments" element={<Termini />} />
              <Route path="head-spa" element={<HeadSpa />} />
              
              {/* Serbian URL Aliases - 301 Redirects with query params preserved */}
              <Route path="usluge" element={<Navigate to="/masaze" replace />} />
              <Route path="cenovnik" element={<Navigate to="/spa" replace />} />
              <Route path="rezervacije" element={<NavigateWithParams to="/contact" />} />
              <Route path="vauceri" element={<NavigateWithParams to="/contact" />} />
              <Route path="kontakt" element={<NavigateWithParams to="/contact" />} />
              
              {/* REMOVED: Old /booking route */}
              <Route path="booking" element={<NavigateWithParams to="/contact" />} />
              
              {/* English URL Aliases - 301 Redirects with query params preserved */}
              <Route path="en/services" element={<Navigate to="/massage" replace />} />
              <Route path="en/pricing" element={<Navigate to="/spa" replace />} />
              <Route path="en/booking" element={<NavigateWithParams to="/contact" />} />
              <Route path="en/vouchers" element={<NavigateWithParams to="/contact" />} />
              <Route path="en/contact" element={<NavigateWithParams to="/contact" />} />
            </Route>
          </Routes>
          <Toaster 
            theme="dark"
            position="bottom-right"
            toastOptions={{
              style: {
                background: 'rgba(212, 175, 55, 0.1)',
                borderColor: 'rgba(212, 175, 55, 0.3)',
                color: '#f5f2e8',
              },
            }}
          />
        </BrowserRouter>
      </LanguageProvider>
      </BackendHealthCheck>
    </div>
  );
}

export default App;
