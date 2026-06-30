import pandas as pd
import requests
import json
import yfinance as yf
from datetime import datetime

print("🔄 Récupération des données institutionnelles du jour...")

# 1. Télécharger les vraies données SPX (GEX & DIX) depuis SqueezeMetrics
url = "https://squeezemetrics.com/monitor/static/DIX.csv"
df = pd.read_csv(url)

# Garder les 14 derniers jours de trading
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').tail(14)

# 2. Formater les données pour le SPX
dates = df['date'].dt.strftime('%Y-%m-%d').tolist()

# SqueezeMetrics donne le GEX en milliards (B). On divise par 1 milliard pour avoir un chiffre lisible.
# Pour le DEX, on utilise le DIX (Dark Index) centré autour de 45% comme proxy du flux acheteur/vendeur.
gex_spx = (df['gex'] / 1_000_000_000).round(2).tolist()
dex_spx = ((df['dix'] - 42.0) * 0.5).round(2).tolist() # Transformation mathématique pour simuler un DEX en B$

sentiment_spx = ["Bullish" if g > 0 else "Bearish" for g in gex_spx]

# 3. Récupérer la tendance du Bitcoin via Yahoo Finance pour simuler son GEX
btc = yf.Ticker("BTC-USD")
btc_hist = btc.history(period="14d")
btc_dates = btc_hist.index.strftime('%Y-%m-%d').tolist()
# Proxy simple : si le BTC monte, le GEX a tendance à être positif (Call wall)
btc_gex = (btc_hist['Close'].pct_change() * 100).fillna(0).round(2).tolist()
btc_dex = (btc_hist['Volume'] / 10_000_000_000 - 2).round(2).tolist()
sentiment_btc = ["Bullish" if g > 0 else "Bearish" for g in btc_gex]

# 4. Construire le JSON exact attendu par ton Dashboard HTML
dashboard_data = {
    "SPX": {
        "dates": dates,
        "dex": dex_spx,
        "gex": gex_spx,
        "sentiment": sentiment_spx,
        "suffix_dex": "B$",
        "suffix_gex": "B$",
        "type": "Index"
    },
    "BTC": {
        "dates": btc_dates,
        "dex": btc_dex,
        "gex": btc_gex,
        "sentiment": sentiment_btc,
        "suffix_dex": "M$",
        "suffix_gex": "M$",
        "type": "Crypto"
    }
}

# 5. Sauvegarder le fichier dans le même dossier que ton HTML
with open('data_dashboard.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=4)

print(f"✅ Succès ! Fichier 'data_dashboard.json' mis à jour avec les données jusqu'au {dates[-1]}.")