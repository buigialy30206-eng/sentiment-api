"""
Sentiment Analysis API
VADER sentiment analysis. Offline, free.
"""

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI(title="Sentiment Analysis API", version="1.0.0", dependencies=[Depends(_rate_limit)])
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
import time as _t, threading as _th
_rl_win, _rl_max, _rl_hits, _rl_lk = 60, 60, {}, _th.Lock()

async def _rate_limit(request):
    from fastapi import Request, HTTPException
    ip = (request.headers.get('X-Forwarded-For','') or request.headers.get('X-Real-IP','') or (request.client.host if request.client else '127.0.0.1')).split(',')[0].strip()
    now = _t.time()
    with _rl_lk:
        e = _rl_hits.get(ip)
        if e:
            if now - e['s'] > _rl_win: e['s'], e['c'] = now, 1
            else:
                e['c'] += 1
                if e['c'] > _rl_max: raise HTTPException(429, 'Too many requests')
        else: _rl_hits[ip] = {'s': now, 'c': 1}
    return True

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

analyzer = SentimentIntensityAnalyzer()


class SentimentResult(BaseModel):
    text: str
    sentiment: str
    compound: float
    positive: float
    negative: float
    neutral: float


@app.api_route("/health", methods=["GET", "HEAD"])
async def health(): return {"status": "ok"}


@app.get("/")
async def root(): return {"service": "Sentiment Analysis API", "version": "1.0.0"}


@app.get("/analyze", response_model=SentimentResult)
async def analyze(text: str = Query(..., description="Text to analyze")):
    scores = analyzer.polarity_scores(text[:5000])
    compound = scores["compound"]
    if compound >= 0.05: sentiment = "Positive"
    elif compound <= -0.05: sentiment = "Negative"
    else: sentiment = "Neutral"

    return SentimentResult(text=text[:200], sentiment=sentiment, compound=round(compound, 4),
                           positive=round(scores["pos"], 4), negative=round(scores["neg"], 4),
                           neutral=round(scores["neu"], 4))
