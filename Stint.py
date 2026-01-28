# Stint Telemetry Data Logger
# simula un data logger para emitir telemetria en tiempo real simulando sensores; gps, aerodinamica, entre otros.
import ac
import acsys
import sys
import os.path
import platform

if platform.architecture()[0] == "64bit":
    sysdir = os.path.join(os.path.dirname(__file__), 'stdlib64')
    sys.path.insert(0, sysdir)
    os.environ['PATH'] = os.environ['PATH'] + ";."

import socket
import json
import configparser
import math

try:
    from features.sim_info import SimInfo
except Exception as e:
    ac.log("StintRC ERROR: 'shared.py' " + str(e))

try:
    from features.radar import RadarSystem
except Exception as e:
    ac.log("Stint ERROR: 'radar.py' not found: " + str(e))

# valores DEFAULT
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9996
UPDATE_FREQ = 20 # 20Hz
UPDATE_SLOW_FREQ = 5 # 5s

sock = None
sim_info = None
radar_sys = None

timer_fast = 0
timer_slow = 0
tick = 0
period_fast = 1.0 / float(UPDATE_FREQ)
period_slow = UPDATE_SLOW_FREQ

PKT_INFO = 1
PKT_INPUT = 2
PKT_SUSP_GFORCE = 3
PKT_LIVE_TIMING = 4
PKT_TYRE = 5
PKT_AERO = 6
PKT_GPS_RADAR = 7

DRIVER_NAME = "Driver"
CAR_MODEL = "UNKNOWN"
CAR_NUMBER = "0"
TEAM_ID = "DMG"

RADAR_RANGE = 40.0 # 40m

def load_config():

    global SERVER_IP, SERVER_PORT, UPDATE_FREQ, UPDATE_SLOW_FREQ, TEAM_ID, period_fast, period_slow
    global RADAR_RANGE

    try:
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)

        if config.has_section("SETTINGS"):
            val = config.get("SETTINGS", "SERVER_IP", fallback="").strip()
            if val:
                SERVER_IP = val
            
            val = config.get("SETTINGS", "SERVER_PORT", fallback="").strip()
            if val:
                SERVER_PORT = int(val)
            
            val = config.get("SETTINGS", "UPDATE_FREQ", fallback="").strip()
            if val:
                UPDATE_FREQ = int(val)

            val = config.get("SETTINGS", "UPDATE_SLOW_FREQ", fallback="").strip()
            if val:
                UPDATE_SLOW_FREQ = float(val)
        
        if config.has_section("DRIVER"):
            val = config.get("DRIVER", "TEAM_ID", fallback="").strip()
            if val:
                TEAM_ID = val

        if config.has_section("SENSORS"):
            val = config.get("SENSORS", "RADAR_RANGE", fallback="").strip()
            if val:
                RADAR_RANGE = float(val)
        
        UPDATE_FREQ = int(max(1, min(UPDATE_FREQ, 60)))
        UPDATE_SLOW_FREQ = max(0.5, min(UPDATE_SLOW_FREQ, 60.0))
        period_fast = 1.0 / float(UPDATE_FREQ)
        period_slow = UPDATE_SLOW_FREQ

        RADAR_RANGE = max(5.0, min(RADAR_RANGE, 200.0))

    except Exception as e:
        ac.log("Stint ERROR: config.ini: " + str(e))

def get_number_from_livery(car_model, skin_name):
    try:
        file_path = "content/cars/{}/skins/{}/ui_skin.json".format(car_model, skin_name)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return str(data.get("number", ""))

    except Exception:
        return None
    return None

def send_udp(dict_payload):

    global sock, SERVER_IP, SERVER_PORT

    if sock:
        try:
            msg = json.dumps(dict_payload).encode('utf-8')
            sock.sendto(msg, (SERVER_IP, SERVER_PORT))
        except:
            pass


def send_input_data():

    global sim_info

    try:
        if sim_info is None:
            return
        
        rpm = int(ac.getCarState(0, acsys.CS.RPM))
        turbo = round(ac.getCarState(0, acsys.CS.TurboBoost),2) #kpa
        speed = round(ac.getCarState(0, acsys.CS.SpeedKMH),1)
        gear = ac.getCarState(0, acsys.CS.Gear) - 1
        throttle = round(ac.getCarState(0, acsys.CS.Gas),2)
        brake = round(ac.getCarState(0, acsys.CS.Brake),2)
        steer = round(ac.getCarState(0, acsys.CS.Steer),2)
        fuel = round(sim_info.physics.fuel,2)
        kers_charge = round(sim_info.physics.kersCharge,2)
        kers_input = round(sim_info.physics.kersInput,2)

        payload = {
            "type": PKT_INPUT,
            "car": {
                "rpm": rpm,
                "turbo": turbo,
                "speed": speed,
                "gear": gear,
                "throttle": throttle,
                "brake": brake,
                "steer": steer,
                "fuel": fuel
            },
            "kers": {
                "charge": kers_charge,
                "input": kers_input
            }
        }
        send_udp(payload)
        #ac.log("STINT: " + json.dumps(payload, indent=2))
    except:
        pass

def send_susp_gforce_data():

    global sim_info

    try:
        if sim_info is None:
            return

        travel = list(sim_info.physics.suspensionTravel) # [FL,FR,RL,RR]
        g_forces = list(sim_info.physics.accG) # [x,y,z]

        payload = {
            "type": PKT_SUSP_GFORCE,
            "data": {
                "travel": travel,
                "g": g_forces
            }
        }
        send_udp(payload)
        
    except:
        pass

def send_live_timing_data():
    
    global sim_info

    try:
        if sim_info is None:
            return

        pos = ac.getCarRealTimeLeaderboardPosition(0) + 1
        current_lap_ms = ac.getCarState(0, acsys.CS.LapTime)
        delta = ac.getCarState(0, acsys.CS.PerformanceMeter)
        sector_idx = sim_info.graphics.currentSectorIndex
        sector_time = sim_info.graphics.lastSectorTime
        last_lap_ms = ac.getCarState(0, acsys.CS.LastLap)
        best_lap_ms = ac.getCarState(0, acsys.CS.BestLap)
        lap_num  = ac.getCarState(0, acsys.CS.LapCount) + 1
        in_pit_lane = ac.isCarInPitline(0) == 1
        flag = sim_info.graphics.flag

        payload = {
            "type": PKT_LIVE_TIMING,
            "data": {
                "pos": pos,
                "current": current_lap_ms,
                "delta": delta,
                "spIdx": sector_idx,
                "spTime": sector_time,
                "last": last_lap_ms,
                "best": best_lap_ms,
                "num": lap_num,
                "pit": in_pit_lane,
                "flag": flag
            }
        }
        send_udp(payload)

    except:
        pass

def send_tyre_data():

    global sim_info

    try:
        if sim_info is None:
            return
        
        tyre_compound = ac.getCarTyreCompound(0) or "NC"
        raw_temps = ac.getCarState(0, acsys.CS.CurrentTyresCoreTemp)
        raw_pressures = ac.getCarState(0, acsys.CS.DynamicPressure)
        raw_wear = sim_info.physics.tyreWear
        raw_dirt = ac.getCarState(0, acsys.CS.TyreDirtyLevel)
        raw_wheel_s = sim_info.physics.wheelSlip

        temps = list(raw_temps)          # C
        pressures = list(raw_pressures)   # psi
        wear = list(raw_wear)              # ~50-100
        dirt_level = list(raw_dirt)        # 0-5
        slip = list(raw_wheel_s)

        payload = {
            "type": PKT_TYRE,
            "data": {
                "compound": tyre_compound,
                "temp": temps,
                "p": pressures,
                "w": wear,
                "dirt": dirt_level,
                "slip": slip
            }
        }
        send_udp(payload)
        
    except:
        pass

def send_aero_data():

    global sim_info

    try:
        if sim_info is None:
            return

        drag = round(ac.ext_getDrag(),2)
        downforce = round(ac.ext_getDownforce(2),2) # total (0 = front, 1 = rear, pero da 0)
        cl_front = round(ac.getCarState(0, acsys.AERO.CL_Front),4)
        cl_rear = round(ac.getCarState(0, acsys.AERO.CL_Rear),4)
        cd_aero = round(ac.getCarState(0, acsys.AERO.CD),4)
        ride_height = list(sim_info.physics.rideHeight)

        payload = {
            "type": PKT_AERO,
            "data": {
                "drag": drag,
                "downforce": downforce,
                "clFront": cl_front,
                "clRear": cl_rear,
                "cdAero": cd_aero,
                "rh": ride_height
            }
        }
        send_udp(payload)
        
    except:
        pass

def send_gps_radar_data():
    
    global radar_sys, sim_info

    try:
        if sim_info is None:
            return

        nearby_cars = []
        nose_dir = sim_info.physics.heading
        pos = ac.getCarState(0, acsys.CS.WorldPosition)

        x = round(pos[0],2)
        z = round(pos[2],2)

        if radar_sys:
            nearby_cars = radar_sys.get_nearby_cars(x, z)
        
        payload = {
            "type": PKT_GPS_RADAR,
            "data": {
                "nose": nose_dir,
                "x": x,
                "z": z
            },
            "radar": nearby_cars
        }
        send_udp(payload)

    except:
        pass

def send_info():
    
    global sim_info, DRIVER_NAME, CAR_MODEL, CAR_NUMBER
    
    try:
        if sim_info is None:
            return
        
        position_lead = ac.getCarRealTimeLeaderboardPosition(0) + 1
        tyre_compound = ac.getCarTyreCompound(0) or "NC"
        in_pit_box = ac.isCarInPit(0) == 1

        s_payload = {
            "type": PKT_INFO,
            "num": CAR_NUMBER,
            "driver": DRIVER_NAME,
            "teamId": TEAM_ID,
            "car": CAR_MODEL,
            "data": {
                "position": position_lead,
                "compound": tyre_compound,
                "box": in_pit_box
            }
        }
        send_udp(s_payload)

    except:
        pass

def acMain(ac_version):

    global sock, lbl_status, radar_sys, DRIVER_NAME, CAR_MODEL, CAR_NUMBER
    global sim_info, RADAR_RANGE
    
    load_config()

    try:
        sim_info = SimInfo()
    except:
        ac.log("Stint ERROR: Reading sim info")

    try:
        radar_sys = RadarSystem(radar_range=RADAR_RANGE)
        radar_sys.scan_grid()
        
    except:
        ac.log("Stint ERROR: Initializing Radar system")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
    except:
        ac.log("Stint ERROR: Socket")

    appWindow = ac.newApp("Stint Logger")
    ac.setSize(appWindow, 200, 50)
    
    livery = ac.getCarSkin(0)
    DRIVER_NAME = ac.getDriverName(0)
    CAR_MODEL = ac.getCarName(0) or "UNKNOWN"
    CAR_NUMBER = get_number_from_livery(CAR_MODEL, livery)

    ac.log("Stint sending telemetry data")

    return "Stint"

def acUpdate(deltaT):

    global timer_fast, timer_slow, period_fast, period_slow, tick

    timer_fast += deltaT
    timer_slow += deltaT
    
    if timer_fast > period_fast:
        send_input_data()
        send_susp_gforce_data()

        rot_idx = tick % 4

        if rot_idx == 0:
            send_live_timing_data()
        elif rot_idx == 1:
            send_gps_radar_data()
        elif rot_idx == 2:
            send_tyre_data()
        elif rot_idx == 4:
            send_aero_data()

        tick += 1
        timer_fast = 0
        

    if timer_slow > period_slow:
        send_info()
        timer_slow = 0