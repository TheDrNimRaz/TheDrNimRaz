from flight_controllers.FC44 import flight_controller
import numpy as np


class ProbeAPI:
    """
    This class is used to interact through a command line interface with the highly classified FC44 flight controller
    module. The FC44 module isn't open source, and it's source code is not available anywhere.
    This API provides all the needed functionality to use the FC44.
    """
    def __init__(self, flight_controller):
        self.flight_controller = flight_controller

    def run_commands(self, command_str):
        """
        runs a series of probe commands seperated by ;
        The possible commands are: state, load, clear, fuel, start
        * state returns the current state of the probe, takes no arguments
        * load loads a series of thrust commands, each command in the format [Delta v [m/s],angle [deg],t [days]]
        *   example load command: load [[1229, 7, 10], [11410, 9, 20], [1051, 10, 30]];
        * clear clears the probe's memory, removing all thrust and land commands that were loaded, takes no arguments.
        * land loads a landing command which takes the approach velocity in m/s as an argument
        *   example load command: fuel 0.;
        * start activates the thrust and fuel commands that were loaded, takes no arguments.


        * A full execution command sequence might look like:
        *   load [[82, 78, 77], [86, 65, 96], [32, 99, 108], [86, 67, 109], [111, 119, 110]]; fuel 20; start;

        :param command_str: a list of commands seperated by ;
        """
        for line in command_str.split(';'):  # iterate over all commands
            command, *args = line.split()  # separate command and arguments
            command = command.lower()
            match command:
                case 'state':
                    return self.state()
                case 'load':
                    thrusts, times = map(eval, args)
                    self.flight_controller.add_thrust_commands(thrusts, times)
                case 'fuel':
                    # when attempting to fuel a satellite, must be in a 10,000 Km range from the satellite
                    # WARNING: using relative velocity over 1 Km/s is highly dangerous and may cause probe to explode
                    relative_velocity = map(eval, args)
                    self.flight_controller.add_fuel_satellite_command(relative_velocity)
                case 'clear':
                    self.flight_controller.clear_thrust()
                case 'start':
                    # test the mission result, if it is predicted
                    # to succeed launch it, else abort and clear thrust commands
                    test_mission = self.flight_controller.predict_mission_result()
                    if test_mission:
                        self.flight_controller.launch_mission()
                        return "Mission succeeded"
                    else:
                        self.flight_controller.clear_thrust()
                        return "Mission will fail, aborted"
                case _:
                    return "Invalid command"

    def state(self):
        location, velocity, time = self.flight_controller.state()
        return f"Current location: {location}, Current velocity: {velocity}, Current time: {time}"
