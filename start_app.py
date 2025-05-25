#!/usr/bin/env python3
"""
Nymo Art v4 - Application Startup Script
Checks for occupied ports, terminates existing processes, and starts the application cleanly.
"""

import os
import sys
import time
import signal
import subprocess
import platform
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(message: str, status: str = "INFO") -> None:
    """Print formatted status message."""
    colors = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "HEADER": Colors.HEADER
    }
    color = colors.get(status, Colors.OKBLUE)
    print(f"{color}[{status}]{Colors.ENDC} {message}")


def check_port_occupied(port: int) -> List[int]:
    """Check if a port is occupied and return list of PIDs using it."""
    pids = []
    
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = [int(pid) for pid in result.stdout.strip().split('\n') if pid.strip()]
                
        elif platform.system() == "Linux":
            result = subprocess.run(
                ["ss", "-tlnp", f"sport = {port}"],
                capture_output=True,
                text=True,
                check=False
            )
            # Parse ss output to extract PIDs
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "pid=" in line:
                        # Extract PID from ss output
                        pid_part = line.split("pid=")[1].split(",")[0]
                        try:
                            pids.append(int(pid_part))
                        except ValueError:
                            continue
                            
        elif platform.system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                pids.append(int(parts[-1]))
                            except ValueError:
                                continue
                                
    except Exception as e:
        print_status(f"Error checking port {port}: {e}", "ERROR")
        
    return pids


def terminate_processes(pids: List[int], port: int) -> bool:
    """Terminate processes by PID."""
    if not pids:
        return True
        
    print_status(f"Found processes on port {port}: {pids}", "WARNING")
    
    for pid in pids:
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                # Check if process still exists, force kill if necessary
                try:
                    os.kill(pid, 0)  # Check if process exists
                    print_status(f"Process {pid} still running, force killing...", "WARNING")
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already terminated
                    
            print_status(f"Terminated process {pid}", "SUCCESS")
            
        except (ProcessLookupError, PermissionError) as e:
            print_status(f"Could not terminate process {pid}: {e}", "WARNING")
        except Exception as e:
            print_status(f"Error terminating process {pid}: {e}", "ERROR")
            return False
            
    # Wait a bit for ports to be freed
    time.sleep(2)
    return True


def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    print_status("Checking dependencies...", "INFO")
    
    # Check if Python requirements are met
    backend_path = Path(__file__).parent / "backend"
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print_status("requirements.txt not found", "ERROR")
        return False
        
    # Check if Node.js and npm are available
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("Node.js and npm are required for frontend", "ERROR")
        return False
        
    # Check if frontend dependencies are installed
    frontend_path = Path(__file__).parent / "frontend"
    node_modules = frontend_path / "node_modules"
    
    if not node_modules.exists():
        print_status("Frontend dependencies not installed, running npm install...", "WARNING")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
            print_status("Frontend dependencies installed", "SUCCESS")
        except subprocess.CalledProcessError:
            print_status("Failed to install frontend dependencies", "ERROR")
            return False
            
    print_status("Dependencies check completed", "SUCCESS")
    return True


def start_backend() -> Optional[subprocess.Popen]:
    """Start the FastAPI backend server."""
    print_status("Starting backend server...", "INFO")
    
    backend_path = Path(__file__).parent / "backend"
    
    try:
        # Start uvicorn server
        process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--reload", 
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit and check if process is still running
        time.sleep(3)
        
        if process.poll() is None:
            print_status("Backend server started successfully on port 8000", "SUCCESS")
            return process
        else:
            stdout, stderr = process.communicate()
            print_status(f"Backend failed to start: {stderr.decode()}", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"Error starting backend: {e}", "ERROR")
        return None


def start_frontend() -> Optional[subprocess.Popen]:
    """Start the React frontend development server."""
    print_status("Starting frontend server...", "INFO")
    
    frontend_path = Path(__file__).parent / "frontend"
    
    try:
        # Start Vite dev server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit and check if process is still running
        time.sleep(3)
        
        if process.poll() is None:
            print_status("Frontend server started successfully on port 5173", "SUCCESS")
            return process
        else:
            stdout, stderr = process.communicate()
            print_status(f"Frontend failed to start: {stderr.decode()}", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"Error starting frontend: {e}", "ERROR")
        return None


def main():
    """Main startup function."""
    print_status("🚀 Nymo Art v4 - Application Startup", "HEADER")
    print_status("=" * 50, "HEADER")
    
    # Define ports to check
    ports = [8000, 5173]  # Backend, Frontend
    
    # Check and clean up occupied ports
    for port in ports:
        print_status(f"Checking port {port}...", "INFO")
        occupied_pids = check_port_occupied(port)
        
        if occupied_pids:
            print_status(f"Port {port} is occupied", "WARNING")
            if not terminate_processes(occupied_pids, port):
                print_status(f"Failed to clean up port {port}", "ERROR")
                sys.exit(1)
        else:
            print_status(f"Port {port} is free", "SUCCESS")
    
    # Check dependencies
    if not check_dependencies():
        print_status("Dependency check failed", "ERROR")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print_status("Failed to start backend", "ERROR")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print_status("Failed to start frontend", "ERROR")
        # Clean up backend process
        backend_process.terminate()
        sys.exit(1)
    
    # Success message
    print_status("=" * 50, "HEADER")
    print_status("🎉 Application started successfully!", "SUCCESS")
    print_status("Backend:  http://localhost:8000", "SUCCESS")
    print_status("Frontend: http://localhost:5173", "SUCCESS")
    print_status("API Docs: http://localhost:8000/docs", "SUCCESS")
    print_status("=" * 50, "HEADER")
    print_status("Press Ctrl+C to stop all services", "INFO")
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print_status("Backend process died unexpectedly", "ERROR")
                break
                
            if frontend_process.poll() is not None:
                print_status("Frontend process died unexpectedly", "ERROR")
                break
                
    except KeyboardInterrupt:
        print_status("\n🛑 Shutting down services...", "WARNING")
        
        # Terminate processes gracefully
        try:
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for graceful shutdown
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            print_status("Force killing processes...", "WARNING")
            backend_process.kill()
            frontend_process.kill()
        
        print_status("All services stopped", "SUCCESS")


if __name__ == "__main__":
    main()
