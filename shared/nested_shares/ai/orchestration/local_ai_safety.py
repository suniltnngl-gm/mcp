#!/usr/bin/env python3
"""Local AI Safety Monitor - Protect system performance during llama.cpp execution"""

import psutil
import subprocess
import time
from typing import Dict, Optional, List

class LocalAISafety:
    """Monitor and control llama.cpp resource usage"""
    
    def __init__(self, 
                 max_ram_percent: float = 60,
                 max_cpu_percent: float = 80,
                 max_response_time: float = 20):
        self.max_ram_percent = max_ram_percent
        self.max_cpu_percent = max_cpu_percent
        self.max_response_time = max_response_time
    
    def check_resources(self) -> Dict:
        """Check current system resources"""
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        return {
            'ram_used_percent': mem.percent,
            'ram_available_mb': mem.available / (1024**2),
            'cpu_percent': cpu,
            'swap_used_percent': psutil.swap_memory().percent,
            'safe_to_run': mem.percent < self.max_ram_percent and cpu < self.max_cpu_percent
        }
    
    def get_llama_processes(self) -> List[psutil.Process]:
        """Find all llama.cpp processes"""
        processes = []
        try:
            for proc in psutil.process_iter(['name', 'cmdline']):
                name = proc.info['name'] or ''
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'llama' in name.lower() or 'llama.cpp' in cmdline:
                    processes.append(proc)
        except:
            pass
        return processes
    
    def get_llama_usage(self) -> Optional[Dict]:
        """Get llama.cpp process resource usage"""
        processes = self.get_llama_processes()
        if not processes:
            return None
        
        total_ram = 0
        total_cpu = 0
        
        for proc in processes:
            try:
                total_ram += proc.memory_info().rss / (1024**2)
                total_cpu += proc.cpu_percent()
            except:
                pass
        
        return {
            'ram_mb': total_ram,
            'cpu_percent': total_cpu,
            'process_count': len(processes)
        }
    
    def safe_to_start(self) -> tuple[bool, str]:
        """Check if safe to start llama.cpp"""
        resources = self.check_resources()
        
        # Need at least 1GB free for phi-3-mini-q4
        if resources['ram_available_mb'] < 1000:
            return False, f"Low RAM: {resources['ram_available_mb']:.0f}MB available (need 1000MB)"
        
        if resources['ram_used_percent'] > 70:
            return False, f"High RAM usage: {resources['ram_used_percent']:.0f}%"
        
        if resources['cpu_percent'] > 80:
            return False, f"High CPU usage: {resources['cpu_percent']:.0f}%"
        
        return True, "Safe to start"
    
    def kill_llama_processes(self) -> int:
        """Kill all llama.cpp processes (emergency stop)"""
        processes = self.get_llama_processes()
        killed = 0
        
        for proc in processes:
            try:
                proc.kill()
                killed += 1
            except:
                pass
        
        return killed
    
    def get_recommendations(self) -> list:
        """Get recommendations based on current state"""
        resources = self.check_resources()
        recommendations = []
        
        if resources['ram_available_mb'] < 1000:
            recommendations.append("Close browser/IDE to free RAM")
        
        if resources['swap_used_percent'] > 20:
            recommendations.append("System using swap - performance will be slow")
        
        if resources['cpu_percent'] > 70:
            recommendations.append("High CPU usage - wait before starting local AI")
        
        if not recommendations:
            recommendations.append("System ready for local AI")
        
        return recommendations

def main():
    """CLI interface"""
    import sys
    
    safety = LocalAISafety()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  local_ai_safety.py check    # Check if safe to run")
        print("  local_ai_safety.py status   # Show current status")
        print("  local_ai_safety.py kill     # Kill all llama.cpp processes")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'check':
        safe, reason = safety.safe_to_start()
        print(f"Safe to run: {safe}")
        print(f"Reason: {reason}")
        
        if not safe:
            print("\nRecommendations:")
            for rec in safety.get_recommendations():
                print(f"  - {rec}")
    
    elif cmd == 'status':
        resources = safety.check_resources()
        print(f"\n=== System Status ===")
        print(f"RAM: {resources['ram_used_percent']:.1f}% used")
        print(f"Available: {resources['ram_available_mb']:.0f}MB")
        print(f"CPU: {resources['cpu_percent']:.1f}%")
        print(f"Swap: {resources['swap_used_percent']:.1f}%")
        print(f"Safe: {resources['safe_to_run']}")
        
        usage = safety.get_llama_usage()
        if usage:
            print(f"\n=== llama.cpp Status ===")
            print(f"Processes: {usage['process_count']}")
            print(f"RAM: {usage['ram_mb']:.0f}MB")
            print(f"CPU: {usage['cpu_percent']:.1f}%")
        else:
            print(f"\n=== llama.cpp Status ===")
            print("No processes running")
    
    elif cmd == 'kill':
        killed = safety.kill_llama_processes()
        print(f"Killed {killed} llama.cpp process(es)")

if __name__ == '__main__':
    main()
