// formata para BRL
const brl = (v) =>
  (v ?? 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL"
  });

const pad2 = (value) => String(value).padStart(2, "0");

const formatDateInput = (date) =>
  `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;

const formatVendaData = (dateStr) => {
  if (!dateStr) return "-";
  const clean = dateStr.replace("T", " ");
  const [datePart, timePart] = clean.split(" ");
  if (!datePart) return dateStr;
  const [y, m, d] = datePart.split("-");
  if (!y || !m || !d) return dateStr;
  const time = timePart ? ` ${timePart.slice(0, 5)}` : "";
  return `${d}/${m}/${y}${time}`;
};

const escapeHTML = (value) =>
  String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

let chartHoras;
let chartVendedores;
let vendaAtual = null;

let modalVenda;
let modalVendaId;
let modalVendaData;
let modalVendaVendedor;
let modalVendaStatus;
let modalVendaItens;
let modalVendaPagamentos;
let modalVendaTotal;
let btnVendaPrint;

document.addEventListener("DOMContentLoaded", () => {
  const hoje = formatDateInput(new Date());
  document.getElementById("data-inicio").value = hoje;
  document.getElementById("data-fim").value = hoje;
  const filtrosBar = document.getElementById("filtros-bar");
  if (filtrosBar) {
    filtrosBar.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        btn.classList.remove("btn-feedback");
        void btn.offsetWidth;
        btn.classList.add("btn-feedback");
        setTimeout(() => btn.classList.remove("btn-feedback"), 260);
      });
    });
  }

  modalVenda = document.getElementById("modal-venda");
  modalVendaId = document.getElementById("modal-venda-id");
  modalVendaData = document.getElementById("modal-venda-data");
  modalVendaVendedor = document.getElementById("modal-venda-vendedor");
  modalVendaStatus = document.getElementById("modal-venda-status");
  modalVendaItens = document.getElementById("modal-venda-itens");
  modalVendaPagamentos = document.getElementById("modal-venda-pagamentos");
  modalVendaTotal = document.getElementById("modal-venda-total");
  btnVendaPrint = document.getElementById("btn-venda-print");

  if (modalVenda) {
    modalVenda.addEventListener("click", (event) => {
      const target = event.target;
      if (target && target.dataset && target.dataset.close === "true") {
        fecharModalVenda();
      }
    });
  }

  if (btnVendaPrint) {
    btnVendaPrint.addEventListener("click", () => {
      if (!vendaAtual) return;
      const vendaCupom = montarVendaParaCupom(vendaAtual);
      generateReceiptPDF(vendaCupom, "print");
      fecharModalVenda();
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      fecharModalVenda();
    }
  });

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
        x: { ticks: { color: "#666" }, grid: { color: "#e6e6e6" } },
        y: {
          beginAtZero: true,
          ticks: { color: "#666", stepSize: 1, precision: 0 },
          grid: { color: "#e6e6e6" }
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
          x: { ticks: { color: "#666" }, grid: { color: "#e6e6e6" } },
          y: {
            ticks: { color: "#666", callback: (v) => brl(v) },
            grid: { color: "#e6e6e6" }
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
    const dt = formatVendaData(v.created_at);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>#${v.id}</td>
      <td>${dt}</td>
      <td>${v.seller_name || "-"}</td>
      <td style='color:#666'>${v.total_itens ?? "-"}</td>
      <td style='color:#FFD700'>${brl(v.total)}</td>
      <td style='color:#666'>${v.metodos ?? "-"}</td>
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
  if (!v || v.erro) {
    alert(v?.erro || "Nao foi possivel carregar a venda.");
    return;
  }
  preencherModalVenda(v);
  abrirModalVenda();
}

function filtrarHoje() {
  const h = formatDateInput(new Date());
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
  setDatas(formatDateInput(seg), formatDateInput(dom));
  carregarTudo();
}
function filtrarMes() {
  const hoje = new Date();
  const ini = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
  const fim = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0);
  setDatas(formatDateInput(ini), formatDateInput(fim));
  carregarTudo();
}
function setDatas(di, df) {
  document.getElementById("data-inicio").value = di;
  document.getElementById("data-fim").value = df;
}

function abrirModalVenda() {
  if (!modalVenda) return;
  modalVenda.classList.remove("hidden");
  modalVenda.setAttribute("aria-hidden", "false");
}

function fecharModalVenda() {
  if (!modalVenda) return;
  modalVenda.classList.add("hidden");
  modalVenda.setAttribute("aria-hidden", "true");
}

function preencherModalVenda(venda) {
  vendaAtual = venda;

  if (modalVendaId) {
    modalVendaId.textContent = `#${venda.id}`;
  }
  if (modalVendaData) {
    modalVendaData.textContent = formatVendaData(venda.created_at);
  }
  if (modalVendaVendedor) {
    modalVendaVendedor.textContent = venda.seller_name || "-";
  }
  if (modalVendaStatus) {
    modalVendaStatus.textContent = venda.status || "-";
  }

  if (modalVendaItens) {
    const itensHtml = (venda.itens || [])
      .map((item) => {
        const nome = escapeHTML(item.item_name || "-");
        const qtd = item.quantidade ?? 0;
        const preco = Number(item.preco_unit) || 0;
        const subtotal = Number(item.subtotal) || preco * qtd;
        return `
          <div class="modal-venda-linha">
            <span>${nome} x${qtd} (${brl(preco)})</span>
            <strong>${brl(subtotal)}</strong>
          </div>
        `;
      })
      .join("");
    modalVendaItens.innerHTML =
      itensHtml ||
      `<div class="modal-venda-linha"><span>Nenhum item</span><strong>-</strong></div>`;
  }

  if (modalVendaPagamentos) {
    const pagamentosHtml = (venda.pagamentos || [])
      .map((pag) => {
        const metodo = escapeHTML(pag.metodo || "-");
        const valor = Number(pag.valor) || 0;
        return `
          <div class="modal-venda-linha">
            <span>${metodo}</span>
            <strong>${brl(valor)}</strong>
          </div>
        `;
      })
      .join("");
    modalVendaPagamentos.innerHTML =
      pagamentosHtml ||
      `<div class="modal-venda-linha"><span>Nenhum pagamento</span><strong>-</strong></div>`;
  }

  if (modalVendaTotal) {
    modalVendaTotal.textContent = brl(venda.total);
  }
}

function formatarPagamentoCupom(pagamentosVenda) {
  const partes = (pagamentosVenda || [])
    .filter((pag) => pag.metodo)
    .map((pag) => {
      const valor = parseFloat(pag.valor);
      if (Number.isFinite(valor) && valor > 0) {
        return `${pag.metodo} ${brl(valor)}`;
      }
      return pag.metodo;
    });

  return partes.length > 0 ? partes.join(" + ") : "Nao informado";
}

function calcularTroco(pagamentosVenda, total) {
  const pagamentos = pagamentosVenda || [];
  const valorDinheiro = pagamentos
    .filter((pag) => pag.metodo === "Dinheiro")
    .reduce((soma, pag) => soma + (parseFloat(pag.valor) || 0), 0);

  const pagoSemDinheiro = pagamentos
    .filter((pag) => pag.metodo && pag.metodo !== "Dinheiro")
    .reduce((soma, pag) => soma + (parseFloat(pag.valor) || 0), 0);

  const restanteParaDinheiro = Math.max(0, total - pagoSemDinheiro);
  return Math.max(0, valorDinheiro - restanteParaDinheiro);
}

function montarVendaParaCupom(venda) {
  const subtotal = Number(venda.subtotal) || 0;
  const descontoValor = Number(venda.desconto) || 0;
  const descontoTipo = venda.desconto_tipo || "R$";
  const descontoAplicado =
    descontoTipo === "%" ? subtotal * (descontoValor / 100) : descontoValor;
  const troco = calcularTroco(venda.pagamentos, Number(venda.total) || 0);

  return {
    number: String(venda.id || 0).padStart(6, "0"),
    date: formatVendaData(venda.created_at),
    seller: venda.seller_name || "",
    payment: formatarPagamentoCupom(venda.pagamentos),
    items: (venda.itens || []).map((item) => ({
      name: item.item_name || "",
      qty: Number(item.quantidade) || 0,
      price: Number(item.preco_unit) || 0
    })),
    total: Number(venda.total) || 0,
    discount: descontoAplicado,
    change: troco
  };
}

function generateReceiptPDF(sale, action = "print") {
  const discountValue = Number(sale.discount || 0);
  const changeValue = Number(sale.change || 0);
  const hasDiscount = discountValue > 0;
  const hasChange = changeValue > 0;

  const rows = sale.items
    .map((item) => {
      const subtotal = (item.qty * item.price).toFixed(2);
      return `
        <tr>
          <td>${escapeHTML(item.name)}</td>
          <td>${item.qty}</td>
          <td>${item.price.toFixed(2)}</td>
          <td>${subtotal}</td>
        </tr>
      `;
    })
    .join("");

  const descontoHTML = hasDiscount
    ? `<p class="desconto">Desconto: - ${brl(discountValue)}</p>`
    : "";

  const trocoHTML = hasChange ? `<br>Troco: ${brl(changeValue)}` : "";

  const html = `
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Cupom A4</title>
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: Arial, sans-serif;
    background: #e0e0e0;
    display: flex;
    justify-content: center;
    padding: 30px;
  }

  .page {
    width: 210mm;
    min-height: 297mm;
    background: white;
    padding: 20mm;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
  }

  h1 {
    text-align: center;
    font-size: 24px;
    margin-bottom: 8px;
  }

  .info {
    text-align: center;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 15px;
  }

  hr {
    border: none;
    border-top: 1px solid #aaa;
    margin: 12px 0;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }

  th {
    text-align: left;
    padding: 8px 6px;
    border-bottom: 2px solid black;
    font-size: 14px;
  }

  td {
    text-align: left;
    padding: 10px 6px;
    font-size: 14px;
  }

  .desconto {
    text-align: right;
    font-size: 14px;
    margin-top: 10px;
  }

  .total {
    text-align: right;
    font-size: 22px;
    font-weight: bold;
    margin-top: 8px;
  }

  .footer {
    margin-top: 20px;
    font-size: 13px;
    line-height: 1.8;
  }

  .agradecimento {
    text-align: center;
    margin-top: 40px;
    font-size: 14px;
  }

  .aviso {
    text-align: center;
    margin-top: 10px;
    font-size: 10px;
    font-weight: bold;
  }

  @media print {
    body {
      background: none;
      padding: 0;
    }
    .page {
      box-shadow: none;
      width: 210mm;
      min-height: 297mm;
      padding: 20mm;
    }
    @page {
      size: A4;
      margin: 0;
    }
  }
</style>
</head>
<body>
<div class="page">
  <h1>GOLD CELL FRANCO LTDA</h1>
  <div class="info">
    CNPJ: 29.552.240/0001-80 <br>
    Av. dos Expedicionarios, 77 - Loja 141 <br>
    Franco da Rocha - CEP: 07803-010 <br>
    No. ${escapeHTML(sale.number)} &nbsp;&nbsp; ${escapeHTML(sale.date)} <br>
    Vendedor: ${escapeHTML(sale.seller || "Nao informado")}
  </div>

  <hr>

  <table>
    <tr>
      <th>ITEM</th>
      <th>QTD</th>
      <th>UNIT</th>
      <th>TOTAL</th>
    </tr>
    ${rows}
  </table>

  <hr>

  ${descontoHTML}
  <p class="total">TOTAL: ${brl(sale.total)}</p>

  <div class="footer">
    Pagamento: ${escapeHTML(sale.payment)}
    ${trocoHTML}
  </div>

  <div class="agradecimento">
    Obrigado pela preferencia!
  </div>
  <div class="aviso">
    Para produtos eletrônicos, o prazo para troca é de até 30 dias, mediante apresentação deste cupom fiscal, com o produto em perfeito estado de conservação e acompanhado de sua embalagem original.
  </div>
</div>
</body>
</html>
  `;

  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Nao foi possivel abrir a janela do cupom.");
    return;
  }

  printWindow.document.open();
  printWindow.document.write(html);
  printWindow.document.close();

  const normalizedAction = action === "imprimir" ? "print" : action;
  if (normalizedAction === "print" || normalizedAction === "download") {
    printWindow.onload = () => {
      printWindow.focus();
      printWindow.print();
    };
  }
}
