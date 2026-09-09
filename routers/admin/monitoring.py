"""
Pilgrim Gateway - Conector de Monitoreo y Telemetría para Admin
Enruta métricas de rendimiento, usuarios activos y logs operativos hacia el microservicio de stats,
y expone un canal WebSocket de telemetría en tiempo real (/api/monitoring/ws).
"""
import asyncio
import os
import psutil
from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect
from pilgrim.core.config import SERVICES, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Monitoreo"])

def collect_system_and_db_metrics():
    """Recolecta métricas reales del sistema y de MySQL."""
    # Métricas de sistema
    cpu_pct = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    system_metrics = {
        "cpu": {"percent": round(cpu_pct, 1)},
        "memory": {
            "percent": round(mem.percent, 1),
            "used_mb": round(mem.used / (1024 * 1024), 1),
            "total_mb": round(mem.total / (1024 * 1024), 1)
        },
        "disk": {
            "percent": round(disk.percent, 1),
            "used_gb": round(disk.used / (1024 * 1024 * 1024), 1),
            "total_gb": round(disk.total / (1024 * 1024 * 1024), 1)
        }
    }

    # Métricas de base de datos
    db_metrics = {
        "status": "healthy",
        "uptime": 0,
        "connections": {"active": 1, "running": 1, "max": 150, "usage_percent": 1},
        "queries": {"total": 0, "slow": 0}
    }
    performance_metrics = {
        "buffer_pool": {"hit_ratio": 99.2, "size_mb": 128.0}
    }
    sessions_metrics = {"active_sessions": 1}

    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4",
            connect_timeout=2
        )
        with conn.cursor() as cur:
            # Uptime y conexiones
            cur.execute("SHOW GLOBAL STATUS WHERE Variable_name IN ('Uptime', 'Threads_connected', 'Threads_running', 'Questions', 'Slow_queries', 'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests')")
            status_map = {row[0]: row[1] for row in cur.fetchall()}
            
            cur.execute("SHOW GLOBAL VARIABLES WHERE Variable_name IN ('max_connections', 'innodb_buffer_pool_size')")
            var_map = {row[0]: row[1] for row in cur.fetchall()}

            uptime = int(status_map.get("Uptime", 0))
            threads_conn = int(status_map.get("Threads_connected", 1))
            threads_run = int(status_map.get("Threads_running", 1))
            max_conn = int(var_map.get("max_connections", 150))
            questions = int(status_map.get("Questions", 0))
            slow_q = int(status_map.get("Slow_queries", 0))

            pool_reads = float(status_map.get("Innodb_buffer_pool_reads", 0))
            pool_reqs = float(status_map.get("Innodb_buffer_pool_read_requests", 1))
            hit_ratio = round((1.0 - (pool_reads / pool_reqs if pool_reqs > 0 else 0)) * 100, 1)
            pool_size_mb = round(int(var_map.get("innodb_buffer_pool_size", 134217728)) / (1024 * 1024), 1)

            db_metrics["status"] = "healthy"
            db_metrics["uptime"] = uptime
            db_metrics["connections"] = {
                "active": threads_conn,
                "running": threads_run,
                "max": max_conn,
                "usage_percent": round((threads_conn / max_conn) * 100, 1) if max_conn > 0 else 0
            }
            db_metrics["queries"] = {
                "total": questions,
                "slow": slow_q
            }
            performance_metrics["buffer_pool"] = {
                "hit_ratio": hit_ratio,
                "size_mb": pool_size_mb
            }
            sessions_metrics["active_sessions"] = threads_conn
        conn.close()
    except Exception as e:
        db_metrics["status"] = "warning"
        db_metrics["error"] = str(e)

    return {
        "status": "success",
        "data": {
            "database": db_metrics,
            "performance": performance_metrics,
            "sessions": sessions_metrics,
            "system": system_metrics
        }
    }

@router.api_route("/api/monitoring", methods=["GET"])
@router.api_route("/api/monitoring/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def monitoring_proxy(request: Request, sub_path: str = "") -> Response:
    """Reenvía la telemetría al microservicio stats o responde con métricas locales si falla."""
    target_path = f"/{sub_path}" if sub_path else ""
    resp = await proxy_request(request, SERVICES["stats"], target_path)
    
    # Si el microservicio de stats no responde y se pide métricas/estado, servir métricas directas
    if resp.status_code >= 500 and (not sub_path or sub_path in ["status", "metrics"]):
        metrics = collect_system_and_db_metrics()
        import json
        return Response(content=json.dumps(metrics), media_type="application/json")

    return resp

@router.websocket("/api/monitoring/ws")
@router.websocket("/monitoring/ws")
async def monitoring_ws(websocket: WebSocket):
    """Canal WebSocket para emisión continua de telemetría a la vista DatabaseMonitor."""
    await websocket.accept()
    try:
        while True:
            metrics = collect_system_and_db_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[PILGRIM WS MONITOR ERROR] {e}")
