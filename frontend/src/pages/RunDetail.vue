<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const run = ref(null)
const notFound = ref(false)
onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    notFound.value = true
  }
})
function orderOf() {
  return run.value.result?.order_rolls ?? run.value.result?.rolls
}
</script>
<template>
  <div class="page">
    <h1>记录 #{{ id }}</h1>
    <p v-if="notFound" class="warn">记录不存在</p>
    <div v-else-if="run">
      <p>{{ run.wall_name }} → {{ run.roll_name }}<span v-if="run.note"> · {{ run.note }}</span></p>
      <p>基础卷数 <strong>{{ run.result?.rolls }} 卷</strong>
        <template v-if="run.result?.waste_enabled">
          · 备损 {{ run.result.waste_pct }}% · 订货卷数 <strong>{{ orderOf() }} 卷</strong>
        </template>
        <template v-else> · 未启用备损 · 订货卷数 <strong>{{ orderOf() }} 卷</strong></template>
      </p>
      <p>{{ run.result?.drops }} 条 · 每条 {{ run.result?.drop_len_m }}m</p>
      <p class="hint">写入时数据，不随设置页默认百分比变化。</p>
      <p><router-link to="/history">← 返回记录列表</router-link></p>
    </div>
  </div>
</template>
