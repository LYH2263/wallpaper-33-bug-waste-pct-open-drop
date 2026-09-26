<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
function orderOf(r) { return r.result?.order_rolls ?? r.result?.rolls }
function wasteLabel(r) {
  if (!r.result?.waste_enabled) return ''
  return `基础 ${r.result.rolls} 卷 · 备损 ${r.result.waste_pct}%`
}
</script>
<template>
  <div class="page"><h1>记录</h1><ul>
    <li v-for="r in items" :key="r.id">
      <router-link :to="`/history/${r.id}`" class="run-link">#{{ r.id }}</router-link>
      {{ r.wall_name }} →
      订货 <strong>{{ orderOf(r) }}</strong> 卷
      <template v-if="r.result?.waste_enabled">（{{ wasteLabel(r) }}）</template>
    </li>
  </ul>
  <p class="hint">点编号打开详情：显示写入时的基础卷数、备损百分比与订货卷数，不随后续设置变化。</p>
  </div>
</template>
