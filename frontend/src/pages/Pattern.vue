<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const wastePct = ref(10)
const msg = ref('')
const errMsg = ref('')
onMounted(async () => {
  const s = await getJSON('/api/settings')
  if (s.default_waste_pct != null) wastePct.value = Number(s.default_waste_pct)
})
async function saveWaste() {
  msg.value = ''; errMsg.value = ''
  try {
    const r = await putJSON('/api/settings/waste-pct', { waste_pct: Number(wastePct.value) })
    wastePct.value = r.default_waste_pct
    msg.value = '已保存默认备损百分比（不影响已有记录）'
  } catch (e) {
    errMsg.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>对花说明</h1>
    <p>有花距时在墙高上加 pattern_cm/100 作为每条长度，再算每卷可裁条数。大花对花损耗更大，可在此维护默认备损百分比，测算台启用备损且未单独填百分比时取用。</p>
    <div class="settings-row">
      <label>默认备损百分比
        <input type="number" min="0" max="100" step="1" v-model.number="wastePct" />%
      </label>
      <button @click="saveWaste">保存默认值</button>
    </div>
    <p v-if="msg" class="ok">{{ msg }}</p>
    <p v-if="errMsg" class="error">保存失败：{{ errMsg }}</p>
  </div>
</template>
