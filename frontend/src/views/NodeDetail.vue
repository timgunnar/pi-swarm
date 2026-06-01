<template><div><h2>节点详情: {{ name }}</h2><p>详细信息将在后续迭代实现</p></div></template>
<script setup lang="ts">
interface Props { name: string }
defineProps<Props>()
</script>
