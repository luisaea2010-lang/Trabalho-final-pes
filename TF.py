#Feito

"""Protótipo EDULU – interface em modo texto (estilo chatbot)."""
 
from datetime import datetime
 
from Classes import Sistema, Administrador, Cliente, Cartao, Pedido, Pagamento
 
 
# ---------------------------------------------------------------------------
# Funções auxiliares de leitura
# ---------------------------------------------------------------------------
def ler_inteiro(mensagem):
    """Lê um número inteiro. Retorna None se o valor for inválido."""
    try:
        return int(input(mensagem))
    except ValueError:
        print("Erro: Você não digitou um número.")
        return None
 
 
def ler_cpf(mensagem):
    """Lê um CPF e mantém apenas os dígitos."""
    return "".join(c for c in input(mensagem) if c.isdigit())
 
 
def ler_data(mensagem):
    """Lê uma data no formato dd/mm/aaaa. Retorna None se for inválida."""
    try:
        return datetime.strptime(input(mensagem), "%d/%m/%Y").date()
    except ValueError:
        return None
 
 
def proximo_codigo(sistema):
    """Gera o próximo código de pedido disponível."""
    codigos = [p.codigo
               for u in sistema.usuarios if isinstance(u, Cliente)
               for p in u.pedidos]
    return max(codigos, default=0) + 1
 
 
def pedir_cliente(sistema, mensagem="Qual o CPF do cliente? "):
    """Pede um CPF e devolve o cliente (ou None, avisando que não achou)."""
    cliente = sistema.buscar_cliente(ler_cpf(mensagem))
    if cliente is None:
        print("CPF não encontrado!")
    return cliente
 
 
def escolher_pedido(sistema, cliente):
    """Mostra os pedidos do cliente e devolve o escolhido (ou None)."""
    pedidos = sistema.listar_pedidos(cliente)
    if len(pedidos) == 0:
        print("Lista vazia!")
        return None
    for pedido in pedidos:
        print(pedido)
    codigo = ler_inteiro("Qual o código do pedido? ")
    if codigo is None:
        return None
    for pedido in pedidos:
        if pedido.codigo == codigo:
            return pedido
    print("Código não encontrado!")
    return None
 
 
# ---------------------------------------------------------------------------
# Ações do administrador
# ---------------------------------------------------------------------------
def adm_cadastrar_cliente(sistema):
    nome = input("Qual o nome completo do cliente? ")
    telefone = input("Qual o telefone do cliente? ")
    endereco = input("Qual o endereço do cliente? ")
    cpf = ler_cpf("Qual o CPF do cliente? ")
    login = input("Qual o login do cliente? ")
    senha = input("Qual a senha do cliente? ")
    if sistema.cadastrar_cliente(Cliente(nome, telefone, endereco, cpf, login, senha)):
        print("Sucesso!")
    else:
        print("Falha no cadastro! Preencha todos os dados e use CPF e login que ainda não foram cadastrados.")
 
 
def adm_ver_cliente(sistema):
    cliente = pedir_cliente(sistema)
    if cliente is not None:
        sistema.listar_pedidos(cliente)
        print(cliente)
 
 
def adm_cadastrar_pedido(sistema):
    cliente = sistema.buscar_cliente(ler_cpf("Qual o CPF do cliente do pedido? "))
    if cliente is None:
        print("Não é possível cadastrar um pedido sem um cliente cadastrado!")
        return
    descricao = input("Qual a descrição do trabalho? ")
    inicio = ler_data("Qual a data de início? (dd/mm/aaaa) ")
    fim = ler_data("Qual a data esperada de conclusão? (dd/mm/aaaa) ")
    try:
        valor = float(input("Qual o valor do pedido (R$)? ").replace(",", "."))
    except ValueError:
        valor = None
    vencimento = ler_data("Qual a data de vencimento do pagamento? (dd/mm/aaaa) ")
    if None in (inicio, fim, valor, vencimento):
        print("Erro: data ou valor inválido.")
        return
    if valor <= 0:
        print("Erro: o valor do pedido deve ser maior que zero.")
        return
    if fim < inicio:
        print("Erro: a data de conclusão não pode ser anterior à data de início.")
        return
    codigo = proximo_codigo(sistema)
    if sistema.cadastrar_pedido(cliente, Pedido(codigo, descricao, inicio, fim, Pagamento(valor, vencimento))):
        print("Sucesso! Pedido", codigo, "cadastrado.")
    else:
        print("Falha: cadastro bloqueado por atraso de pagamento!")
 
 
def adm_analisar_justificativas(sistema, admin):
    pendentes = []
    for usuario in sistema.usuarios:
        if isinstance(usuario, Cliente):
            for pedido in sistema.listar_pedidos(usuario):
                just = pedido.pagamento.justificativa
                if just is not None and just.status == "pendente":
                    pendentes.append((usuario, pedido))
    if len(pendentes) == 0:
        print("Não há justificativas pendentes!")
        return
    for i, (cliente, pedido) in enumerate(pendentes, start=1):
        print(i, "– Cliente:", cliente.nome, "| Pedido", pedido.codigo,
              "| Justificativa:", pedido.pagamento.justificativa.texto)
    escolha = ler_inteiro("Qual justificativa deseja analisar? ")
    if escolha is None:
        return
    decisao = ler_inteiro("1 – Aceitar \n2 – Recusar \n")
    if decisao is None:
        return
    if escolha < 1 or escolha > len(pendentes) or decisao not in (1, 2):
        print("Opção inválida!")
        return
    cliente, pedido = pendentes[escolha - 1]
    justificativa = pedido.pagamento.justificativa
    if decisao == 1:
        admin.aceitar_justificativa(justificativa, cliente)
        print("Justificativa aceita! O prazo do cliente foi estendido.")
    else:
        admin.recusar_justificativa(justificativa, cliente)
        print("Justificativa recusada! O cadastro do cliente foi bloqueado.")
 
 
def adm_alterar_status_pedido(sistema):
    cliente = pedir_cliente(sistema)
    if cliente is None:
        return
    pedido = escolher_pedido(sistema, cliente)
    if pedido is None:
        return
    opcao = ler_inteiro("Qual o novo status? \n 1 – em andamento \n 2 – finalizado \n 3 – cancelado \n")
    if opcao is None:
        return
    if opcao < 1 or opcao > 3:
        print("Opção inválida!")
        return
    pedido.alterar_status(["em andamento", "finalizado", "cancelado"][opcao - 1])
    print("Sucesso!")
 
 
def adm_alterar_status_pagamento(sistema):
    cliente = pedir_cliente(sistema)
    if cliente is None:
        return
    pedido = escolher_pedido(sistema, cliente)
    if pedido is None:
        return
    opcao = ler_inteiro("Qual o novo status do pagamento? \n 1 – pendente \n 2 – realizado \n 3 – atrasado \n")
    if opcao is None:
        return
    if opcao < 1 or opcao > 3:
        print("Opção inválida!")
        return
    pedido.pagamento.alterar_status(["pendente", "realizado", "atrasado"][opcao - 1])
    sistema.listar_pedidos(cliente)
    print("Sucesso!")
 
 
def menu_administrador(sistema, admin):
    while True:
        opcao = ler_inteiro(
            "Escolha uma opção: \n"
            " 1 – Cadastrar cliente \n"
            " 2 – Visualizar dados de um cliente \n"
            " 3 – Cadastrar pedido \n"
            " 4 – Analisar justificativas de atraso \n"
            " 5 – Alterar status de um pedido \n"
            " 6 – Alterar status de um pagamento \n"
            " 7 – Salvar dados \n"
            " 0 – Sair \n")
        if opcao is None:
            continue
        if opcao == 1:
            adm_cadastrar_cliente(sistema)
        elif opcao == 2:
            adm_ver_cliente(sistema)
        elif opcao == 3:
            adm_cadastrar_pedido(sistema)
        elif opcao == 4:
            adm_analisar_justificativas(sistema, admin)
        elif opcao == 5:
            adm_alterar_status_pedido(sistema)
        elif opcao == 6:
            adm_alterar_status_pagamento(sistema)
        elif opcao == 7:
            sistema.salvar()
            print("Dados salvos!")
        elif opcao == 0:
            break
        else:
            print("Opção inválida!")
 
 
# ---------------------------------------------------------------------------
# Ações do cliente
# ---------------------------------------------------------------------------
def cli_cadastrar_cartao(sistema, cliente):
    tipo_op = ler_inteiro("Qual o tipo do cartão? \n 1 – crédito \n 2 – débito \n")
    if tipo_op is None:
        return
    if tipo_op not in (1, 2):
        print("Opção inválida!")
        return
    numero = ler_cpf("Qual o número do cartão? (16 dígitos) ")
    validade = input("Qual a validade do cartão? (mm/aa) ")
    cvv = input("Qual o código de segurança (CVV)? ")
    titular = input("Qual o nome do titular? ")
    cpf_titular = ler_cpf("Qual o CPF do titular? ")
    tipo = "crédito" if tipo_op == 1 else "débito"
    if sistema.cadastrar_cartao(cliente, Cartao(numero, validade, cvv, titular, cpf_titular, tipo)):
        print("Sucesso!")
    else:
        print("Falha no cadastro do cartão! Confira os dados informados.")
 
 
def cli_ver_pedidos(sistema, cliente):
    pedidos = sistema.listar_pedidos(cliente)
    if len(pedidos) == 0:
        print("Lista vazia!")
    for pedido in pedidos:
        print(pedido)
 
 
def cli_enviar_justificativa(sistema, cliente):
    atrasados = [p for p in sistema.listar_pedidos(cliente) if p.pagamento.dias_atraso() > 0]
    if len(atrasados) == 0:
        print("Você não possui pagamentos atrasados!")
        return
    for pedido in atrasados:
        print(pedido)
    codigo = ler_inteiro("Qual o código do pedido que deseja justificar? ")
    if codigo is None:
        return
    for pedido in atrasados:
        if pedido.codigo == codigo:
            texto = input("Escreva sua justificativa: ")
            if sistema.enviar_justificativa(pedido.pagamento, texto):
                print("Sucesso! Justificativa enviada ao administrador.")
            else:
                print("Não foi possível enviar: texto vazio ou já existe uma justificativa para este pagamento.")
            return
    print("Código não encontrado!")
 
 
def menu_cliente(sistema, cliente):
    sistema.listar_pedidos(cliente)
    if cliente.bloqueado:
        print("Atenção: seu cadastro está bloqueado por atraso de pagamento.")
    while True:
        opcao = ler_inteiro(
            "Escolha uma opção: \n"
            " 1 – Ver meus dados \n"
            " 2 – Cadastrar cartão \n"
            " 3 – Ver meus pedidos e pagamentos \n"
            " 4 – Enviar justificativa de atraso \n"
            " 5 – Salvar dados \n"
            " 0 – Sair \n")
        if opcao is None:
            continue
        if opcao == 1:
            sistema.listar_pedidos(cliente)
            print(cliente)
        elif opcao == 2:
            cli_cadastrar_cartao(sistema, cliente)
        elif opcao == 3:
            cli_ver_pedidos(sistema, cliente)
        elif opcao == 4:
            cli_enviar_justificativa(sistema, cliente)
        elif opcao == 5:
            sistema.salvar()
            print("Dados salvos!")
        elif opcao == 0:
            break
        else:
            print("Opção inválida!")
 
 
# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
sistema = Sistema()
try:
    sistema.carregar()
except FileNotFoundError:
    print("Nenhum dado salvo encontrado. Iniciando um sistema novo.")
 
print("Olá! Bem-vindo(a) à EDULU.")
while True:
    opcao = ler_inteiro("Escolha uma opção: \n 1 – Entrar \n 2 – Salvar dados \n 3 – Carregar dados \n 0 – Sair \n")
    if opcao is None:
        continue
    if opcao == 1:
        login = input("Login: ")
        senha = input("Senha: ")
        usuario = sistema.login(login, senha)
        if usuario is None:
            print("Login ou senha incorretos!")
            continue
        print("Login realizado com sucesso!")
        if isinstance(usuario, Administrador):
            menu_administrador(sistema, usuario)
        else:
            menu_cliente(sistema, usuario)
        sistema.usuario_logado = None
        sistema.salvar()
    elif opcao == 2:
        sistema.salvar()
        print("Dados salvos!")
    elif opcao == 3:
        try:
            sistema.carregar()
            print("Dados carregados!")
        except FileNotFoundError:
            print("Nenhum arquivo de dados encontrado!")
    elif opcao == 0:
        sistema.salvar()
        print("Até logo!")
        break
    else:
        print("Opção inválida!")