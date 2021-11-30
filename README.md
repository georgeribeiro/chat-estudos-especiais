# Chat para demonstração de criptografia da disciplina de Estudos Especiais - PPGGEC

O sistema deverá trabalhar usando sockets para comunicação e a interface de comunicação deverá
seguir uma ordem simples de AÇÂO + parametros, como representando uma função.

Por exemplo, para o cliente se autenticar no servidor, após ele se conectar ele deverá enviar uma mensagem
no seguinte formato:

AUTH username -- AUTH = ação de autenticação no servidor, USERNAME = nome do usuário autenticado

## Ações

As ações previstas no sistema são:

#### AUTH

```AUTH username```

- **AUTH**: ação de autenticar o usuário no sistema
- **username**: nome do usuário a ser autenticado

### HANDSHAKE

```HANDSHAKE username pubKey```

- **HANDSHAKE**: ação de trocar chaves entre os usuários
- **username**: nome do usuário ao qual a comunição é desejada
- **pubKey**: chave pública do usuário que está solicitando a ação

### SEND

```SEND username message```

- **SEND**: ação de enviar uma mensagem
- **username**: receptor da mensagem
- **message**: mensagem a ser enviada

### SIGN AND END

```SIGNSEND username message signature```
- **SIGNSEND**: enviar uma mensagem assinada
- **username**: repector da mensagem
- **message**: mensagem a ser enviada
- **signature**: assinatura da mensagem


## Retornos do server

### OK

```OK```

Uma ação que foi realizada com sucesso e não há outro retorno retornará OK ao cliente.

### ERROR

```ERROR message```

Uma ação que não foi realizada com sucesso retornará ERROR e a mensagem de erro ao cliente.
