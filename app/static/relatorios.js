// formata para BRL
const brl = (v) =>
  (v ?? 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL"
  });

let chartHoras;
let chartVendedores;

document.addEventListener("DOMContentLoaded", () => {
  const hoje = new Date().toISOString().slice(0, 10);
  document.getElementById("data-inicio").value = hoje;
  document.getElementById("data-fim").value = hoje;
  carregarTudo();
});

async function carregarTudo() {
  const di = document.getElementById("data-inicio").value;
  const df = document.getElementById("data-fim").value;
  const metodo = document.getElementById("filtro-metodo").value;
  const metodoQs = metodo ? `&metodo=${encodeURIComponent(metodo)}` : "";
  const qs = `?data_inicio=${di}&data_fim=${df}${metodoQs}`;

  const [resumo, horas, vendedores, vendas] = await Promise.all([
    fetch("/api/dashboard/resumo" + qs).then((r) => r.json()),
    fetch("/api/dashboard/por-hora" + qs).then((r) => r.json()),
    fetch("/api/dashboard/por-vendedor" + qs).then((r) => r.json()),
    fetch("/api/vendas" + qs).then((r) => r.json())
  ]);

  renderKPIs(resumo);
  renderGraficoHoras(horas);
  renderGraficoVendedores(vendedores);
  renderTabela(vendas);
}

function renderKPIs(r) {
  document.getElementById("kpi-fat").textContent = brl(r.faturamento);
  document.getElementById("kpi-qtd").textContent = r.qtd_vendas ?? 0;
  document.getElementById("kpi-ticket").textContent = brl(r.ticket_medio);
  document.getElementById("kpi-maior").textContent = brl(r.maior_venda);
}

function renderGraficoHoras(dados) {
  if (chartHoras) chartHoras.destroy();
  const labels = Array.from({ length: 24 }, (_, i) => i + "h");
  const valores = Array(24).fill(0);
  dados.forEach((d) => {
    if (d.hora !== null && d.hora !== undefined) {
      valores[d.hora] = d.qtd_vendas;
    }
  });

  chartHoras = new Chart(document.getElementById("grafico-horas"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Vendas",
          data: valores,
          backgroundColor: "#FFD700",
          borderRadius: 4
        }
      ]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#666" }, grid: { color: "#222" } },
        y: {
          beginAtZero: true,
          ticks: { color: "#666", stepSize: 1, precision: 0 },
          grid: { color: "#222" }
        }
      }
    }
  });
}

function renderGraficoVendedores(dados) {
  if (chartVendedores) chartVendedores.destroy();
  const labels = dados.map((d) => d.seller_name);
  const faturamento = dados.map((d) => d.faturamento);
  const qtdVendas = dados.map((d) => d.qtd_vendas ?? 0);
  const ticketMedio = dados.map((d) => d.ticket_medio ?? 0);

  chartVendedores = new Chart(
    document.getElementById("grafico-vendedores"),
    {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Faturamento",
            data: faturamento,
            backgroundColor: "#DDAA00",
            borderRadius: 4
          }
        ]
      },
      options: {
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const idx = ctx.dataIndex;
                return [
                  `Faturamento: ${brl(faturamento[idx])}`,
                  `Vendas: ${qtdVendas[idx]}`,
                  `Ticket médio: ${brl(ticketMedio[idx])}`
                ];
              }
            }
          }
        },
        scales: {
          x: { ticks: { color: "#888" }, grid: { color: "#222" } },
          y: {
            ticks: { color: "#888", callback: (v) => brl(v) },
            grid: { color: "#222" }
          }
        }
      }
    }
  );
}

function renderTabela(vendas) {
  const tbody = document.getElementById("tbody-vendas");
  const vazio = document.getElementById("tabela-vazia");
  tbody.innerHTML = "";

  if (!vendas.length) {
    vazio.style.display = "block";
    return;
  }
  vazio.style.display = "none";

  vendas.forEach((v) => {
    const dt = (v.created_at || "").replace("T", " ").slice(0, 16) || "-";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>#${v.id}</td>
      <td>${dt}</td>
      <td>${v.seller_name || "-"}</td>
      <td style='color:#666'>${v.total_itens ?? "-"}</td>
      <td style='color:#FFD700'>${brl(v.total)}</td>
      <td style='color:#888'>${v.metodos ?? "-"}</td>
      <td>
        <span class='badge-${v.status}'>${v.status}</span>
      </td>
      <td>
        <button class='btn-acao'
          onclick='verVenda(${v.id})'>Ver</button>
        <button class='btn-acao btn-cancelar-venda'
          onclick='cancelarVenda(${v.id})'>Cancelar</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function cancelarVenda(id) {
  if (!confirm("Cancelar venda #" + id + "?")) return;
  await fetch("/api/vendas/" + id + "/cancelar", { method: "PATCH" });
  carregarTudo();
}

async function verVenda(id) {
  const v = await fetch("/api/vendas/" + id).then((r) => r.json());
  const itens = v.itens
    .map((i) => `${i.item_name} x${i.quantidade} = ${brl(i.subtotal)}`)
    .join("\n");
  const pags = v.pagamentos
    .map((p) => `${p.metodo}: ${brl(p.valor)}`)
    .join("\n");
  alert(`Venda #${v.id}\n\nItens:\n${itens}\n\nPagamentos:\n${pags}`);
}

function filtrarHoje() {
  const h = new Date().toISOString().slice(0, 10);
  setDatas(h, h);
  carregarTudo();
}
function filtrarSemana() {
  const hoje = new Date();
  const dia = hoje.getDay() || 7;
  const seg = new Date(hoje);
  seg.setDate(hoje.getDate() - dia + 1);
  const dom = new Date(seg);
  dom.setDate(seg.getDate() + 6);
  setDatas(seg.toISOString().slice(0, 10), dom.toISOString().slice(0, 10));
  carregarTudo();
}
function filtrarMes() {
  const hoje = new Date();
  const ini = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
  const fim = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0);
  setDatas(ini.toISOString().slice(0, 10), fim.toISOString().slice(0, 10));
  carregarTudo();
}
function setDatas(di, df) {
  document.getElementById("data-inicio").value = di;
  document.getElementById("data-fim").value = df;
}
