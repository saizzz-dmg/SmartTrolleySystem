import cv2
import time
from prettytable import PrettyTable
import os

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

vid = cv2.VideoCapture(0)
if not vid.isOpened():
    print("Error: Could not open camera.")
    exit()

detector = cv2.QRCodeDetector()
items = {}
last_scan_times = {}  # Dictionary to store last scan times for items
terminate_program = False
total = 0

while not terminate_program:
    ret, frame = vid.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    data, bbox, straight_qrcode = detector.detectAndDecode(frame)

    if len(data) > 0:
        if data.strip().lower() == "terminate":
            terminate_program = True
            for item_key, info in items.items():
                total += info[0] * float(info[3])  # Use index 2 for price
            print("Total Bill: Rs.", total)
        else:
            item_key = tuple(data.split())  # Assume QR code content is in the format: name price weight
            if len(item_key) == 3:
                name = item_key[0]
                price = item_key[1]
                weight = item_key[2]
                current_time = time.time()
                last_scan_time = last_scan_times.get(item_key, 0)

                if current_time - last_scan_time >= 3:  # Allow an update every 3 seconds
                    if item_key in items:
                        choice = input(f"'{name}' is already in the bill. Do you want to add (A) or delete (D) it? ").strip().lower()
                        if choice == 'a':
                            items[item_key][0] += 1
                        elif choice == 'd':
                            del items[item_key]
                        else:
                            print("Invalid choice. Item not modified.")
                    else:
                        items[item_key] = [1, time.strftime("%Y-%m-%d %H:%M:%S"), name, price, weight]
                    last_scan_times[item_key] = current_time

                clear_console()
                print("\t\tBILL")
                table = PrettyTable()
                table.field_names = ["Name", "Quantity", "Price", "Weight", "Timestamp"]
                for item_key, info in items.items():
                    name = info[2]
                    price = info[3]
                    weight = info[4]
                    quantity = info[0]
                    timestamp = info[1]
                    table.add_row([name, quantity, price, weight, timestamp])
                print(table)
                cv2.putText(frame, "Scanned Product: " + data, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                time.sleep(0.5)  # Display the text for 0.5 seconds

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        for item_key, info in items.items():
            total += info[0] * float(info[3])  # Use index 2 for price
        print("Total Bill: Rs.", total)
        break

vid.release()
cv2.destroyAllWindows()