import React from "react";
import "./Play.css";
import { useNavigate } from "react-router-dom";

type HintKeys = "price" | "day_high" | "day_low" | "avg_volume" | "market_cap";
type HintMap = Partial<Record<HintKeys, number>>;

type GuessRow = {
  ticker: string;
  hints: HintMap;
};

const STAT_LABELS: Record<HintKeys, string> = {
  price: "Price",
  day_high: "High",
  day_low: "Low",
  avg_volume: "Avg Vol",
  market_cap: "Mkt Cap",
};

export default function Play() {
  const navigate = useNavigate();

  const [guess, setGuess] = React.useState("");
  const [rows, setRows] = React.useState<GuessRow[]>([]);
  const [triesLeft, setTriesLeft] = React.useState<number | null>(null);
  const [status, setStatus] = React.useState("");
  const [finished, setFinished] = React.useState(false);
  const [won, setWon] = React.useState<boolean | null>(null);

  async function submitGuess() {
    const ticker = guess.trim().toUpperCase();
    if (!ticker || finished) return;

    setStatus("");
    try {
      const res = await fetch("/api/guess", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker }),
      });

      const ctype = res.headers.get("content-type") ?? "";

      if (ctype.includes("application/json")) {
        const data: any = await res.json();

        if (data?.ok && data?.data) {
          setRows((prev) => [{ ticker, hints: data.data as HintMap }, ...prev]);
          const left = typeof data["guesses left"] === "number" ? data["guesses left"] : null;
          setTriesLeft(left);
          if (left !== null && left <= 0) {
            await endState();
          }
        } else if (data?.ok && typeof data?.win === "boolean") {
          handleEnd(data.win, Number(data.guesses ?? rows.length));
        } else {
          await endState();
        }
      } else {
        await endState();
      }
      setGuess("");
    } catch (e: any) {
      setStatus(e?.message || "Guess failed.");
    }
  }

  async function endState() {
    try {
      const r = await fetch("/api/end", { method: "POST", credentials: "include" });
      const d: any = await r.json().catch(() => ({}));
      if (d?.ok) handleEnd(Boolean(d.win), Number(d.guesses ?? rows.length));
      else setFinished(true);
    } catch {
      setFinished(true);
    }
  }

  function handleEnd(win: boolean, _total: number) {
    setFinished(true);
    setWon(win);
    setStatus(win ? "You got it! 🎉" : "Out of guesses. Try again tomorrow.");
    setTriesLeft(0);
  }

  function Tile({ label, val }: { label: string; val: number | undefined }) {
    if (val == null) return <div className="tile">–</div>;
    if (Math.abs(val) < 1e-9) return <div className="tile good">✓<span className="tHint">{label}</span></div>;
    const up = val < 0;
    const pct = `${(Math.abs(val) * 100).toFixed(1)}%`;
    const cls = Math.abs(val) <= 0.02 ? "tile good" : Math.abs(val) <= 0.05 ? "tile warn" : "tile bad";
    return (
      <div className={cls}>
        {up ? "↑" : "↓"} {pct}
        <span className="tHint">{label}</span>
      </div>
    );
  }

  return (
    <div className="game">
      <header className="gameHeader">
        <button className="btnGhost" onClick={() => navigate("/")}>← Home</button>
        <h1 className="gameTitle">Tickdle</h1>
        <div className="tries">{triesLeft == null ? "" : `${triesLeft} left`}</div>
      </header>

      <div className="chartMask">
        <img
          src="/api/chart"
          alt="Daily candlestick chart"
          className="chartBig"
          onError={() => setStatus("Failed to load chart.")}
        />
      </div>

      <div className="inputRow">
        <input
          className="bigInput"
          placeholder="Guess the ticker (AAPL)"
          value={guess}
          onChange={(e) => setGuess(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && submitGuess()}
          autoFocus
          inputMode="text"
          autoComplete="off"
          disabled={finished}
          aria-label="Guess ticker"
        />
        <button className="bigBtn" onClick={submitGuess} disabled={!guess.trim() || finished}>
          Guess
        </button>
      </div>

      {status && <div className="banner">{status}</div>}

      <div className="board">
        {rows.length === 0 && <div className="muted">No guesses yet.</div>}
        {rows.map((r, i) => (
          <div className="row" key={`${r.ticker}-${i}`}>
            <div className="rowLabel">{r.ticker}</div>
            <div className="tiles">
              <Tile label={STAT_LABELS.price}       val={r.hints.price} />
              <Tile label={STAT_LABELS.day_high}    val={r.hints.day_high} />
              <Tile label={STAT_LABELS.day_low}     val={r.hints.day_low} />
              <Tile label={STAT_LABELS.avg_volume}  val={r.hints.avg_volume} />
              <Tile label={STAT_LABELS.market_cap}  val={r.hints.market_cap} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
