import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nodeApi, type NodeSummary } from '@/api/client'

export type { NodeSummary }

export const useNodesStore = defineStore('nodes', () => {
  const nodes = ref<NodeSummary[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchNodes() {
    loading.value = true; error.value = null
    try { const { data } = await nodeApi.list(); nodes.value = data } catch (e: unknown) { error.value = (e as Error).message } finally { loading.value = false }
  }

  async function joinNode(host: string, name?: string) { await nodeApi.join({ host, name }); await fetchNodes() }
  async function drainNode(name: string) { await nodeApi.drain(name); await fetchNodes() }

  return { nodes, loading, error, fetchNodes, joinNode, drainNode }
})
