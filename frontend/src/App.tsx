import React from "react";
import "./App.css";
import bgUrl from "./assets/candlestick.jpeg";

export default function App() {
  const [loading, setLoading] = React.useState(false);
  const [status, setStatus] = React.useState<string>("");

  async function startGame() {
    setLoading(true);
    setStatus("");
    try {
      const res = await fetch("/api/start", {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || "Failed to start");
      }
      // implement navigate("/play")
    } catch (err: any) {
      setStatus(`Error: ${err?.message || "Could not start the game"}`);
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="bg">
      <img className="bgImg" src={bgUrl} alt="" aria-hidden />
      <div className="bgOverlay" aria-hidden />

      <main className="wrap" role="main">
        <h1 className="title">Tickdle</h1>
        <p className="sub">Guess today’s stock in as few tries as possible. New ticker daily.</p>
        <button className="btn" onClick={startGame} disabled={loading} aria-busy={loading}>
          {loading ? "Starting…" : "Start Game"}
        </button>
        {status && <div className="status" role="status">{status}</div>}
      </main>
    </div>
  );
}