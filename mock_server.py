import socket
import json
import time
import os
import sys
import argparse
import select

# --- CONFIGURATION ---
DEFAULT_FOLDER = "test_scenes"
ARTNET_PORT = 6454
ARTNET_HEADER = b'Art-Net\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x00\x00'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def play_engine(target_ip, scene_path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        with open(scene_path, "r") as f:
            frames = json.load(f)
    except Exception as e:
        print(f"\n[Error] Could not load file: {e}")
        time.sleep(2)
        return

    print(f"\n>>> NOW PLAYING: {os.path.basename(scene_path)}")
    print(f">>> Target IP: {target_ip}")
    print(">>> [Type 'q' + Enter] to return to menu")
    print(">>> [Ctrl+C] to quit the server entirely\n")

    last_log_time = 0
    try:
        while True:
            start_time = time.time()
            for frame in frames:
                target_time = start_time + frame['timestamp']
                
                # High-precision wait + Input listener
                while time.time() < target_time:
                    # Check if user typed something
                    if select.select([sys.stdin], [], [], 0)[0]:
                        user_input = sys.stdin.readline().strip().lower()
                        if user_input in ['q']:
                            return

                # Send Data to Hardware
                packet = ARTNET_HEADER + bytes(frame['data'][:512])
                sock.sendto(packet, (target_ip, ARTNET_PORT))

                # Per-second Debug Logging
                if time.time() - last_log_time > 1.0:
                    sample = frame['data'][:8] # First 2 RGBW LEDs
                    print(f"[{time.strftime('%H:%M:%S')}] DMX Sample (LED 1&2): {sample}   ", end='\r')
                    last_log_time = time.time()
            
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit()
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True, help="Static IP of the LED controller")
    args = parser.parse_args()

    colors = ["solid_red", "solid_green", "solid_blue", "solid_white", 
              "solid_yellow", "solid_pink", "solid_turquoise", "hue_rotation"]

    while True:
        clear_screen()
        print("====================================")
        print("      WS2814 HARDWARE TEST BENCH    ")
        print("====================================")
        print(f"Target Controller: {args.ip}\n")
        print("Select Color Mode:")
        for i, color in enumerate(colors, 1):
            print(f"{i}. {color}")
        
        try:
            c_input = input("\nChoice (1-8): ")
            if not c_input: continue
            c_choice = int(c_input)
            selected_color = colors[c_choice-1]
            
            clear_screen()
            print(f"=== Select Intensity for {selected_color} ===")
            
            # Logic for brightness options
            if selected_color == "hue_rotation":
                options = ["50", "70", "100"]
            else:
                options = ["50", "100", "range"]
            
            for i, opt in enumerate(options, 1):
                print(f"{i}. {opt}")
            
            b_input = input("\nChoice: ")
            if not b_input: continue
            b_choice = int(b_input)
            selected_brightness = options[b_choice-1]
            
            # Construct filename: color_brightness.json
            filename = f"{selected_color}_{selected_brightness}.json"
            full_path = os.path.join(DEFAULT_FOLDER, filename)
            
            play_engine(args.ip, full_path)

        except (ValueError, IndexError):
            print("\n[!] Invalid selection. Please try again.")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break

if __name__ == "__main__":
    main()