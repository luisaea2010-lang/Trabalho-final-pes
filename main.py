from datetime import datetime

from Classes import (Sistema, Administrador, Cliente, Cartao, Pedido,
                     Pagamento, STATUS_PEDIDO, STATUS_PAGAMENTO)


# ---------- interface em modo texto (estilo chatbot) ----------

def bot(mensagem):
    print(f"\nEDULU: {mensagem}")


def perguntar(pergunta):
    bot(pergunta)
    return input("Você: ").strip()


def ler_data(pergunta):
    while True:
        texto = perguntar(pergunta + " (dd/mm/aaaa)")
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            bot("Data inválida. Tente novamente.")


def ler_valor(pergunta):
    while True:
        texto = perguntar(pergunta).replace(",", ".")
        try:
            valor = float(texto)
            if valor > 0:
                return valor
        except ValueError:
            pass
        bot("Valor inválido. Tente novamente.")


def apenas_digitos(texto):
    return "".join(c for c in texto if c.isdigit())


def escolher_status(opcoes):
    texto = " / ".join(f"{i} - {o}" for i, o in enumerate(opcoes, 1))
    escolha = perguntar(f"Escolha o novo status: {texto}")
    if escolha.isdigit() and 1 <= int(escolha) <= len(opcoes):
        return opcoes[int(escolha) - 1]
    return None


def todos_clientes(sistema):
    return [u for u in sistema.usuarios if isinstance(u, Cliente)]


def proximo_codigo(sistema):
    codigos = [p.codigo for c in todos_clientes(sistema) for p in c.pedidos]
    return max(codigos, default=0) + 1


def escolher_pedido(sistema, cliente):
    pedidos = sistema.listar_pedidos(cliente)
    if not pedidos:
        bot("Este cliente não possui pedidos.")
        return None
    codigo = perguntar("Informe o código do pedido:")
    for p in pedidos:
        if str(p.codigo) == codigo:
            return p
    bot("Pedido não encontrado.")
    return None


# ---------- casos de uso do administrador ----------

def uc01_cadastrar_cliente(sistema):
    nome = perguntar("Nome do cliente:")
    telefone = perguntar("Telefone:")
    endereco = perguntar("Endereço:")
    cpf = apenas_digitos(perguntar("CPF:"))
    login = perguntar("Login do cliente:")
    senha = perguntar("Senha do cliente:")
    if sistema.cadastrar_cliente(Cliente(nome, telefone, endereco, cpf, login, senha)):
        sistema.salvar()
        bot("Cliente cadastrado com sucesso!")
    else:
        bot("Falha no cadastro: preencha todos os dados e use CPF e login ainda não cadastrados.")


def uc04_visualizar_cliente_adm(sistema):
    cliente = sistema.buscar_cliente(apenas_digitos(perguntar("CPF do cliente:")))
    if cliente is None:
        bot("Cliente não encontrado.")
        return
    sistema.listar_pedidos(cliente)
    sistema.salvar()
    bot(f"Dados do cliente:\n  {cliente}")


def uc09_cadastrar_pedido(sistema):
    cliente = sistema.buscar_cliente(apenas_digitos(perguntar("CPF do cliente do pedido:")))
    if cliente is None:
        bot("Não é possível cadastrar um pedido sem um cliente cadastrado.")
        return
    descricao = perguntar("Descrição do trabalho:")
    inicio = ler_data("Data de início")
    previsao = ler_data("Data esperada de conclusão")
    valor = ler_valor("Valor do pedido (R$):")
    vencimento = ler_data("Data de vencimento do pagamento")
    pedido = Pedido(proximo_codigo(sistema), descricao, inicio, previsao,
                    Pagamento(valor, vencimento))
    if sistema.cadastrar_pedido(cliente, pedido):
        sistema.salvar()
        bot(f"Pedido {pedido.codigo} cadastrado com sucesso!")
    else:
        bot("Falha: cadastro bloqueado por atraso de pagamento. O pedido não foi adicionado.")


def uc07_uc08_analisar_justificativas(sistema):
    pendentes = []
    for cliente in todos_clientes(sistema):
        for pedido in sistema.listar_pedidos(cliente):
            j = pedido.pagamento.justificativa
            if j is not None and j.status == "pendente":
                pendentes.append((cliente, pedido))
    sistema.salvar()
    if not pendentes:
        bot("Não há justificativas pendentes.")
        return
    for i, (cliente, pedido) in enumerate(pendentes, 1):
        bot(f"[{i}] Cliente: {cliente.nome} | Pedido {pedido.codigo}\n"
            f"    Justificativa: {pedido.pagamento.justificativa.texto}")
    escolha = perguntar("Qual justificativa deseja analisar? (número)")
    if not (escolha.isdigit() and 1 <= int(escolha) <= len(pendentes)):
        bot("Opção inválida.")
        return
    cliente, pedido = pendentes[int(escolha) - 1]
    decisao = perguntar("1 - Aceitar | 2 - Recusar")
    admin = sistema.usuario_logado
    justificativa = pedido.pagamento.justificativa
    if decisao == "1":
        admin.aceitar_justificativa(justificativa, cliente)
        bot("Justificativa aceita. O prazo do cliente foi estendido.")
    elif decisao == "2":
        admin.recusar_justificativa(justificativa, cliente)
        bot("Justificativa recusada. O cadastro do cliente foi bloqueado.")
    else:
        bot("Opção inválida.")
        return
    sistema.salvar()


def uc10_alterar_status_pedido(sistema):
    cliente = sistema.buscar_cliente(apenas_digitos(perguntar("CPF do cliente:")))
    if cliente is None:
        bot("Cliente não encontrado.")
        return
    pedido = escolher_pedido(sistema, cliente)
    if pedido is None:
        return
    status = escolher_status(STATUS_PEDIDO)
    if status is None:
        bot("Opção inválida.")
        return
    pedido.alterar_status(status)
    sistema.salvar()
    bot(f"Status do pedido {pedido.codigo} alterado para '{status}'.")


def uc11_alterar_status_pagamento(sistema):
    cliente = sistema.buscar_cliente(apenas_digitos(perguntar("CPF do cliente:")))
    if cliente is None:
        bot("Cliente não encontrado.")
        return
    pedido = escolher_pedido(sistema, cliente)
    if pedido is None:
        return
    status = escolher_status(STATUS_PAGAMENTO)
    if status is None:
        bot("Opção inválida.")
        return
    pedido.pagamento.alterar_status(status)
    sistema.listar_pedidos(cliente)
    sistema.salvar()
    bot(f"Status do pagamento do pedido {pedido.codigo} alterado para '{status}'.")


# ---------- casos de uso do cliente ----------

def uc03_cadastrar_cartao(sistema, cliente):
    tipo = perguntar("Tipo do cartão: 1 - crédito | 2 - débito")
    tipo = {"1": "crédito", "2": "débito"}.get(tipo, "")
    numero = apenas_digitos(perguntar("Número do cartão (16 dígitos):"))
    validade = perguntar("Validade (mm/aa):")
    cvv = perguntar("Código de segurança (CVV):")
    titular = perguntar("Nome do titular:")
    cpf = apenas_digitos(perguntar("CPF do titular:"))
    if sistema.cadastrar_cartao(cliente, Cartao(numero, validade, cvv, titular, cpf, tipo)):
        sistema.salvar()
        bot("Cartão cadastrado com sucesso!")
    else:
        bot("Falha no cadastro do cartão. Confira os dados informados.")


def uc04_visualizar_dados_cliente(sistema, cliente):
    sistema.listar_pedidos(cliente)
    sistema.salvar()
    bot(f"Seus dados:\n  {cliente}")


def uc05_visualizar_pedidos(sistema, cliente):
    pedidos = sistema.listar_pedidos(cliente)
    sistema.salvar()
    if not pedidos:
        bot("Você ainda não possui pedidos.")
        return
    bot("Seus pedidos:\n" + "\n".join(str(p) for p in pedidos))


def uc06_enviar_justificativa(sistema, cliente):
    atrasados = [p for p in sistema.listar_pedidos(cliente) if p.pagamento.dias_atraso() > 0]
    sistema.salvar()
    if not atrasados:
        bot("Você não possui pagamentos atrasados.")
        return
    bot("Pagamentos atrasados:\n" + "\n".join(str(p) for p in atrasados))
    codigo = perguntar("Código do pedido para justificar:")
    pedido = next((p for p in atrasados if str(p.codigo) == codigo), None)
    if pedido is None:
        bot("Pedido não encontrado entre os atrasados.")
        return
    texto = perguntar("Escreva sua justificativa:")
    if sistema.enviar_justificativa(pedido.pagamento, texto):
        sistema.salvar()
        bot("Justificativa enviada ao administrador.")
    else:
        bot("Não foi possível enviar: texto vazio ou já existe uma justificativa para este pagamento.")


# ---------- menus ----------

def menu_administrador(sistema):
    opcoes = {
        "1": ("Cadastrar cliente", uc01_cadastrar_cliente),
        "2": ("Visualizar dados de um cliente", uc04_visualizar_cliente_adm),
        "3": ("Cadastrar pedido", uc09_cadastrar_pedido),
        "4": ("Analisar justificativas de atraso", uc07_uc08_analisar_justificativas),
        "5": ("Alterar status de um pedido", uc10_alterar_status_pedido),
        "6": ("Alterar status de um pagamento", uc11_alterar_status_pagamento),
    }
    while True:
        lista = "\n".join(f"  {k} - {v[0]}" for k, v in opcoes.items())
        escolha = perguntar(f"Menu do administrador:\n{lista}\n  0 - Sair")
        if escolha == "0":
            return
        if escolha in opcoes:
            opcoes[escolha][1](sistema)
        else:
            bot("Opção inválida.")


def menu_cliente(sistema, cliente):
    opcoes = {
        "1": ("Ver meus dados", uc04_visualizar_dados_cliente),
        "2": ("Cadastrar cartão", uc03_cadastrar_cartao),
        "3": ("Ver meus pedidos e pagamentos", uc05_visualizar_pedidos),
        "4": ("Enviar justificativa de atraso", uc06_enviar_justificativa),
    }
    while True:
        lista = "\n".join(f"  {k} - {v[0]}" for k, v in opcoes.items())
        escolha = perguntar(f"Menu do cliente:\n{lista}\n  0 - Sair")
        if escolha == "0":
            return
        if escolha in opcoes:
            opcoes[escolha][1](sistema, cliente)
        else:
            bot("Opção inválida.")


def fazer_login(sistema):
    login = perguntar("Login:")
    senha = perguntar("Senha:")
    usuario = sistema.login(login, senha)
    if usuario is None:
        bot("Falha no login: usuário ou senha incorretos.")
        return
    bot("Login realizado com sucesso!")
    if isinstance(usuario, Administrador):
        menu_administrador(sistema)
    else:
        if usuario.bloqueado:
            bot("Atenção: seu cadastro está bloqueado por atraso de pagamento.")
        menu_cliente(sistema, usuario)
    sistema.usuario_logado = None


def main():
    sistema = Sistema()
    sistema.carregar()
    bot("Olá! Bem-vindo(a) à EDULU.")
    while True:
        escolha = perguntar("1 - Entrar\n  0 - Encerrar")
        if escolha == "1":
            fazer_login(sistema)
        elif escolha == "0":
            sistema.salvar()
            bot("Até logo!")
            return
        else:
            bot("Opção inválida.")


if __name__ == "__main__":
    main()
