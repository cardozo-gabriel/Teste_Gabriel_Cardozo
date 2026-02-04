<script setup>
/*
=========================================================================
4.3. ORQUESTRADOR PRINCIPAL DA INTERFACE (VUE.JS)
=========================================================================
Estratégia: Composition API para gerenciamento de estado e fluxo de dados.
-------------------------------------------------------------------------
ANÁLISE CRÍTICA: GERENCIAMENTO DE ESTADO E I/O (ITEM 4.3.2)
-------------------------------------------------------------------------
1. Centralização de Requisições:
   - Abordagem: O App.vue atua como o único "Single Source of Truth".
   - Justificativa: Facilita o controle de loading global e o tratamento 
     de erros cross-component, evitando inconsistências visuais.

2. Lazy Loading de Detalhes (Item 4.3.1):
   - Estratégia: O histórico de despesas não é carregado no fetch inicial.
   - Justificativa: Redução drástica no payload inicial da página. O 
     detalhamento só é solicitado quando há intenção real do usuário (clique).
=========================================================================
*/

import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import OperadorasTable from './components/OperadorasTable.vue';
import EstatisticasChart from './components/EstatisticasChart.vue';
import OperadoraDetalhes from './components/OperadoraDetalhes.vue';

// --- ESTADOS REATIVOS ---
const operadoras = ref([]);
const total = ref(0);
const page = ref(1);
const isLoading = ref(false);
const errorMsg = ref('');
const searchQuery = ref('');
const stats = ref([]);

// Estados para Modal de Detalhes
const operadoraSelecionada = ref(null);
const historicoDespesas = ref([]);

// --- MÉTODOS DE BUSCA (BACKEND INTERACTION) ---

/**
 * Busca a listagem paginada e filtrada (Item 4.3.1 / 4.3.3)
 */
const fetchOperadoras = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/operadoras`, {
      params: {
        page: page.value,
        limit: 10,
        q: searchQuery.value
      }
    });
    operadoras.value = response.data.data;
    total.value = response.data.total;
  } catch (err) {
    errorMsg.value = 'Erro ao carregar dados. Verifique se a API está rodando.';
  } finally {
    isLoading.value = false;
  }
};

/**
 * Busca estatísticas agregadas para o gráfico (Item 4.3)
 */
const fetchStats = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/estatisticas');
    stats.value = response.data.top_5;
  } catch (err) {
    console.error("Erro ao buscar estatísticas", err);
  }
};

/**
 * Busca detalhes profundos ao selecionar uma operadora (Item 4.2 / 4.3)
 */
const verDetalhes = async (cnpj) => {
  try {
    // Busca paralela para otimizar tempo de resposta
    const [resDet, resHist] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/operadoras/${cnpj}`),
      axios.get(`http://127.0.0.1:8000/api/operadoras/${cnpj}/despesas`)
    ]);
    
    operadoraSelecionada.value = resDet.data;
    historicoDespesas.value = resHist.data;
  } catch (err) {
    alert("Erro ao buscar detalhes da operadora.");
  }
};

// --- CONTROLE DE FLUXO ---

const handleSearch = () => {
  page.value = 1; // Reseta para a primeira página em nova busca
  fetchOperadoras();
};

onMounted(() => {
  fetchOperadoras();
  fetchStats();
});

watch(page, fetchOperadoras); // Observa mudança de página para novo fetch
</script>

<template>
  <main class="container">
    <header>
      <h1>ANS - Consulta de Operadoras</h1>
      <p class="subtitle">Análise Cadastral e Financeira de Operadoras de Saúde</p>
    </header>
    
    <section class="search-box">
      <input 
        v-model="searchQuery" 
        placeholder="Digite CNPJ ou Razão Social..." 
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch">🔍 Buscar</button>
    </section>

    <div v-if="isLoading" class="loader">Processando requisição...</div>
    <div v-else-if="errorMsg" class="error">{{ errorMsg }}</div>
    
    <div v-else>
      <OperadorasTable :operadoras="operadoras" @selecionar="verDetalhes" />
      
      <div class="pagination">
        <button @click="page--" :disabled="page <= 1">Anterior</button>
        <span class="page-indicator">Página {{ page }}</span>
        <button @click="page++" :disabled="operadoras.length < 10">Próxima</button>
      </div>
    </div>

    <hr class="divider" />

    <EstatisticasChart :stats="stats" />

    <OperadoraDetalhes 
      v-if="operadoraSelecionada" 
      :detalhes="operadoraSelecionada" 
      :historico="historicoDespesas"
      @fechar="operadoraSelecionada = null"
    />
  </main>
</template>

<style>
/* ESTILIZAÇÃO GLOBAL DA APLICAÇÃO 
Foco: Interface limpa, profissional e legibilidade.
*/
.container { max-width: 900px; margin: 0 auto; padding: 40px 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
header { margin-bottom: 30px; border-left: 5px solid #007bff; padding-left: 20px; }
h1 { margin: 0; font-size: 24px; color: #2c3e50; }
.subtitle { color: #666; margin-top: 5px; }

.search-box { margin-bottom: 30px; display: flex; gap: 10px; }
.search-box input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; outline: none; transition: border 0.3s; }
.search-box input:focus { border-color: #007bff; }
.search-box button { padding: 12px 24px; background-color: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.3s; }
.search-box button:hover { background-color: #0056b3; }

.pagination { margin-top: 25px; display: flex; gap: 15px; align-items: center; justify-content: center; }
.page-indicator { font-weight: 600; color: #555; }
.pagination button { padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.pagination button:disabled { cursor: not-allowed; opacity: 0.5; }

.divider { margin: 50px 0; border: 0; border-top: 1px solid #eee; }
.error { padding: 20px; background: #fff5f5; color: #c0392b; border-radius: 6px; text-align: center; }
.loader { padding: 20px; text-align: center; color: #007bff; font-weight: bold; }
</style>

/*
-------------------------------------------------------------------------
ANÁLISE CRÍTICA: EXPERIÊNCIA DO USUÁRIO E RESILIÊNCIA (ITEM 4.3.4)
-------------------------------------------------------------------------
1. Tratamento de Estados Assíncronos:
   - Abordagem: Variáveis reativas (isLoading, errorMsg).
   - Justificativa: Evita que o usuário interaja com componentes vazios ou 
     inconsistentes durante o tempo de resposta da rede.

2. Estratégia de Busca (Item 4.3.1):
   - Justificativa: A busca ocorre no servidor via parâmetros de query.
     Isso preserva a memória do cliente, transferindo a carga computacional 
     de filtragem (Regex/Like) para o banco de dados PostgreSQL, que é 
     otimizado para tal tarefa.

3. Desacoplamento de Componentes:
   - Abordagem: Passagem de dados via Props para 'OperadorasTable'.
   - Justificativa: Facilita a manutenção e testes isolados, seguindo os 
     princípios de responsabilidade única do Vue.js.
-------------------------------------------------------------------------
*/