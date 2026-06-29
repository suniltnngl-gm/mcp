import pathlib
import psutil

def list_listening_ports():
    """
    List listening ports and their associated processes.

    Returns:
        None
    """
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.status == psutil.CONN_LISTEN:
                    print(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, Port: {conn.laddr.port}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def main():
    list_listening_ports()

if __name__ == "__main__":
    main()