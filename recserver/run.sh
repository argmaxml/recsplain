until ./recserver; do
    echo "Recsplain Server crashed with exit code $?.  Respawning.." >&2
    sleep 1
done