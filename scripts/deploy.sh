# deploy.sh
#!/usr/bin/env bash
# ─────────────────────────────────────────────
# CitizenAI — Local Deploy/Dev Helper
# Usage:
#   ./scripts/deploy.sh dev       → start dev stack (live reload)
#   ./scripts/deploy.sh prod      → start production stack
#   ./scripts/deploy.sh down      → stop all containers
#   ./scripts/deploy.sh logs      → tail logs
#   ./scripts/deploy.sh rebuild   → force rebuild + restart
# ─────────────────────────────────────────────

set -euo pipefail
CMD="${1:-help}"

case "$CMD" in
  dev)
    echo "🔧 Starting DEV stack..."
    docker compose \
      -f docker-compose.yml \
      -f docker-compose.dev.yml \
      up --build
    ;;

  prod)
    echo "🚀 Starting PRODUCTION stack..."
    docker compose up -d --build
    echo "✅ Running at http://localhost"
    ;;

  down)
    echo "🛑 Stopping all services..."
    docker compose down
    ;;

  logs)
    docker compose logs -f --tail=100
    ;;

  rebuild)
    echo "🔄 Rebuilding images..."
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    ;;

  *)
    echo "Usage: $0 {dev|prod|down|logs|rebuild}"
    exit 1
    ;;
esac