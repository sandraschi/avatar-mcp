"""
System information tool for the Avatar MCP chatbot.

This tool allows the chatbot to query system information and status.
"""

import asyncio
import json
import logging
import platform
import psutil
import socket
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_tool import (
    ChatTool,
    ToolResult,
    ToolParameter,
    ToolParameterType,
    ToolExecutionStatus,
)

logger = logging.getLogger(__name__)

class SystemInfoTool(ChatTool):
    """Tool for retrieving system information and status."""
    
    def __init__(self):
        """Initialize the system info tool."""
        super().__init__()
        self._start_time = time.time()
        
        # Initialize system metrics
        self._cpu_count = psutil.cpu_count()
        self._boot_time = psutil.boot_time()
        self._hostname = socket.gethostname()
        self._ip_address = self._get_ip_address()
    
    @property
    def name(self) -> str:
        return "get_system_info"
    
    @property
    def description(self) -> str:
        return "Get information about the system, including CPU, memory, disk usage, and network status."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="category",
                type=ToolParameterType.STRING,
                description="Category of system information to retrieve",
                required=False,
                enum=[
                    "all", "cpu", "memory", "disk", "network", 
                    "processes", "system", "status"
                ],
                default="all"
            ),
            ToolParameter(
                name="details",
                type=ToolParameterType.BOOLEAN,
                description="Whether to include detailed information",
                required=False,
                default=False
            ),
            ToolParameter(
                name="refresh",
                type=ToolParameterType.BOOLEAN,
                description="Whether to refresh cached information",
                required=False,
                default=False
            )
        ]
    
    def _get_ip_address(self) -> str:
        """Get the primary IP address of the system."""
        try:
            # Create a socket connection to a remote server (doesn't actually establish a connection)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            # Using Google's public DNS server to find the best route
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception:
            return "127.0.0.1"
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_times = psutil.cpu_times_percent(interval=0.1)
            
            return {
                "cpu_count": self._cpu_count,
                "cpu_percent": cpu_percent,
                "cpu_times": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle,
                    "iowait": getattr(cpu_times, 'iowait', 0.0),
                    "irq": getattr(cpu_times, 'irq', 0.0),
                    "softirq": getattr(cpu_times, 'softirq', 0.0),
                    "steal": getattr(cpu_times, 'steal', 0.0),
                    "guest": getattr(cpu_times, 'guest', 0.0),
                    "guest_nice": getattr(cpu_times, 'guest_nice', 0.0)
                },
                "freq": {
                    "current": psutil.cpu_freq().current if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None,
                    "min": psutil.cpu_freq().min if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None,
                    "max": psutil.cpu_freq().max if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None
                } if hasattr(psutil, 'cpu_freq') else {}
            }
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}", exc_info=True)
            return {"error": f"Failed to get CPU info: {str(e)}"}
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            return {
                "virtual": {
                    "total": virtual_mem.total,
                    "available": virtual_mem.available,
                    "used": virtual_mem.used,
                    "free": virtual_mem.free,
                    "percent": virtual_mem.percent,
                    "unit": "bytes"
                },
                "swap": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "free": swap_mem.free,
                    "percent": swap_mem.percent,
                    "sin": swap_mem.sin,
                    "sout": swap_mem.sout,
                    "unit": "bytes"
                }
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}", exc_info=True)
            return {"error": f"Failed to get memory info: {str(e)}"}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                "partitions": [
                    {
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "opts": part.opts,
                        "usage": {
                            "total": psutil.disk_usage(part.mountpoint).total,
                            "used": psutil.disk_usage(part.mountpoint).used,
                            "free": psutil.disk_usage(part.mountpoint).free,
                            "percent": psutil.disk_usage(part.mountpoint).percent,
                            "unit": "bytes"
                        }
                    }
                    for part in psutil.disk_partitions(all=False)
                ],
                "io": {
                    "read_count": disk_io.read_count if disk_io else None,
                    "write_count": disk_io.write_count if disk_io else None,
                    "read_bytes": disk_io.read_bytes if disk_io else None,
                    "write_bytes": disk_io.write_bytes if disk_io else None,
                    "read_time": disk_io.read_time if disk_io else None,
                    "write_time": disk_io.write_time if disk_io else None,
                    "busy_time": disk_io.busy_time if disk_io and hasattr(disk_io, 'busy_time') else None
                } if disk_io else {}
            }
        except Exception as e:
            logger.error(f"Error getting disk info: {e}", exc_info=True)
            return {"error": f"Failed to get disk info: {str(e)}"}
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        try:
            net_io = psutil.net_io_counters()
            net_connections = psutil.net_connections(kind='inet')
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            return {
                "hostname": self._hostname,
                "ip_address": self._ip_address,
                "io": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout,
                    "unit": "bytes"
                },
                "interfaces": [
                    {
                        "name": name,
                        "addresses": [
                            {
                                "family": str(addr.family),
                                "address": addr.address,
                                "netmask": addr.netmask,
                                "broadcast": addr.broadcast,
                                "ptp": addr.ptp
                            }
                            for addr in addrs
                        ],
                        "stats": {
                            "isup": net_if_stats[name].isup if name in net_if_stats else None,
                            "duplex": net_if_stats[name].duplex if name in net_if_stats else None,
                            "speed": net_if_stats[name].speed if name in net_if_stats else None,
                            "mtu": net_if_stats[name].mtu if name in net_if_stats else None
                        } if name in net_if_stats else {}
                    }
                    for name, addrs in net_if_addrs.items()
                ],
                "connections": [
                    {
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    }
                    for conn in net_connections
                    if conn.status == 'ESTABLISHED'  # Only show established connections
                ]
            }
        except Exception as e:
            logger.error(f"Error getting network info: {e}", exc_info=True)
            return {"error": f"Failed to get network info: {str(e)}"}
    
    def _get_processes_info(self) -> Dict[str, Any]:
        """Get information about running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "username": pinfo['username'],
                        "status": pinfo['status'],
                        "cpu_percent": pinfo['cpu_percent'],
                        "memory_percent": pinfo['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU usage (descending)
            processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                "process_count": len(processes),
                "processes": processes[:10]  # Only return top 10 by CPU
            }
        except Exception as e:
            logger.error(f"Error getting processes info: {e}", exc_info=True)
            return {"error": f"Failed to get processes info: {str(e)}"}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        try:
            return {
                "platform": {
                    "system": platform.system(),
                    "node": platform.node(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version()
                },
                "boot_time": datetime.fromtimestamp(self._boot_time).isoformat(),
                "uptime": time.time() - self._boot_time,
                "timezone": time.tzname[0],
                "time": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}", exc_info=True)
            return {"error": f"Failed to get system info: {str(e)}"}
    
    def _get_status_info(self) -> Dict[str, Any]:
        """Get system status information."""
        try:
            cpu = self._get_cpu_info()
            memory = self._get_memory_info()
            disk = self._get_disk_info()
            
            return {
                "status": "operational",  # This would be determined by checking various metrics
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - self._boot_time,
                "cpu": {
                    "usage_percent": cpu.get("cpu_percent", 0),
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else []
                },
                "memory": {
                    "virtual_used_percent": memory.get("virtual", {}).get("percent", 0),
                    "swap_used_percent": memory.get("swap", {}).get("percent", 0)
                },
                "disk": {
                    "root_used_percent": next(
                        (p["usage"]["percent"] for p in disk.get("partitions", []) 
                         if p["mountpoint"] == "/"), 
                        0
                    )
                }
            }
        except Exception as e:
            logger.error(f"Error getting status info: {e}", exc_info=True)
            return {"error": f"Failed to get status info: {str(e)}"}
    
    async def execute(
        self,
        category: str = "all",
        details: bool = False,
        refresh: bool = False,
        **kwargs
    ) -> ToolResult:
        """
        Get system information.
        
        Args:
            category: Category of system information to retrieve
            details: Whether to include detailed information
            refresh: Whether to refresh cached information
            
        Returns:
            ToolResult with system information
        """
        try:
            # In a real implementation, we might cache some of this information
            # and use the refresh parameter to determine whether to update it
            
            result = {}
            
            if category in ["all", "cpu"]:
                result["cpu"] = self._get_cpu_info()
                
            if category in ["all", "memory"]:
                result["memory"] = self._get_memory_info()
                
            if category in ["all", "disk"]:
                result["disk"] = self._get_disk_info()
                
            if category in ["all", "network"]:
                result["network"] = self._get_network_info()
                
            if category in ["all", "processes"] or (details and category == "all"):
                result["processes"] = self._get_processes_info()
                
            if category in ["all", "system"] or (details and category == "all"):
                result["system"] = self._get_system_info()
                
            if category in ["all", "status"] or category == "all":
                result["status"] = self._get_status_info()
            
            # Add server-specific information if available
            if hasattr(self, 'server') and self.server:
                result["server"] = {
                    "start_time": self._start_time,
                    "uptime": time.time() - self._start_time,
                    "version": getattr(self.server, 'version', 'unknown'),
                    "status": getattr(self.server, 'status', 'unknown')
                }
            
            return ToolResult.success(
                content=result,
                metadata={
                    "category": category,
                    "details": details,
                    "timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting system information: {e}", exc_info=True)
            return ToolResult.error(f"Failed to get system information: {str(e)}")

# Example usage:
# tool = SystemInfoTool()
# result = await tool.execute(
#     category="status",
#     details=False
# )
# print(json.dumps(result.to_dict(), indent=2))
