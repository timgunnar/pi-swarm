import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export interface NodeSummary {
  name: string; status: string; cpu_usage: number; memory_usage: number
  temperature: number; labels: Record<string, string>; kubelet_version: string; is_active: boolean
}
export interface NodeDetail extends NodeSummary {
  cpu_capacity: string; memory_capacity: string; pods: Record<string, unknown>[]
  joined_at: string; last_heartbeat: string
}
export interface ModelSummary { name: string; nodes: string[]; status: string }
export interface ChatRequest { model: string; messages: { role: string; content: string }[]; temperature?: number; max_tokens?: number; stream?: boolean }
export interface ChatResponse { model: string; message: { role: string; content: string }; total_duration: number; eval_count: number }
export interface SystemInfo { app: string; version: string; api_versions: string[] }

export const nodeApi = {
  list: () => api.get<NodeSummary[]>('/nodes'),
  get: (name: string) => api.get<NodeDetail>(`/nodes/${name}`),
  join: (data: { host: string; name?: string; labels?: Record<string, string> }) => api.post('/nodes/join', data),
  drain: (name: string) => api.delete(`/nodes/${name}`),
}

export const modelApi = {
  list: () => api.get<ModelSummary[]>('/models'),
  deploy: (name: string, nodeNames?: string[]) => api.post('/inference/models/deploy', { name, node_names: nodeNames }),
}

export const inferenceApi = {
  models: () => api.get('/inference/models'),
  chat: (data: ChatRequest) => api.post<ChatResponse>('/inference/chat/completions', data),
}

export const systemApi = { info: () => api.get<SystemInfo>('/system/info') }

export default api
