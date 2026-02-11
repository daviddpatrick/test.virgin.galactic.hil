import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(min(value, maximum), minimum)


def _wrap_heading(degrees_value: float) -> float:
    return degrees_value % 360.0


@dataclass(frozen=True)
class ControlInputs:
    throttle: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0


@dataclass
class SimConfig:
    min_airspeed: float = 30.0
    max_airspeed: float = 240.0
    speed_response: float = 0.35
    max_pitch_rate_deg_s: float = 25.0
    max_roll_rate_deg_s: float = 35.0
    max_yaw_rate_deg_s: float = 20.0
    max_pitch_deg: float = 45.0
    max_roll_deg: float = 60.0
    climb_factor: float = 0.18
    battery_drain_idle: float = 0.01
    battery_drain_throttle: float = 0.12
    stall_speed: float = 40.0
    overspeed_margin: float = 1.05
    battery_low_threshold: float = 20.0
    noise_deg: float = 0.4
    noise_speed: float = 0.6
    noise_altitude: float = 0.8


@dataclass
class FlightState:
    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0
    airspeed: float = 35.0
    altitude: float = 50.0
    battery: float = 100.0
    gps_lat: float = 37.6213
    gps_lon: float = -122.3790


@dataclass
class SensorState:
    pitch: float
    roll: float
    yaw: float
    airspeed: float
    altitude: float
    battery: float
    gps_lat: float
    gps_lon: float


@dataclass
class StepResult:
    state: FlightState
    sensors: SensorState
    warnings: List[str] = field(default_factory=list)


class FlightControlSim:
    def __init__(self, seed: int = 0, config: SimConfig | None = None) -> None:
        self.config = config or SimConfig()
        self.state = FlightState()
        self._rng = random.Random(seed)

    def step(self, dt: float, inputs: ControlInputs) -> StepResult:
        warnings: List[str] = []

        throttle = inputs.throttle
        pitch = inputs.pitch
        roll = inputs.roll
        yaw = inputs.yaw

        if throttle < 0.0 or throttle > 1.0:
            warnings.append("throttle_clamped")
        if abs(pitch) > 1.0:
            warnings.append("pitch_command_clamped")
        if abs(roll) > 1.0:
            warnings.append("roll_command_clamped")
        if abs(yaw) > 1.0:
            warnings.append("yaw_command_clamped")

        throttle = _clamp(throttle, 0.0, 1.0)
        pitch = _clamp(pitch, -1.0, 1.0)
        roll = _clamp(roll, -1.0, 1.0)
        yaw = _clamp(yaw, -1.0, 1.0)

        pitch_rate = pitch * self.config.max_pitch_rate_deg_s
        roll_rate = roll * self.config.max_roll_rate_deg_s
        yaw_rate = yaw * self.config.max_yaw_rate_deg_s

        self.state.pitch = _clamp(
            self.state.pitch + pitch_rate * dt,
            -self.config.max_pitch_deg,
            self.config.max_pitch_deg,
        )
        self.state.roll = _clamp(
            self.state.roll + roll_rate * dt,
            -self.config.max_roll_deg,
            self.config.max_roll_deg,
        )
        self.state.yaw = _wrap_heading(self.state.yaw + yaw_rate * dt)

        target_speed = self.config.min_airspeed + throttle * (self.config.max_airspeed - self.config.min_airspeed)
        self.state.airspeed += (target_speed - self.state.airspeed) * self.config.speed_response * dt

        pitch_rad = math.radians(self.state.pitch)
        climb_rate = math.sin(pitch_rad) * self.state.airspeed * self.config.climb_factor
        self.state.altitude = max(0.0, self.state.altitude + climb_rate * dt)

        drain = self.config.battery_drain_idle + throttle * self.config.battery_drain_throttle
        self.state.battery = max(0.0, self.state.battery - drain * dt)

        if self.state.airspeed < self.config.stall_speed:
            warnings.append("stall_risk")
        if self.state.airspeed > self.config.max_airspeed * self.config.overspeed_margin:
            warnings.append("overspeed_risk")
        if self.state.battery <= self.config.battery_low_threshold:
            warnings.append("battery_low")

        distance_m = self.state.airspeed * dt
        heading_rad = math.radians(self.state.yaw)
        north_m = math.cos(heading_rad) * distance_m
        east_m = math.sin(heading_rad) * distance_m
        meters_per_degree = 111_000.0
        self.state.gps_lat += north_m / meters_per_degree
        self.state.gps_lon += east_m / (meters_per_degree * math.cos(math.radians(self.state.gps_lat)))

        sensors = self._sensor_snapshot()
        return StepResult(state=self.state, sensors=sensors, warnings=warnings)

    def run_for_seconds(self, seconds: float, inputs: ControlInputs, step: float = 0.1) -> StepResult:
        elapsed = 0.0
        last_result = None
        while elapsed < seconds:
            last_result = self.step(step, inputs)
            elapsed += step
        if last_result is None:
            last_result = self.step(step, inputs)
        return last_result

    def _sensor_snapshot(self) -> SensorState:
        return SensorState(
            pitch=self._noisy(self.state.pitch, self.config.noise_deg),
            roll=self._noisy(self.state.roll, self.config.noise_deg),
            yaw=self._noisy(self.state.yaw, self.config.noise_deg),
            airspeed=self._noisy(self.state.airspeed, self.config.noise_speed),
            altitude=self._noisy(self.state.altitude, self.config.noise_altitude),
            battery=self.state.battery,
            gps_lat=self._noisy(self.state.gps_lat, 0.00005),
            gps_lon=self._noisy(self.state.gps_lon, 0.00005),
        )

    def _noisy(self, value: float, spread: float) -> float:
        if spread <= 0.0:
            return value
        return value + self._rng.uniform(-spread, spread)
