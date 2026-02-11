import math

import allure
import pytest

from common.hardware.flight_control_sim import ControlInputs, FlightControlSim


@allure.feature("Hardware Simulation")
@allure.story("Pitch control affects climb")
@pytest.mark.hardware
def test_pitch_up_increases_altitude_and_speed():
    sim = FlightControlSim(seed=7)
    start_altitude = sim.state.altitude
    start_speed = sim.state.airspeed

    result = sim.run_for_seconds(6.0, ControlInputs(throttle=0.75, pitch=0.4))

    assert result.state.altitude > start_altitude + 5.0
    assert result.state.airspeed > start_speed
    assert "stall_risk" not in result.warnings


@allure.feature("Hardware Simulation")
@allure.story("Roll command changes bank angle")
@pytest.mark.hardware
def test_roll_left_changes_bank_angle_and_imu():
    sim = FlightControlSim(seed=11)

    result = sim.run_for_seconds(2.5, ControlInputs(throttle=0.55, roll=-0.8))

    assert result.state.roll < 0.0
    assert math.isclose(result.sensors.roll, result.state.roll, abs_tol=2.0)


@allure.feature("Hardware Simulation")
@allure.story("Yaw command updates heading and GPS")
@pytest.mark.hardware
def test_yaw_right_updates_heading_and_gps_position():
    sim = FlightControlSim(seed=3)
    start_lat = sim.state.gps_lat
    start_lon = sim.state.gps_lon

    result = sim.run_for_seconds(4.0, ControlInputs(throttle=0.6, yaw=0.7))

    assert result.state.yaw > 0.0
    assert (result.sensors.gps_lat, result.sensors.gps_lon) != (start_lat, start_lon)


@allure.feature("Hardware Simulation")
@allure.story("Out-of-range commands are clamped")
@pytest.mark.hardware
def test_out_of_range_inputs_generate_warnings():
    sim = FlightControlSim(seed=5)

    result = sim.step(0.2, ControlInputs(throttle=1.4, pitch=1.8, roll=-1.5, yaw=2.2))

    assert "throttle_clamped" in result.warnings
    assert "pitch_command_clamped" in result.warnings
    assert "roll_command_clamped" in result.warnings
    assert "yaw_command_clamped" in result.warnings
    assert 0.0 <= sim.state.airspeed
