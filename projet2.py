import requests
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

api_cle = "ebf5364ea8ac49fb5d6800dda8ca28ac"

villes = [
    "Paris","Lyon","Marseille","Toulouse","Nice","Nantes","Strasbourg","Montpellier",
    "Bordeaux","Lille","Rennes","Reims","Saint-Etienne","Toulon","Grenoble","Dijon",
    "Angers","Nîmes","Le Havre","Clermont-Ferrand","Limoges","Metz","Besançon","Orléans",
    "Rouen","Caen","Perpignan","Amiens","Annecy","Bayonne","Pau","La Rochelle","Poitiers",
    "Tours","Avignon","Cannes"
]

# juste la requetee api pour recuperer la ville
def obtenir_ville(nom: str, cle=api_cle):
    try:
        base = "http://api.openweathermap.org/geo/1.0/direct?q="
        url = f"{base}{nom}&limit=1&appid={cle}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# pour prendre lat et lon
def geoloc_ville(nom: str):
    data = obtenir_ville(nom)
    if not data:
        return [nom, None, None]
    try:
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        return [nom, lat, lon]
    except:
        return [nom, None, None]

# on boucle et on fait le csv
def geoloc_liste(lst, csv_out="villes_geoloc.csv"):
    lignes = [geoloc_ville(v) for v in lst]
    df = pd.DataFrame(lignes, columns=["ville","lat","lon"])
    df.to_csv(csv_out, index=False, encoding="utf-8-sig")
    return df

# simuler une journee meteo
def simuler_jour():
    t = round(np.random.normal(20,5),1)
    h = int(np.clip(np.random.normal(55,15),20,95))
    pl = round(max(0, np.random.exponential(2)-0.5),1)
    return t,h,pl

# scoore meteo
def score_meteo(t, h, pl):
    st = math.exp(-((t-22)**2)/(2*5**2)) * 5
    ph = max(0,(h-70)/30)
    pp = min(pl/5,1)
    s = st*2 + 5*(1-ph) + 5*(1-pp) - 5
    return round(min(max(s,0),10),2)

#tablleau 7 jours
def construire_meteo(df_villes, csv_out="meteo.csv"):
    np.random.seed(42)
    deb = datetime.today().date()
    rows = []
    for _, r in df_villes.iterrows():
        nom = r["ville"]
        for d in range(7):
            jour = deb + timedelta(days=d)
            t,h,pl = simuler_jour()
            s = score_meteo(t,h,pl)
            rows.append({
                "ville": nom,
                "date": str(jour),
                "temp_c": t,
                "humidite": h,
                "pluie_mm": pl,
                "score": s
            })
    df = pd.DataFrame(rows)
    df.to_csv(csv_out, index=False, encoding="utf-8-sig")
    return df

# top5
def top5(df_meteo, csv_out="top5.csv"):
    agg = df_meteo.groupby("ville", as_index=False).agg(score_moyen=("score","mean"))
    agg["score_moyen"] = agg["score_moyen"].round(2)
    top = agg.sort_values("score_moyen", ascending=False).head(5)
    top.to_csv(csv_out, index=False, encoding="utf-8-sig")
    return top

#carte des 5 villes
def carte(top_df, villes_df, png_out="carte.png"):
    m = top_df.merge(villes_df, on="ville", how="left").dropna(subset=["lat","lon"])
    if m.empty:
        return None
    plt.figure(figsize=(8,8))
    plt.scatter(m["lon"], m["lat"], s=150)
    for _, r in m.iterrows():
        plt.text(r["lon"]+0.1, r["lat"]+0.1, f"{r['ville']} ({r['score_moyen']})", fontsize=9)
    plt.xlim([-5.5, 9.5])
    plt.ylim([41, 51.5])
    plt.grid(True)
    plt.title("top 5 villes (météo)")
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.savefig(png_out, dpi=150, bbox_inches="tight")
    plt.close()
    return png_out

def main():
    df_villes = geoloc_liste(villes, "villes_geoloc.csv")
    df_meteo = construire_meteo(df_villes, "meteo.csv")
    df_top = top5(df_meteo, "top5.csv")
    img = carte(df_top, df_villes, "carte.png")
    print("ok")
    print(df_top)
    print("carte:", img)

    # pour la carte je ne sais pas comment on peut mettre la France en fond

if __name__ == "__main__":
    main()
