# AC Stint Data Logger

Stint es una Python app para Assetto Corsa destinada a enviar datos de telemetría en tiempo real vía UDP socket simulando una unidad data logger en circuito.

**Nota**: La app está destinada a enviar los datos a un servidor. Más información en [ac-stint-race-data-server](https://github.com/fabetabilo/ac-stint-race-data-server.git)

### Requisitos

- Assetto Corsa
- Content Manager
- CSP Custom Shaders Patch (Versión estable)

## Features

La app envía datos de telemetría en tiempo real a través de paquetes UDP binarios. Cada paquete contiene un header que identifica el tipo de dato, el dispositivo y un timestamp, permitiendo al servidor receptor procesar y sincronizar los datos correctamente.

**Datos de telemetría del coche que envía:**

- **Información del coche** - Información estática, daño y estado
- **Inputs del Piloto** - RPM, velocidad, marcha, throttle, freno, embrague, volante y combustible
- **IMU** - Aceleración (G-force), roll, pitch, yaw rate y altura del centro de gravedad (CoG)
- **Suspensión** - Recorrido, camber, carga en ruedas, velocidad angular y altura de marcha
- **Tiempos en Pista** - Posición, tiempos de vuelta/sector, bandera y estado de pit lane
- **GPS** - Posición mundial y dirección del vehículo
- **Neumáticos** - Temperatura, presión, suciedad, desgaste y deslizamiento
- **Aerodinámica** - Drag, downforce y coeficientes aerodinámicos

## Instalación

Descargar último asset release desde https://github.com/fabetabilo/ac-stint-telemetry-datalogger/releases/latest y descomprimir en la ruta de Assetto Corsa:
- `C:/Users/tu-usuario/Steam/steamapps/common/assettocorsa/apps/python/`

Dentro de la carpeta `apps/python/`, la carpeta de la app Stint **debe** llamarse "`Stint`". Deberías quedar con una estructura similar a:

![Stint Enabled](docs/images/stint-folder-location.png)

Dentro de la carpeta `Stint` de la app, el archivo `Stint.py` **debe** llamarse igual que la carpeta que contiene los archivos de la app `Stint`

![Stint Enabled](docs/images/stint-folder.png)

#### En Content Manager
Dirígete a: `Settings` → `Assetto Corsa` → `Python Apps`

![Stint Enabled](docs/images/app-enabled.png)

Asegúrate de tener marcadas las casillas:
- `Enable Python Apps`
- `Stint`

Para activar o desactivar la app en Assetto Corsa y modificar parámetros de comunicación:

`Settings` → `Assetto Corsa` → `Python Apps Settings`

![Stint Settings](docs/images/app-settings.png)

## Desarrollo de la aplicación

Si estás interesado en el desarrollo de la app, revisa la wiki  :) → [Wiki]()

## Links & Referencias

AC Python Documentation - Oficial