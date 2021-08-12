# sala_conversa_virtual

Trabalho da disciplina de 'Redes de Computadores 2'

<!-- TOC -->

- [sala_conversa_virtual](#sala_conversa_virtual)
    - [Objetivo](#objetivo)
    - [Informações](#informa%C3%A7%C3%B5es)
        - [Feito com](#feito-com)
        - [Requerimentos](#requerimentos)
            - [**Linux**](#linux)
            - [**Python3.8**](#python38)
        - [Execução](#execu%C3%A7%C3%A3o)
    - [Implementação da primeira parte do trabalho](#implementa%C3%A7%C3%A3o-da-primeira-parte-do-trabalho)
        - [___Interface servidor___](#___interface-servidor___)
        - [___Servidor___](#___servidor___)
        - [___Mensagens da aplicação___](#___mensagens-da-aplica%C3%A7%C3%A3o___)
        - [___Transmissao___](#___transmissao___)
        - [___Interface cliente___](#___interface-cliente___)
        - [___Cliente___](#___cliente___)
    - [Atualizações futuras](#atualiza%C3%A7%C3%B5es-futuras)
    - [Links](#links)
    - [Autores](#autores)

<!-- /TOC -->

---

## Objetivo

- Desenvolver uma aplicação que simula uma sala virtual de conversa, onde os diferentes usuários registrados podem realizar ligações de voz entre eles. Qualquer usuário registrado pode ligar para outro usuário registrado, permitindo somente conversação entre dois usuários. Para isso, a aplicação deve ter um módulo servidor de registros que contém uma tabela atualizada com todos os usuários registrados.
- Desenvolver uma aplicação baseado no paradigma cliente-servidor e utilizando socket de rede.
- A identificação do servidor de registro (endereço IP) deverá ser informada ao módulo cliente pelo usuário da aplicação.
- O servidor de registros deve usar a porta 5000 para a comunicação com os clientes.
- A troca de mensagens deve ser feita utilizando o protocolo TCP.
- O servidor deve imprimir na tela a lista de usuários registrados, sempre que adicione um novo usuário.
- Os módulos cliente e servidor devem imprimir na tela todas as mensagens enviadas e recebidas.
- A aplicação deve ter uma interface gráfica, mesmo sendo simples, seja intuitiva e satisfaça as funcionalidades da aplicação.

## Informações

### Feito com

- Python3.8
- tkinter

### Requerimentos

#### **Linux**

- pacote python3-pil
- pacote python3-pil.imagetk
- pacote python-imaging

Para instalar esses pacotes digite no terminal:

> `sudo apt-get install python3-pil python3-pil.imagetk python-imaging`

#### **Python3.8**

- Pillow

> Caso não queira instalar os requerimentos python desse projeto em todo o sistema, primeiramente crie e ative um ambiente virtual python, instale os requerimentos python e execute os scripts do projeto com o ambiente visual ativado.
>
> Para criar um ambiente abra a pasta do projeto no terminal e digite:
>
> `python3.8 -m venv .venv`
>
> Para ativar o ambiente virtual:
>
> `source .venv/bin/activate`
>
> Caso queira desativar o ambiente vitual:
>
> `deactivate`

Para instalar os requerimentos do Python digite:

> `python3.8 -m pip install -r ./requirements_python.txt`

### Execução

1. Abra a pasta do projeto no terminal;

2. Para executar o script do servidor, digite:

    > `python3.8 mainServidor.py`

3. Para executar o script do cliente, digite:

    > `python3.8 mainServidor.py`

---

## Implementação da primeira parte do trabalho

### ___Interface servidor___

![Interface do servidor da aplicação](./readme_files/interfaceServidor.png)

A interface do servidor apresenta o endereço e a porta onde o servidor está sendo executado, dois botões, e uma área destinada aos logs feitos pelo servidor.

O primeiro botão ('Abrir Servidor') faz com que o servidor comece a aceitar por novas conexões, já o segundo botão ('Fechar servidor') faz com que ele pare de aceitar novas conexões, mas esse segundo botão não força que as conexões sendo processadas sejam interrompidas.

A área destinada aos logs é atualizada periodicamente (uma vez a cada 300ms) para exibir algumas das informações que o servidor processa, especificamente, as mensagens enviadas e recebidas pelo servidor e também a tabela de usuários registrados no servidor.

Ao fechar a interface do servidor, ele parará de ouvir por novas conexões e esperará que todas as conexões terminem.

> Obs.: A interface od servidor se encontra no módulo mainServidor em `./` (raiz do projeto)

### ___Servidor___

No momento em que o servidor é instanciado, um objeto do tipo socket também é instanciado, configurado como TCP, configurado como um socket não bloqueante, e é realizado o bind com o endereço localhost e a porta 5000. O motivo do socket não ser bloqueante é para que o servidor possa ser capaz de verificar se deve para de aceitar novas conexões, pois no caso de um socket bloqueante o método accept() faria com que o programa ficasse parado esperando que uma conexão fosse realizada.

Quando o servidor passa a aceitar conexões, uma nova thread é iniciada liberando assim a thread principal para a realização de outras tarefas, a thread criada fica responsável por receber as novas conexões e por verificar se deve para de aceitar novas conexões. Ao receber uma nova conexão, mais outra thread é criada para tratar dessa conexão, liberando a thread anterior do servidor para aceitar outras conexões.

O servidor contém métodos para registrar um usuário na tabela, consultar se um certo usuário esta cadastrado, descadastrar um usuário da tabela. O método para registrar um usuário armazena um nome, um ip e um numero de porta internamente na tabela (na realidade a tabela é um dicionário python), o método de consulta retorna toda a linha correspondente a um nome e o método que descadastra percorre os valores do dicionario buscando o endereço ip e porta que pediu o descadastramento e remove a entrada associada ao endereço e porta.

Além dos métodos referentes ao uso da aplicação, o servidor define métodos para receber um pedido, para processar um pedido de registro, processar um pedido de consulta e também um pedido de encerramento.

O método para recebimento de um pedido/mensagem terceiriza o trabalho para uma outra função (que faz parte do módulo mensagens_aplicacao, essa função sim, sabe como receber mensagens da aplicação), faz o log da mensagem recebida e também retorna a mensagem para que ela seja usado pelos outros métodos do servidor.

O método para processar um registro aceita o nome que o usuário enviou através do cliente e tenta cadastrá-lo, dependendo do resultado do cadastro o servidor responde positivamente ou não ao cliente (a reposta é feita através de uma função do módulo mensagens_aplicacao) e faz o log da mensagem de resposta.

O método para processar uma consulta e de encerramento funciona de maneira análoga ao método para processar um registro (tentando consultar, respondendo de acordo com resultado da consulta e realizando o log da mensagem de resposta transmitida).

O método para processar um encerramento simplesmente tenta descadastrar um usuário da tabela do servidor.

![Estados do processamento da conexão](./readme_files/processamentoConexao.png)

Todo esse o tratamento do processamentos requisitados pelas conexões dos clientes é feita por um 'processador' de conexões (uma máquina de estados) chamar que transiciona os estados de forma a atender à mensagem/ao pedido de cada conexão.

Além do que já foi mencionado, pelo fato do servidor poder trabalhar com várias threads, foi feito o uso de mutexes para algumas propriedades do servidor, entre elas a tabela de usuários registrados no servidor.

> Obs.: Esse módulo se encontra em `./src/cliente_servidor/`

### ___Mensagens da aplicação___

Mensagens Aplicacao é o módulo responsável por manipular e padronizar as transmissões e os recebimentos de todas as mensagens da aplicação, seja o envio de pedidos, seja o envio de respostas ou seja o recebimento de pedidos e respostas.

Esse módulo também define uma enumeração com todas as possíveis mensagens que a aplicação manipula, que atualmente são: pedido de registro, registro efetuado com exito, registro falhou, pedido de consulta, consulta efetuada com exito, consulta falhou e pedido de encerramento.

> Obs.: Esse módulo se encontra em `./src/aplicacao/`

### ___Transmissao___

Transmissao é o módulo responsável por transmitir e receber bytes.
A biblioteca de sockets requer que a aplicação faça o controle de se todos os bytes foram enviados e recebidos através do socket. Para o controle do recebimento (isso é, saber quando todos os bytes de uma transmissão foram recebidos) o esse módulo implementa o caractere stuffing para fazer a delimitação do início e o fim de uma transmissão.

> Obs.: Esse módulo se encontra em `./src/util/`

### ___Interface cliente___

![Primeira tela da interface do Cliente](./readme_files/interfaceCliente_tela1.png)
![Segunda tela da interface do Cliente](./readme_files/interfaceCliente_tela2.png)

A interface do cliente tem duas telas, onde a primeira tela tem por objetivo adquirir o nome de usuário que será registrado, adquirir o endereço Ip do servidor da aplicação, apresentar um botão para que o usuário interaja iniciando assim a tentativa de conexão e logo em sequência a tentativa de registro do nome de usuário na tabela do servidor, nessa tela também podem ser são apresentados algumas mensagens de alerta notificando ao usuário caso ele não tenha e fornecido um nome de usuário, ou caso o servidor não esteja aceitando conexões.

A segunda tela da interface do cliente dá opção para que o usuário envie uma requisição de consulta de ao endereço ip e porta associados a um nome na tabela de usuários registrados no servidor da aplicação; nessa tela há uma área destinada a visualização das mensagens enviadas e recebidas na conexão e por último há um ocal para que seja possível realizar uma ligação a um usuário registrado no servidor (_essa funcionalidade deverá ser implementada na segunda parte do trabalho_)

> Obs.: O código da interface do cliente está dividida em dois módulos, mainCliente em `./` (raiz do projeto) e tela_inicial que se encontra em `./src/interface/`

### ___Cliente___

O cliente é uma classe simples que implementa métodos para abrir a conexaõ com o servidor, métodos que fazem um pedido ao servidor e que retornam a resposta ao pedido; esses métodos que fazem um pedido e esperam um retorno são métodos que embrulham funções do módulo mensagens_aplicacao.

Ainda sobre os métodos do cliente, a função de um dos métodos do cliente é fazer o pedido de registro de um certo nome, recebendo a resposta desse pedido (se ele foi bem-sucedido ou não) e retorna a mensagem enviada assim como também a mensagem recebida (esse retorno é para possibilitar a realização do log das mensagens transmitidas), outro método do cliente, de maneira análoga ao anterior, tem por função realizar o pedido de consulta a um nome, um terceiro método do cliente faz um pedido de encerramento e retorna a mensagem enviada ao servidor.

> Obs.: Esse módulo se encontra em `./src/cliente_servidor/`

---

## Atualizações futuras

- [ ] Permitir que usuários conectados façam ligações de voz

## Links

- [Repositório](https://github.com/gborba-uff-cc/sala_virtual_conversa)

## Autores

- [@gborba-uff-cc](https://github.com/gborba-uff-cc)

- [@JorgeStief](https://github.com/JorgeStief)
