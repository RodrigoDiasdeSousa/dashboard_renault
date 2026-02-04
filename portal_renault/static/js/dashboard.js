$(function () {
  // =====================================
  // 1. Evolução do NPS Index (Antigo "Profit")
  // =====================================
  var options_evolution = {
    series: [
      { 
        name: "NPS Index:", 
        // Aqui usamos o nome que vem do Python/HTML
        data: chartScores 
      },
    ],

    chart: {
      type: "line",
      height: 345,
      offsetX: -15,
      toolbar: { show: false },
      foreColor: "#adb0bb",
      fontFamily: 'inherit',
      sparkline: { enabled: false },
    },

    colors: ["#5D87FF"],

    stroke: {
      curve: "smooth",
      width: 3,
    },

    markers: {
      size: 5,
      colors: ["#5D87FF"],
      strokeColors: "#fff",
      strokeWidth: 2,
    },

    grid: {
      borderColor: "rgba(0,0,0,0.1)",
      strokeDashArray: 3,
      xaxis: {
        lines: { show: false },
      },
    },

    xaxis: {
      type: "category",
      // Aqui usamos as datas que vêm do Python/HTML
      categories: chartDates,
      labels: {
        style: { cssClass: "grey--text lighten-2--text fill-color" },
      },
    },

    yaxis: {
      show: true,
      min: -100,
      max: 100,
      tickAmount: 4,
      labels: {
        formatter: function (value) {
          return value.toFixed(1);
        },
        style: {
          cssClass: "grey--text lighten-2--text fill-color",
        },
      },
    },

    tooltip: { theme: "light" },
  };

  // Renderiza no ID #chart (que era o gráfico de barras geral)
  var chart_evo = new ApexCharts(document.querySelector("#chart"), options_evolution);
  chart_evo.render();


  // =====================================
  // 2. Distribuição de Notas (Antigo "Breakup")
  // =====================================
  var options_dist = {
    series: chartDistValues, // Usa os valores 1, 2, 3, 4, 5 do Python
    labels: ["Nota 1", "Nota 2", "Nota 3", "Nota 4", "Nota 5"],
    chart: {
      height: 180,
      type: "donut",
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      foreColor: "#adb0bb",
    },
    plotOptions: {
      pie: {
        startAngle: 0,
        endAngle: 360,
        donut: {
          size: '75%',
        },
      },
    },
    stroke: { show: false },
    dataLabels: { enabled: false },
    legend: { show: false },
    colors: ["#FA896B", "#FFAE1F", "#F9F9FD", "#ecf2ff", "#5D87FF"],
    tooltip: { theme: "dark", fillSeriesColor: false },
  };

  var chart_dist = new ApexCharts(document.querySelector("#breakup"), options_dist);
  chart_dist.render();

  // =====================================
  // 3. Earning (Mantido como Sparkline de exemplo)
  // =====================================
  var earning = {
    chart: {
      id: "sparkline3",
      type: "area",
      height: 60,
      sparkline: { enabled: true },
      group: "sparklines",
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      foreColor: "#adb0bb",
    },
    series: [
      { name: "Earnings", color: "#49BEFF", data: [25, 66, 20, 40, 12, 58, 20] },
    ],
    stroke: { curve: "smooth", width: 2 },
    fill: { colors: ["#f3feff"], type: "solid", opacity: 0.05 },
    markers: { size: 0 },
    tooltip: {
      theme: "dark",
      fixed: { enabled: true, position: "right" },
      x: { show: false },
    },
  };
  new ApexCharts(document.querySelector("#earning"), earning).render();

}); // Fim do $(function)