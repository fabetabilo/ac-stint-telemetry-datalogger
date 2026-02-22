# Diccionario de Paquetes UDP

Para propósitos de desarrollo, este documento presenta información técnica necesaria para procesar los datos en el servidor o motor de procesamiento. Cualquier cambio en la estructura de paquetes de Stint app **debe** ser documentada aquí.

## Estructura General
Todos los paquetes tienen un **HEADER** de 10 bytes, incluyendo un timestamp por paquete:
```python
HEADER_STRUCT = '<BBQ'  # 10 bytes
├─ Byte 0: Packet ID (1-8)
├─ Byte 1: Device Index
└─ Bytes 2-9: Timestamp (microsegundos)
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| packet_id | B | 1 | ID del tipo de paquete (1-8) |
| device_id | B | 1 | ID del dispositivo/Stint app/data logger |
| timestamp | Q | 8 | Microsegundos desde Unix epoch (1970-01-01 00:00:00 UTC) |

---

## PKT_INFO (ID: 1) - Información del Piloto/Auto
**Frecuencia:** Cada 5 segundos (UPDATE_SLOW_FREQ)

```python
INFO_STRUCT = '<4s32s20s?6f??'  # 67 bytes
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| num | 4s | 4 | Número del auto (string UTF-8) |
| driver | 32s | 32 | Nombre del piloto (string UTF-8) |
| team_id | 20s | 20 | ID del equipo (string UTF-8) |
| in_pit_box | ? | 1 | En box (boolean) |
| dist | f | 4 | Distancia total recorrida (float) |
| c_dmg[0] | f | 4 | Daño frontal (float) |
| c_dmg[1] | f | 4 | Daño trasero (float) |
| c_dmg[2] | f | 4 | Daño lateral izq (float) |
| c_dmg[3] | f | 4 | Daño lateral der (float) |
| c_dmg[4] | f | 4 | Daño central (float) |
| tc_on | ? | 1 | Control de tracción activo (boolean) |
| abs_on | ? | 1 | ABS activo (boolean) |

**Peso total:** 10 (header) + 67 = **77 bytes**

---

## PKT_INPUT (ID: 2) - Inputs del Piloto
**Frecuencia:** 20 Hz (UPDATE_FREQ)

```python
INPUT_STRUCT = '<I10f'  # 44 bytes
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| rpm | I | 4 | Revoluciones por minuto (int unsigned) |
| turbo | f | 4 | Presión turbo en kPa (float) |
| speed | f | 4 | Velocidad en km/h (float) |
| gear | f | 4 | Marcha actual (float, pero es int) |
| throttle | f | 4 | Acelerador 0.0-1.0 (float) |
| brake | f | 4 | Freno 0.0-1.0 (float) |
| clutch | f | 4 | Embrague 0.0-1.0 (float) |
| steer | f | 4 | Volante -1.0 a 1.0 (float) |
| fuel | f | 4 | Combustible en litros (float) |
| kers_charge | f | 4 | Carga KERS 0.0-1.0 (float) |
| kers_input | f | 4 | Input KERS 0.0-1.0 (float) |

**Peso total:** 10 (header) + 44 = **54 bytes**

---

## PKT_IMU (ID: 3) - Acelerómetro y Giroscopio
**Frecuencia:** 20 Hz (UPDATE_FREQ)

```python
IMU_STRUCT = '<8f'  # 32 bytes
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| accG[0] | f | 4 | Aceleración lateral X en G (float) |
| accG[1] | f | 4 | Aceleración vertical Y en G (float) |
| accG[2] | f | 4 | Aceleración longitudinal Z en G (float) |
| roll | f | 4 | Ángulo de balanceo en radianes (float) |
| pitch | f | 4 | Ángulo de cabeceo en radianes (float) |
| yaw_rate | f | 4 | Velocidad angular yaw en rad/s (float) |
| side_slip | f | 4 | Ángulo de deslizamiento lateral en radianes (float) |
| cgh | f | 4 | Altura del centro de gravedad CoG en metros (float) |

**Peso total:** 10 (header) + 32 = **42 bytes**

---

## PKT_SUSP (ID: 4) - Suspensión y Ruedas
**Frecuencia:** 20 Hz (UPDATE_FREQ)

```python
SUSP_STRUCT = '<18f'  # 72 bytes
```

| Campo | Tipo | Bytes | Descripción | Orden |
|-------|------|-------|-------------|-------|
| suspensionTravel[0-3] | 4f | 16 | Recorrido suspensión en metros | FL, FR, RL, RR |
| camberRAD[0-3] | 4f | 16 | Ángulo camber en radianes | FL, FR, RL, RR |
| wheelLoad[0-3] | 4f | 16 | Carga en ruedas en Newton | FL, FR, RL, RR |
| wheelAngularSpeed[0-3] | 4f | 16 | Velocidad angular rad/s | FL, FR, RL, RR |
| rideHeight[0] | f | 4 | Altura frontal en metros (float) | FRONT |
| rideHeight[1] | f | 4 | Altura trasera en metros (float) | REAR |

**Peso total:** 10 (header) + 72 = **82 bytes**

---

## PKT_LIVE_TIMING (ID: 5) - Tiempos de Vuelta
**Frecuencia:** ~10 Hz (DIV_MID)

```python
TIMING_STRUCT = '<BIfBIIIH?B'  # 28 bytes
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| pos | B | 1 | Posición en carrera (unsigned byte) |
| current_lap_ms | I | 4 | Tiempo vuelta actual en ms (int unsigned) |
| delta | f | 4 | Delta vs mejor vuelta (float) |
| sector_idx | B | 1 | Índice sector actual 1-3 (unsigned byte) |
| sector_time | I | 4 | Tiempo último sector en ms (int unsigned) |
| last_lap_ms | I | 4 | Tiempo última vuelta en ms (int unsigned) |
| best_lap_ms | I | 4 | Tiempo mejor vuelta en ms (int unsigned) |
| lap_num | H | 2 | Número de vuelta actual (unsigned short) |
| in_pit_lane | ? | 1 | En pit lane (boolean) |
| flag | B | 1 | Bandera actual (unsigned byte) |

**Peso total:** 10 (header) + 28 = **38 bytes**

---

## PKT_GPS (ID: 6) - GPS
**Frecuencia:** ~10 Hz (DIV_MID)

```python
GPS_STRUCT = '<3f'  # 12 bytes
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| nose_dir | f | 4 | Dirección del auto en radianes (float) |
| x | f | 4 | Posición X en metros (float) |
| z | f | 4 | Posición Z en metros (float) |

**Peso total:** 10 (header) + 12 = **22 bytes**

---

## PKT_TYRE (ID: 7) - Neumáticos
**Frecuencia:** ~5 Hz (DIV_SLOW)

```python
TYRE_STRUCT = '<10s20f'  # 90 bytes
```

| Campo | Tipo | Bytes | Descripción | Orden |
|-------|------|-------|-------------|-------|
| tyre_compound | 10s | 10 | Compuesto de neumático (string UTF-8) | - |
| temps[0-3] | 4f | 16 | Temperatura core en °C | FL, FR, RL, RR |
| press[0-3] | 4f | 16 | Presión en PSI | FL, FR, RL, RR |
| dirt[0-3] | 4f | 16 | Nivel de suciedad 0.0-1.0 | FL, FR, RL, RR |
| wear[0-3] | 4f | 16 | Desgaste 0.0-1.0 | FL, FR, RL, RR |
| slip[0-3] | 4f | 16 | Deslizamiento 0.0-1.0 | FL, FR, RL, RR |

**Peso total:** 10 (header) + 90 = **100 bytes**

---

## PKT_AERO (ID: 8) - Aerodinámica
**Frecuencia:** ~5 Hz (DIV_SLOW)

```python
AERO_STRUCT = '<5f'  # 20 bytes
```

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| drag | f | 4 | Fuerza de arrastre en Newton (float) |
| downforce | f | 4 | Carga aerodinámica total en Newton (float) |
| cl_front | f | 4 | Coeficiente sustentación frontal (float) |
| cl_rear | f | 4 | Coeficiente sustentación trasero (float) |
| cd_aero | f | 4 | Coeficiente de arrastre (float) |

**Peso total:** 10 (header) + 20 = **30 bytes**

---

## Resumen de Pesos y Frecuencias

| Paquete | ID | Frecuencia | Bytes/Paquete | Bytes/Segundo |
|---------|----|-----------:|-------------:|--------------:|
| PKT_INFO | 1 | 0.2 Hz | 77 | ~15 |
| PKT_INPUT | 2 | 20 Hz | 54 | 1,080 |
| PKT_IMU | 3 | 20 Hz | 42 | 840 |
| PKT_SUSP | 4 | 20 Hz | 82 | 1,640 |
| PKT_LIVE_TIMING | 5 | ~10 Hz | 38 | 380 |
| PKT_GPS | 6 | ~10 Hz | 22 | 220 |
| PKT_TYRE | 7 | ~5 Hz | 100 | 500 |
| PKT_AERO | 8 | ~5 Hz | 30 | 150 |

#### Totales Estimados:
- **Total:** ~4,825 bytes/segundo (~38.6 Kbps)

---

## Notas

1. **Endianness:** Todos los structs usan formato little-endian (`<`)
2. **Timestamp:** Se genera en el data logger al momento de captura, no al recibir en servidor. Formato: microsegundos desde Unix epoch (int(time.time() * 1000000))
3. **Device ID:** Identifica el data logger/cliente que envía los datos (configurable desde config.ini)
4. **Strings:** Son bytes UTF-8, deben decodificarse: `value.decode('utf-8').rstrip('\x00')`
5. **Booleans:** 1 byte (0 = False, 1 = True)