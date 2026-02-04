<template>
  <div class="chart-container">
    <h3>Top 5 Operadoras (Maiores Despesas)</h3>
    <Bar v-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else>Carregando gráfico...</p>
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { computed } from 'vue';

// Registro dos componentes do Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps(['stats']);

// Transformamos os dados da API para o formato que o Chart.js entende
const chartData = computed(() => ({
  labels: props.stats.map(item => item.razao_social.substring(0, 20) + '...'),
  datasets: [
    {
      label: 'Total de Despesas (R$)',
      backgroundColor: '#007bff',
      data: props.stats.map(item => item.total_despesas)
    }
  ]
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
};
</script>

<style scoped>
.chart-container { height: 300px; margin-top: 40px; padding: 20px; background: #f9f9f9; border-radius: 8px; }
</style>