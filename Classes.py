#Feito

import pickle
from datetime import date


class Usuario:
    def __init__(self, login, senha):
        self.login = login
        self.senha = senha

    def autenticar(self, login, senha):
        return self.login == login and self.senha == senha


class Administrador(Usuario):
    def __init__(self, login, senha):
        super().__init__(login, senha)

    def aceitar_justificativa(self, justificativa, cliente):
        justificativa.aceitar()
        cliente.desbloquear()

    def recusar_justificativa(self, justificativa, cliente):
        justificativa.recusar()
        cliente.bloquear()


class Cliente(Usuario):
    def __init__(self, nome, telefone, endereco, cpf, login, senha):
        super().__init__(login, senha)
        self.nome = nome
        self.telefone = telefone
        self.endereco = endereco
        self.cpf = cpf
        self.bloqueado = False
        self.cartoes = []
        self.pedidos = []

    def bloquear(self):
        self.bloqueado = True

    def desbloquear(self):
        self.bloqueado = False

    def __repr__(self):
        if self.bloqueado:
            situacao = "BLOQUEADO"
        else:
            situacao = "ativo"
        texto = "Nome: " + self.nome + "\n"
        texto += "  CPF: " + self.cpf + "\n"
        texto += "  Telefone: " + self.telefone + "\n"
        texto += "  Endereço: " + self.endereco + "\n"
        texto += "  Login: " + self.login + "\n"
        texto += "  Cadastro: " + situacao + "\n"
        texto += "  Cartões:"
        if len(self.cartoes) == 0:
            texto += " nenhum"
        for c in self.cartoes:
            texto += "\n    - " + str(c)
        return texto


class Cartao:
    def __init__(self, numero, validade, cvv, titular, cpf, tipo):
        self.numero = numero
        self.validade = validade
        self.cvv = cvv
        self.titular = titular
        self.cpf = cpf
        self.tipo = tipo

    def __repr__(self):
        return self.tipo + " final " + self.numero[-4:] + " | validade " + self.validade + " | titular " + self.titular


class Justificativa:
    def __init__(self, texto):
        self.texto = texto
        self.data = date.today()
        self.status = "pendente"

    def aceitar(self):
        self.status = "aceita"

    def recusar(self):
        self.status = "recusada"

    def __repr__(self):
        return "\"" + self.texto + "\" (enviada em " + self.data.strftime("%d/%m/%Y") + ", " + self.status + ")"


class Pagamento:
    def __init__(self, valor, data_vencimento):
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.status = "pendente"
        self.justificativa = None

    def alterar_status(self, status):
        if status != "pendente" and status != "realizado" and status != "atrasado":
            raise ValueError("Status de pagamento inválido.")
        self.status = status

    def dias_atraso(self):
        if self.status == "realizado":
            return 0
        dias = (date.today() - self.data_vencimento).days
        if dias < 0:
            dias = 0
        return dias

    def __repr__(self):
        texto = "Pagamento: R$ " + "%.2f" % self.valor + " | vencimento " + self.data_vencimento.strftime("%d/%m/%Y") + " | " + self.status
        if self.dias_atraso() > 0:
            texto += " (" + str(self.dias_atraso()) + " dia(s) de atraso)"
        if self.justificativa != None:
            texto += "\n    Justificativa: " + str(self.justificativa)
        return texto


class Pedido:
    def __init__(self, codigo, descricao, data_inicio, data_prevista, pagamento):
        self.codigo = codigo
        self.descricao = descricao
        self.data_inicio = data_inicio
        self.data_prevista = data_prevista
        self.status = "em andamento"
        self.pagamento = pagamento

    def alterar_status(self, status):
        if status != "em andamento" and status != "finalizado" and status != "cancelado":
            raise ValueError("Status de pedido inválido.")
        self.status = status

    def __repr__(self):
        texto = "Pedido " + str(self.codigo) + ": " + self.descricao + "\n"
        texto += "  Início: " + self.data_inicio.strftime("%d/%m/%Y")
        texto += " | Previsão: " + self.data_prevista.strftime("%d/%m/%Y")
        texto += " | Status: " + self.status + "\n"
        texto += "  " + str(self.pagamento)
        return texto


class Sistema:
    def __init__(self):
        self.usuarios = []
        self.usuario_logado = None

    def cadastrar_cliente(self, cliente):
        if cliente.nome.strip() == "" or cliente.telefone.strip() == "" or cliente.endereco.strip() == "":
            return False
        if cliente.cpf.strip() == "" or cliente.login.strip() == "" or cliente.senha.strip() == "":
            return False
        for u in self.usuarios:
            if u.login == cliente.login:
                return False
            if isinstance(u, Cliente) and u.cpf == cliente.cpf:
                return False
        self.usuarios.append(cliente)
        return True

    def login(self, login, senha):
        for u in self.usuarios:
            if u.autenticar(login, senha):
                self.usuario_logado = u
                return u
        return None

    def cadastrar_cartao(self, cliente, cartao):
        if cliente == None:
            return False
        if not cartao.numero.isdigit() or len(cartao.numero) != 16:
            return False
        if cartao.tipo != "crédito" and cartao.tipo != "débito":
            return False
        # validade no formato mm/aa
        partes = cartao.validade.split("/")
        if len(partes) != 2:
            return False
        if not partes[0].isdigit() or not partes[1].isdigit():
            return False
        if len(partes[0]) != 2 or len(partes[1]) != 2:
            return False
        if int(partes[0]) < 1 or int(partes[0]) > 12:
            return False
        # cvv com 3 ou 4 dígitos
        if not cartao.cvv.isdigit() or (len(cartao.cvv) != 3 and len(cartao.cvv) != 4):
            return False
        if cartao.titular.strip() == "" or cartao.cpf.strip() == "":
            return False
        cliente.cartoes.append(cartao)
        return True

    def buscar_cliente(self, cpf):
        for u in self.usuarios:
            if isinstance(u, Cliente) and u.cpf == cpf:
                return u
        return None

    def cadastrar_pedido(self, cliente, pedido):
        if cliente == None:
            return False
        self.listar_pedidos(cliente)  # atualiza o bloqueio antes de aceitar o pedido
        if cliente.bloqueado:
            return False
        cliente.pedidos.append(pedido)
        return True

    def listar_pedidos(self, cliente):
        bloquear = False
        for pedido in cliente.pedidos:
            pg = pedido.pagamento
            if pg.status == "pendente" and pg.dias_atraso() > 0:
                pg.alterar_status("atrasado")
            if pg.dias_atraso() > 0:
                j = pg.justificativa
                if j != None and j.status == "recusada":
                    bloquear = True
                elif pg.dias_atraso() > 7:
                    if j == None or j.status != "aceita":
                        bloquear = True
        if bloquear:
            cliente.bloquear()
        else:
            cliente.desbloquear()
        return cliente.pedidos

    def enviar_justificativa(self, pagamento, texto):
        if texto.strip() == "" or pagamento.dias_atraso() == 0:
            return False
        if pagamento.justificativa != None:
            return False
        pagamento.justificativa = Justificativa(texto)
        return True

    def salvar(self):
        arquivo = open("dados_edulu.pkl", "wb")
        pickle.dump(self.usuarios, arquivo)
        arquivo.close()

    def carregar(self):
        try:
            arquivo = open("dados_edulu.pkl", "rb")
            self.usuarios = pickle.load(arquivo)
            arquivo.close()
        except FileNotFoundError:
            self.usuarios = []
        tem_admin = False
        for u in self.usuarios:
            if isinstance(u, Administrador):
                tem_admin = True
        if tem_admin == False:
            self.usuarios.append(Administrador("admin", "admin"))
            self.salvar()