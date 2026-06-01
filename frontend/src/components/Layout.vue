<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h1 class="logo">🖥 pi-swarm</h1>
      <nav>
        <router-link to="/">📊 总览</router-link>
        <router-link to="/nodes">🖥 节点管理</router-link>
        <router-link to="/models">🧠 模型管理</router-link>
        <router-link to="/logs">📋 日志</router-link>
        <router-link to="/settings">⚙️ 设置</router-link>
      </nav>
    </aside>
    <main class="content"><router-view /></main>
  </div>
</template>

<style scoped>
.app-layout { display: flex; height: 100vh; }
.sidebar { width: 220px; background: #1a1a2e; color: #eee; padding: 20px; display: flex; flex-direction: column; gap: 24px; }
.logo { font-size: 18px; margin: 0; }
nav { display: flex; flex-direction: column; gap: 12px; }
nav a { color: #aaa; text-decoration: none; padding: 8px 12px; border-radius: 6px; transition: background 0.2s; }
nav a:hover, nav a.router-link-active { background: #16213e; color: #fff; }
.content { flex: 1; padding: 24px; overflow-y: auto; background: #f5f5f5; }
</style>
