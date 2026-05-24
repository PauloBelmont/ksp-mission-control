import os
import logging
import krpc

logger = logging.getLogger(__name__)

KRPC_ADDRESS = os.getenv("KRPC_ADDRESS", "host.docker.internal")
KRPC_RPC_PORT = int(os.getenv("KRPC_RPC_PORT", "5000"))
KRPC_STREAM_PORT = int(os.getenv("KRPC_STREAM_PORT", "5001"))

_connection = None


def get_connection():
    """Return the existing kRPC connection, creating or reconnecting if needed."""
    global _connection
    try:
        # Probe the connection with a lightweight call
        _ = _connection.krpc.get_status()
    except Exception:
        logger.info("kRPC connection not available, attempting to connect...")
        _connection = krpc.connect(
            name="KSP Mission Control",
            address=KRPC_ADDRESS,
            rpc_port=KRPC_RPC_PORT,
            stream_port=KRPC_STREAM_PORT,
        )
        logger.info("kRPC connection established.")
    return _connection


def get_vessel_data():
    """Fetch telemetry data from the active vessel."""
    try:
        conn = get_connection()
        vessel = conn.space_center.active_vessel
        flight = vessel.flight()

        try:
            fuel_amount = float(vessel.resources.amount("LiquidFuel"))
        except Exception:
            fuel_amount = 0.0

        return {
            # Flight data
            "altitude": float(flight.mean_altitude),
            "vertical_speed": float(flight.vertical_speed),
            "horizontal_speed": float(flight.horizontal_speed),
            "heading": float(flight.heading),
            # Orbital data
            "apoapsis": float(vessel.orbit.apoapsis_altitude),
            "periapsis": float(vessel.orbit.periapsis_altitude),
            "body": vessel.orbit.body.name,
            # Resources
            "fuel": fuel_amount,
        }
    except Exception as e:
        raise RuntimeError(f"kRPC error: {e}")
