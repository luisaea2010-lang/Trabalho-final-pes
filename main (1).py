"""Protótipo EDULU – interface em modo texto (estilo chatbot)."""

from Classes import Sistema, Administrador, Cliente, Cartao, Pedido, Pagamento
from datetime import datetime

sistema = Sistema()
sistema.carregar()
print ("Olá! Bem-vindo(a) à EDULU.")
while True:
    try:
        x=int(input("Escolha uma opção: \n 1 – Entrar \n 2 – Salvar dados \n 3 – Carregar dados \n 0 – Sair;"))
    except ValueError:
        print ("Erro: Você não digitou um número.")
        continue
    if x==1:
        lg=input("Login: ")
        sn=input("Senha: ")
        u=sistema.login(lg,sn)
        if u == None:
            print ("Login ou senha incorretos!")
            continue
        print ("Login realizado com sucesso!")
        if isinstance(u, Administrador):
            while True:
                try:
                    y=int(input("Escolha uma opção: \n 1 – Cadastrar cliente \n 2 – Visualizar dados de um cliente \n 3 – Cadastrar pedido \n 4 – Analisar justificativas de atraso \n 5 – Alterar status de um pedido \n 6 – Alterar status de um pagamento \n 7 – Salvar dados \n 0 – Sair;"))
                except ValueError:
                    print ("Erro: Você não digitou um número.")
                    continue
                if y==1:
                    n=input("Qual o nome completo do cliente? ")
                    t=input("Qual o telefone do cliente? ")
                    e=input("Qual o endereço do cliente? ")
                    c="".join(k for k in input("Qual o CPF do cliente? ") if k.isdigit())
                    lg=input("Qual o login do cliente? ")
                    sn=input("Qual a senha do cliente? ")
                    if sistema.cadastrar_cliente(Cliente(n,t,e,c,lg,sn)):
                        print ("Sucesso!")
                    else:
                        print ("Falha no cadastro! Preencha todos os dados e use CPF e login que ainda não foram cadastrados.")
                else:
                    if y==2:
                        c="".join(k for k in input("Qual o CPF do cliente? ") if k.isdigit())
                        cl=sistema.buscar_cliente(c)
                        if cl == None:
                            print ("CPF não encontrado!")
                        else:
                            sistema.listar_pedidos(cl)
                            print (cl)
                    else:
                        if y==3:
                            c="".join(k for k in input("Qual o CPF do cliente do pedido? ") if k.isdigit())
                            cl=sistema.buscar_cliente(c)
                            if cl == None:
                                print ("Não é possível cadastrar um pedido sem um cliente cadastrado!")
                                continue
                            d=input("Qual a descrição do trabalho? ")
                            try:
                                di=datetime.strptime(input("Qual a data de início? (dd/mm/aaaa) "), "%d/%m/%Y").date()
                                df=datetime.strptime(input("Qual a data esperada de conclusão? (dd/mm/aaaa) "), "%d/%m/%Y").date()
                                vl=float(input("Qual o valor do pedido (R$)? ").replace(",", "."))
                                dv=datetime.strptime(input("Qual a data de vencimento do pagamento? (dd/mm/aaaa) "), "%d/%m/%Y").date()
                            except ValueError:
                                print ("Erro: data ou valor inválido.")
                                continue
                            cod=1
                            for k in sistema.usuarios:
                                if isinstance(k, Cliente):
                                    for p in k.pedidos:
                                        if p.codigo >= cod:
                                            cod=p.codigo+1
                            if sistema.cadastrar_pedido(cl, Pedido(cod,d,di,df,Pagamento(vl,dv))):
                                print ("Sucesso! Pedido", cod, "cadastrado.")
                            else:
                                print ("Falha: cadastro bloqueado por atraso de pagamento!")
                        else:
                            if y==4:
                                pend=[]
                                for k in sistema.usuarios:
                                    if isinstance(k, Cliente):
                                        for p in sistema.listar_pedidos(k):
                                            if p.pagamento.justificativa != None and p.pagamento.justificativa.status == "pendente":
                                                pend.append((k,p))
                                if len(pend)==0:
                                    print ("Não há justificativas pendentes!")
                                    continue
                                for w in range(len(pend)):
                                    print (w+1, "– Cliente:", pend[w][0].nome, "| Pedido", pend[w][1].codigo, "| Justificativa:", pend[w][1].pagamento.justificativa.texto)
                                try:
                                    q=int(input("Qual justificativa deseja analisar? "))
                                    r=int(input("1 – Aceitar \n 2 – Recusar \n"))
                                except ValueError:
                                    print ("Erro: Você não digitou um número.")
                                    continue
                                if q<1 or q>len(pend) or (r!=1 and r!=2):
                                    print ("Opção invalida!")
                                    continue
                                cl=pend[q-1][0]
                                j=pend[q-1][1].pagamento.justificativa
                                if r==1:
                                    u.aceitar_justificativa(j,cl)
                                    print ("Justificativa aceita! O prazo do cliente foi estendido.")
                                else:
                                    u.recusar_justificativa(j,cl)
                                    print ("Justificativa recusada! O cadastro do cliente foi bloqueado.")
                            else:
                                if y==5:
                                    c="".join(k for k in input("Qual o CPF do cliente? ") if k.isdigit())
                                    cl=sistema.buscar_cliente(c)
                                    if cl == None:
                                        print ("CPF não encontrado!")
                                        continue
                                    try:
                                        cod=int(input("Qual o código do pedido? "))
                                        s=int(input("Qual o novo status? \n 1 – em andamento \n 2 – finalizado \n 3 – cancelado \n"))
                                    except ValueError:
                                        print ("Erro: Você não digitou um número.")
                                        continue
                                    if s<1 or s>3:
                                        print ("Opção invalida!")
                                        continue
                                    teste= False
                                    for p in sistema.listar_pedidos(cl):
                                        if p.codigo == cod:
                                            teste= True
                                            p.alterar_status(["em andamento","finalizado","cancelado"][s-1])
                                            print ("Sucesso!")
                                            break
                                    if teste== False:
                                        print ("código não encontrado!")
                                else:
                                    if y==6:
                                        c="".join(k for k in input("Qual o CPF do cliente? ") if k.isdigit())
                                        cl=sistema.buscar_cliente(c)
                                        if cl == None:
                                            print ("CPF não encontrado!")
                                            continue
                                        try:
                                            cod=int(input("Qual o código do pedido? "))
                                            s=int(input("Qual o novo status do pagamento? \n 1 – pendente \n 2 – realizado \n 3 – atrasado \n"))
                                        except ValueError:
                                            print ("Erro: Você não digitou um número.")
                                            continue
                                        if s<1 or s>3:
                                            print ("Opção invalida!")
                                            continue
                                        teste= False
                                        for p in cl.pedidos:
                                            if p.codigo == cod:
                                                teste= True
                                                p.pagamento.alterar_status(["pendente","realizado","atrasado"][s-1])
                                                sistema.listar_pedidos(cl)
                                                print ("Sucesso!")
                                                break
                                        if teste== False:
                                            print ("código não encontrado!")
                                    else:
                                        if y==7:
                                            sistema.salvar()
                                            print ("dados salvos!")
                                        else:
                                            if y==0:
                                                break
                                            else:
                                                print ("Opção invalida!")
        else:
            sistema.listar_pedidos(u)
            if u.bloqueado:
                print ("Atenção: seu cadastro está bloqueado por atraso de pagamento.")
            while True:
                try:
                    y=int(input("Escolha uma opção: \n 1 – Ver meus dados \n 2 – Cadastrar cartão \n 3 – Ver meus pedidos e pagamentos \n 4 – Enviar justificativa de atraso \n 5 – Salvar dados \n 0 – Sair;"))
                except ValueError:
                    print ("Erro: Você não digitou um número.")
                    continue
                if y==1:
                    sistema.listar_pedidos(u)
                    print (u)
                else:
                    if y==2:
                        try:
                            tp=int(input("Qual o tipo do cartão? \n 1 – crédito \n 2 – débito \n"))
                        except ValueError:
                            print ("Erro: Você não digitou um número.")
                            continue
                        if tp!=1 and tp!=2:
                            print ("Opção invalida!")
                            continue
                        nc="".join(k for k in input("Qual o número do cartão? (16 dígitos) ") if k.isdigit())
                        va=input("Qual a validade do cartão? (mm/aa) ")
                        cv=input("Qual o código de segurança (CVV)? ")
                        tt=input("Qual o nome do titular? ")
                        cp="".join(k for k in input("Qual o CPF do titular? ") if k.isdigit())
                        if tp==1:
                            tipo="crédito"
                        else:
                            tipo="débito"
                        if sistema.cadastrar_cartao(u, Cartao(nc,va,cv,tt,cp,tipo)):
                            print ("Sucesso!")
                        else:
                            print ("Falha no cadastro do cartão! Confira os dados informados.")
                    else:
                        if y==3:
                            ped=sistema.listar_pedidos(u)
                            if len(ped)==0:
                                print ("lista vazia!")
                            else:
                                for w in ped:
                                    print (w)
                        else:
                            if y==4:
                                atr=[]
                                for p in sistema.listar_pedidos(u):
                                    if p.pagamento.dias_atraso() > 0:
                                        atr.append(p)
                                if len(atr)==0:
                                    print ("Você não possui pagamentos atrasados!")
                                    continue
                                for w in atr:
                                    print (w)
                                try:
                                    cod=int(input("Qual o código do pedido que deseja justificar? "))
                                except ValueError:
                                    print ("Erro: Você não digitou um número.")
                                    continue
                                teste= False
                                for w in atr:
                                    if w.codigo == cod:
                                        teste= True
                                        tx=input("Escreva sua justificativa: ")
                                        if sistema.enviar_justificativa(w.pagamento, tx):
                                            print ("Sucesso! Justificativa enviada ao administrador.")
                                        else:
                                            print ("Não foi possível enviar: texto vazio ou já existe uma justificativa para este pagamento.")
                                        break
                                if teste== False:
                                    print ("código não encontrado!")
                            else:
                                if y==5:
                                    sistema.salvar()
                                    print ("dados salvos!")
                                else:
                                    if y==0:
                                        break
                                    else:
                                        print ("Opção invalida!")
        sistema.usuario_logado = None
        sistema.salvar()
    else:
        if x==2:
            sistema.salvar()
            print ("dados salvos!")
        else:
            if x==3:
                sistema.carregar()
                print ("dados carregados")
            else:
                if x==0:
                    sistema.salvar()
                    print ("Até logo!")
                    break
                else:
                    print ("Opção invalida!")
