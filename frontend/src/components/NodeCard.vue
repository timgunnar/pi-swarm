<template>
  <div class="node-card" :class="`status-${node.status}`" @click="$router.push(`/nodes/${node.name}`)">
    <div class="node-header">
      <span class="status-dot"></span>
      <strong>{{ node.name }}</strong>
      <span class="version">{{ node.kubelet_version }}</span>
    </div>
    <div class="node-metrics">
      <div class="metric"><label>CPU</label><div class="bar"><div class="fill" :style="{ width: node.cpu_usage + '%' }"></div></div><span>{{ node.cpu_usage.toFixed(1) }}%</span></div>
      <div class="metric"><label>MEM</label><div class="bar"><div class="fill" :style="{ width: node.memory_usage + '%' }"></div></div><span>{{ node.memory_usage.toFixed(1) }}%</span></div>
      <div class="metric"><label>TEMP</label><span :class="{ hot: node.temperature > 75 }">{{ node.temperature }}°C</span></div>
    </div>
    <div class="node-labels"><span v-for="(v, k) in node.labels" :key="k" class="tag">{{ k }}={{ v }}</span></div>
  </div>
</template>

<script setup lang="ts">
import type { NodeSummary } from '@/stores/nodes'
defineProps<{ node: NodeSummary }>()
</script>

<style scoped>
.node-card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #ccc; cursor: pointer; }
.node-card.status-online { border-left-color: #4caf50; } .node-card.status-offline { border-left-color: #f44336; } .node-card.status-pending { border-left-color: #ff9800; }
.node-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; background: #ccc; }
.status-online .status-dot { background: #4caf50; } .status-offline .status-dot { background: #f44336; }
.version { font-size: 12px; color: #999; margin-left: auto; }
.node-metrics { display: flex; flex-direction: column; gap: 8px; }
.metric { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.metric label { width: 40px; color: #666; }
.bar { flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
.fill { height: 100%; background: #2196f3; border-radius: 3px; transition: width 0.3s; }
.tag { font-size: 11px; background: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 3px; }
.hot { color: #f44336; font-weight: bold; }
</style>
