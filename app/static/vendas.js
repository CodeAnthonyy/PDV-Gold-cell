(() => {
    const produtosRaw = Array.isArray(window.__PRODUTOS__) ? window.__PRODUTOS__ : [];
    const vendedoresRaw = Array.isArray(window.__VENDEDORES__) ? window.__VENDEDORES__ : [];

    const produtos = produtosRaw.map((prod) => ({
        id: Number(prod.id),
        name: (prod.name || "").toString(),
        price: Number(prod.price) || 0,
        stock: Number(prod.stock) || 0,
        category: (prod.category || "").toString()
    }));

    const vendedores = vendedoresRaw.map((seller) => ({
        id: seller.id,
        name: seller.name || ""
    }));

    const buscaInput = document.getElementById("busca-produto");
    const listaProdutos = document.getElementById("lista-produtos");
    const produtosVazio = document.getElementById("produtos-vazio");

    const vendedorSelect = document.getElementById("vendedor");
    const carrinhoLista = document.getElementById("carrinho-lista");
    const carrinhoVazio = document.getElementById("carrinho-vazio");

    const subtotalEl = document.getElementById("subtotal");
    const totalEl = document.getElementById("total");
    const descontoValorEl = document.getElementById("desconto-valor");
    const descontoTipoEl = document.getElementById("desconto-tipo");
    const trocoEl = document.getElementById("troco");
    const trocoContainer = document.getElementById("div-troco");

    const pagamentosLista = document.getElementById("pagamentos-lista");
    const btnAddPagamento = document.getElementById("btn-add-pagamento");

    const mensagemEl = document.getElementById("mensagem-venda");
    const formVenda = document.getElementById("form-venda");
    const btnCancelar = document.getElementById("btn-cancelar");

    const modalCupom = document.getElementById("modal-cupom");
    const modalCupomText = document.getElementById("modal-cupom-text");
    const btnCupomDownload = document.getElementById("btn-cupom-download");
    const btnCupomPrint = document.getElementById("btn-cupom-print");

    const carrinho = new Map();
    let pagamentos = [{ metodo: "", valor: "" }];
    let ultimaVenda = null;

    const formatBRL = (value) => new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL"
    }).format(value || 0);

    const normalizar = (texto) => (texto || "").toString().toLowerCase();

    const mostrarMensagem = (texto, tipo = "erro") => {
        mensagemEl.textContent = texto;
        mensagemEl.classList.remove("sucesso");
        if (tipo === "sucesso") {
            mensagemEl.classList.add("sucesso");
        }
    };

    const limparMensagem = () => {
        mensagemEl.textContent = "";
        mensagemEl.classList.remove("sucesso");
    };

    const pad2 = (value) => String(value).padStart(2, "0");

    const formatDateTime = (date) => {
        const dia = pad2(date.getDate());
        const mes = pad2(date.getMonth() + 1);
        const ano = date.getFullYear();
        const hora = pad2(date.getHours());
        const minuto = pad2(date.getMinutes());
        return `${dia}/${mes}/${ano} ${hora}:${minuto}`;
    };

    const formatarPagamentoCupom = (pagamentosVenda) => {
        const partes = pagamentosVenda
            .filter((pag) => pag.metodo)
            .map((pag) => {
                const valor = parseFloat(pag.valor);
                if (Number.isFinite(valor) && valor > 0) {
                    return `${pag.metodo} ${formatBRL(valor)}`;
                }
                return pag.metodo;
            });

        return partes.length > 0 ? partes.join(" + ") : "Nao informado";
    };

    const escapeHTML = (value) => {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    };

    const criarVendaParaCupom = (
        vendaId,
        totalVenda,
        descontoAplicado,
        troco,
        vendedorNome
    ) => {
        const numero = vendaId ? String(vendaId).padStart(6, "0") : "000000";
        const dataVenda = formatDateTime(new Date());
        const itens = Array.from(carrinho.values()).map((item) => ({
            name: item.name,
            qty: item.qtd,
            price: item.price
        }));

        return {
            number: numero,
            date: dataVenda,
            seller: vendedorNome || "",
            payment: formatarPagamentoCupom(pagamentos),
            items: itens,
            total: totalVenda,
            discount: Number(descontoAplicado) || 0,
            change: Number(troco) || 0
        };
    };

    const abrirModalCupom = (venda) => {
        if (!modalCupom) return;
        ultimaVenda = venda;
        if (modalCupomText) {
            modalCupomText.textContent = `Venda #${venda.number} concluida. Escolha como deseja gerar o cupom:`;
        }
        modalCupom.classList.remove("hidden");
        modalCupom.setAttribute("aria-hidden", "false");
    };

    const fecharModalCupom = () => {
        if (!modalCupom) return;
        modalCupom.classList.add("hidden");
        modalCupom.setAttribute("aria-hidden", "true");
    };

    const generateReceiptPDF = (sale, action = "print") => {
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
            ? `<p class="desconto">Desconto: - ${formatBRL(discountValue)}</p>`
            : "";

        const trocoHTML = hasChange
            ? `<br>Troco: ${formatBRL(changeValue)}`
            : "";

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
  <p class="total">TOTAL: ${formatBRL(sale.total)}</p>

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
            mostrarMensagem("Nao foi possivel abrir a janela do cupom.");
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
    };

    const preencherVendedores = () => {
        vendedores.forEach((seller) => {
            const option = document.createElement("option");
            option.value = seller.id;
            option.textContent = seller.name;
            vendedorSelect.appendChild(option);
        });
    };

    const criarCardProduto = (produto) => {
        const card = document.createElement("div");
        card.className = "produto-card";
        card.dataset.id = produto.id;

        const info = document.createElement("div");
        info.className = "produto-info";

        const nome = document.createElement("div");
        nome.className = "produto-nome";
        nome.textContent = produto.name || "Produto";

        const codigo = String(produto.id || 0).padStart(3, "0");
        const categoria = produto.category || "Sem categoria";
        const meta = document.createElement("div");
        meta.className = "produto-meta";
        meta.textContent = `Cód: ${codigo} · ${categoria}`;

        const estoque = document.createElement("div");
        estoque.className = "produto-estoque";
        estoque.textContent = `Estoque: ${produto.stock}`;
        if (produto.stock < 5) {
            estoque.classList.add("baixo");
        }

        info.append(nome, meta, estoque);

        const actions = document.createElement("div");
        actions.className = "produto-actions";

        const preco = document.createElement("div");
        preco.className = "produto-preco";
        preco.textContent = formatBRL(produto.price);

        const addBtn = document.createElement("button");
        addBtn.type = "button";
        addBtn.className = "produto-add";
        addBtn.textContent = "+";
        addBtn.dataset.addId = produto.id;

        actions.append(preco, addBtn);

        card.append(info, actions);

        return card;
    };

    const renderProdutos = (filtro = "") => {
        const termo = normalizar(filtro);

        const filtrados = produtos.filter((produto) => {
            if (!termo) return true;
            const codigo = String(produto.id || "").padStart(3, "0");
            return (
                normalizar(produto.name).includes(termo) ||
                normalizar(produto.category).includes(termo) ||
                normalizar(codigo).includes(termo)
            );
        });

        listaProdutos.innerHTML = "";

        if (filtrados.length === 0) {
            produtosVazio.classList.remove("hidden");
            return;
        }

        produtosVazio.classList.add("hidden");

        filtrados.forEach((produto) => {
            const card = criarCardProduto(produto);
            listaProdutos.appendChild(card);
        });
    };

    const addAoCarrinho = (produtoId) => {
        const produto = produtos.find((item) => item.id === produtoId);
        if (!produto) return;

        if (carrinho.has(produtoId)) {
            carrinho.get(produtoId).qtd += 1;
        } else {
            carrinho.set(produtoId, {
                ...produto,
                qtd: 1
            });
        }

        renderCarrinho();
    };

    const atualizarQuantidade = (produtoId, novaQtd) => {
        const item = carrinho.get(produtoId);
        if (!item) return;
        const qtd = Math.max(1, Number(novaQtd) || 1);
        item.qtd = qtd;
        renderCarrinho();
    };

    const removerItem = (produtoId) => {
        carrinho.delete(produtoId);
        renderCarrinho();
    };

    const atualizarPagamento = (index, campo, valor) => {
        pagamentos[index][campo] = valor;
        calcularTotais();
    };

    const adicionarPagamento = () => {
        pagamentos.push({ metodo: "", valor: "" });
        renderPagamentos();
        calcularTotais();
    };

    const removerPagamento = (index) => {
        pagamentos = pagamentos.filter((_, i) => i !== index);
        if (pagamentos.length === 0) {
            pagamentos = [{ metodo: "", valor: "" }];
        }
        renderPagamentos();
        calcularTotais();
    };

    const renderPagamentos = () => {
        pagamentosLista.innerHTML = "";

        pagamentos.forEach((pag, index) => {
            const linha = document.createElement("div");
            linha.className = "pagamento-linha";

            const select = document.createElement("select");
            const opcoes = [
                { value: "", label: "Selecione" },
                { value: "Dinheiro", label: "Dinheiro" },
                { value: "Crédito", label: "Crédito" },
                { value: "Débito", label: "Débito" },
                { value: "Pix", label: "Pix" }
            ];

            opcoes.forEach((opcao) => {
                const option = document.createElement("option");
                option.value = opcao.value;
                option.textContent = opcao.label;
                select.appendChild(option);
            });

            select.value = pag.metodo;
            select.addEventListener("change", (event) => {
                atualizarPagamento(index, "metodo", event.target.value);
            });

            const input = document.createElement("input");
            input.type = "number";
            input.step = "0.01";
            input.min = "0";
            input.placeholder = "0,00";
            input.value = pag.valor;
            input.addEventListener("input", (event) => {
                atualizarPagamento(index, "valor", event.target.value);
            });

            linha.append(select, input);

            if (pagamentos.length > 1) {
                const remover = document.createElement("button");
                remover.type = "button";
                remover.className = "btn-remover-pagamento";
                remover.textContent = "×";
                remover.addEventListener("click", () => removerPagamento(index));
                linha.appendChild(remover);
            }

            pagamentosLista.appendChild(linha);
        });
    };

    const calcularTotais = () => {
        let subtotal = 0;
        carrinho.forEach((item) => {
            subtotal += item.price * item.qtd;
        });

        const descontoValor = Number(descontoValorEl.value) || 0;
        let descontoAplicado = 0;

        if (descontoTipoEl.value === "porcento") {
            descontoAplicado = subtotal * (descontoValor / 100);
        } else {
            descontoAplicado = descontoValor;
        }

        if (descontoAplicado > subtotal) {
            descontoAplicado = subtotal;
        }

        const total = Math.max(subtotal - descontoAplicado, 0);

        subtotalEl.textContent = formatBRL(subtotal);
        totalEl.textContent = formatBRL(total);

        const totalPago = pagamentos.reduce((soma, pag) => {
            return soma + (parseFloat(pag.valor) || 0);
        }, 0);

        const valorEmDinheiro = pagamentos
            .filter((pag) => pag.metodo === "Dinheiro")
            .reduce((soma, pag) => soma + (parseFloat(pag.valor) || 0), 0);

        const pagoSemDinheiro = pagamentos
            .filter((pag) => pag.metodo && pag.metodo !== "Dinheiro")
            .reduce((soma, pag) => soma + (parseFloat(pag.valor) || 0), 0);

        const restanteParaDinheiro = Math.max(0, total - pagoSemDinheiro);
        const troco = Math.max(0, valorEmDinheiro - restanteParaDinheiro);
        const temDinheiro = pagamentos.some((pag) => pag.metodo === "Dinheiro");

        trocoContainer.style.display = temDinheiro ? "flex" : "none";
        trocoEl.textContent = formatBRL(troco);

        return { subtotal, total, totalPago, descontoAplicado, troco };
    };

    const renderCarrinho = () => {
        carrinhoLista.innerHTML = "";

        if (carrinho.size === 0) {
            carrinhoVazio.style.display = "block";
            calcularTotais();
            return;
        }

        carrinhoVazio.style.display = "none";

        carrinho.forEach((item) => {
            const row = document.createElement("div");
            row.className = "item-row";

            const prod = document.createElement("div");
            prod.className = "item-prod";

            const nome = document.createElement("div");
            nome.className = "nome";
            nome.textContent = item.name;

            const preco = document.createElement("div");
            preco.className = "preco";
            preco.textContent = formatBRL(item.price);

            prod.append(nome, preco);

            const qtd = document.createElement("input");
            qtd.type = "number";
            qtd.min = "1";
            qtd.value = item.qtd;
            qtd.className = "item-qtd";
            qtd.addEventListener("change", (event) => {
                atualizarQuantidade(item.id, event.target.value);
            });

            const subtotal = document.createElement("div");
            subtotal.className = "item-subtotal";
            subtotal.textContent = formatBRL(item.price * item.qtd);

            const remover = document.createElement("button");
            remover.type = "button";
            remover.className = "item-remover";
            remover.textContent = "×";
            remover.addEventListener("click", () => removerItem(item.id));

            row.append(prod, qtd, subtotal, remover);
            carrinhoLista.appendChild(row);
        });

        calcularTotais();
    };

    const resetVenda = () => {
        carrinho.clear();
        pagamentos = [{ metodo: "", valor: "" }];
        vendedorSelect.value = "";
        descontoValorEl.value = "";
        descontoTipoEl.value = "reais";
        renderPagamentos();
        renderCarrinho();
    };

    listaProdutos.addEventListener("click", (event) => {
        const addBtn = event.target.closest(".produto-add");
        const card = event.target.closest(".produto-card");

        if (addBtn && addBtn.dataset.addId) {
            addAoCarrinho(Number(addBtn.dataset.addId));
            return;
        }

        if (card && card.dataset.id) {
            addAoCarrinho(Number(card.dataset.id));
        }
    });

    buscaInput.addEventListener("input", (event) => {
        renderProdutos(event.target.value);
    });

    descontoValorEl.addEventListener("input", calcularTotais);
    descontoTipoEl.addEventListener("change", calcularTotais);

    btnAddPagamento.addEventListener("click", adicionarPagamento);

    btnCancelar.addEventListener("click", () => {
        limparMensagem();
        resetVenda();
    });

    if (modalCupom) {
        modalCupom.addEventListener("click", (event) => {
            const target = event.target;
            if (target && target.dataset && target.dataset.close === "true") {
                fecharModalCupom();
            }
        });
    }

    if (btnCupomPrint) {
        btnCupomPrint.addEventListener("click", () => {
            if (!ultimaVenda) return;
            generateReceiptPDF(ultimaVenda, "print");
            fecharModalCupom();
        });
    }

    if (btnCupomDownload) {
        btnCupomDownload.addEventListener("click", () => {
            if (!ultimaVenda) return;
            generateReceiptPDF(ultimaVenda, "download");
            fecharModalCupom();
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            fecharModalCupom();
        }
    });

    formVenda.addEventListener("submit", async (event) => {
        event.preventDefault();
        limparMensagem();

        if (carrinho.size === 0) {
            mostrarMensagem("Adicione pelo menos um item ao carrinho.");
            return;
        }

        if (!vendedorSelect.value) {
            mostrarMensagem("Selecione um vendedor.");
            return;
        }

        const algumInvalido = pagamentos.some((pag) => {
            return !pag.metodo || !pag.valor || parseFloat(pag.valor) <= 0;
        });

        if (algumInvalido) {
            mostrarMensagem("Preencha todos os métodos e valores de pagamento.");
            return;
        }

        const { subtotal, total, totalPago, descontoAplicado, troco } =
            calcularTotais();

        if (totalPago < total) {
            mostrarMensagem("Valor pago insuficiente.");
            return;
        }

        if (!window.confirm("Confirmar a venda?")) {
            return;
        }

        const vendedorId = Number(vendedorSelect.value);
        const vendedorSelecionado = vendedores.find(
            (seller) => Number(seller.id) === vendedorId
        );

        if (!vendedorSelecionado) {
            mostrarMensagem("Vendedor invalido.");
            return;
        }

        const descontoTipo =
            descontoTipoEl.value === "porcento" ? "%" : "R$";

        const payload = {
            seller_id: vendedorId,
            seller_name: vendedorSelecionado.name,
            subtotal: subtotal,
            desconto: Number(descontoValorEl.value) || 0,
            desconto_tipo: descontoTipo,
            total: total,
            itens: Array.from(carrinho.values()).map((item) => ({
                item_id: item.id,
                item_name: item.name,
                quantidade: item.qtd,
                preco_unit: item.price,
                subtotal: item.qtd * item.price
            })),
            pagamentos: pagamentos.map((pag) => ({
                metodo: pag.metodo,
                valor: parseFloat(pag.valor)
            }))
        };

        try {
            const res = await fetch("/api/vendas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            let data = {};
            try {
                data = await res.json();
            } catch (err) {
                data = {};
            }

            if (res.ok) {
                const vendaCupom = criarVendaParaCupom(
                    data.id,
                    total,
                    descontoAplicado,
                    troco,
                    vendedorSelecionado.name
                );
                mostrarMensagem(
                    `Venda #${data.id} registrada com sucesso!`,
                    "sucesso"
                );
                resetVenda();
                abrirModalCupom(vendaCupom);
            } else {
                mostrarMensagem(
                    data.erro || "Erro ao salvar a venda. Tente novamente."
                );
            }
        } catch (err) {
            mostrarMensagem(`Erro de conexao: ${err.message}`);
        }
    });

    preencherVendedores();
    renderProdutos("");
    renderPagamentos();
    renderCarrinho();
})();
