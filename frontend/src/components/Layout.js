import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";

const Layout = () => {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  return (
    <div className={`min-h-screen ${isHomePage ? '' : 'bg-spa-dark'}`}>
      <Header />
      
      <main>
        <Outlet />
      </main>
      
      {isHomePage && (
        <div className="transparent-footer-bar" id="transparent-footer">
          {/* Empty transparent bar - positioned below Buddha image */}
        </div>
      )}
      
      <Footer />
    </div>
  );
};

export default Layout;