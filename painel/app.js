const API_URL = "";

const alertaEl = document.getElementById("alerta");
const tabelaEl = document.getElementById("tabela-agendamentos");
const formEl = document.getElementById("form-agendamento");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");

let mapaClientes = {};
let mapaProfissionais = {};
let mapaServicos = {};

function exibirAlerta(mensagem, tipo = "sucesso") {
  alertaEl.textContent = mensagem;
  alertaEl.className =
    tipo === "erro"
      ? "mb-4 p-3 rounded-lg text-sm font-medium bg-red-50 text-red-700 border border-red-200"
      : "mb-4 p-3 rounded-lg text-sm font-medium bg-emerald-50 text-emerald-700 border border-emerald-200";
  alertaEl.classList.remove("hidden");
  setTimeout(() => alertaEl.classList.add("hidden"), 5000);
}

function badgeStatus(status) {
  const cores = {
    agendado: "bg-blue-100 text-blue-800",
    confirmado: "bg-amber-100 text-amber-800",
    concluido: "bg-emerald-100 text-emerald-800",
    cancelado: "bg-red-100 text-red-800",
  };
  const classe = cores[status] || "bg-slate-100 text-slate-800";
  return `<span class="px-2.5 py-0.5 rounded-full text-xs font-medium ${classe}">${status}</span>`;
}

function formatarHora(isoString) {
  return new Date(isoString).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatarData(isoString) {
  return new Date(isoString).toLocaleDateString("pt-BR");
}

async function carregarCatalogos() {
  const [resClientes, resProf, resServicos] = await Promise.all([
    fetch(`${API_URL}/clientes/`),
    fetch(`${API_URL}/profissionais/`),
    fetch(`${API_URL}/servicos/`),
  ]);

  const clientes = await resClientes.json();
  const profissionais = await resProf.json();
  const servicos = await resServicos.json();

  mapaClientes = Object.fromEntries(clientes.map((c) => [c.id, c.nome]));
  mapaProfissionais = Object.fromEntries(profissionais.map((p) => [p.id, p.especialidade ? `${p.nome} (${p.especialidade})` : p.nome]));
  mapaServicos = Object.fromEntries(servicos.map((s) => [s.id, s]));

  document.getElementById("cliente_id").innerHTML =
    `<option value="">Selecione um cliente...</option>` +
    clientes.map((c) => `<option value="${c.id}">${c.nome}</option>`).join("");

  document.getElementById("profissional_id").innerHTML =
    `<option value="">Selecione um profissional...</option>` +
    profissionais.map((p) => `<option value="${p.id}">${p.nome}${p.especialidade ? ` — ${p.especialidade}` : ``}</option>`).join("");

  document.getElementById("servico_id").innerHTML =
    `<option value="">Selecione um serviço...</option>` +
    servicos
      .filter((s) => s.ativo !== false)
      .map(
        (s) =>
          `<option value="${s.id}">${s.nome} (${s.duracao_minutos} min - R$ ${Number(s.preco).toFixed(2)})</option>`
      )
      .join("");
}

async function carregarTudo() {
  try {
    await carregarCatalogos();
    const resp = await fetch(`${API_URL}/agendamentos/`);
    if (!resp.ok) throw new Error("Falha ao consultar agendamentos");

    statusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400";
    statusText.textContent = "API Conectada";

    const dados = await resp.json();
    if (dados.length === 0) {
      tabelaEl.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-slate-400">Nenhum agendamento cadastrado ainda.</td></tr>`;
      return;
    }

    tabelaEl.innerHTML = dados
      .map((item) => {
        const nomeCliente = mapaClientes[item.cliente_id] || `Cliente #${item.cliente_id}`;
        const nomeProf = mapaProfissionais[item.profissional_id] || `Prof. #${item.profissional_id}`;
        const servicoObj = mapaServicos[item.servico_id];
        const nomeServico = servicoObj ? servicoObj.nome : `Serviço #${item.servico_id}`;

        return `
        <tr class="hover:bg-slate-50">
          <td class="py-3 pr-3">
            <div class="font-medium text-slate-800">${nomeCliente}</div>
            <div class="text-xs text-slate-400">#${item.id}${item.observacoes ? ` • ${item.observacoes}` : ""}</div>
          </td>
          <td class="py-3 px-3">
            <div class="text-slate-800">${nomeServico}</div>
            <div class="text-xs text-slate-500">${nomeProf}</div>
          </td>
          <td class="py-3 px-3 text-slate-600">
            <div>${formatarData(item.data_hora_inicio)}</div>
            <div class="text-xs font-medium">${formatarHora(item.data_hora_inicio)} → ${formatarHora(item.data_hora_fim)}</div>
          </td>
          <td class="py-3 px-3">${badgeStatus(item.status)}</td>
          <td class="py-3 pl-3 text-right space-x-1">
            ${
              item.status === "agendado"
                ? `<button onclick="alterarStatus(${item.id}, 'confirmado')" class="text-xs bg-amber-50 text-amber-700 hover:bg-amber-100 px-2 py-1 rounded">Confirmar</button>`
                : ""
            }
            ${
              item.status !== "concluido" && item.status !== "cancelado"
                ? `<button onclick="alterarStatus(${item.id}, 'concluido')" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 px-2 py-1 rounded">Concluir</button>
                   <button onclick="alterarStatus(${item.id}, 'cancelado')" class="text-xs bg-red-50 text-red-700 hover:bg-red-100 px-2 py-1 rounded">Cancelar</button>`
                : ""
            }
          </td>
        </tr>
      `;
      })
      .join("");
  } catch (err) {
    statusDot.className = "w-2.5 h-2.5 rounded-full bg-red-400";
    statusText.textContent = "API Offline";
    tabelaEl.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-red-500">Não foi possível conectar à API em ${API_URL}. Verifique se o servidor FastAPI está rodando.</td></tr>`;
  }
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    cliente_id: Number(document.getElementById("cliente_id").value),
    profissional_id: Number(document.getElementById("profissional_id").value),
    servico_id: Number(document.getElementById("servico_id").value),
    data_hora_inicio: document.getElementById("data_hora_inicio").value,
    observacoes: document.getElementById("observacoes").value.trim() || null,
  };

  try {
    const resp = await fetch(`${API_URL}/agendamentos/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await resp.json();
    if (!resp.ok) {
      exibirAlerta(data.detail || "Erro ao criar agendamento.", "erro");
      return;
    }

    exibirAlerta("Agendamento criado com sucesso!");
    formEl.reset();
    carregarTudo();
  } catch (err) {
    exibirAlerta("Falha de conexão com a API.", "erro");
  }
});

async function alterarStatus(id, novoStatus) {
  try {
    const resp = await fetch(`${API_URL}/agendamentos/${id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: novoStatus }),
    });

    const data = await resp.json();
    if (!resp.ok) {
      exibirAlerta(data.detail || "Transição de status inválida.", "erro");
      return;
    }

    exibirAlerta(`Status atualizado para "${novoStatus}".`);
    carregarTudo();
  } catch (err) {
    exibirAlerta("Erro ao comunicar com a API.", "erro");
  }
}

document.getElementById("btn-atualizar").addEventListener("click", carregarTudo);
carregarTudo();


async function editarAgendamento(id) {
  try {
    const listaResp = await fetch(`${API_URL}/agendamentos`);
    if (!listaResp.ok) {
      exibirAlerta("Não foi possível carregar o agendamento para edição.", "erro");
      return;
    }
    const lista = await listaResp.json();
    const ag = lista.find((item) => Number(item.id) === Number(id));
    if (!ag) {
      exibirAlerta("Agendamento não encontrado.", "erro");
      return;
    }

    const novaDataHora = prompt(
      "Nova data e hora de início (AAAA-MM-DDTHH:MM):",
      (ag.data_hora_inicio || "").slice(0, 16)
    );
    if (novaDataHora === null) return;

    const novoProfId = prompt(
      "ID do profissional:",
      String(ag.profissional_id ?? "")
    );
    if (novoProfId === null) return;

    const novoServId = prompt(
      "ID do serviço:",
      String(ag.servico_id ?? "")
    );
    if (novoServId === null) return;

    const novasObs = prompt(
      "Observações:",
      ag.observacoes ?? ""
    );
    if (novasObs === null) return;

    const payload = {};
    if (novaDataHora.trim()) payload.data_hora_inicio = novaDataHora.trim();
    if (novoProfId.trim()) payload.profissional_id = Number(novoProfId.trim());
    if (novoServId.trim()) payload.servico_id = Number(novoServId.trim());
    payload.observacoes = novasObs;

    const resp = await fetch(`${API_URL}/agendamentos/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await resp.json();
    if (!resp.ok) {
      exibirAlerta(data.detail || "Não foi possível salvar a edição.", "erro");
      return;
    }

    exibirAlerta(`Agendamento #${id} atualizado com sucesso!`, "sucesso");
    carregarTudo();
  } catch (err) {
    exibirAlerta("Falha de conexão com a API ao editar.", "erro");
  }
}
