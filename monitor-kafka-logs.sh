#!/bin/bash

echo "🔍 Monitorando logs do Kafka em tempo real..."
echo "📊 Tópico: callerwatch-logs"
echo "🚀 Pressione Ctrl+C para parar"
echo ""

docker exec -it callerwatch-kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic callerwatch-logs \
  --from-beginning \
  --property print.key=true \
  --property key.separator=" | " | \
  while IFS= read -r line; do
    echo "$(date '+%H:%M:%S') $line"
  done