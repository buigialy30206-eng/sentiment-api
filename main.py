"""
Sentiment Analysis API
VADER sentiment analysis. Offline, free.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI(title="Sentiment Analysis API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
@app.get("/health")
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


@app.get("/health")
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
