#!/usr/bin/env python3

import socket
import threading
import time
import logging
from datetime import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address, server):
        self.connection = connection
        self.address = address
        self.server = server
        threading.Thread.__init__(self)
    
    def run(self):
        """Menangani komunikasi dengan client"""
        try:
            while self.server.running:
                data = self.connection.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                print(f"[REQUEST] {self.address}: {message}")

                response = self.server.process_command(message)
                
                if response:
                    self.connection.send(response.encode('utf-8'))
                    print(f"[RESPONSE] {self.address}: {response.strip()}")

                if message.upper() == "QUIT":
                    break
                    
        except ConnectionResetError:
            print(f"[INFO] Client {self.address} terputus")
        except Exception as e:
            print(f"[ERROR] Error menangani client {self.address}: {e}")
        finally:
            try:
                self.connection.close()
                print(f"[INFO] Koneksi dengan {self.address} ditutup")
            except:
                pass

class TimeServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=45000):
        self.host = host
        self.port = port
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        threading.Thread.__init__(self)
    
    def run(self):
        """Memulai server"""
        try:
            self.my_socket.bind((self.host, self.port))
            self.my_socket.listen(5)
            self.running = True
            
            print(f"[INFO] Time Server dimulai di {self.host}:{self.port}")
            print("[INFO] Menunggu koneksi client...")
            
            while self.running:
                try:
                    connection, client_address = self.my_socket.accept()
                    logging.warning(f"connection from {client_address}")
                    print(f"[INFO] Client terhubung dari {client_address}")
                    
                    clt = ProcessTheClient(connection, client_address, self)
                    clt.start()
                    self.the_clients.append(clt)
                    
                except OSError:
                    if self.running:
                        print("[ERROR] Error saat menerima koneksi")
                    break
                    
        except Exception as e:
            print(f"[ERROR] Error memulai server: {e}")
        finally:
            self.stop()
    
    def process_command(self, command):
        """Memproses perintah dari client"""
        command = command.strip().upper()
        
        if command == "TIME":
            current_time = datetime.now()
            formatted_time = current_time.strftime("%H:%M:%S")
            return f"JAM: {formatted_time}\r\n"
        
        elif command == "QUIT":
            return "GOODBYE\r\n"
        
        else:
            return "ERROR: Unknown command. Available commands: TIME, QUIT\r\n"
    
    def stop(self):
        """Menghentikan server"""
        self.running = False
        if self.my_socket:
            try:
                self.my_socket.close()
                print("[INFO] Server dihentikan")
            except:
                pass

def main():
    """Fungsi utama"""
    import sys
    
    host = '0.0.0.0'
    port = 45000
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("[ERROR] Port harus berupa angka")
            return

    logging.basicConfig(level=logging.WARNING)
    
    server = TimeServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[INFO] Server dihentikan oleh user")
        server.stop()

if __name__ == "__main__":
    main()