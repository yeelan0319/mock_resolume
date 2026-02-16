import socket
import json
import time
import os

# Settings
ARTNET_PORT = 6454
DEFAULT_FOLDER = "test_scenes"

def flush_buffer(sock):
    """ Clears any leftover packets from the network queue. """
    sock.setblocking(False)
    count = 0
    try:
        while True:
            sock.recvfrom(1024)
            count += 1
    except BlockingIOError:
        pass
    sock.setblocking(True)
    if count > 0:
        print(f"Cleared {count} 'ghost' packets from buffer.")

def continuous_recorder():
    if not os.path.exists(DEFAULT_FOLDER):
        os.makedirs(DEFAULT_FOLDER)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError: pass
    
    sock.bind(('127.0.0.1', ARTNET_PORT))
    sock.settimeout(0.5)

    print("\n--- Art-Net Debugging Recorder (No-Ghosting Edition) ---")
    
    try:
        while True:
            scene_name = input("\nEnter scene name (or 'q' to quit): ")
            if scene_name.lower() == 'q': break
            
            # --- THE FIX: Clear the old packets before starting ---
            flush_buffer(sock)
            
            duration_input = input("Duration (default 10s): ")
            duration = int(duration_input) if duration_input else 10
            
            frames = []
            start_time = None
            last_log_time = 0

            print(f"Waiting for Resolume data for '{scene_name}'...")
            
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    if start_time is None:
                        start_time = time.time()
                        print(">>> RECORDING STARTED")

                    elapsed = time.time() - start_time
                    if elapsed > duration: break
                    
                    dmx_raw = list(data[18:])
                    frames.append({"timestamp": elapsed, "data": dmx_raw})

                    if time.time() - last_log_time > 1.0:
                        sample = dmx_raw[:8] 
                        print(f"[{elapsed:.1f}s] Data Sample: {sample}")
                        last_log_time = time.time()

                except socket.timeout:
                    if start_time: 
                        print("\nStream stopped. Saving...")
                        break
                    continue
            
            file_path = os.path.join(DEFAULT_FOLDER, f"{scene_name}.json")
            with open(file_path, "w") as f:
                json.dump(frames, f)
            print(f"--- Finished: {file_path} ---")

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        sock.close()

if __name__ == "__main__":
    continuous_recorder()