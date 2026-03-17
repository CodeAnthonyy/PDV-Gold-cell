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
    const valorPagoEl = document.getElementById("valor-pago");
    const trocoEl = document.getElementById("troco");

    const mensagemEl = document.getElementById("mensagem-venda");
    const formVenda = document.getElementById("form-venda");
    const btnCancelar = document.getElementById("btn-cancelar");

    const carrinho = new Map();

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

        const valorPago = Number(valorPagoEl.value) || 0;
        const troco = valorPago > total ? valorPago - total : 0;
        trocoEl.textContent = formatBRL(troco);
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
        descontoValorEl.value = "";
        descontoTipoEl.value = "reais";
        valorPagoEl.value = "";
        vendedorSelect.value = "";
        document.getElementById("forma-pagamento").value = "";
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
    valorPagoEl.addEventListener("input", calcularTotais);

    btnCancelar.addEventListener("click", () => {
        limparMensagem();
        resetVenda();
    });

    formVenda.addEventListener("submit", (event) => {
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

        const formaPagamento = document.getElementById("forma-pagamento").value;
        if (!formaPagamento) {
            mostrarMensagem("Selecione a forma de pagamento.");
            return;
        }

        if (!window.confirm("Confirmar a venda?")) {
            return;
        }

        mostrarMensagem("Venda finalizada com sucesso!", "sucesso");
        resetVenda();
    });

    preencherVendedores();
    renderProdutos("");
    renderCarrinho();
})();
