<template>
  <div class="table-container">
    <table v-if="operadoras.length > 0">
      <thead>
        <tr>
          <th>Registro ANS</th>
          <th>CNPJ</th>
          <th>Razão Social</th>
          <th>UF</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="op in operadoras" 
          :key="op.registro_ans" 
          @click="$emit('selecionar', op.cnpj)" 
          class="clickable-row"
        >
          <td>{{ op.registro_ans }}</td>
          <td>{{ op.cnpj }}</td>
          <td>{{ op.razao_social }}</td>
          <td>{{ op.uf }}</td>
        </tr>
      </tbody>
    </table>
    
    <div v-else class="empty-state">
      Nenhuma operadora encontrada para o critério de busca.
    </div>
  </div>
</template>

<script setup>
/*
=========================================================================
4.3. COMPONENTE DE LISTAGEM DE OPERADORAS (REUSABILIDADE)
=========================================================================
Estratégia: Componente funcional que utiliza o padrão de emissão de eventos.
-------------------------------------------------------------------------
ANÁLISE CRÍTICA: DESACOPLAMENTO E PERFORMANCE
-------------------------------------------------------------------------
1. Comunicação via Emits:
   - Abordagem: O componente não faz chamadas à API diretamente. 
   - Justificativa: Ao emitir apenas o CNPJ, mantemos o componente "stateless".
     Isso centraliza a lógica de I/O no App.vue, facilitando a depuração.

2. Otimização de DOM:
   - Estratégia: Uso de :key="op.registro_ans".
   - Justificativa: Chave única obrigatória para o algoritmo de diff do Vue, 
     garantindo que apenas as linhas alteradas sejam re-renderizadas 
     durante a paginação.
=========================================================================
*/

// Definição de entrada de dados (Props) e saída de eventos (Emits)
defineProps(['operadoras']); 
defineEmits(['selecionar']);
</script>

<style scoped>
.table-container { 
  margin-top: 20px; 
  overflow-x: auto; 
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

table { 
  width: 100%; 
  border-collapse: collapse; 
}

th, td { 
  border-bottom: 1px solid #eee; 
  padding: 12px 15px; 
  text-align: left; 
}

th { 
  background-color: #f8f9fa; 
  color: #333;
  font-weight: 600;
}

/* Estilização da linha interativa (Item 4.3) */
.clickable-row { 
  cursor: pointer; 
  transition: all 0.2s ease; 
}

.clickable-row:hover { 
  background-color: #f0f7ff; 
  transform: scale(1.002);
}

.empty-state { 
  padding: 40px; 
  text-align: center; 
  color: #888; 
  font-style: italic;
}
</style>