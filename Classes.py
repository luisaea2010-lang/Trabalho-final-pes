class Pessoa:
    def __init__(self, nome, cpf, endereço,celular, login, senha, tipo):
        self.nome = nome
        self.cpf = cpf
        self.endereço = endereço
        self.celular = celular
        self.login = login
        self.senha = senha
    def __repr__(self):
        return f"Nome: {self.nome} \n CPF: {self.cpf} \n Endereço: {self.endereço} \n Celular: {self.celular} \n Login: {self.login}"
    
class Trabalho:
    def __init__(self, descricao, datainicial, datafinal, status, valor):
        self.descricao = descricao
        self.datainicial = datainicial
        self.datafinal = datafinal
        self.valor = valor
        self.status = status
    def __repr__(self):
        return f"Descrição: {self.descricao} \n Data de Início: {self.datainicial} \n Data de Fim: {self.datafinal} \n Valor: {self.valor}\n Status: {self.status}"
    
class AvisoDeAtraso:
    def __init__(self, dscrição):
        self.dscrição = dscrição
    def __repr__(self):
        return f"Aviso de Atraso: {self.dscrição}"
    
class Pagamento:
    def __init__(self, valor, data_limite, forma_pagamento, juros):
        self.valor = valor
        self.forma_pagamento = forma_pagamento
        self.juros = juros
        self.data_limite = data_limite
    def __repr__(self);:
        return f"Valor: {self.valor} \n Forma de Pagamento: {self.forma_pagamento} \n Juros: {self.juros} \n Data Limite: {self.data_limite}"
    
class Notificacao:
    def __init__(self, mensagem, tipo):
        self.mensagem = mensagem
        self.tipo = tipo
        self.statusaviso = False

    def __repr__(self):
        return f"Notificação: {self.mensagem} \n Tipo: {self.tipo}"

    def marcar_como_lida(self):
        self.status = True
        return f"A notificação \n '{self.mensagem}' \n foi marcada como lida."
    
    def consultar_status(self):
        if self.status==True:
            if self.tipo == "aviso de atraso":
                if self.statusaviso==True:
                    return f"A notificação \n '{self.mensagem}' \n foi lida. E aceita."
                else:
                    return f"A notificação \n '{self.mensagem}' \n foi lida. E não aceita."
        else:
            return f"A notificação \n '{self.mensagem}' \n não foi lida."