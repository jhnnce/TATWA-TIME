from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
import requests
import pytz
from datetime import datetime, timedelta, time, date

app = FastAPI()


def get_sunrise(lat, lng, dia='today', timezone="America/Lima"):
    url = "https://api.sunrisesunset.io/json"
    params = {"lat": lat, "lng": lng, "date": dia, "timezone": timezone}
    data = requests.get(url, params=params).json()["results"]

    sunrise_utc = data["sunrise"]
    sunset_utc = data["sunset"]
    date = data["date"]

    #print(date, sunrise_utc, sunset_utc)
    return date, sunrise_utc, sunset_utc


def get_current_value(date, sunrise_time, tz="America/Lima"):
    now = datetime.now(pytz.timezone(tz))
    sunrise_time = datetime.strptime(date + " " + sunrise_time, "%Y-%m-%d %I:%M:%S %p")

    minutos = now.time().strftime("%H:%M:%S").split(":")
    tz = pytz.timezone("America/Lima")
    combined = datetime.combine(datetime.now(tz).date(), datetime.strptime(f"{minutos[0]}:{minutos[1]}:{minutos[2]}", "%H:%M:%S").time())
    minutes_passed = int((combined - sunrise_time).total_seconds() / 60)

    if minutes_passed < 0:
        return None  # aún no amanece
    
    # ciclo de 24 min y duración 2h (24*5)
    value = ((minutes_passed / 24) % 5) + 1
    return value, now, minutes_passed

LAT = -13.53195
LNG = -71.96746

def next_tatwa_time(hora_inicial: str, repeticiones: int = 60) -> None:
    """Calcula y muestra las siguientes horas en el ciclo de TATWA."""
    formato = "%I:%M:%S %p %Y-%m-%d"

    # Convertir texto a objeto datetime
    t = datetime.strptime(hora_inicial, formato)
    # Intervalo de 24 minutos
    intervalo = timedelta(minutes=24)

    w = 1
    valor=''
    for _ in range(repeticiones):

 
            t += intervalo
            w += 1
            
            if w > 5:
                w = 1
            
            if w == 1:
                
                value_name = "AKASH"

            elif w == 2:
        
                value_name = "VAYÚ"

            elif w == 3:
        
                value_name = "TEJAS"

        
            elif w == 4:
            
                value_name = "PRITHVI"

            elif w == 5:
            
                value_name = "APAS"

            now = datetime.now(pytz.timezone("America/Lima"))
            minutos = now.time().strftime("%H:%M:%S").split(":")
            tz = pytz.timezone("America/Lima")

            combined = datetime.combine(datetime.now(tz).date(), time(int(minutos[0]), int(minutos[1]), int(minutos[2])))
            
            if t > combined:
                if value_name== "APAS":
                    valor += f'{t.time().strftime("%I:%M:%S %p")} | {value_name}<br><br>'
                else:
                    valor += f'{t.time().strftime("%I:%M:%S %p")} | {value_name}<br>'

    return valor

def get_sunrise_value():

    date, sunrise, sunset = get_sunrise(LAT, LNG)
    sunrise = datetime.strptime(sunrise, "%I:%M:%S %p")
    sunset = datetime.strptime(sunset, "%I:%M:%S %p")
    date = datetime.strptime(date+' '+sunrise.strftime("%I:%M:%S %p"), "%Y-%m-%d %I:%M:%S %p")
 

    now = datetime.now(pytz.timezone("America/Lima"))
    
    minutos = now.time().strftime("%H:%M:%S").split(":")
    tz = pytz.timezone("America/Lima")

    combined = datetime.combine(datetime.now(tz).date(), time(int(minutos[0]), int(minutos[1]), int(minutos[2])))

    if combined < date:
       
        dia='yesterday'
    else:
        dia='today'

    

    date, sunrise, sunset = get_sunrise(LAT, LNG, dia)
    amanecer = sunrise
    atardecer = sunset
    actual = now.strftime("%H:%M")

    #next_tatwa_time(sunrise+' '+ date)

    if get_current_value(date, sunrise):

        value, now, minutes = get_current_value(date, sunrise)
        enTatwa = minutes % 24
        restante = 24 - minutes % 24
        valor = value
        value_name = ""


        if int(value) == 1:
                
            value_name = "AKASH"

        elif int(value) == 2:
        
            value_name = "VAYÚ"

        elif int(value) == 3:
    
            value_name = "TEJAS"
        
        elif int(value) == 4:
        
            value_name = "PRITHVI"

        elif int(value) == 5:
        
            value_name = "APAS"
        
        



        return {"amanecer": amanecer, 'atardecer': atardecer, 'date_sun':date,"actual": actual, 'now': now.date().isoformat(),  'minutos':minutes,"enTatwa": enTatwa, 'restante': restante, 'valor': valor, 'nombre_valor': value_name, 'proximos': next_tatwa_time(sunrise+' '+ date) }
    


@app.get("/value")
def get_value():
    return JSONResponse(get_sunrise_value())


@app.get("/")
def home():
    return HTMLResponse("""
        <html>
<head>
    <title>Sun Value</title>

    <style>
        body {
            background-color: #1D4796;
            color: #fff;
            font-family: Arial;
        }
    </style>

    <script>
        async function load() {
            let r = await fetch('/value');
            let data = await r.json();
            document.getElementById("val").innerHTML =
                'Fecha Actual: ' + data.now + '<br>' +
                'Hora Actual: ' + data.actual + '<br>' +
                'Salida de Sol: ' + data.amanecer + ' (' + data.date_sun + ')' + '<br>' +
                'Puesta de Sol: ' + data.atardecer + ' (' + data.date_sun + ')' + '<br>' +
                'Minutos desde el Amanecer: ' + data.minutos + '<br><br>' +
                'TATWA: ' + data.nombre_valor + '<br>' +
                'Minutos pasados en el Tatwa: ' + data.enTatwa + '<br>' +
                'Minutos restantes en el Tatwa: ' + data.restante + '<br>' +
                'Valor: ' + data.valor + '<br><br>' +
                'Próximos Tatwas:<br><br>' +
                data.proximos;
        }
        setInterval(load, 20000);
        load();
    </script>
</head>

<body style="text-align:center;padding-top:30px;">
    <h1 style="font-size:40px;" id="val"></h1>
</body>
</html>

    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5001, reload=True)
