from Mayak600.MachineClient import MachineClient

if __name__ == "__main__":
    client = MachineClient(server_ip="127.0.0.1", server_port=23002,keepalive_limit=3, reconnect_delay=5)
    try:
        client.run()
    except KeyboardInterrupt:
        print("[INFO] Остановка по Ctrl+C.")
    finally:
        client.running = False
        client.close()
