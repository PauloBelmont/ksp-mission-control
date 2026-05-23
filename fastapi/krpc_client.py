import os
import krpc

KRPC_ADDRESS = os.getenv("KRPC_ADDRESS", "host.docker.internal")
KRPC_RPC_PORT = int(os.getenv("KRPC_RPC_PORT", "5000"))
KRPC_STREAM_PORT = int(os.getenv("KRPC_STREAM_PORT", "5001"))

def get_connection():
    return krpc.connect(
        name="FastAPI Dashboard",
        address=KRPC_ADDRESS,
        rpc_port=KRPC_RPC_PORT,
        stream_port=KRPC_STREAM_PORT,
    )

def get_vessel_data():
    try:
        conn = get_connection()
        vessel = conn.space_center.active_vessel
        flight = vessel.flight()
        fuel_amount = 0.0
        try:
            fuel_amount = vessel.resources.amount("LiquidFuel")
        except Exception:
            fuel_amount = 0.0

        return {
            "altitude": float(flight.mean_altitude),
            "velocity": float(flight.speed),
            "apoapsis": float(vessel.orbit.apoapsis_altitude),
            "periapsis": float(vessel.orbit.periapsis_altitude),
            "fuel": float(fuel_amount),
        }
    except Exception as e:
        raise RuntimeError(f"kRPC connection error: {e}")