#!/usr/bin/env python3
"""Ollama Safety Monitor - Protect system performance"""

import psutil
import subprocess
import time
from typing import Dict, Optional

class OllamaSafety:
    """Monitor and control Ollama resource usage"""
    
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
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            for proc in psutil.process_iter(['name']):
                if 'ollama' in proc.info['name'].lower():
                    return True
        except:
            pass
        return False
    
    def get_ollama_usage(self) -> Optional[Dict]:
        """Get Ollama process resource usage"""
        try:
            for proc in psutil.process_iter(['name', 'memory_percent', 'cpu_percent']):
                if 'ollama' in proc.info['name'].lower():
                    return {
                        'ram_percent': proc.info['memory_percent'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'ram_mb': proc.memory_info().rss / (1024**2)
                    }
        except:
            pass
        return None
    
    def safe_to_start(self) -> tuple[bool, str]:
        """Check if safe to start Ollama"""
        resources = self.check_resources()
        
        # Need at least 1.5GB free for phi:2.7b
        if resources['ram_available_mb'] < 1500:
            return False, f"Low RAM: {resources['ram_available_mb']:.0f}MB available (need 1500MB)"
        
        if resources['ram_used_percent'] > 70:
            return False, f"High RAM usage: {resources['ram_used_percent']:.0f}%"
        
        if resources['cpu_percent'] > 80:
            return False, f"High CPU usage: {resources['cpu_percent']:.0f}%"
        
        return True, "Safe to start"
    
    def monitor_during_run(self, duration: int = 10) -> Dict:
        """Monitor resources during Ollama execution"""
        samples = []
        
        for _ in range(duration):
            resources = self.check_resources()
            ollama = self.get_ollama_usage()
            
            samples.append({
                'system_ram': resources['ram_used_percent'],
                'system_cpu': resources['cpu_percent'],
                'ollama_ram': ollama['ram_percent'] if ollama else 0,
                'ollama_cpu': ollama['cpu_percent'] if ollama else 0
            })
            
            time.sleep(1)
        
        # Calculate averages
        avg = {
            'avg_system_ram': sum(s['system_ram'] for s in samples) / len(samples),
            'avg_system_cpu': sum(s['system_cpu'] for s in samples) / len(samples),
            'avg_ollama_ram': sum(s['ollama_ram'] for s in samples) / len(samples),
            'avg_ollama_cpu': sum(s['ollama_cpu'] for s in samples) / len(samples),
            'max_system_ram': max(s['system_ram'] for s in samples),
            'max_system_cpu': max(s['system_cpu'] for s in samples)
        }
        
        return avg
    
    def emergency_stop(self) -> bool:
        """Emergency stop Ollama if system overloaded"""
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'ollama'], 
                         capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def safe_start(self) -> tuple[bool, str]:
        """Safely start Ollama with checks"""
        safe, reason = self.safe_to_start()
        
        if not safe:
            return False, reason
        
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'ollama'],
                         capture_output=True, timeout=5)
            time.sleep(2)
            
            if self.is_ollama_running():
                return True, "Started successfully"
            else:
                return False, "Failed to start"
        except Exception as e:
            return False, str(e)
    
    def get_recommendations(self) -> list:
        """Get recommendations based on current state"""
        resources = self.check_resources()
        recommendations = []
        
        if resources['ram_available_mb'] < 1500:
            recommendations.append("Close browser/IDE to free RAM")
        
        if resources['swap_used_percent'] > 20:
            recommendations.append("System using swap - performance will be slow")
        
        if resources['cpu_percent'] > 70:
            recommendations.append("High CPU usage - wait before starting Ollama")
        
        if not recommendations:
            recommendations.append("System ready for Ollama")
        
        return recommendations

def main():
    """CLI interface"""
    import sys
    
    safety = OllamaSafety()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ollama_safety.py check      # Check if safe to run")
        print("  ollama_safety.py status     # Show current status")
        print("  ollama_safety.py monitor    # Monitor during run")
        print("  ollama_safety.py start      # Safe start")
        print("  ollama_safety.py stop       # Emergency stop")
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
        
        if safety.is_ollama_running():
            print(f"\n=== Ollama Status ===")
            usage = safety.get_ollama_usage()
            if usage:
                print(f"RAM: {usage['ram_mb']:.0f}MB ({usage['ram_percent']:.1f}%)")
                print(f"CPU: {usage['cpu_percent']:.1f}%")
    
    elif cmd == 'monitor':
        print("Monitoring for 10 seconds...")
        stats = safety.monitor_during_run(10)
        print(f"\n=== Monitoring Results ===")
        print(f"Avg System RAM: {stats['avg_system_ram']:.1f}%")
        print(f"Avg System CPU: {stats['avg_system_cpu']:.1f}%")
        print(f"Avg Ollama RAM: {stats['avg_ollama_ram']:.1f}%")
        print(f"Avg Ollama CPU: {stats['avg_ollama_cpu']:.1f}%")
        print(f"Max System RAM: {stats['max_system_ram']:.1f}%")
        print(f"Max System CPU: {stats['max_system_cpu']:.1f}%")
        
        if stats['max_system_ram'] > 85:
            print("\n⚠️  WARNING: High RAM usage detected!")
        if stats['max_system_cpu'] > 90:
            print("\n⚠️  WARNING: High CPU usage detected!")
    
    elif cmd == 'start':
        success, msg = safety.safe_start()
        print(f"Start: {success}")
        print(f"Message: {msg}")
    
    elif cmd == 'stop':
        success = safety.emergency_stop()
        print(f"Stopped: {success}")

if __name__ == '__main__':
    main()
