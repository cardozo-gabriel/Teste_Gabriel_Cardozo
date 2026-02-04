<script setup>
/**
 * =========================================================================
 * 4.3. COMPONENTE DE DETALHES E HISTÓRICO FINANCEIRO
 * =========================================================================
 * Estratégia: Busca granular por CNPJ para exibição de séries temporais.
 * =========================================================================
 */
defineProps(['detalhes', 'historico']);
defineEmits(['fechar']);
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('fechar')">
    <div class="modal-content">
      <button class="close-btn" @click="$emit('fechar')">X</button>
      
      <h2>{{ detalhes.razao_social }}</h2>
      <p><strong>CNPJ:</strong> {{ detalhes.cnpj }} | <strong>Modalidade:</strong> {{ detalhes.modalidade }}</p>

      <h3>Histórico de Despesas</h3>
      <table v-if="historico.length > 0">
        <thead>
          <tr>
            <th>Ano</th>
            <th>Trimestre</th>
            <th>Valor da Despesa</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in historico" :key="item.ano + item.trimestre">
            <td>{{ item.ano }}</td>
            <td>{{ item.trimestre }}º</td>
            <td>{{ new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.valor_despesa) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>Nenhum histórico financeiro encontrado para esta operadora.</p>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.modal-content { background: white; padding: 30px; border-radius: 8px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative; }
.close-btn { position: absolute; top: 10px; right: 10px; border: none; background: none; font-size: 20px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border-bottom: 1px solid #eee; padding: 10px; text-align: left; }
</style>