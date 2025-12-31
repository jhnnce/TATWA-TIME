from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
import requests
import pytz
from datetime import datetime

app = FastAPI()


def get_sunrise(lat, lng, tz="America/Lima"):
    url = "https://api.sunrise-sunset.org/json"
    params = {"lat": lat, "lng": lng, "date": "today", "formatted": 0, 'tzid': tz}
    data = requests.get(url, params=params).json()["results"]
    
    sunrise_utc = datetime.fromisoformat(data["sunrise"])
    sunset_utc = datetime.fromisoformat(data["sunset"])
    local_tz = pytz.timezone(tz)
    sunrise_local = sunrise_utc.astimezone(local_tz)
    sunset_local = sunset_utc.astimezone(local_tz)
    return sunrise_local, sunset_local

def get_current_value(sunrise_time, tz="America/Lima"):
    now = datetime.now(pytz.timezone(tz))
    minutes_passed = int((now - sunrise_time).total_seconds() / 60)
    
    # ciclo de 24 min y duración 2h (24*5)
    value = ((minutes_passed / 24) % 5)
    return value, now, minutes_passed

LAT = -13.53195
LNG = -71.96746


def get_sunrise_value():
    sunrise, sunset = get_sunrise(LAT, LNG)
    value, now, minutes = get_current_value(sunrise)
    amanecer = sunrise.strftime("%H:%M")
    atardecer = sunset.strftime("%H:%M")
    now = datetime.now(pytz.timezone("America/Lima"))
    actual = now.strftime("%H:%M")
    enTatwa = minutes % 24
    restante = 24 - minutes % 24
    valor = value
    value_name = ""

    if int(value) == 1:
             
        value_name = "AKASHA"

    elif int(value) == 2:
     
        value_name = "VAYU"

    elif int(value) == 3:
   
        value_name = "TEJAS"
    
    elif int(value) == 4:
     
        value_name = "PRITHIVI"

    elif int(value) == 5 or int(value) == 0:
    
        value_name = "APAS"



    return {"amanecer": amanecer, 'atardecer': atardecer, "actual": actual, 'now': now.date().isoformat(),  'minutos':minutes,"enTatwa": enTatwa, 'restante': restante, 'valor': valor, 'nombre_valor': value_name}


@app.get("/value")
def get_value():
    return JSONResponse(get_sunrise_value())


@app.get("/")
def home():
    return HTMLResponse("""
        <html>
        <head>
            <title>Sun Value</title>
            <script>
                async function load() {
                    let r = await fetch('/value');
                    let data = await r.json();
                    document.getElementById("val").innerHTML = 'Fecha Actual: ' + data.now + '<br>' +
                        'Salida de Sol: ' + data.amanecer + '<br>' +
                        'Puesta de Sol: ' + data.atardecer + '<br>' +
                        'Hora Actual: ' + data.actual + '<br>' +
                        'Minutos desde el Amanecer: ' + data.minutos + '<br>' +
                        'Minutos pasados: ' + data.enTatwa + '<br>' +
                        'Minutos restantes: ' + data.restante + '<br>' +
                        'Valor: ' + data.valor + '<br>' +
                        'Tatwa: ' + data.nombre_valor;
                }
                setInterval(load, 2000);
                load();
            </script>
        </head>
        <body style="font-family:Arial;text-align:center;padding-top:30px;">
            <h1 style="font-size:40px;" id="val"></h1>
        </body>
        </html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
