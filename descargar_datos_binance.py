"""
Descargador de datos historicos de Binance (BTC, ETH, SOL)
============================================================
Este script NO necesita tus API keys de Binance.
Descarga velas (klines) publicas en formato 1 hora, de los ultimos ~18 meses,
para BTCUSDT, ETHUSDT y SOLUSDT, y las guarda como archivos CSV en la
carpeta "datos_binance" al lado de este script.

COMO USARLO:
1. Asegurate de tener Python instalado (ya lo tienes, lo usaste para el bot de SOL).
2. Abre una terminal (cmd o PowerShell) en la carpeta donde guardaste este archivo.
3. Ejecuta:
       pip install requests
       python descargar_datos_binance.py
4. Cuando termine, comprime la carpeta "datos_binance" en un .zip y subela
   al chat de Claude.

No modifica nada en tu cuenta de Binance. Solo descarga datos publicos.
"""

import os
import io
import zipfile
import datetime
import requests

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "5m"
MESES_A_DESCARGAR = 12  # 1 anio de historia a 5 minutos
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_binance")

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"

COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]


def meses_a_descargar(n):
    hoy = datetime.date.today().replace(day=1)
    meses = []
    for i in range(1, n + 1):
        mes = hoy
        for _ in range(i):
            mes = (mes.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        meses.append(mes)
    return sorted(set(meses))


def descargar_symbol(symbol):
    print(f"\n=== Descargando {symbol} ===")
    filas_totales = []
    faltantes = []

    for mes in meses_a_descargar(MESES_A_DESCARGAR):
        etiqueta = mes.strftime("%Y-%m")
        url = f"{BASE_URL}/{symbol}/{INTERVAL}/{symbol}-{INTERVAL}-{etiqueta}.zip"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                faltantes.append(etiqueta)
                print(f"  {etiqueta}: no disponible (status {r.status_code})")
                continue
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                nombre_csv = z.namelist()[0]
                with z.open(nombre_csv) as f:
                    for linea in f.read().decode("utf-8").splitlines():
                        filas_totales.append(linea)
            print(f"  {etiqueta}: OK")
        except Exception as e:
            faltantes.append(etiqueta)
            print(f"  {etiqueta}: error ({e})")

    if not filas_totales:
        print(f"  ATENCION: no se pudo descargar nada para {symbol}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{symbol}_{INTERVAL}.csv")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(",".join(COLUMNS) + "\n")
        for linea in filas_totales:
            f.write(linea + "\n")

    print(f"  Guardado: {out_path}  ({len(filas_totales)} velas)")
    if faltantes:
        print(f"  Meses faltantes (normal si son muy recientes): {faltantes}")


def main():
    print("Descargando datos historicos publicos de Binance...")
    print(f"Simbolos: {SYMBOLS} | Intervalo: {INTERVAL} | Meses: {MESES_A_DESCARGAR}")
    for symbol in SYMBOLS:
        descargar_symbol(symbol)
    print("\nListo. Comprime la carpeta 'datos_binance' en un .zip y subela al chat.")


if __name__ == "__main__":
    main()
