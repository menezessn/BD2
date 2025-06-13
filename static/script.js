// Pequena correção na forma como você chama a função no carregamento da página

const checkInDailyConfig = [
    { valueKey: 'total_checkins', label: 'total de check-ins', color: 'blue' }
]
const checkInMonthlyConfig = [
    { valueKey: 'total_checkins', label: 'total de check-ins', color: 'blue' }
]
const mauSubscriberConfig = [
    { valueKey: 'monthly_active_users', label: 'MAU', color: 'blue' },
    { valueKey: 'monthly_subscribed_users', label: 'Assinados', color: 'red' },
]
const configCancelamentos = {
    labelKey: 'descricao_motivo_cancelamento',
    valueKey: 'total_cancelamentos',
    chartTitle: 'Principais Motivos de Cancelamento',
    valueAxisTitle: 'Total de Cancelamentos',
    datasetLabel: 'Cancelamentos'
};

const configTopUnidades = {
    labelKey: 'nome_unidade',
    valueKey: 'total_checkins',
    chartTitle: 'Top 10 Unidades por Check-ins',
    valueAxisTitle: 'check-ins',
    datasetLabel: 'Unidades'
};

const configBottomUnidades = {
    labelKey: 'nome_unidade',
    valueKey: 'total_checkins',
    chartTitle: 'Top 10 Unidades com menos Check-ins',
    valueAxisTitle: 'check-ins',
    datasetLabel: 'Unidades'
};


document.addEventListener("DOMContentLoaded", () => {
    createMultiLineChart("checkins-rede-mensal", "checkinChart", checkInDailyConfig);
});

document.addEventListener("DOMContentLoaded", () => {
    createMultiLineChart('checkins-rede-diario', 'checkinChartDaily', checkInMonthlyConfig);
});

document.addEventListener("DOMContentLoaded", () => {
    createMultiLineChart('mau-comparison', 'mauSubChart', mauSubscriberConfig);
});

document.addEventListener("DOMContentLoaded", () => {
    createGenericBarChart( 'cancelamentos-motivo', 'cancelamentoChart', configCancelamentos);
});

document.addEventListener("DOMContentLoaded", () => {
    createGenericBarChart( 'top-unidades-checkins', 'topUnidadesChart', configTopUnidades);
});

document.addEventListener("DOMContentLoaded", () => {
    createGenericBarChart( 'bottom-unidades-checkins', 'bottomUnidadesChart', configBottomUnidades);
});



let chartInstances = {};



/**
 * Cria um gráfico de linha com múltiplos datasets (linhas).
 * @param {string} chartType - O endpoint da API para buscar os dados.
 * @param {string} id - O ID do elemento canvas.
 * @param {object} datasetsConfig - Configuração para cada linha do gráfico.
 * Exemplo: [
 * { valueKey: 'monthly_active_users', label: 'Usuários Ativos (MAU)', color: 'blue' },
 * { valueKey: 'monthly_subscribed_users', label: 'Usuários Inscritos', color: 'green' }
 * ]
 */
async function createMultiLineChart(chartType, id, datasetsConfig) {
  try {
    const response = await fetch(`/api/${chartType}`);
    const data = await response.json();

    const dados = Object.values(data['data']);
    
    // As labels (eixo X) são as mesmas para todas as linhas
    const labels = dados.map(item => item.ano_mes);

    // Mapeia a configuração para criar os datasets do Chart.js
    const datasets = datasetsConfig.map(config => {
      return {
        label: config.label,
        data: dados.map(item => item[config.valueKey]), // Pega o valor da chave especificada
        borderColor: config.color,
        //backgroundColor: `rgba(${hexToRgb(config.color)}, 0.1)`, // Gera cor de fundo a partir da cor da linha
        tension: 0.3,
        fill: false,
        yAxisID: 'y' // Garante que todos usem o mesmo eixo Y principal
      };
    });

    const ctx = document.getElementById(id).getContext("2d");

    // Destrói o gráfico anterior se ele existir
    if (chartInstances[id]) {
      chartInstances[id].destroy();
    }
    
    // Cria o novo gráfico com múltiplos datasets
    chartInstances[id] = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: datasets // A propriedade 'datasets' agora recebe o array com as duas linhas
      },
      options: {
        responsive: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Mês"
            }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: "Contagem de Usuários"
            },
            beginAtZero: true
          }
        }
      }
    });

  } catch (error) {
    console.error(`Erro ao carregar gráfico ${id}:`, error);
  }
}

// Função auxiliar para converter cor HEX para RGB (usado no backgroundColor)
function hexToRgb(hex) {
    let r = 0, g = 0, b = 0;
    if (hex.length == 4) {
        r = "0x" + hex[1] + hex[1];
        g = "0x" + hex[2] + hex[2];
        b = "0x" + hex[3] + hex[3];
    } else if (hex.length == 7) {
        r = "0x" + hex[1] + hex[2];
        g = "0x" + hex[3] + hex[4];
        b = "0x" + hex[5] + hex[6];
    }
    return `${+r},${+g},${+b}`;
}

/**
 * Cria um gráfico de barras genérico e configurável.
 * @param {string} chartType - O endpoint da API (ex: 'cancelamentos-motivo').
 * @param {string} canvasId - O ID do elemento canvas onde o gráfico será renderizado.
 * @param {object} config - Um objeto com as configurações do gráfico.
 * @param {string} config.labelKey - A chave do JSON para as categorias (eixo Y).
 * @param {string} config.valueKey - A chave do JSON para os valores (eixo X).
 * @param {string} config.chartTitle - O título principal do gráfico.
 * @param {string} config.valueAxisTitle - O título do eixo dos valores (eixo X).
 * @param {string} config.datasetLabel - O rótulo para o conjunto de dados (usado em tooltips).
 */
async function createGenericBarChart(chartType, canvasId, config) {
  try {
    const response = await fetch(`/api/${chartType}`);
    const data = await response.json();
    let dados = Object.values(data['data']);

    // Ordena os dados usando a chave de valor fornecida na configuração
    dados.sort((a, b) => b[config.valueKey] - a[config.valueKey]);

    // Usa as chaves da configuração para mapear os dados corretamente
    const labels = dados.map(item => item[config.labelKey]);
    const valores = dados.map(item => item[config.valueKey]);

    const ctx = document.getElementById(canvasId).getContext("2d");

    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }

    chartInstances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: config.datasetLabel, // Usa o rótulo da configuração
          data: valores,
          backgroundColor: [
            'rgba(54, 162, 235, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(255, 99, 132, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(199, 199, 199, 0.7)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y', // Mantém o gráfico na horizontal para melhor leitura
        responsive: true,
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: false,
            text: config.chartTitle // Usa o título da configuração
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: config.valueAxisTitle // Usa o título do eixo da configuração
            }
          },
          y: {
            beginAtZero: true
          }
        }
      }
    });
  } catch (error) {
    console.error(`Erro ao carregar gráfico de barras ${canvasId}:`, error);
  }
}

async function reloadAll(){
    // Recarrega todos os gráficos
    await createMultiLineChart("checkins-rede-mensal", "checkinChart", checkInDailyConfig);
    await createMultiLineChart('checkins-rede-diario', 'checkinChartDaily', checkInMonthlyConfig);
    await createMultiLineChart('mau-comparison', 'mauSubChart', mauSubscriberConfig);
    await createGenericBarChart('cancelamentos-motivo', 'cancelamentoChart', configCancelamentos);
    await createGenericBarChart('top-unidades-checkins', 'topUnidadesChart', configTopUnidades);
    await createGenericBarChart('bottom-unidades-checkins', 'bottomUnidadesChart', configBottomUnidades);
}