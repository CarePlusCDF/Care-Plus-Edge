"""
1ESPA25 Sprint 3 — Care Plus BoostCare
======================================
Sistema de gamificação de saúde da Care Plus.
Permite cadastro/login de usuários, geração de missões personalizadas
baseadas em hábitos de saúde, resgate de benefícios por troféus,
recursos de saúde mental (Mind+) e integração com dispositivos (Connect+).

Autores:
    Felipe Menezes  | RM: 566607
    Gabriel Ardito  | RM: 568318
    João Sarracine  | RM: 567407
    João Gonzales   | RM: 568166

Arquivo de dados:
    users.txt — armazena usuários no formato:
    [id];[nome];[senha];[streak];[trofeus];[respostas]
"""

# ── Variável global ───────────────────────────────────────────────────────────
id_usuario = None
"""
int | None: ID do usuário autenticado na sessão atual.
Definido após login ou cadastro bem-sucedido.
Usado por funções que precisam identificar o usuário no arquivo users.txt.
"""

contador = 0
"""
int: Contador de missões concluídas na sessão atual.
Utilizado para controlar a atualização do streak do usuário.
O streak só é atualizado ao atingir 3 missões concluídas.
"""


# ── Funções ───────────────────────────────────────────────────────────────────

def boas_vindas() -> None:
    """
    Exibe a tela de boas-vindas com o nome do sistema em arte ASCII.

    Não recebe parâmetros e não retorna valores.
    Deve ser chamada no início da execução do programa.
    """
    print('Boa Vindas')
    print(r'''  ___   __   ____  ____    ____  __    _  _  ____       
 / __) / _\ (  _ \(  __)  (  _ \(  )  / )( \/ ___)      
( (__ /    \ )   / ) _)    ) __// (_/\) \/ (\___ \      
 \___)\_/\_/(__\_)(____)  (__)  \____/\____/(____/      ''')
    print()


def aceitar_lgpd() -> None:
    """
    Exibe os termos de consentimento da LGPD e solicita aceite do usuário.

    Apresenta um resumo dos dados coletados, finalidade do uso e direitos
    do usuário conforme a Lei Geral de Proteção de Dados (LGPD).

    Comportamento:
        - Se o usuário digitar 's': aceita os termos e continua.
        - Se o usuário digitar 'n': encerra o programa via exit().
        - Qualquer outra entrada: solicita novamente.

    Não recebe parâmetros e não retorna valores.
    """
    print('Termos de concentimento:')
    print('Na Care Plus levamos a sério o tratamento de\n'
          'dados dos nossos usuários, por isso elaboramos\n'
          'um resumo de tudo que será requisitado no\n'
          'recurso BoostCare')
    print()
    print('Como tratamos seus dados?')
    print("""Para personalizar missões, acompanhar seu progresso e liberar
    recompensas, precisamos acessar algumas informações de saúde.
    Tudo é tratado com segurança, transparência e apenas
    para fins de bem-estar.

    O que coletamos:
    - passos, distância e calorias
    - horas de sono
    - hidratação
    - BPM e dados do smartwatch
    - informações do scan diário (pele e sinais faciais)

    Para que usamos:
    - criar missões e desafios
    - liberar pontos, troféus e recompensas
    - gerar recomendações personalizadas
    - oferecer suporte no Mind+
    - melhorar sua experiência no app

    Você decide:
    - permitir dados de atividade
    - permitir dados de sono
    - permitir BPM/smartwatch
    - participar do ranking (opt-in)
    - receber notificações
    - revogar tudo a qualquer momento

    Seus dados não são vendidos e não aparecem para outros
    usuários — apenas seu desempenho dentro
    dos desafios.

    Botões — Gerencie seus dados e permissões:
    - Ver dados coletados
    - Editar consentimentos
    - Sair do ranking
    - Alterar / Excluir dados de saúde
    - Revogar consentimento

    Seus dados estão protegidos pela LGPD.
    """)
    while True:
        escolha: str = input("Deseja aceitar os termos de LGPD? S/N:").lower()
        match escolha:
            case "s":
                print('Obrigado por aceitar os termos de LGPD!')
                print()
                break
            case "n":
                print('Termos não aceitos!')
                print()
                exit()
            case _:
                print("Escolha uma opção váida!")
                print()
                continue


def pedir_login() -> None:
    """
    Apresenta o menu inicial de acesso e direciona o usuário para
    cadastro ou login conforme a escolha.

    Modifica a variável global `id_usuario` indiretamente via
    as funções `login()` e `entrar()`.

    Comportamento:
        - 'login': redireciona para cadastro de novo usuário.
        - 'entrar': redireciona para autenticação de usuário existente.
        - Qualquer outra entrada: solicita novamente.

    Não recebe parâmetros e não retorna valores.
    """
    print('Bem vindo a página de login da Care Plus')
    global id_usuario
    while True:
        escolha: str = input("Caso seja sua primeira vez digite 'login', caso ja tenha conta, digite 'entrar':").lower()
        match escolha:
            case "login":
                login()
                break
            case "entrar":
                id_usuario = entrar()
                break
            case _:
                print('Digite uma opção válida!')
                continue


def login() -> None:
    """
    Realiza o cadastro de um novo usuário no sistema.

    Coleta e valida os seguintes dados:
        - nome (str): apenas letras e espaços.
        - numeroCarteirinha (int): número inteiro identificador único.
        - senha (str): mínimo 8 caracteres com pelo menos um caractere especial.

    Após validação:
        - Chama `missoes_contextuais()` para coletar hábitos de saúde.
        - Persiste o novo usuário em users.txt no formato:
          [id];[nome];[senha];[streak];[trofeus];[respostas]

    Modifica a variável global `id_usuario` com o número da carteirinha.

    Variáveis locais:
        streak (str): iniciado em '0'.
        trofeus (str): iniciado em '0'.
        confirmarSenha (str): usada para confirmar a senha digitada.
        nome (str): nome do usuário.
        numeroCarteirinha (int): identificador do usuário.
        senha (str): senha escolhida pelo usuário.
        respostas (list): respostas das perguntas contextuais de saúde.

    Não recebe parâmetros e não retorna valores.
    """
    streak = '0'
    trofeus = '0'
    print()
    print('Login da Care Plus')
    confirmarSenha: str = ''
    while True:
        try:
            nome: str = input('Digite seu nome: ')
            if not nome.replace(" ", "").isalpha():
                raise ValueError
        except ValueError:
            print("O nome deve conter apenas letras!")
            continue
        break

    while True:
        try:
            numeroCarteirinha: int = int(input('Digite o número da carteirinha: '))
        except ValueError:
            print('O número de carteirinha deve conter apenas números!')
            continue
        break

    while True:
        try:
            senha: str = input('Digite sua senha:')
            if len(senha) < 8:
                print("A senha deve ter mais de 8 caracteres.")
                continue
            if senha.isalnum():
                print('A senha precisa ter pelo menos um caractere especial!')
                continue
        except ValueError:
            print('Erro inesperado!')
        break

    global id_usuario
    id_usuario = numeroCarteirinha

    while True:
        if senha != confirmarSenha:
            print('As senhas precisam ser identicas!')
            confirmarSenha = input('Digite a senha novamente:')
            continue
        else:
            print('Login realizado com sucesso!')
            respostas = missoes_contextuais()
            with open('users.txt', 'a', encoding='utf-8') as u:
                u.write(";".join([
                    str(numeroCarteirinha),
                    nome,
                    senha,
                    streak,
                    trofeus,
                    ",".join(map(str, respostas))
                ]) + "\n")
            break


def entrar() -> int | None:
    """
    Autentica um usuário existente no sistema.

    Solicita o número da carteirinha e a senha, valida o formato
    e busca no arquivo users.txt por correspondência.

    Validações aplicadas:
        - numeroCarteirinha deve ser inteiro.
        - senha deve ter mais de 8 caracteres.
        - senha deve conter ao menos um caractere especial.

    Comportamento em caso de falha:
        - Exibe mensagem de erro.
        - Oferece opção de criar conta ('criar') ou tentar novamente (Enter).

    Variáveis locais:
        numeroCarteirinha (int): identificador digitado pelo usuário.
        senha (str): senha digitada pelo usuário.
        encontrado (bool): controle interno de busca no arquivo.
        id_, nome, senha_salva, streak, trofeus, respostas (str):
            campos extraídos de cada linha do users.txt.

    Retorna:
        int: ID do usuário autenticado com sucesso.
        None: em caso de falha não recuperada (raramente atingido).
    """
    print('Para acessar sua conta digite:')

    while True:
        try:
            numeroCarteirinha = int(input('Número da carteirinha: '))
        except ValueError:
            print('O número de carteirinha deve conter apenas números!')
            continue

        senha = input('Digite sua senha: ')

        if len(senha) < 8:
            print("A senha deve ter mais de 8 caracteres.")
            continue

        if senha.isalnum():
            print('A senha precisa ter pelo menos um caractere especial!')
            continue

        encontrado = False

        with open("users.txt", "a+", encoding='utf-8') as f:
            f.seek(0)
            for linha in f:
                if linha.strip() == "":
                    continue
                id_, nome, senha_salva, streak, trofeus, respostas = linha.strip().split(";")
                if numeroCarteirinha == int(id_) and senha == senha_salva:
                    print(f"Bem-vindo, {nome}!")
                    return int(id_)

        print("Carteirinha ou senha incorretos!")
        opcao = input('Digite "criar" para criar conta ou Enter para tentar novamente: ').lower()

        if opcao == "criar":
            login()
            return id_usuario
        elif opcao == "":
            continue
        else:
            print("Opção inválida! Digite apenas 'criar' ou pressione Enter.")

    return None


def perguntar_numerico(pergunta: str) -> float:
    """
    Solicita ao usuário um valor numérico com validação de entrada.

    Repete a pergunta até que o usuário forneça um número válido.

    Parâmetros:
        pergunta (str): texto exibido ao usuário como prompt.

    Retorna:
        float: valor numérico fornecido pelo usuário.
    """
    while True:
        try:
            valor = float(input(pergunta))
            return valor
        except ValueError:
            print("Digite um número válido!")


def missoes_contextuais() -> list:
    """
    Coleta dados de hábitos de saúde do usuário por meio de perguntas numéricas.

    Utiliza `perguntar_numerico()` para garantir que todas as respostas
    sejam valores numéricos válidos.

    Perguntas realizadas (nesta ordem):
        0 - Dias de atividade física por semana
        1 - Minutos sentado por dia
        2 - Distância percorrida por dia (km)
        3 - Litros de água por dia
        4 - Horas de sono por noite
        5 - Horas de uso do celular por dia
        6 - Pausas durante o dia
        7 - Copos de cafeína por dia
        8 - Minutos ao ar livre por dia
        9 - Refeições por dia

    Variáveis locais:
        respostas (list): lista acumulada de respostas float.
        perguntas (list): lista de strings com os prompts de cada pergunta.

    Retorna:
        list: lista de floats com as 10 respostas na ordem das perguntas.
    """
    print('Agora responda algumas perguntas para melhorarmos sua experiência')
    respostas: list = []
    perguntas = [
        'Quantos dias por semana você pratica atividade física? ',
        'Quantos minutos você passa sentado por dia? ',
        'Qual a distância média que você percorre por dia (em km)? ',
        'Quantos litros de água você bebe por dia? ',
        'Quantas horas você dorme por noite? ',
        'Quantas horas por dia você passa no celular? ',
        'Quantas pausas você faz durante o dia? ',
        'Quantos copos de cafeína você consome por dia? ',
        'Quantos minutos por dia você passa ao ar livre? ',
        'Quantas refeições você faz por dia? '
    ]

    for p in perguntas:
        respostas.append(perguntar_numerico(p))
    return respostas


def definir_missoes(id_usuario: int) -> list:
    """
    Gera uma lista de missões personalizadas com base nas respostas
    de saúde armazenadas no perfil do usuário.

    Lê o arquivo users.txt, localiza o usuário pelo id_usuario e
    avalia cada hábito de saúde para atribuir uma missão adequada
    com pontuação em troféus.

    Critérios de missão por hábito:
        - Atividade física: baseado em dias/semana (0, <=2, >2)
        - Tempo sentado: baseado em minutos/dia (>600, >300, <=300)
        - Distância: baseado em km/dia (<1, <3, >=3)
        - Água: baseado em litros/dia (<1, <2, >=2)
        - Sono: baseado em horas/noite (<5, <7, >=7)
        - Celular: baseado em horas/dia (>8, >5, <=5)
        - Pausas: baseado em quantidade (0, <3, >=3)
        - Cafeína: baseado em copos/dia (>5, >2, <=2)
        - Ar livre: baseado em minutos/dia (<10, <30, >=30)
        - Refeições: baseado em quantidade (<3, <=4, >4)

    Parâmetros:
        id_usuario (int): ID do usuário autenticado.

    Variáveis locais:
        missoes (list): lista de strings no formato "descrição | X troféus".
        respostas (list): lista de floats com os hábitos do usuário.
        dias_atividade, tempo_sentado, distancia, agua, sono,
        celular, pausas, cafeina, ar_livre, refeicoes (float):
            valores extraídos das respostas do usuário.

    Retorna:
        list: lista de strings com as missões geradas, uma por hábito avaliado.
              Retorna lista vazia se o usuário não for encontrado.
    """
    missoes = []

    with open("users.txt", "r", encoding="utf-8", errors='ignore') as f:
        for linha in f:
            if linha.strip() == "":
                continue

            id_, nome, senha, streak, trofeus, respostas_str = linha.strip().split(";")

            if int(id_) != id_usuario:
                continue

            respostas = list(map(float, respostas_str.split(",")))

            dias_atividade = respostas[0]
            tempo_sentado  = respostas[1]
            distancia      = respostas[2]
            agua           = respostas[3]
            sono           = respostas[4]
            celular        = respostas[5]
            pausas         = respostas[6]
            cafeina        = respostas[7]
            ar_livre       = respostas[8]
            refeicoes      = respostas[9]

            if dias_atividade == 0:
                missoes.append("Comece com 1 dia de atividade física essa semana | 50 troféus")
            elif dias_atividade <= 2:
                missoes.append("Aumente para 3 dias de atividade física | 40 troféus")
            else:
                missoes.append("Mantenha sua rotina ativa e faça 1 atividade hoje | 30 troféus")

            if tempo_sentado > 600:
                missoes.append("Levante-se e caminhe por 5 minutos agora | 40 troféus")
            elif tempo_sentado > 300:
                missoes.append("Faça uma pausa para alongamento | 30 troféus")
            else:
                missoes.append("Ótimo! Continue se movimentando ao longo do dia | 20 troféus")

            if distancia < 1:
                missoes.append("Caminhe pelo menos 1 km hoje | 40 troféus")
            elif distancia < 3:
                missoes.append("Tente aumentar sua caminhada para 3 km | 30 troféus")
            else:
                missoes.append("Excelente! Continue com seu nível de movimento | 20 troféus")

            if agua < 1:
                missoes.append("Beba pelo menos 1 litro de água hoje | 40 troféus")
            elif agua < 2:
                missoes.append("Tente atingir 2 litros de água hoje | 30 troféus")
            else:
                missoes.append("Ótimo! Continue se hidratando bem | 20 troféus")

            if sono < 5:
                missoes.append("Durma pelo menos 6 horas hoje | 50 troféus")
            elif sono < 7:
                missoes.append("Tente melhorar seu sono para 7-8 horas | 40 troféus")
            else:
                missoes.append("Excelente! Continue com um bom descanso | 20 troféus")

            if celular > 8:
                missoes.append("Reduza 1 hora de uso do celular hoje | 50 troféus")
            elif celular > 5:
                missoes.append("Tente diminuir o tempo de tela | 40 troféus")
            else:
                missoes.append("Ótimo controle de tempo de tela! | 20 troféus")

            if pausas == 0:
                missoes.append("Faça pelo menos 2 pausas hoje | 40 troféus")
            elif pausas < 3:
                missoes.append("Aumente para 3 pausas ao longo do dia | 30 troféus")
            else:
                missoes.append("Ótimo! Continue fazendo pausas regulares | 20 troféus")

            if cafeina > 5:
                missoes.append("Reduza o consumo de cafeína hoje | 40 troféus")
            elif cafeina > 2:
                missoes.append("Tente diminuir um pouco a cafeína | 30 troféus")
            else:
                missoes.append("Bom controle no consumo de cafeína | 20 troféus")

            if ar_livre < 10:
                missoes.append("Passe pelo menos 10 minutos ao ar livre hoje | 40 troféus")
            elif ar_livre < 30:
                missoes.append("Tente ficar 30 minutos ao ar livre | 30 troféus")
            else:
                missoes.append("Ótimo! Continue aproveitando o tempo externo | 20 troféus")

            if refeicoes < 3:
                missoes.append("Faça pelo menos 3 refeições hoje | 40 troféus")
            elif refeicoes <= 4:
                missoes.append("Tente manter uma alimentação equilibrada | 30 troféus")
            else:
                missoes.append("Cuidado com excessos, mantenha equilíbrio | 20 troféus")

            break

    return missoes


def gerar_missoes(missoes: list) -> list:
    """
    Seleciona aleatoriamente um subconjunto de missões para o usuário.

    Combina 2 missões personalizadas (baseadas nos hábitos do usuário)
    com 1 missão genérica lida do arquivo missoesgenericas.txt.

    Parâmetros:
        missoes (list): lista completa de missões personalizadas geradas
                        por `definir_missoes()`.

    Variáveis locais:
        missoes_escolhidas (list): amostra aleatória das missões personalizadas.
        missoes_genericas (list): lista de missões lidas de missoesgenericas.txt.

    Retorna:
        list: lista com no máximo 3 missões (2 personalizadas + 1 genérica).
    """
    import random

    missoes_escolhidas = random.sample(missoes, min(2, len(missoes)))

    with open('missoesgenericas.txt', 'r', encoding='utf-8') as m:
        missoes_genericas = [linha.strip() for linha in m.readlines()]

    missoes_escolhidas += random.sample(missoes_genericas, 1)

    return missoes_escolhidas


def mostrar_missoes(missoes_escolhidas: list, contador: int, id_usuario: int,
                    trofeus_usuario: int, todas_missoes: list) -> tuple:
    """
    Exibe as missões ativas do usuário e processa a conclusão de uma missão.

    Se não houver missões ativas, oferece opção de gerar novas.
    Ao concluir uma missão, remove-a da lista, atualiza os troféus
    no arquivo e incrementa o contador de missões concluídas.

    Parâmetros:
        missoes_escolhidas (list): lista de missões atualmente ativas.
        contador (int): número de missões concluídas na sessão.
        id_usuario (int): ID do usuário autenticado.
        trofeus_usuario (int): quantidade atual de troféus do usuário.
        todas_missoes (list): pool completo de missões para gerar novas se necessário.

    Variáveis locais:
        escolha (int): número da missão selecionada pelo usuário.
        removida (str): string da missão concluída.
        trofeus_ganhos (int): troféus extraídos da string da missão concluída.

    Retorna:
        tuple: (contador, trofeus_usuario, missoes_escolhidas)
            - contador (int): atualizado se missão foi concluída.
            - trofeus_usuario (int): atualizado com troféus ganhos.
            - missoes_escolhidas (list): lista atualizada sem a missão concluída.
    """
    if len(missoes_escolhidas) == 0:
        print("\nVocê não possui mais missões ativas.")
        escolha = input("Deseja gerar novas missões? (s/n): ").lower()
        if escolha == "s":
            missoes_escolhidas = gerar_missoes(todas_missoes)
            contador = 0
        else:
            return contador, trofeus_usuario, missoes_escolhidas

    print("\n" + "=" * 40)
    print("        MISSÕES ATIVAS")
    print("=" * 40)

    for i, m in enumerate(missoes_escolhidas, 1):
        print(f"{i} - {m}")

    print("=" * 40)

    try:
        escolha = int(input('Digite o número da missão que você realizou (0 para nenhuma): '))
    except ValueError:
        print("Entrada inválida!")
        return contador, trofeus_usuario, missoes_escolhidas

    if escolha == 0:
        return contador, trofeus_usuario, missoes_escolhidas

    if 1 <= escolha <= len(missoes_escolhidas):
        removida = missoes_escolhidas.pop(escolha - 1)
        trofeus_ganhos = int(removida.split("|")[1].split()[0])
        print(f"Missão concluída: {removida}")
        print(f"Você ganhou {trofeus_ganhos} troféus!")
        atualizar_trofeus_arquivo(id_usuario, trofeus_ganhos)
        trofeus_usuario = pegar_trofeus(id_usuario)
        contador += 1
    else:
        print("Número inválido!")

    return contador, trofeus_usuario, missoes_escolhidas


def menu(missoes_escolhidas: list, contador: int, id_usuario: int, trofeus_usuario: int) -> None:
    """
    Exibe o menu principal do sistema e gerencia a navegação entre módulos.

    Loop principal do programa após autenticação. Permanece ativo até
    o usuário escolher sair (opção '0').

    Opções disponíveis:
        1 - Missões Ativas   → `mostrar_missoes()`
        2 - Benefícios       → `beneficios_menu()`
        3 - Mind+            → `mind_plus()`
        4 - Seu Streak       → `atualizar_streak_arquivo()`
        5 - Connect+         → `connect_plus()`
        6 - Notícias         → `noticias()`
        7 - Meu Perfil       → `perfil()`
        0 - Sair

    Parâmetros:
        missoes_escolhidas (list): missões ativas do usuário na sessão.
        contador (int): número de missões concluídas na sessão.
        id_usuario (int): ID do usuário autenticado.
        trofeus_usuario (int): quantidade atual de troféus do usuário.

    Não retorna valores.
    """
    while True:
        print("\n" + "=" * 40)
        print("        CARE PLUS - MENU")
        print("=" * 40)
        print("1 - Missões Ativas")
        print("2 - Benefícios")
        print("3 - Mind+")
        print("4 - Seu Streak")
        print("5 - Conect+")
        print("6 - Notícias")
        print("7 - Meu Perfil")
        print("0 - Sair")
        print("=" * 40)

        escolha = input("Escolha uma opção: ")

        match escolha:
            case "1":
                contador, trofeus_usuario, missoes_escolhidas = mostrar_missoes(
                    missoes_escolhidas,
                    contador,
                    id_usuario,
                    trofeus_usuario,
                    missoes
                )
            case "2":
                print("\nAcessando Benefícios...\n")
                trofeus_usuario = beneficios_menu(trofeus_usuario)
            case "3":
                print("\nAcessando Mind+...\n")
                mind_plus()
            case "4":
                print("\nAcessando Seu Streak...\n")
                atualizar_streak_arquivo(id_usuario, contador)
            case "5":
                print("\nAcessando Conect+...\n")
                connect_plus()
            case "6":
                print("\nAcessando Notícias...\n")
                noticias()
            case "7":
                print("\nAcessando Meu Perfil...\n")
                perfil(id_usuario)
            case "0":
                print("\nEncerrando... Até mais!")
                break
            case _:
                print("\n Opção inválida! Tente novamente.\n")


def atualizar_streak_arquivo(id_usuario: int, contador: int) -> None:
    """
    Atualiza o streak do usuário no arquivo users.txt se ele completou
    pelo menos 3 missões na sessão atual.

    Lê todas as linhas do arquivo, localiza o usuário pelo id_usuario,
    incrementa o campo streak em 1 e reescreve o arquivo inteiro.

    Parâmetros:
        id_usuario (int): ID do usuário autenticado.
        contador (int): número de missões concluídas na sessão atual.

    Variáveis locais:
        linhas (list): lista de todas as linhas do arquivo processadas.
        id_, nome, senha, streak, trofeus, respostas (str):
            campos extraídos de cada linha do arquivo.
        nova_linha (str): linha reconstruída após atualização do streak.

    Não retorna valores.
    Condição de guarda: encerra sem modificar o arquivo se contador < 3.
    """
    if contador < 3:
        print("Você ainda não completou 3 missões.")
        return

    linhas = []

    with open("users.txt", "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip() == "":
                continue
            partes = linha.strip().split(";")
            id_, nome, senha, streak, trofeus, respostas = partes
            if int(id_) == id_usuario:
                streak = str(int(streak) + 1)
                print(f"Streak atualizado! Novo streak: {streak}")
            nova_linha = ";".join([id_, nome, senha, streak, trofeus, respostas])
            linhas.append(nova_linha)

    with open("users.txt", "w", encoding="utf-8") as f:
        for l in linhas:
            f.write(l + "\n")


def atualizar_trofeus_arquivo(id_usuario: int, trofeus_ganhos: int) -> None:
    """
    Adiciona troféus ao saldo do usuário no arquivo users.txt.

    Lê todas as linhas, localiza o usuário pelo id_usuario,
    soma os troféus ganhos ao total atual e reescreve o arquivo.

    Parâmetros:
        id_usuario (int): ID do usuário autenticado.
        trofeus_ganhos (int): quantidade de troféus a adicionar.

    Variáveis locais:
        linhas (list): lista de linhas processadas para reescrita.
        id_, nome, senha, streak, trofeus, respostas (str):
            campos extraídos de cada linha do arquivo.
        novo_total (int): saldo de troféus após adição.
        nova_linha (str): linha reconstruída com o novo total.

    Não retorna valores.
    """
    linhas = []

    with open("users.txt", "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip() == "":
                continue
            id_, nome, senha, streak, trofeus, respostas = linha.strip().split(";")
            if int(id_) == id_usuario:
                novo_total = int(trofeus) + trofeus_ganhos
                trofeus = str(novo_total)
                print(f"Total de troféus agora: {trofeus}")
            nova_linha = ";".join([id_, nome, senha, streak, trofeus, respostas])
            linhas.append(nova_linha)

    with open("users.txt", "w", encoding="utf-8") as f:
        for l in linhas:
            f.write(l + "\n")


def remover_trofeus_arquivo(id_usuario: int, trofeus_gastos: int) -> None:
    """
    Subtrai troféus do saldo do usuário no arquivo users.txt.

    Lê todas as linhas, localiza o usuário pelo id_usuario,
    subtrai os troféus gastos do total atual e reescreve o arquivo.

    Parâmetros:
        id_usuario (int): ID do usuário autenticado.
        trofeus_gastos (int): quantidade de troféus a subtrair.

    Variáveis locais:
        linhas (list): lista de linhas processadas para reescrita.
        id_, nome, senha, streak, trofeus, respostas (str):
            campos extraídos de cada linha do arquivo.
        novo_total (int): saldo de troféus após subtração.
        nova_linha (str): linha reconstruída com o novo total.

    Não retorna valores.
    """
    linhas = []

    with open("users.txt", "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip() == "":
                continue
            id_, nome, senha, streak, trofeus, respostas = linha.strip().split(";")
            if int(id_) == id_usuario:
                novo_total = int(trofeus) - trofeus_gastos
                trofeus = str(novo_total)
            nova_linha = ";".join([id_, nome, senha, streak, trofeus, respostas])
            linhas.append(nova_linha)

    with open("users.txt", "w", encoding="utf-8") as f:
        for l in linhas:
            f.write(l + "\n")


def pegar_trofeus(id_usuario: int) -> int:
    """
    Lê o saldo atual de troféus do usuário no arquivo users.txt.

    Parâmetros:
        id_usuario (int): ID do usuário autenticado.

    Variáveis locais:
        id_, nome, senha, streak, trofeus, respostas (str):
            campos extraídos de cada linha do arquivo.

    Retorna:
        int: quantidade de troféus do usuário.
             Retorna 0 se o usuário não for encontrado.
    """
    with open("users.txt", "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip() == "":
                continue
            id_, nome, senha, streak, trofeus, respostas = linha.strip().split(";")
            if int(id_) == id_usuario:
                return int(trofeus)
    return 0


def perfil(id_usuario: int) -> int | None:
    """
    Exibe os dados do perfil do usuário autenticado.

    Lê o arquivo users.txt e imprime nome, carteirinha, senha,
    streak e troféus do usuário identificado por id_usuario.

    Parâmetros:
        id_usuario (int): ID do usuário autenticado.

    Variáveis locais:
        id_, nome, senha, streak, trofeus, respostas (str):
            campos extraídos de cada linha do arquivo.

    Retorna:
        int: quantidade de troféus do usuário encontrado.
        None: se o usuário não for encontrado no arquivo.
    """
    with open("users.txt", "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip() == "":
                continue
            id_, nome, senha, streak, trofeus, respostas = linha.strip().split(";")
            if int(id_) == id_usuario:
                print("\n" + "=" * 40)
                print("          MEU PERFIL")
                print("=" * 40)
                print(f"Nome: {nome}")
                print(f"Carteirinha: {id_}")
                print(f"Senha: {senha}")
                print(f"Streak: {streak} dias")
                print(f"Troféus: {trofeus}")
                print("=" * 40)
                return int(trofeus)


def beneficios_menu(trofeus_usuario: int) -> int:
    """
    Exibe o catálogo de benefícios e permite ao usuário resgatar
    itens usando seus troféus acumulados.

    Cada benefício tem um custo em troféus extraído da própria string
    no formato "descrição | X troféus". Ao resgatar, o benefício é
    removido da lista da sessão e os troféus são descontados no arquivo.

    Parâmetros:
        trofeus_usuario (int): saldo atual de troféus do usuário.

    Variáveis locais:
        beneficios (list): lista de strings com descrição e custo de cada benefício.
        escolha (int): índice do benefício selecionado.
        beneficio (str): string do benefício selecionado.
        custo (int): custo em troféus extraído da string do benefício.
        removido (str): string do benefício resgatado e removido da lista.

    Retorna:
        int: saldo de troféus atualizado após resgates da sessão.
    """
    beneficios = [
        "Desconto de 20% em corridas da Uber | 300 troféus",
        "1 mês grátis de Spotify Premium | 400 troféus",
        "Barrinha de proteína da Growth Supplements | 150 troféus",
        "Desconto de 30% em consulta na Dr. Consulta | 500 troféus",
        "Cupom de R$20 no iFood | 350 troféus",
        "Shake proteico da Max Titanium | 200 troféus",
        "Desconto de 25% em academia Smart Fit | 600 troféus",
        "Garrafa térmica esportiva | 250 troféus",
        "Desconto de R$15 em corrida 99 | 300 troféus",
        "Plano mensal da Headspace (meditação) | 450 troféus",
        "Kit de snacks saudáveis (barra + nuts) | 300 troféus",
        "Desconto de 20% na Decathlon | 400 troféus",
        "Fone esportivo Bluetooth | 700 troféus",
        "Voucher de R$30 em farmácia Drogasil | 500 troféus",
        "Desconto de 25% em massagem relaxante | 600 troféus",
        "Suplemento multivitamínico (1 mês) | 350 troféus",
        "Desconto de 20% em nutricionista | 550 troféus",
        "Camiseta esportiva dry-fit | 450 troféus",
        "Voucher de R$25 na Amazon | 600 troféus",
        "Plano básico do Gympass (1 semana) | 700 troféus"
    ]

    while True:
        print("\n" + "=" * 40)
        print("          BENEFÍCIOS")
        print("=" * 40)
        print(f"Seus troféus: {trofeus_usuario}")
        print("-" * 40)

        for i, b in enumerate(beneficios, 1):
            print(f"{i} - {b}")

        print("=" * 40)
        print("0 - Voltar")

        try:
            escolha = int(input("Escolha um benefício para resgatar: "))
        except ValueError:
            print("Entrada inválida!")
            continue

        if escolha == 0:
            break

        if 1 <= escolha <= len(beneficios):
            beneficio = beneficios[escolha - 1]
            custo = int(beneficio.split("|")[1].split()[0])

            if trofeus_usuario >= custo:
                trofeus_usuario -= custo
                remover_trofeus_arquivo(id_usuario, custo)
                removido = beneficios.pop(escolha - 1)
                print("\nBenefício resgatado com sucesso!")
                print(removido)
                print(f"Troféus restantes: {trofeus_usuario}")
            else:
                print("\nTroféus insuficientes!")
        else:
            print("Opção inválida!")

    return trofeus_usuario


def mind_plus() -> None:
    """
    Exibe o módulo de saúde mental Mind+ com recursos de apoio psicológico.

    Apresenta um menu com as seguintes opções:
        1 - Quando procurar um psicólogo (sinais de alerta)
        2 - Crise de ansiedade (técnica 5-4-3-2-1)
        3 - Não está se sentindo bem (CVV — linha 188)
        4 - Reduzir tensão (método de respiração 4-4-6)
        5 - Pronto atendimento
        0 - Voltar

    Permanece em loop até o usuário escolher voltar (opção '0').

    Não recebe parâmetros e não retorna valores.
    """
    print("\n" + "=" * 40)
    print("           MIND+")
    print("=" * 40)
    print("Pedir ajuda não é sinal de fraqueza,")
    print("é a coragem de escolher cuidar de si.")
    print("=" * 40)

    while True:
        print()
        print('1. Quando procurar um psicólogo?')
        print('   Atento a sinais de alteração da saúde mental')
        print()
        print('2. Crise de ansiedade?')
        print('   Técnica 5-4-3-2-1')
        print()
        print('3. Não está se sentindo bem?')
        print('   Centro de Valorização da Vida')
        print()
        print('4. Reduzir tensão?')
        print('   Método simples de relaxamento')
        print()
        print('5. Pronto atendimento')
        print()
        print('0. Voltar')

        escolha = input('Digite o número da opção: ')

        match escolha:
            case "1":
                print("\nQuando procurar um psicólogo:")
                print("- Quando você sente tristeza constante ou desânimo")
                print("- Dificuldade para lidar com emoções")
                print("- Ansiedade frequente ou crises")
                print("- Problemas de sono ou concentração")
                print("- Sensação de estar sobrecarregado")
                print("Procurar ajuda é um passo importante para o bem-estar.\n")

            case "2":
                print("\nTécnica 5-4-3-2-1 para ansiedade:")
                print("Observe ao seu redor e identifique:")
                print("5 coisas que você pode ver")
                print("4 coisas que pode tocar")
                print("3 coisas que pode ouvir")
                print("2 coisas que pode cheirar")
                print("1 coisa que pode saborear")
                print("Isso ajuda a trazer sua atenção para o presente.\n")

            case "3":
                print("\nCentro de Valorização da Vida (CVV):")
                print("Você pode ligar gratuitamente para o número 188")
                print("Atendimento 24 horas por dia, todos os dias")
                print("Também disponível via chat no site oficial")
                print("Você não está sozinho.\n")

            case "4":
                print("\nMétodo de 2 minutos para reduzir tensão:")
                print("1. Pare o que estiver fazendo")
                print("2. Inspire profundamente pelo nariz por 4 segundos")
                print("3. Segure o ar por 4 segundos")
                print("4. Solte lentamente pela boca por 6 segundos")
                print("5. Repita por 2 minutos")
                print("Isso ajuda a desacelerar o corpo e a mente.\n")

            case "5":
                print("\nPronto atendimento:")
                print("Sua solicitação foi registrada.")
                print("Você será contatado em breve por um profissional.\n")

            case "0":
                break

            case _:
                print('Digite um número válido')


def connect_plus() -> None:
    """
    Exibe o menu do módulo Connect+ de integração com dispositivos inteligentes.

    Apresenta informações sobre dispositivos compatíveis (smartwatch,
    pulseiras fitness, aplicativos de saúde) e dados sincronizáveis
    (passos, batimentos, sono).

    Não recebe parâmetros e não retorna valores.
    """
    print("\n" + "=" * 40)
    print("          CONNECT+")
    print("=" * 40)
    print("Integre seu dispositivo inteligente")
    print("e acompanhe seus dados em tempo real.")
    print("-" * 40)
    print("Dispositivos compatíveis:")
    print("- Smartwatch")
    print("- Pulseiras fitness")
    print("- Aplicativos de saúde")
    print("-" * 40)
    print("Sincronize passos, batimentos, sono")
    print("e outras informações automaticamente.")
    print("=" * 40)


def noticias() -> None:
    """
    Exibe um boletim de notícias sobre saúde e bem-estar.

    Apresenta 3 notícias fixas relacionadas a saúde mental,
    uso de smartwatches e hábitos saudáveis.

    Não recebe parâmetros e não retorna valores.
    """
    print("\n" + "=" * 40)
    print("            NOTÍCIAS")
    print("=" * 40)

    print("1. Saúde mental ganha destaque em 2026")
    print("Cresce a busca por apoio psicológico e bem-estar emocional.")
    print("-" * 40)

    print("2. Uso de smartwatches aumenta no Brasil")
    print("Dispositivos ajudam no monitoramento de saúde diária.")
    print("-" * 40)

    print("3. Pequenos hábitos melhoram qualidade de vida")
    print("Especialistas reforçam a importância de rotina saudável.")
    print("-" * 40)

    print("Fique atento às novidades e cuide da sua saúde.")
    print("=" * 40)


# ── Execução principal ────────────────────────────────────────────────────────
boas_vindas()
aceitar_lgpd()
pedir_login()

trofeus_usuario = pegar_trofeus(id_usuario)
missoes = definir_missoes(id_usuario)
missoes_escolhidas = gerar_missoes(missoes)

menu(missoes_escolhidas, contador, id_usuario, trofeus_usuario)
