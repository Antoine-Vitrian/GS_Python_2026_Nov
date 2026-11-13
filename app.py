from __future__ import annotations

import json
import mimetypes
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


PASTA_PROJETO = Path(__file__).parent
PASTA_WEB = PASTA_PROJETO / "web"
LIMITE_TAREFAS = 12

FAMILIARES = [
    {"id": "ana", "name": "Ana Martins", "role": "Filha", "availability": 5, "load": 75, "color": "#6478f4", "initials": "AM"},
    {"id": "marcos", "name": "Marcos Martins", "role": "Filho", "availability": 4, "load": 90, "color": "#ec8c60", "initials": "MM"},
    {"id": "lucia", "name": "Lúcia Martins", "role": "Irmã", "availability": 6, "load": 45, "color": "#b17bc9", "initials": "LM"},
    {"id": "pedro", "name": "Pedro Martins", "role": "Neto", "availability": 3, "load": 60, "color": "#49a991", "initials": "PM"},
]

TAREFAS = [
    {"id": "consulta", "title": "Levar à consulta", "detail": "Cardiologista · 10:30", "minutes": 90, "category": "Saúde", "day": "Ter, 18"},
    {"id": "remedios", "title": "Organizar medicamentos", "detail": "Separar doses da semana", "minutes": 45, "category": "Rotina", "day": "Seg, 17"},
    {"id": "mercado", "title": "Fazer compras", "detail": "Lista da semana", "minutes": 60, "category": "Casa", "day": "Qua, 19"},
    {"id": "caminhada", "title": "Acompanhar caminhada", "detail": "Volta no parque", "minutes": 45, "category": "Bem-estar", "day": "Qui, 20"},
    {"id": "exames", "title": "Buscar resultado dos exames", "detail": "Laboratório Santa Clara", "minutes": 30, "category": "Saúde", "day": "Sex, 21"},
    {"id": "ligacao", "title": "Ligar para a vó", "detail": "Um tempinho para conversar", "minutes": 30, "category": "Afeto", "day": "Todos os dias"},
]

COMPROMISSOS = [
    {"time": "09:00", "title": "Separar medicamentos da semana", "kind": "Rotina", "owner": "Lúcia", "color": "mint"},
    {"time": "10:30", "title": "Consulta com cardiologista", "kind": "Saúde", "owner": "Ana", "color": "blue"},
    {"time": "14:00", "title": "Buscar resultado de exames", "kind": "Saúde", "owner": "Marcos", "color": "peach"},
]

GRAFO_APOIO = {
    "familia": ["saude", "descanso", "orientacao", "convivencia"],
    "saude": ["ubs", "farmacia_popular"],
    "descanso": ["centro_dia", "assistencia"],
    "orientacao": ["cras", "defensoria"],
    "convivencia": ["centro_convivencia", "ong_viver"],
    "ubs": [],
    "farmacia_popular": [],
    "centro_dia": [],
    "assistencia": [],
    "cras": [],
    "defensoria": [],
    "centro_convivencia": [],
    "ong_viver": [],
}

SERVICOS_APOIO = {
    "ubs": {"name": "Unidade Básica de Saúde", "type": "Saúde pública", "description": "Orientação de saúde, acompanhamento e encaminhamentos.", "tag": "Atenção básica"},
    "farmacia_popular": {"name": "Farmácia Popular", "type": "Medicamentos", "description": "Acesso a medicamentos gratuitos ou com desconto.", "tag": "Programa público"},
    "centro_dia": {"name": "Centro Dia para Idosos", "type": "Apoio e descanso", "description": "Convivência e cuidado durante o dia para a pessoa idosa.", "tag": "Respiro para quem cuida"},
    "assistencia": {"name": "Serviço de Assistência Social", "type": "Apoio familiar", "description": "Orientação sobre serviços e benefícios socioassistenciais.", "tag": "Apoio à família"},
    "cras": {"name": "CRAS", "type": "Orientação social", "description": "Acolhimento e orientação sobre direitos e programas sociais.", "tag": "Serviço público"},
    "defensoria": {"name": "Defensoria Pública", "type": "Direitos", "description": "Orientação jurídica gratuita para quem precisa.", "tag": "Direitos"},
    "centro_convivencia": {"name": "Centro de Convivência", "type": "Comunidade", "description": "Atividades e vínculos para idosos e comunidade.", "tag": "Conexão local"},
    "ong_viver": {"name": "ONG de apoio a cuidadores", "type": "ONG comunitária", "description": "Grupos de apoio e atividades para cuidadores e famílias.", "tag": "Exemplo comunitário"},
}

NOMES_NECESSIDADES = {
    "saude": "Saúde e medicamentos",
    "descanso": "Um tempo para respirar",
    "orientacao": "Orientação e direitos",
    "convivencia": "Convivência e comunidade",
}


def validar_entrada(familiares: Any, tarefas: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(familiares, list) or not isinstance(tarefas, list):
        raise ValueError("Envie uma lista de familiares e uma lista de tarefas.")
    if not familiares or len(familiares) > 8:
        raise ValueError("A divisão precisa ter de 1 a 8 familiares.")
    if not tarefas or len(tarefas) > LIMITE_TAREFAS:
        raise ValueError(f"A divisão precisa ter de 1 a {LIMITE_TAREFAS} tarefas.")

    familiares_validos = []
    ids_familiares_vistos = set()
    for familiar in familiares:
        if not isinstance(familiar, dict):
            raise ValueError("Cada familiar precisa ser um objeto válido.")
        id_familiar = familiar.get("id")
        nome = familiar.get("name")
        disponibilidade = familiar.get("availability")
        carga_atual = familiar.get("load", 0)
        if (not isinstance(id_familiar, str) or not id_familiar or id_familiar in ids_familiares_vistos
                or not isinstance(nome, str) or not nome.strip()
                or isinstance(disponibilidade, bool) or not isinstance(disponibilidade, (int, float))
                or isinstance(carga_atual, bool) or not isinstance(carga_atual, (int, float))
                or disponibilidade <= 0 or carga_atual < 0 or carga_atual > disponibilidade * 60):
            raise ValueError("Confira o nome, a disponibilidade e a carga atual de cada familiar.")
        ids_familiares_vistos.add(id_familiar)
        familiares_validos.append({**familiar, "availability": float(disponibilidade), "load": float(carga_atual)})

    tarefas_validas = []
    ids_tarefas_vistos = set()
    for tarefa in tarefas:
        if not isinstance(tarefa, dict):
            raise ValueError("Cada tarefa precisa ser um objeto válido.")
        id_tarefa = tarefa.get("id")
        titulo = tarefa.get("title")
        minutos = tarefa.get("minutes")
        if (not isinstance(id_tarefa, str) or not id_tarefa or id_tarefa in ids_tarefas_vistos
                or not isinstance(titulo, str) or not titulo.strip()
                or isinstance(minutos, bool) or not isinstance(minutos, (int, float))
                or minutos <= 0):
            raise ValueError("Confira o título e a duração de cada tarefa.")
        ids_tarefas_vistos.add(id_tarefa)
        tarefas_validas.append({**tarefa, "minutes": int(minutos)})
    return familiares_validos, tarefas_validas


def gerar_subconjuntos(familiares: list[dict[str, Any]], tarefas: list[dict[str, Any]]) -> list[list[tuple[int, float, float]]]:
    mascara_todas_tarefas = (1 << len(tarefas)) - 1
    resultado = []
    for familiar in familiares:
        minutos_disponiveis = familiar["availability"] * 60
        subconjuntos = []
        mascara = mascara_todas_tarefas
        while True:
            minutos = sum(tarefas[indice]["minutes"] for indice in range(len(tarefas)) if mascara & (1 << indice))
            carga_total = familiar["load"] + minutos
            if carga_total <= minutos_disponiveis:
                proporcao = carga_total / minutos_disponiveis
                subconjuntos.append((mascara, proporcao, proporcao * proporcao))
            if mascara == 0:
                break
            mascara = (mascara - 1) & mascara_todas_tarefas
        resultado.append(subconjuntos)
    return resultado


def montar_resultado(familiares: list[dict[str, Any]], tarefas: list[dict[str, Any]], mascaras: tuple[int, ...], algoritmo: str) -> dict[str, Any]:
    distribuicoes = []
    for familiar, mascara in zip(familiares, mascaras):
        tarefas_atribuidas = [tarefa for indice, tarefa in enumerate(tarefas) if mascara & (1 << indice)]
        minutos_atribuidos = sum(tarefa["minutes"] for tarefa in tarefas_atribuidas)
        minutos_totais = familiar["load"] + minutos_atribuidos
        distribuicoes.append({
            "id": familiar["id"],
            "name": familiar["name"],
            "role": familiar.get("role", "Familiar"),
            "color": familiar.get("color", "#6478f4"),
            "initials": familiar.get("initials", familiar["name"][:2].upper()),
            "availability": familiar["availability"],
            "load": familiar["load"],
            "assignedMinutes": minutos_atribuidos,
            "totalMinutes": minutos_totais,
            "loadPercent": round(minutos_totais / (familiar["availability"] * 60) * 100),
            "tasks": tarefas_atribuidas,
        })
    return {
        "algorithm": algoritmo,
        "assignments": distribuicoes,
        "assignedTaskCount": sum(len(pessoa["tasks"]) for pessoa in distribuicoes),
        "totalMinutes": sum(tarefa["minutes"] for tarefa in tarefas),
    }


def distribuir_com_memoizacao(familiares: list[dict[str, Any]], tarefas: list[dict[str, Any]]) -> dict[str, Any]:
    familiares, tarefas = validar_entrada(familiares, tarefas)
    subconjuntos = gerar_subconjuntos(familiares, tarefas)
    mascara_todas_tarefas = (1 << len(tarefas)) - 1

    @lru_cache(maxsize=None)
    def resolver(indice_familiar: int, tarefas_restantes: int) -> tuple[float, float, tuple[int, ...]] | None:
        if indice_familiar == len(familiares):
            return (0.0, 0.0, ()) if tarefas_restantes == 0 else None
        melhor = None
        for mascara, proporcao, proporcao_ao_quadrado in subconjuntos[indice_familiar]:
            if mascara & tarefas_restantes != mascara:
                continue
            proximo_resultado = resolver(indice_familiar + 1, tarefas_restantes ^ mascara)
            if proximo_resultado is None:
                continue
            candidato = (
                max(proporcao, proximo_resultado[0]),
                proporcao_ao_quadrado + proximo_resultado[1],
                (mascara, *proximo_resultado[2]),
            )
            if melhor is None or candidato[:2] < melhor[:2]:
                melhor = candidato
        return melhor

    resultado = resolver(0, mascara_todas_tarefas)
    if resultado is None:
        raise ValueError("Não há disponibilidade suficiente para acomodar todas as tarefas. Ajuste os horários ou a carga atual.")
    return montar_resultado(familiares, tarefas, resultado[2], "memoizacao")


def distribuir_com_tabulacao(familiares: list[dict[str, Any]], tarefas: list[dict[str, Any]]) -> dict[str, Any]:
    familiares, tarefas = validar_entrada(familiares, tarefas)
    subconjuntos = gerar_subconjuntos(familiares, tarefas)
    mascara_todas_tarefas = (1 << len(tarefas)) - 1
    estados: dict[int, tuple[float, float, tuple[int, ...]]] = {0: (0.0, 0.0, ())}

    for subconjuntos_familiar in subconjuntos:
        proximos_estados: dict[int, tuple[float, float, tuple[int, ...]]] = {}
        for mascara_atribuidas, pontuacao in estados.items():
            for mascara, proporcao, proporcao_ao_quadrado in subconjuntos_familiar:
                if mascara_atribuidas & mascara:
                    continue
                mascara_combinada = mascara_atribuidas | mascara
                candidato = (
                    max(pontuacao[0], proporcao),
                    pontuacao[1] + proporcao_ao_quadrado,
                    (*pontuacao[2], mascara),
                )
                atual = proximos_estados.get(mascara_combinada)
                if atual is None or candidato[:2] < atual[:2]:
                    proximos_estados[mascara_combinada] = candidato
        estados = proximos_estados

    resultado = estados.get(mascara_todas_tarefas)
    if resultado is None:
        raise ValueError("Não há disponibilidade suficiente para acomodar todas as tarefas. Ajuste os horários ou a carga atual.")
    return montar_resultado(familiares, tarefas, resultado[2], "tabulacao")


def buscar_caminhos_de_apoio(necessidade: str) -> list[dict[str, Any]]:
    if necessidade not in NOMES_NECESSIDADES:
        raise ValueError("Escolha uma necessidade disponível para buscar apoio.")
    fila = [("familia", ["familia"])]
    visitados = {"familia"}
    caminhos = []
    while fila:
        no, caminho = fila.pop(0)
        if no not in GRAFO_APOIO:
            continue
        for vizinho in GRAFO_APOIO[no]:
            if vizinho in visitados:
                continue
            visitados.add(vizinho)
            proximo_caminho = [*caminho, vizinho]
            if vizinho in SERVICOS_APOIO:
                caminhos.append({**SERVICOS_APOIO[vizinho], "id": vizinho, "path": proximo_caminho})
            else:
                fila.append((vizinho, proximo_caminho))
    return [
        {"need": NOMES_NECESSIDADES[necessidade], **servico}
        for servico in caminhos
        if necessidade in categoria_do_caminho(servico["path"])
    ]


def categoria_do_caminho(caminho: list[str]) -> str | None:
    return next((no for no in caminho if no in NOMES_NECESSIDADES), None)


class ManipuladorElo(BaseHTTPRequestHandler):
    def _enviar_json(self, codigo: int, dados: dict[str, Any]) -> None:
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _ler_json(self) -> dict[str, Any]:
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho <= 0 or tamanho > 100_000:
                raise ValueError("Envie um corpo JSON válido (até 100 KB).")
            valor = json.loads(self.rfile.read(tamanho))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("O corpo da requisição não contém JSON válido.") from error
        if not isinstance(valor, dict):
            raise ValueError("O corpo da requisição precisa ser um objeto JSON.")
        return valor

    def do_GET(self) -> None:
        requisicao = urlparse(self.path)
        if requisicao.path == "/api/overview":
            self._enviar_json(200, {"team": FAMILIARES, "tasks": TAREFAS, "events": COMPROMISSOS})
            return
        if requisicao.path == "/api/support":
            necessidade = parse_qs(requisicao.query).get("need", [""])[0]
            try:
                self._enviar_json(200, {"results": buscar_caminhos_de_apoio(necessidade)})
            except ValueError as error:
                self._enviar_json(400, {"error": str(error)})
            return
        self._servir_arquivo(requisicao.path)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/allocate":
            self._enviar_json(404, {"error": "Rota não encontrada."})
            return
        try:
            dados = self._ler_json()
            algoritmo = dados.get("algorithm", "tabulacao")
            if algoritmo not in ("memoizacao", "tabulacao"):
                raise ValueError("Escolha memoização ou tabulação.")
            distribuidora = distribuir_com_memoizacao if algoritmo == "memoizacao" else distribuir_com_tabulacao
            resultado = distribuidora(dados.get("members"), dados.get("tasks"))
            self._enviar_json(200, resultado)
        except ValueError as error:
            self._enviar_json(400, {"error": str(error)})

    def _servir_arquivo(self, caminho_solicitado: str) -> None:
        caminho_relativo = "index.html" if caminho_solicitado == "/" else caminho_solicitado.lstrip("/")
        if caminho_relativo not in {"index.html", "styles.css", "app.js"}:
            self._enviar_json(404, {"error": "Página não encontrada."})
            return
        caminho_arquivo = PASTA_WEB / caminho_relativo
        conteudo = caminho_arquivo.read_bytes()
        tipo_conteudo = mimetypes.guess_type(caminho_arquivo.name)[0] or "application/octet-stream"
        if tipo_conteudo.startswith("text/") or tipo_conteudo == "application/javascript":
            tipo_conteudo += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", tipo_conteudo)
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")


def iniciar_servidor(endereco: str = "127.0.0.1", porta: int = 8000) -> None:
    servidor = ThreadingHTTPServer((endereco, porta), ManipuladorElo)
    print(f"Elo está no ar em http://{endereco}:{porta}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar_servidor()
