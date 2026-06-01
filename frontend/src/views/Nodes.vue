<template>
  <div class="nodes-page">
    <div class="page-header"><h2>节点管理</h2><button class="btn-primary" @click="showJoinDialog = true">+ 添加节点</button></div>
    <div v-if="nodesStore.loading">加载中...</div>
    <div v-else class="node-grid"><NodeCard v-for="node in nodes" :key="node.name" :node="node" /></div>
    <div v-if="showJoinDialog" class="dialog-overlay" @click.self="showJoinDialog = false">
      <div class="dialog">
        <h3>添加 Pi 节点</h3>
        <form @submit.prevent="handleJoin">
          <label>Pi IP 地址</label><input v-model="joinHost" placeholder="192.168.1.x" required />
          <label>节点名称 (可选)</label><input v-model="joinName" placeholder="pi-4" />
          <div class="dialog-actions"><button type="button" @click="showJoinDialog = false">取消</button><button type="submit" class="btn-primary">加入集群</button></div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useNodesStore } from '@/stores/nodes'
import NodeCard from '@/components/NodeCard.vue'
const nodesStore = useNodesStore(); const nodes = computed(() => nodesStore.nodes)
const showJoinDialog = ref(false); const joinHost = ref(''); const joinName = ref('')
async function handleJoin() { await nodesStore.joinNode(joinHost.value, joinName.value || undefined); showJoinDialog.value = false; joinHost.value = ''; joinName.value = '' }
</script>
