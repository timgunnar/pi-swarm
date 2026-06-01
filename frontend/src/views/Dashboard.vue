<template>
  <div class="dashboard">
    <div class="stats-row">
      <div class="stat-card"><span class="stat-value">{{ nodes.length }}</span><span class="stat-label">节点总数</span></div>
      <div class="stat-card"><span class="stat-value">{{ onlineCount }}</span><span class="stat-label">在线</span></div>
      <div class="stat-card"><span class="stat-value">{{ models.length }}</span><span class="stat-label">已部署模型</span></div>
    </div>
    <h3>节点列表</h3>
    <div v-if="nodesStore.loading">加载中...</div>
    <div v-else class="node-grid">
      <NodeCard v-for="node in nodes" :key="node.name" :node="node" />
    </div>
    <div v-if="nodes.length === 0 && !nodesStore.loading" class="empty">
      暂无节点 — 运行 <code>k3s-pi node add &lt;ip&gt;</code> 添加 Pi 节点
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useNodesStore } from '@/stores/nodes'
import { useModelsStore } from '@/stores/models'
import NodeCard from '@/components/NodeCard.vue'

const nodesStore = useNodesStore(); const modelsStore = useModelsStore()
const nodes = computed(() => nodesStore.nodes); const models = computed(() => modelsStore.models)
const onlineCount = computed(() => nodes.value.filter(n => n.status === 'online').length)
onMounted(() => { nodesStore.fetchNodes(); modelsStore.fetchModels() })
</script>

<style scoped>
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; padding: 16px 24px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; min-width: 120px; }
.stat-value { display: block; font-size: 28px; font-weight: bold; color: #1a1a2e; }
.stat-label { font-size: 13px; color: #999; }
.node-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.empty { color: #999; text-align: center; padding: 40px; }
.empty code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }
</style>
