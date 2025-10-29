from Mayak600.MachineClient import MachineClient

if __name__ == "__main__":
    client = MachineClient(server_ip="192.168.0.201", server_port=23321,keepalive_limit=3, reconnect_delay=5)
    try:
        client.run()
    except KeyboardInterrupt:
        print("[INFO] Остановка по Ctrl+C.")
    finally:
        client.running = False
        client.close()
