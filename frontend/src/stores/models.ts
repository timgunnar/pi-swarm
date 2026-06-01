import { defineStore } from 'pinia'
import { ref } from 'vue'
import { modelApi, type ModelSummary } from '@/api/client'

export type { ModelSummary }

export const useModelsStore = defineStore('models', () => {
  const models = ref<ModelSummary[]>([])
  const loading = ref(false)

  async function fetchModels() { loading.value = true; try { const { data } = await modelApi.list(); models.value = data } finally { loading.value = false } }
  async function deployModel(name: string, nodeNames?: string[]) { await modelApi.deploy(name, nodeNames); await fetchModels() }

  return { models, loading, fetchModels, deployModel }
})
