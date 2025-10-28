import "./App.css";

export default function Play() {
  return (
    <div className="bg">
      <img className="bgImg" src="/background.jpg" alt="" aria-hidden />
      <div className="bgOverlay" aria-hidden />

      <main className="wrap" role="main">
        <h1 className="title">Play</h1>
        <p className="sub">Your game UI goes here.</p>
      </main>
    </div>
  );
}