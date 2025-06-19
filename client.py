#!/usr/bin/env python3

import socket
import sys
import time

class TimeClient:
    def __init__(self, host='172.16.16.101', port=45000):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
    
    def connect(self):
        """Membuat koneksi ke server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"[INFO] Terhubung ke Time Server {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"[ERROR] Tidak dapat terhubung ke server {self.host}:{self.port}")
            print("[ERROR] Pastikan server sedang berjalan")
            return False
        except Exception as e:
            print(f"[ERROR] Error koneksi: {e}")
            return False
    
    def disconnect(self):
        """Memutus koneksi dari server"""
        if self.connected and self.client_socket:
            try:
                self.send_request("QUIT")
                self.client_socket.close()
            except:
                pass
            finally:
                self.connected = False
                print("[INFO] Koneksi ditutup")
    
    def send_request(self, message):
        """Mengirim request ke server"""
        if not self.connected:
            print("[ERROR] Tidak terhubung ke server")
            return None
        
        try:
            # Format pesan dengan \r\n sesuai protokol
            formatted_message = f"{message}\r\n"
            self.client_socket.send(formatted_message.encode('utf-8'))
            
            if message.upper() == "QUIT":
                return "QUIT_SENT"
            response = self.client_socket.recv(1024).decode('utf-8').strip()
            return response
            
        except ConnectionResetError:
            print("[ERROR] Koneksi terputus oleh server")
            self.connected = False
            return None
        except Exception as e:
            print(f"[ERROR] Error mengirim request: {e}")
            return None
    
    def get_time(self):
        """Meminta waktu dari server"""
        response = self.send_request("TIME")
        if response:
            print(f"[RESPONSE] {response}")
            return response
        return None
    
    def interactive_mode(self):
        """Mode interaktif untuk berkomunikasi dengan server"""
        print("\n" + "=" * 50)
        print("TIME CLIENT")
        print("=" * 50)
        print("  1. TIME  ")
        print("  2. QUIT  ")
        print("=" * 50)
        print()
        
        while self.connected:
            try:
                command = input(">> ").strip().upper()
                
                if not command:
                    continue
                
                if command == "QUIT":
                    break
                
                elif command == "TIME":
                    self.get_time()
                
                else:
                    print(f"[ERROR] Perintah tidak dikenal: {command}")
                    print("Perintah yang tersedia: TIME, QUIT")
                    
            except KeyboardInterrupt:
                print("\n[INFO] Interrupt received")
                break
            except EOFError:
                print("\n[INFO] EOF received")
                break
    
    def run_single_request(self, command="TIME"):
        """Menjalankan satu request saja"""
        if not self.connect():
            return False
        
        print(f"[REQUEST] Mengirim: {command}")
        response = self.send_request(command)
        
        if response and response != "QUIT_SENT":
            print(f"[RESPONSE] {response}")
        
        self.disconnect()
        return True

def print_usage():
    """Menampilkan cara penggunaan program"""
    print("Penggunaan:")
    print(f"  {sys.argv[0]} [HOST] [PORT] [MODE]")
    print()
    print("Parameter:")
    print("  HOST  - Alamat server (default: 172.16.16.101)")
    print("  PORT  - Port server (default: 45000)")
    print("  MODE  - Mode operasi:")
    print("          interactive : Mode interaktif (default)")
    print("          single      : Satu request TIME saja")
    print()
    print("Contoh:")
    print(f"  {sys.argv[0]}")
    print(f"  {sys.argv[0]} 172.16.16.101 45000 interactive")
    print(f"  {sys.argv[0]} 192.168.1.100 45000 single")

def main():
    """Fungsi utama"""
    host = '172.16.16.101'  
    port = 45000
    mode = 'interactive'
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print_usage()
            return
        host = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("[ERROR] Port harus berupa angka")
            return
    
    if len(sys.argv) > 3:
        mode = sys.argv[3].lower()
        if mode not in ['interactive', 'single']:
            print("[ERROR] Mode harus 'interactive' atau 'single'")
            return
    
    client = TimeClient(host, port)
    
    try:
        if mode == 'single':
            client.run_single_request()
        else:
            if client.connect():
                client.interactive_mode()
                client.disconnect()
            
    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan oleh user")
        client.disconnect()
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        client.disconnect()

if __name__ == "__main__":
    main()