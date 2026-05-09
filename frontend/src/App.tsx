import { Routes, Route } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { WinesPage } from "./pages/WinesPage";
import { SuggestionsPage } from "./pages/SuggestionsPage";

export default function App() {
  return (
    <div className="app-layout">
      <NavBar />
      <main className="main">
        <Routes>
          <Route path="/" element={<WinesPage />} />
          <Route path="/suggestions" element={<SuggestionsPage />} />
        </Routes>
      </main>
    </div>
  );
}
