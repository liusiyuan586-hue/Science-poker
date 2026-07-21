import React from "react";
import { createRoot } from "react-dom/client";
import "./app/globals.css";
import "katex/dist/katex.min.css";
import "./app/enhancements.css";
import Home from "./app/page";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Home />
  </React.StrictMode>,
);
