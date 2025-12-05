import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import MemeDashboard from "./pages/MemeDashboard";
import MemeReviewPage from "./pages/MemeReviewPage";

export default function App() {
  return (
    <BrowserRouter>
      <header style={{ padding: "12px", borderBottom: "1px solid #eee" }}>
        <nav style={{ display: "flex", gap: "12px" }}>
          <Link to="/">Dashboard</Link>
          <Link to="/review">Review</Link>
        </nav>
      </header>
      <main style={{ padding: "16px" }}>
        <Routes>
          <Route path="/" element={<MemeDashboard />} />
          <Route path="/review" element={<MemeReviewPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
