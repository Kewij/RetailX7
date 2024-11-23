import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Products from "./pages/Products";

function App() {
  return (
    <Router>
      <nav style={{ padding: "10px", background: "#ddd" }}>
        <Link to="/" style={{ marginRight: "10px" }}>Accueil</Link>
        <Link to="/products">Produits</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
      </Routes>
    </Router>
  );
}

export default App;
