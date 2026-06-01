<template>
  <div class="models-page">
    <div class="page-header"><h2>模型管理</h2><button class="btn-primary" @click="showDeployDialog = true">+ 部署模型</button></div>
    <div v-if="modelsStore.loading">加载中...</div>
    <div v-else class="model-list">
      <div v-for="model in models" :key="model.name" class="model-card">
        <div class="model-name"><span class="icon">🧠</span><strong>{{ model.name }}</strong><span class="status-badge" :class="model.status">{{ model.status }}</span></div>
        <div class="model-nodes">部署节点: <span v-for="n in model.nodes" :key="n" class="tag">{{ n }}</span></div>
      </div>
    </div>
    <div v-if="showDeployDialog" class="dialog-overlay" @click.self="showDeployDialog = false">
      <div class="dialog">
        <h3>部署模型</h3>
        <form @submit.prevent="handleDeploy">
          <label>模型名称</label><input v-model="deployName" placeholder="qwen2.5:7b" required />
          <div class="dialog-actions"><button type="button" @click="showDeployDialog = false">取消</button><button type="submit" class="btn-primary">部署</button></div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useModelsStore } from '@/stores/models'
const modelsStore = useModelsStore(); const models = computed(() => modelsStore.models)
const showDeployDialog = ref(false); const deployName = ref('')
async function handleDeploy() { await modelsStore.deployModel(deployName.value); showDeployDialog.value = false; deployName.value = '' }
</script>
