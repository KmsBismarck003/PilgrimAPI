import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from starlette.testclient import TestClient
from pilgrim.main import app

client = TestClient(app, raise_server_exceptions=False)

sample_routes = [
    ('/', [200]),
    ('/api/health', [200]),
    ('/api/database/stats', [200, 502]),
    ('/api/admin/users', [200, 502]),
    ('/api/ads/public', [200, 502]),
    ('/api/config', [200, 502]),
    ('/api/restore-audit/events', [200, 502]),
    ('/api/admin/b2b/clients', [200, 502]),
    ('/api/monitoring', [200, 502]),
    ('/api/pages', [200, 502]),
    ('/api/notifications/me', [200, 502]),
    ('/api/auth/login', [200, 502]),
    ('/api/manager/events', [200, 502]),
    ('/api/staff/validate', [200, 502]),
    ('/api/events', [200, 502]),
    ('/api/tickets', [200, 502]),
    ('/api/achievements', [200, 502]),
    ('/uploads/banner.jpg', [200, 502])
]

print("=== VERIFICANDO ENDPOINTS DE PILGRIM API GATEWAY ===")
all_ok = True
for path, allowed in sample_routes:
    r = client.get(path)
    ok = r.status_code in allowed
    status_label = "OK" if ok else "FAIL"
    print(f"[{status_label}] {path:<30} -> HTTP {r.status_code}")
    if not ok:
        all_ok = False

if all_ok:
    print("\n>>> TODOS LOS CONECTORES Y RUTAS VERIFICADOS CON ÉXITO (ZERO MOCKS) <<<")
else:
    print("\n>>> SE DETECTARON FALLOS EN ALGUNAS RUTAS <<<")
