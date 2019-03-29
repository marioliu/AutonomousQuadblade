'''
Adapted from http://python.dronekit.io/guide/quick_start.html
Description: Hello world for drone simulation
'''
def main():
    print("Start simulator (SITL)")
    import dronekit_sitl
    import time
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

    # Import DroneKit-Python
    from dronekit import connect, VehicleMode

    # Connect to the Vehicle.
    print("Connecting to vehicle on: %s" % (connection_string,))
    vehicle = connect(connection_string, wait_ready=True)

    # Get some vehicle attributes (state)
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)    # settable

    # Arm motors in simulation
    # print("Arming motors:")
    # vehicle.mode    = VehicleMode("GUIDED")
    # vehicle.armed   = True
    # while not vehicle.armed:
    #         print("  Waiting for arming to be finished")
    #         time.sleep(1)
    # print("Keeping motors armed for 5s")
    # time.sleep(5)
    # print("Disarming")
    # vehicle.armed   = False

    # Close vehicle object before exiting script
    vehicle.close()

    # Shut down simulator
    sitl.stop()
    print("Completed")

if __name__== "__main__":
    main()