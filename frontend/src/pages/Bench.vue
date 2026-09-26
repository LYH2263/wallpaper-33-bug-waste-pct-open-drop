<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const out = ref(null)
const wasteEnabled = ref(false)
const wastePct = ref(10)
const errMsg = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
  const s = await getJSON('/api/settings')
  if (s.default_waste_pct != null) wastePct.value = Number(s.default_waste_pct)
})
function payload(save) {
  const body = { wall_id: wallId.value, roll_id: rollId.value, save, waste_enabled: wasteEnabled.value }
  if (wasteEnabled.value) body.waste_pct = Number(wastePct.value)
  return body
}
async function run(save) {
  errMsg.value = ''
  try {
    out.value = save
      ? await postJSON('/api/estimate', payload(true))
      : await getJSON(`/api/estimate?${new URLSearchParams(payload(false)).toString()}`)
  } catch (e) {
    errMsg.value = e.message
  }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <label class="waste-toggle"><input type="checkbox" v-model="wasteEnabled" /> 启用备损</label>
  <label v-if="wasteEnabled" class="waste-pct">备损
    <input type="number" min="0" max="100" step="1" v-model.number="wastePct" />%
  </label>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="errMsg" class="error">计算失败：{{ errMsg }}</p>
  <div v-if="out">
    <p>基础卷数 <strong>{{ out.rolls }} 卷</strong>
      <template v-if="out.waste_enabled"> · 备损 {{ out.waste_pct }}% · 订货卷数 <strong>{{ out.order_rolls }} 卷</strong></template>
    </p>
    <p>{{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m</p>
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.order_rolls" /></div>
  </div>
</template>
