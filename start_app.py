#!/usr/bin/env python3
"""
Nymo Art v4 - Application Startup Script
Checks for occupied ports, terminates existing processes, and starts the application cleanly.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from typing import Optional

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from process_manager import (
    print_status, Colors, get_processes_by_port, kill_processes_on_port,
    wait_for_port_clear, is_port_available, get_project_path
)


def check_dependencies():
    """Check if required dependencies are available."""
    print_status("Checking dependencies...", "INFO")
    
    project_path = get_project_path()
    backend_path = os.path.join(project_path, "backend")
    frontend_path = os.path.join(project_path, "frontend")
    
    # Check if backend directory exists
    if not os.path.exists(backend_path):
        print_status(f"Backend directory not found: {backend_path}", "ERROR")
        return False
    
    # Check if frontend directory exists
    if not os.path.exists(frontend_path):
        print_status(f"Frontend directory not found: {frontend_path}", "ERROR")
        return False
    
    # Check if main.py exists in backend
    main_py = os.path.join(backend_path, "app", "main.py")
    if not os.path.exists(main_py):
        print_status(f"Backend main.py not found: {main_py}", "ERROR")
        return False
    
    # Check if package.json exists in frontend
    package_json = os.path.join(frontend_path, "package.json")
    if not os.path.exists(package_json):
        print_status(f"Frontend package.json not found: {package_json}", "ERROR")
        return False
    
    print_status("All dependencies found", "SUCCESS")
    return True


def ensure_ports_available():
    """Ensure required ports are available, clearing Nymo processes if needed."""
    ports = [8000, 5173]  # Backend, Frontend
    
    for port in ports:
        print_status(f"Checking port {port}...", "INFO")
        
        if is_port_available(port):
            print_status(f"Port {port} is available", "SUCCESS")
            continue
        
        # Port is occupied, check what's using it
        all_processes = get_processes_by_port(port)
        nymo_processes = [p for p in all_processes if p.is_nymo_process]
        non_nymo_processes = [p for p in all_processes if not p.is_nymo_process]
        
        if nymo_processes:
            print_status(f"Found {len(nymo_processes)} existing Nymo processes on port {port}", "WARNING")
            for process in nymo_processes:
                print_status(f"  - PID {process.pid}: {process.full_command[:60]}...", "WARNING")
            
            print_status(f"Terminating existing Nymo processes on port {port}...", "INFO")
            nymo_killed, _ = kill_processes_on_port(port, kill_non_nymo=False)
            
            if nymo_killed > 0:
                print_status(f"Terminated {nymo_killed} Nymo processes", "SUCCESS")
                
                # Wait for port to clear
                if wait_for_port_clear(port, timeout=10):
                    print_status(f"Port {port} is now available", "SUCCESS")
                else:
                    print_status(f"Port {port} still occupied after cleanup", "ERROR")
                    return False
            else:
                print_status(f"Failed to clear Nymo processes on port {port}", "ERROR")
                return False
        
        if non_nymo_processes:
            print_status(f"WARNING: Port {port} is occupied by non-Nymo processes:", "WARNING")
            for process in non_nymo_processes:
                print_status(f"  - PID {process.pid}: {process.full_command[:60]}...", "WARNING")
            
            response = input(f"Kill non-Nymo processes on port {port}? (y/N): ").strip().lower()
            if response == 'y':
                _, non_nymo_killed = kill_processes_on_port(port, kill_non_nymo=True)
                if non_nymo_killed > 0:
                    print_status(f"Terminated {non_nymo_killed} non-Nymo processes", "SUCCESS")
                    if wait_for_port_clear(port, timeout=10):
                        print_status(f"Port {port} is now available", "SUCCESS")
                    else:
                        print_status(f"Port {port} still occupied", "ERROR")
                        return False
                else:
                    print_status(f"Failed to clear non-Nymo processes on port {port}", "ERROR")
                    return False
            else:
                print_status(f"Cannot start application: port {port} is occupied", "ERROR")
                return False
    
    return True


def start_backend():
    """Start the backend server."""
    print_status("Starting backend server...", "INFO")
    
    project_path = get_project_path()
    backend_path = os.path.join(project_path, "backend")
    
    try:
        # Change to backend directory and start uvicorn
        process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print_status("Backend server started successfully", "SUCCESS")
            print_status("Backend running on http://localhost:8000", "SUCCESS")
            return process
        else:
            # Process terminated, get error output
            stdout, stderr = process.communicate()
            print_status("Backend server failed to start", "ERROR")
            if stderr:
                print_status(f"Error: {stderr}", "ERROR")
            if stdout:
                print_status(f"Output: {stdout}", "ERROR")
            return None
            
    except FileNotFoundError:
        print_status("uvicorn not found. Install it with: pip install uvicorn", "ERROR")
        return None
    except Exception as e:
        print_status(f"Error starting backend: {e}", "ERROR")
        return None


def start_frontend():
    """Start the frontend development server."""
    print_status("Starting frontend development server...", "INFO")
    
    project_path = get_project_path()
    frontend_path = os.path.join(project_path, "frontend")
    
    try:
        # Change to frontend directory and start development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print_status("Frontend development server started successfully", "SUCCESS")
            print_status("Frontend running on http://localhost:5173", "SUCCESS")
            return process
        else:
            # Process terminated, get error output
            stdout, stderr = process.communicate()
            print_status("Frontend development server failed to start", "ERROR")
            if stderr:
                print_status(f"Error: {stderr}", "ERROR")
            if stdout:
                print_status(f"Output: {stdout}", "ERROR")
            return None
            
    except FileNotFoundError:
        print_status("npm not found. Make sure Node.js and npm are installed", "ERROR")
        return None
    except Exception as e:
        print_status(f"Error starting frontend: {e}", "ERROR")
        return None


def wait_for_services():
    """Wait for services to be fully ready."""
    print_status("Waiting for services to start...", "INFO")
    
    # Wait for backend to be ready
    backend_ready = False
    for _ in range(30):  # 30 second timeout
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:8000/health", timeout=1)
            backend_ready = True
            break
        except:
            time.sleep(1)
    
    if backend_ready:
        print_status("Backend is ready", "SUCCESS")
    else:
        print_status("Backend health check failed", "WARNING")
    
    # Wait for frontend to be ready
    frontend_ready = False
    for _ in range(30):  # 30 second timeout
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:5173", timeout=1)
            frontend_ready = True
            break
        except:
            time.sleep(1)
    
    if frontend_ready:
        print_status("Frontend is ready", "SUCCESS")
    else:
        print_status("Frontend availability check failed", "WARNING")
    
    return backend_ready and frontend_ready


def main():
    """Main startup function."""
    print_status("🚀 Nymo Art v4 - Application Startup", "HEADER")
    print_status("=" * 50, "HEADER")
    
    # Check dependencies
    if not check_dependencies():
        print_status("❌ Dependency check failed", "ERROR")
        sys.exit(1)
    
    # Ensure ports are available
    if not ensure_ports_available():
        print_status("❌ Port setup failed", "ERROR")
        sys.exit(1)
    
    # Start services
    backend_process = start_backend()
    if not backend_process:
        print_status("❌ Backend startup failed", "ERROR")
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        print_status("❌ Frontend startup failed", "ERROR")
        # Kill backend if frontend fails
        backend_process.terminate()
        sys.exit(1)
    
    # Wait for services to be ready
    services_ready = wait_for_services()
    
    # Final status
    print_status("=" * 50, "HEADER")
    if services_ready:
        print_status("✅ Nymo Art v4 started successfully!", "SUCCESS")
        print_status("", "INFO")
        print_status("🌐 Frontend: http://localhost:5173", "SUCCESS")
        print_status("🔧 Backend API: http://localhost:8000", "SUCCESS")
        print_status("📚 API Docs: http://localhost:8000/docs", "SUCCESS")
        print_status("", "INFO")
        print_status("Press Ctrl+C to stop the application", "INFO")
    else:
        print_status("⚠️ Services started but health checks failed", "WARNING")
        print_status("Check the application manually", "WARNING")
    
    print_status("=" * 50, "HEADER")
    
    # Keep the script running and handle graceful shutdown
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print_status("Backend process terminated unexpectedly", "ERROR")
                break
                
            if frontend_process.poll() is not None:
                print_status("Frontend process terminated unexpectedly", "ERROR")
                break
                
    except KeyboardInterrupt:
        print_status("Received shutdown signal", "INFO")
        
        # Graceful shutdown
        print_status("Stopping services...", "INFO")
        
        if frontend_process.poll() is None:
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
                print_status("Frontend stopped", "SUCCESS")
            except subprocess.TimeoutExpired:
                frontend_process.kill()
                print_status("Frontend force killed", "WARNING")
        
        if backend_process.poll() is None:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
                print_status("Backend stopped", "SUCCESS")
            except subprocess.TimeoutExpired:
                backend_process.kill()
                print_status("Backend force killed", "WARNING")
        
        print_status("Application stopped", "SUCCESS")


if __name__ == "__main__":
    main()
