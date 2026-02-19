#!/usr/bin/env bash
# Import Docker images into K3s containerd (single-node)
#
# Usage (local):  ./scripts/import_images.sh latest
# Usage (remote): K3S_HOST=user@host ./scripts/import_images.sh latest
set -euo pipefail

TAG="${1:-latest}"
IMAGES=("streamflow/pyflink" "streamflow/generator" "streamflow/airflow-dbt")

import_local() {
    for img in "${IMAGES[@]}"; do
        echo "Importing ${img}:${TAG} into K3s..."
        docker save "${img}:${TAG}" | sudo k3s ctr images import -
    done
}

import_remote() {
    for img in "${IMAGES[@]}"; do
        echo "Importing ${img}:${TAG} to ${K3S_HOST}..."
        docker save "${img}:${TAG}" | ssh "$K3S_HOST" 'sudo k3s ctr images import -'
    done
}

if [[ -n "${K3S_HOST:-}" ]]; then
    import_remote
else
    import_local
fi

echo "Done. Verify with: sudo k3s ctr images list | grep streamflow"
