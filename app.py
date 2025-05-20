from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
ARQUIVO = "agenda.json"
ARQUIVO_TIMES = "times.json"

def carregar_times():
    if os.path.exists(ARQUIVO_TIMES):
        with open(ARQUIVO_TIMES, "r") as f:
            return json.load(f)
    return []

def salvar_times(times):
    with open(ARQUIVO_TIMES, "w") as f:
        json.dump(times, f, indent=2)

def carregar_agenda():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r") as f:
            agenda = json.load(f)
            for jogo in agenda:
                if "valor" not in jogo:
                    jogo["valor"] = 0.0
                if "pago" not in jogo:
                    jogo["pago"] = False
            return agenda
    return []


def salvar_agenda(agenda):
    with open(ARQUIVO, "w") as f:
        json.dump(agenda, f, indent=4)

@app.route("/times")
def listar_times():
    times = carregar_times()
    return render_template("times.html", times=times)

@app.route("/times/adicionar", methods=["POST"])
def adicionar_time():
    nome = request.form.get("nome", "").strip()
    if nome:
        times = carregar_times()
        times.append(nome)
        salvar_times(times)
    return redirect(url_for("listar_times"))

@app.route("/times/remover/<int:indice>")
def remover_time(indice):
    times = carregar_times()
    if 0 <= indice < len(times):
        times.pop(indice)
        salvar_times(times)
    return redirect(url_for("listar_times"))

@app.route("/")
def index():
    agenda = carregar_agenda()

    # Criar estrutura: { local: { data: [ (indice, jogo), ... ] } }
    jogos_por_local = {}
    for idx, jogo in enumerate(agenda):
        local = jogo["local"]
        data = jogo["data"]
        jogos_por_local.setdefault(local, {}).setdefault(data, []).append((idx, jogo))

    return render_template("index.html", jogos_por_local=jogos_por_local)

from datetime import datetime

@app.route("/calendario")
def calendario():
    agenda = carregar_agenda()
    eventos = []

    for i, jogo in enumerate(agenda):
        try:
            data = datetime.strptime(jogo["data"], "%d/%m/%Y").date()
            horario = jogo.get("horario")
            if horario:
                start = datetime.strptime(f"{jogo['data']} {horario}", "%d/%m/%Y %H:%M").isoformat()
            else:
                start = data.isoformat() + "T00:00:00"
        except Exception as e:
            print(f"Erro ao processar jogo {i}: {e}")
            continue

        eventos.append({
            "title": f"{jogo['time1']} x {jogo['time2']} - {jogo['local']}",
            "start": start,
            "url": url_for("editar", indice=i),
            "color": "#198754" if jogo.get("pago") else "#dc3545"
        })

    return render_template("calendario.html", eventos=eventos)


@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    agenda = carregar_agenda()
    times = carregar_times()  # <-- carrega antes

    if request.method == "POST":
        data = request.form["data"]
        horario = request.form["horario"]
        local = request.form["local"]
        time1 = request.form["time1"]
        time2 = request.form["time2"]
        arbitro = request.form.get("arbitro", "").strip()
        valor = float(request.form["valor"])
        pago = "pago" in request.form

                # Substitua essa parte
        data = request.form["data"]  # será no formato YYYY-MM-DD

        # Para converter para o formato esperado DD/MM/YYYY
        data_iso = data  # ex: '2025-05-20'
        data_obj = datetime.strptime(data_iso, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y")  # '20/05/2025'


        novo_jogo = {
            "data": data_formatada,
            "horario": horario,
            "local": local,
            "time1": time1,
            "time2": time2,
            "arbitro": arbitro,
            "valor": valor,
            "pago": pago,
        }

    

        agenda.append(novo_jogo)
        salvar_agenda(agenda)
        return redirect(url_for("index"))

    return render_template("adicionar.html", times=times)

@app.route("/alternar_pagamento/<int:indice>")
def alternar_pagamento(indice):
    agenda = carregar_agenda()
    if 0 <= indice < len(agenda):
        agenda[indice]["pago"] = not agenda[indice]["pago"]
        salvar_agenda(agenda)
    return redirect(url_for("index"))


@app.route("/remover/<int:indice>")
def remover(indice):
    agenda = carregar_agenda()
    if 0 <= indice < len(agenda):
        del agenda[indice]
        salvar_agenda(agenda)
    return redirect(url_for("index"))

@app.route("/editar/<int:indice>", methods=["GET", "POST"])
def editar(indice):
    agenda = carregar_agenda()
    times = carregar_times()  # <-- carregar aqui no início

    if indice < 0 or indice >= len(agenda):
        return redirect(url_for("index"))

    jogo = agenda[indice]

    if request.method == "POST":
        data_iso = request.form["data"]  # YYYY-MM-DD
        data_obj = datetime.strptime(data_iso, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y")
    
        jogo["data"] = data_formatada
        jogo["horario"] = request.form["horario"]
        jogo["local"] = request.form["local"]
        jogo["time1"] = request.form["time1"]
        jogo["time2"] = request.form["time2"]
        jogo["arbitro"] = request.form.get("arbitro", "").strip()
        jogo["valor"] = float(request.form["valor"])
        jogo["pago"] = "pago" in request.form

        salvar_agenda(agenda)
        return redirect(url_for("index"))
    try:
        data_obj = datetime.strptime(jogo["data"], "%d/%m/%Y")
        jogo["data"] = data_obj.strftime("%Y-%m-%d")
    except ValueError:
        jogo["data"] = ""

    return render_template("editar.html", jogo=jogo, times=times)

if __name__ == "__main__":
    app.run(debug=True)
