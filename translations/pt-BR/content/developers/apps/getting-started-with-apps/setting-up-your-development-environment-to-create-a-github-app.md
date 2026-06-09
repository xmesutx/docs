---
title: Configurar seu ambiente de desenvolvimento para criar um aplicativo GitHub
intro: 'Aprenda os princípios básicos para estender e criar um novo {% data variables.product.prodname_github_apps %}.'
redirect_from:
  - /apps/quickstart-guides/setting-up-your-development-environment
  - /developers/apps/setting-up-your-development-environment-to-create-a-github-app
versions:
  fpt: '*'
  ghes: '*'
  ghae: '*'
  ghec: '*'
topics:
  - GitHub Apps
shortTitle: Ambiente de desenvolvimento
---

## Introdução

Este guia irá analisar os passos necessários para configurar um aplicativo GitHub e executá-lo em um servidor. Os aplicativos GitHub exigem algumas etapas de configuração para gerenciar eventos do webhook e conectar o registro do aplicativo no GitHub ao seu código. O aplicativo neste guia serve como base que você pode usar para estender e criar novos aplicativos no GitHub.

Ao final deste guia, você aprenderá a registrar um aplicativo GitHub e configurar um servidor web para receber eventos de webhook. Você aprenderá a usar uma ferramenta denominada Smee para capturar cargas do webhook e encaminhá-las para seu ambiente de desenvolvimento local. O aplicativo do modelo você irá configurar nesta seção não fará nada especial nesse momento, mas servirá como uma estrutura que você pode usar para começar a escrever o código do aplicativo usando a API ou concluindo outros [guias de início rápido](/apps/quickstart-guides/). {% ifversion fpt or ghec %}Você pode conferir exemplos bem-sucedidos de aplicativos no [GitHub Marketplace](https://github.com/marketplace) e em [Trabalhos com GitHub](https://github.com/works-with).{% endif %}

Após concluir este projeto, você entenderá como efetuar a autenticação como um aplicativo GitHub e uma instalação, bem como e como esses métodos de autenticação são diferentes.

Aqui estão as etapas que você vai seguir para configurar o modelo do aplicativo GitHub:

1. [Inicie um novo canal da Smee](#step-1-start-a-new-smee-channel)
1. [Cadastre um novo aplicativo GitHub](#step-2-register-a-new-github-app)
1. [Salve sua chave privada e o ID do aplicativo](#step-3-save-your-private-key-and-app-id)
1. [Prepare o ambiente do tempo de execução](#step-4-prepare-the-runtime-environment)
1. [Revise o código do modelo do aplicativo GitHub](#step-5-review-the-github-app-template-code)
1. [Inicie servidor](#step-6-start-the-server)
1. [Instale o aplicativo em sua conta](#step-7-install-the-app-on-your-account)

{% data reusables.apps.app-ruby-guides %}

## Pré-requisitos

Você pode achar útil ter um entendimento básico do seguinte:

* [Aplicativos do GitHub](/apps/about-apps)
* [Webhooks](/webhooks)
* [Linguagem de programação Ruby](https://www.ruby-lang.org/en/)
* [APIs REST](/rest)
* [Sinatra](http://sinatrarb.com/)

Mas é possível acompanhar o processo em qualquer nível de experiência. Nós vamos nos conectar a informações de que você precisa ao longo do caminho!

Antes de começar, você precisa clonar o repositório com o código do modelo usado neste início rápido. Abra seu aplicativo de terminal e encontre um diretório em que você gostaria de armazenar o código. Execute este comando para clonar o repositório [modelo do aplicativo GitHub](https://github.com/github-developer/github-app-template):

```shell
$ git clone https://github.com/github-developer/github-app-template.git
```

## Etapa 1. Inicie um novo canal da Smee

Para ajudar o GitHub a enviar webhooks para a sua máquina local sem expô-lo à internet, você pode usar uma ferramenta denominada Smee. Primeiro, acesse https://smee.io e clique em **Iniciar um novo canal**. Se você já está confortável com outras ferramentas que expõem sua máquina local à internet como [`ngrok`](https://dashboard.ngrok.com/get-started) ou [`túnel local`](https://localtunnel.github.io/www/), sinta-se à vontade para usá-las.

![O botão do novo canal da Smee](/assets/images/2021/10/smee-new-channel.png)

Iniciar um novo canal da Smee cria um domínio único em que o GitHub pode enviar cargas do webhook. Para a próxima etapa, você precisa conhecer este domínio. Aqui está um exemplo de um domínio único em `https://smee.io/qrfeVRbFbffd6vD`:

![Um canal único da Smee](/assets/images/2021/10/smee-unique-domain.png)

Em seguida, volte ao Terminal e siga estes passos para executar o cliente da interface da linha de comando da Smee (CLI):

{% note %}

**Observação:** As seguintes etapas são ligeiramente diferentes das instruções "Use a CLI" que você verá na sua página de canal da Smee. Você **não** precisa seguir as instruções "Use o cliente do Node.js" ou "Usando o suporte integrado do Probot".

{% endnote %}

1. Instale o cliente:

    ```shell
    $ npm install --global smee-client
    ```

2. Execute o cliente (substituindo `https://smee.io/qrfeVRbFbffd6vD` pelo seu próprio domínio):

    ```shell
    $ smee --url https://smee.io/qrfeVRbFbffd6vD --path /event_handler --port 3000
    ```

    Você deve ver os resultados da seguinte forma:

    ```shell
    Forwarding https://smee.io/qrfeVRbFbffd6vD to http://127.0.0.1:3000/event_handler
    Connected https://smee.io/qrfeVRbFbffd6vD
    ```

O comando `smee --url <unique_channel>` informa à Smee para encaminhar todos os eventos webhook recebidos pelo canal da Smee para o cliente da Smee em execução no seu computador. A opção `--path /event_handler` envia eventos para o encaminhamento `/event_handler`, que iremos cobrir em uma [seção mais adiante](#step-5-review-the-github-app-template-code). A opção `--port 3000` especifica a porta 3000, que é a porta que o seu servidor estará ouvindo. Usando a Smee. A sua máquina não precisa estar conectada à internet pública para receber os webhooks do GitHub. Você também pode abrir a URL da Smee no seu navegador para inspecionar as cargas do webhook quando entrarem.

Recomendamos deixar esta janela de Terminal aberta e manter a Smee conectada enquanto você realiza as outras etapas deste guia. Embora você _possa_ desconectar e reconectar o cliente da Smee sem perder seu domínio único (diferente do `ngrok`), é possível que seja mais fácil deixá-lo conectado e realizar outras tarefas de linha de comando em uma janela diferente do Terminal.

## Etapa 2. Cadastre um novo aplicativo GitHub

Se você ainda não tem uma conta no GitHub, agora é um [ótimo momento para criar](https://github.com/join). Não se esqueça de verificar seu e-mail antes de continuar! Para registrar um novo aplicativo, acesse a [página de configurações do aplicativo](https://github.com/settings/apps) no seu perfil do GitHub e clique em **Novo aplicativo GitHub**.

![Site do GitHub, que mostra o **Novo aplicativo**](/assets/images/2021/10/new-app.png)

Você verá um formulário em que poderá inserir informações sobre o seu aplicativo. Consulte "[Criando um aplicativo GitHub](/apps/building-github-apps/creating-a-github-app/)" para obter informações gerais sobre os campos nesta página. Para os objetivos deste guia, você deverá inserir dados específicos em alguns campos:

{% note %}

**Observação:** Você sempre poderá atualizar essas configurações mais adiante para apontar para um servidor hospedado.

{% endnote %}

* Para a "URL da página inicial", use o domínio emitido pela Smee. Por exemplo:

    ![Formulário com domínio da Smee preenchido para URL da página inicial](/assets/images/2021/10/homepage-url.png)

* Para a "URL do Webhook", use novamente o domínio emitido pela Smee. Por exemplo:

    ![Formulário com domínio da Smee preenchido para URL do webhook](/assets/images/2021/10/webhook-url.png)

* Para o "segredo do Webhook", crie uma senha para proteger seus pontos de extremidade do webhook. Isto deve ser algo que somente você (e o GitHub, por meio deste formulário) sabe. O segredo é importante porque você receberá cargas da internet pública, além de usar este segredo para verificar o remetente do webhook. Observe que as configurações do aplicativo GitHub informam que o segredo do webhook é opcional, o que é verdade na maioria dos casos, mas para que o código do aplicativo do modelo funcione, você deverá definir um segredo do webhook.

    ![Formulário com segredo do webhook preenchido](/assets/images/2021/10/webhook-secret.png)

* Na página de permissões & dos Webhooks, você pode especificar um conjunto de permissões para o seu aplicativo, que determina quantos dados seu aplicativo tem acesso. Na seção "Permissões do repositório", desça a barra de rolagem até "Metadados" e selecione `Access: Read-only`. Se você decidir estender este aplicativo do modelo, você pode atualizar essas permissões mais tarde.

* Na parte inferior da página de permissões & dos webhooks, especifique se este é um aplicativo privado ou público. Isto se refere a quem pode instalá-lo: apenas você ou qualquer pessoa? Por enquanto, deixe o aplicativo como privado, selecionando **Apenas nesta conta**.

    ![Privacidade do aplicativo GitHub](/assets/images/2021/10/create_app.png)

Clique em **Criar aplicativo GitHub** para criar o seu aplicativo!

## Etapa 3. Salve sua chave privada e o ID do aplicativo

Após criar seu aplicativo, você será levado de volta para a [página de configurações do aplicativo](https://github.com/settings/apps). Você tem mais duas coisas para fazer aqui:

* **Gerar uma chave privada para seu aplicativo.** Isso é necessário para autenticar seu aplicativo mais tarde. Role para baixo na página e clique em **Gerar uma chave privada**. Salve o arquivo `PEM` resultante (denominado algo como  _`app-name`_-_`date`_-`private-key.pem`) em um diretório onde você poderá encontrá-lo novamente.

    ![A caixa de diálogo de geração de chaves privadas](/assets/images/2021/10/private_key.png)

* **Observe que GitHub do ID do aplicativo atribuiu seu aplicativo.** Você precisará disso para preparar seu ambiente do tempo de execução.

    <img src="/assets/images/2021/10/app_id.png" alt="Número de ID do seu aplicativo" width="200px" />

## Etapa 4. Prepare o ambiente do tempo de execução

Para manter suas informações seguras, recomendamos colocar todos os segredos referentes ao aplicativo na memória do computador onde seu aplicativo poderá encontrá-los, em vez de colocá-los diretamente no seu código. Uma ferramenta útil de desenvolvimento denominada [dotenv](https://github.com/bkeepers/dotenv) carrega variáveis de ambiente específicas do projeto a partir de um arquivo `.env` para `ENV`. Nunca verifique o seu arquivo `.env` no GitHub. Este é um arquivo local que armazena informações confidenciais que você não deseja que estejam na internet pública. O arquivo `.env` já está incluído no arquivo do repositório [`.gitignore`](/github/getting-started-with-github/ignoring-files/) para evitar isso.

O código do modelo que você baixou na seção [Pré-requisitos](#prerequisites) já tem um exemplo de arquivo denominado `.env-example`. Renomeie o arquivo de exemplo de `.env-example` para `.env` ou crie uma cópia do arquivo `.env-example` denominada `.env`. Você ainda não instalou a dotenv, mas você irá instalá-la mais adiante neste início rápido ao executar o `pacote de instalação`. **Observação:** Os inícios rápidos que fazem referência às etapas neste guia pode incluir variáveis de ambiente adicionais no arquivo `.env-example`. Faça referência ao guia de início rápido para o projeto que você clonou no GitHub para orientação que define essas variáveis de ambiente adicionais.

Você precisa adicionar estas variáveis ao arquivo `.env`:

* _`GITHUB_PRIVATE_KEY`_: Adicione a chave privada [gerada e salva anteriormente](#step-3-save-your-private-key-and-app-id). Abra o arquivo `.pem` com um editor de texto ou use a linha de comando para exibir o conteúdo do arquivo: `cat path/to/your/private-key.pem`. Copie todo o conteúdo do arquivo como o valor de `GITHUB_PRIVATE_KEY` no seu arquivo `.env`. **Observação:** Uma vez que o arquivo PEM tem mais de uma linha, você deverá adicionar aspas em torno do valor, conforme o exemplo abaixo.
* _`GITHUB_APP_IDENTIFIER`_: Use o ID do aplicativo que você anotou na seção anterior.
* _`GITHUB_WEBHOOK_SECRET`_: Adicione o seu segredo do webhook.

Aqui está um arquivo de exemplo `.env`:

```
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
HkVN9...
...
-----END DSA PRIVATE KEY-----"
GITHUB_APP_IDENTIFIER=12345
GITHUB_WEBHOOK_SECRET=your webhook secret
```

## Etapa 5. Revise o código do modelo do aplicativo GitHub

O código do aplicativo do modelo já contém algum código de que cada aplicativo GitHub vai precisar. Esta seção apresenta o código que já existe no modelo do aplicativo GitHub. Não há etapas que você precisa realizar para concluir esta seção. Se você já está familiarizado com o código do modelo, você pode pular para a "[Etapa 6. Inicie o servidor](#step-6-start-the-server)".

Abra o arquivo `template_server.rb` no seu editor de texto favorito. Você verá comentários em todo este arquivo que fornecem um contexto adicional para o código do modelo. Recomendamos ler esses comentários com atenção e até mesmo adicionar seus próprios comentários para acompanhar o novo código que você escrever.

Na parte superior do arquivo você verá `set :port 3000`, que define a porta usada ao iniciar o servidor web para corresponder à porta à qual você redirecionou suas cargas de webhook na "[Etapa 1. Inicie um novo canal da Smee](#step-1-start-a-new-smee-channel)."

O próximo código que você verá é a declaração `class GHApp < Sinatra::Application` Você irá escrever todo o código para o seu aplicativo GitHub dentro desta classe.

Fora desta caixa, a classe do modelo faz o seguinte:
* [Lê as variáveis de ambiente](#read-the-environment-variables)
* [Ativa o início da sessão](#turn-on-logging)
* [Define um pré-filtro](#define-a-before-filter)
* [Define o gerenciador de encaminhamento](#define-a-route-handler)
* [Define os métodos de ajuda](#define-the-helper-methods)

### Lê as variáveis de ambiente

A primeira coisa que essa classe faz é ler as três variáveis de ambiente definidas na "[Etapa 4. Prepare o ambiente do tempo de execução](#step-4-prepare-the-runtime-environment)" e armazene-o nas variáveis para usar posteriormente:

``` ruby
# Espera que a chave privada no formato PEM. Converte as novas linhas
PRIVATE_KEY = OpenSSL::PKey::RSA.new(ENV['GITHUB_PRIVATE_KEY'].gsub('\n', "\n"))

# Seu aplicativo registrado deve ter um conjunto secreto. O segredo é usado para verificar
# se os webhooks são enviados pelo GitHub.
WEBHOOK_SECRET = ENV['GITHUB_WEBHOOK_SECRET']

# O identificador do aplicativo GitHub (tipo inteiro) definido ao registrar um aplicativo.
APP_IDENTIFIER = ENV['GITHUB_APP_IDENTIFIER']
```

### Ativa o início da sessão

Em seguida, um bloco do código que habilita o login durante o desenvolvimento, que é o ambiente-padrão np Sinatra. Este código ativa o início da sessão no nível `DEBUG` para mostrar um resultado útil no Terminal enquanto você está desenvolvendo o aplicativo:

``` ruby
# Turn on Sinatra's verbose logging during development
configure :development do
  set :logging, Logger::DEBUG
end
```

### Define um pré-filtro

O Sinatra usa [pré-filtros](https://github.com/sinatra/sinatra#filters) que permite que você execute o código antes do manipulador de encaminhamento. O bloco `anterior` no modelo chama quatro [métodos de ajuda](https://github.com/sinatra/sinatra#helpers). O aplicativo do modelo define esses métodos de ajuda em uma [seção posterior](#define-the-helper-methods).

``` ruby
# Before each request to the `/event_handler` route
before '/event_handler' do
  get_payload_request(request)
  verify_webhook_signature
  authenticate_app
  # Authenticate the app installation in order to run API operations
  authenticate_installation(@payload)
end
```

### Defina um gerenciador de encaminhamento

Um encaminhamento vazio está incluído no código do modelo. Este código gerencia todas as solicitações `POST` para o encaminhamento `/event_handler`. Você não vai escrever este manipulador de eventos neste início rápido, mas veja os outros [guias de início rápido](/apps/quickstart-guides/) para obter exemplos de como estender o aplicativo deste modelo.

``` ruby
post '/event_handler' do

end
```

### Define os métodos de ajuda

Os métodos de ajuda neste modelo fazem a maior parte do trabalho pesado. Nesta seção do código, são definidos quatro métodos de ajuda.

#### Gerenciar a carga do webhook

O primeiro método `get_payload_request` captura a carga do webhook e a converte para o formato JSON, o que facilita muito o acesso aos dados do payload.

#### Verificar a assinatura do webhook

O segundo método `verify_webhook_signature` realiza a verificação da assinatura do webhook para garantir que o GitHub gerou o evento. Para saber mais sobre o código no método auxiliar `verify_webhook_signature`, consulte "[Protegendo seus webhooks](/webhooks/securing/)". Se os webhooks estiverem seguros, este método registrará todos as cargas de entrada no seu Terminal. O código do registro é útil para verificar se o seu servidor web está funcionando, mas você sempre poderá removê-lo posteriormente.

#### Efetuar autenticação como um aplicativo GitHub

Para fazer chamadas de API, você usará a [biblioteca do Octokit](http://octokit.github.io/octokit.rb/). Fazer qualquer coisa interessante com esta biblioteca irá exigir que você, ou melhor, seu aplicativo, efetue a autenticação. Os aplicativos GitHub têm dois métodos de autenticação:

- Efetuar a autenticação como um aplicativo GitHub usando um [Token web do JSON (JWT)](https://jwt.io/introduction).
- Efetuar a autenticação como uma instalação específica de um aplicativo GitHub usando um token de acesso de instalação.

Você aprenderá como autenticar como uma instalação na [próxima seção](#authenticating-as-an-installation).

[Efetuar a autenticação como um aplicativo GitHub](/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-a-github-app) permite que você faça algumas coisas:

 * Você pode recuperar informações de gerenciamento de alto nível sobre seu aplicativo GitHub.
 * Você pode solicitar tokens de acesso para uma instalação do aplicativo.

Por exemplo, você irá efetuar a autenticação como um aplicativo GitHub para recuperar uma lista das contas (da organização e pessoal) que instalaram seu aplicativo. Mas esse método de autenticação não permite que você faça muitas coisas com a API. Para acessar os dados de um repositório e realizar operações em nome da instalação, você precisa efetuar a autenticação como uma instalação. Para fazer isso, você precisará efetuar a autenticação como um aplicativo GitHub primeiro para solicitar um token de acesso de instalação.

Antes de usar a biblioteca do Octokit.rb para fazer chamadas de API, você deverá inicializar um [cliente do Octokit](http://octokit.github.io/octokit.rb/Octokit/Client.html) autenticado como um aplicativo GitHub. O método auxiliar `autenticate_app` faz exatamente isso!

``` ruby
# Instancie um cliente do Octokit autenticado como um aplicativo GitHub.
# GitHub App authentication requires that you construct a
# JWT (https://jwt.io/introduction/) signed with the app's private key,
# so GitHub can be sure that it came from the app an not altered by
# a malicious third party.
def authenticate_app
  payload = {
      # The time that this JWT was issued, _i.e._ now.
      iat: Time.now.to_i,

      # JWT expiration time (10 minute maximum)
      exp: Time.now.to_i + (10 * 60),

      # Your GitHub App's identifier number
      iss: APP_IDENTIFIER
  }

  # Cryptographically sign the JWT
  jwt = JWT.encode(payload, PRIVATE_KEY, 'RS256')

  # Create the Octokit client, using the JWT as the auth token.
  @app_client ||= Octokit::Client.new(bearer_token: jwt)
end
```

O código acima gera um [JSON Web Token (JWT)](https://jwt.io/introduction) e o usa (junto com a chave privada do seu aplicativo) para inicializar o cliente Octokit. GitHub verifica a autenticação de uma solicitação, verificando o token com a chave pública armazenada no aplicativo. Para saber mais sobre como este código funciona, consulte "[Efetuando a autenticação como um aplicativo GitHub](/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-a-github-app)".

#### Autenticar como uma instalação

Uma _instalação_ refere-se a qualquer usuário ou conta de organização que instalou o aplicativo. Mesmo que alguém instale o app em mais de um repositório, ele só conta como uma instalação porque está dentro da mesma conta. O último método de ajuda `authenticate_installation` inicializa um [Cliente Octokit](http://octokit.github.io/octokit.rb/Octokit/Client.html) autenticado como uma instalação. Este cliente Octokit é o que você usaria para fazer chamadas de API autenticada.

``` ruby
# Iniciar um cliente Octokit autenticado como uma instalação de um
# Aplicativo GitHub para executar operações da API.
def authenticate_installation(payload)
  installation_id = payload['installation']['id']
  installation_token = @app_client.create_app_installation_access_token(installation_id)[:token]
  @installation_client = Octokit::Client.new(bearer_token: installation_token)
end
```

O método do Octokit [`create_app_installation_access_token`](http://octokit.github.io/octokit.rb/Octokit/Client/Apps.html#create_app_installation_access_token-instance_method) cria um token de instalação. Este método aceita dois argumentos:

* Instalação (inteiro): O ID de uma instalação do aplicativo GitHub
* Opções (hash, o padrão é `{}`): Um conjunto personalizável de opções

Sempre que um GitHub App recebe um webhook, ele inclui um objeto de `instalação` com um `id`. Ao usar o cliente autenticado como um aplicativo GitHub, você irá passar este ID para o método `create_app_installation_access_token` para gerar um token de acesso para cada instalação. Uma vez que você não está passando nenhuma opção para o método, as opções-padrão para um hash vazio. Se você olhar [a documentação](/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-an-installation), você poderá ver que a resposta para `create_app_installation_access_token` inclui dois campos: `token` e `expired_at`. O código de modelo seleciona o token na resposta e inicializa um cliente de instalação.

Com este método em vigor, cada vez que seu aplicativo recebe uma nova carga de webhook, ele cria um cliente para a instalação que acionou o evento. Este processo de autenticação permite que seu aplicativo do GitHub funcione para todas as instalações de qualquer conta.

Agora você está pronto para começar a fazer chamadas de API!

## Etapa 6. Inicie servidor

Seu aplicativo ainda não _faz_ nada, mas, neste momento, você pode executá-lo no servidor.

Mantenha a Smee em execução na aba atual no seu Terminal. Abra uma nova aba e `cd` dentro do diretório onde você [clonou o código do aplicativo do modelo](#prerequisites). O código do Ruby neste repositório irá iniciar um servidor web [Sinatra](http://sinatrarb.com/). Este código tem algumas dependências. Você pode instalá-las, executando:

```shell
$ gem install bundler
```

Seguido por:

```shell
$ bundle install
```

Com as dependências instaladas, você pode iniciar o servidor:

```shell
$ ruby template_server.rb
```

Você deve ver uma resposta como:

```shell
> == Sinatra (v2.0.3) has taken the stage on 3000 for development with backup from Puma
> Puma starting in single mode...
> * Version 3.11.2 (ruby 2.4.0-p0), codename: Love Song
> * Min threads: 0, max threads: 16
> * Environment: development
> * Listening on tcp://localhost:3000
> Use Ctrl-C to stop
```

Se você vir um erro, verifique se você criou o arquivo `.env` no diretório que contém `template_server.rb`.

Uma vez que o servidor estiver sendo executado, você poderá testá-lo acessando `http://localhost:3000` no seu navegador. Se o aplicativo funcionar como esperado, você verá uma página útil de erro:

<img src="/assets/images/2021/10/sinatra-404.png" alt="Página de erro 404 do Sinatra" width="500px" />

Isto é bom! Mesmo sendo uma página de erro, é uma página de erro da página do _Sinatra_, o que significa que seu aplicativo está conectado ao servidor conforme esperado. Você está vendo essa mensagem porque você não deu ao aplicativo mais nada para mostrar.

## Etapa 7. Instale o aplicativo em sua conta

Você pode testar se o servidor está ouvindo seu aplicativo acionando um evento para receber. Um evento simples que você pode testar é instalar o aplicativo em sua conta do GitHub, que deve enviar o evento [`instalação`](/webhooks/event-payloads/#installation). Se o aplicativo o receber, você deverá ver algumas saídas na aba Terminal, onde você iniciou `template_server.rb`.

Para instalar o aplicativo, acesse a [página de configurações do aplicativo](https://github.com/settings/apps), escolha seu aplicativo e clique em **Instalar aplicativo** na barra lateral. Ao lado do seu nome de usuário, clique em **Instalar**.

Será perguntado se você deseja instalar o aplicativo em todos os repositórios ou nos repositórios selecionados. Se você não desejar instalar o aplicativo em _todos_ os repositórios, tudo bem! Você pode criar um repositório de sandbox para fins de teste e instalar seu aplicativo lá.

<img src="/assets/images/2021/10/install_permissions.png" alt="Permissões de instalação do aplicativo" width="500px" />

Após clicar em **Instalar**, veja a saída no seu Terminal. Você deverá ver algo assim:

```shell
> D, [2018-06-29T15:45:43.773077 #30488] DEBUG -- : ---- received event integration_installation
> D, [2018-06-29T15:45:43.773141 #30488] DEBUG -- : ----         action created
> 192.30.252.44 - - [29/Jun/2018:15:45:43 -0400] "POST / HTTP/2" 200 2 0.0067
> D, [2018-06-29T15:45:43.833016 #30488] DEBUG -- : ---- received event installation
> D, [2018-06-29T15:45:43.833062 #30488] DEBUG -- : ----         action created
> 192.30.252.39 - - [29/Jun/2018:15:45:43 -0400] "POST / HTTP/2" 200 2 0.0019
```

Isto é bom! Isso significa que seu aplicativo recebeu uma notificação de que foi instalado na sua conta do GitHub. Se você vir algo assim, seu aplicativo estará em execução no servidor, conforme esperado. 🙌

Se você não vir a saída, certifique-se de que a Smee esteja em sendo corretamente executada em outra guia do Terminal. Se você precisar reiniciar a Smee, observe que você também precisará _desinstalar_ e _reinstalar_ o aplicativo para enviar o evento de `instalação` para seu aplicativo novamente e ver a saída no Terminal. Se a Smee não for o problema, consulte a seção "[Solução de problemas](#troubleshooting) para obter outras ideias a esse respeito.

Se você estiver se perguntando de onde vem a saída do Terminal acima, ela é escrita no [código do modelo do aplicativo](#prerequisites) em `template_server.rb`.

## Solução de Problemas

Aqui estão alguns problemas comuns e algumas soluções sugeridas. Se você tiver qualquer outro problema, poderá pedir ajuda ou orientação em {% data variables.product.prodname_support_forum_with_url %}.

* **P:** Quando eu tento instalar o cliente de linha de comando da Smee, eu recebo o seguinte erro:

    ```shell
    > npm: command not found
    ```

    **R:** Parece que você não instalou o npm. A melhor maneira de instalá-lo é baixar o pacote Node.js em https://nodejs.org e seguir as instruções de instalação do seu sistema. O npm será instalado juntamente com o Node.js.

* **P:** Ao executar o servidor, eu recebo o seguinte erro:

    ```shell
    > server.rb:38:in `initialize': Neither PUB key nor PRIV key: header too long (OpenSSL::PKey::RSAError)
    ```

    **R:** Você provavelmente não configurou sua variável de ambiente de chave privada de forma correta. A sua variável `GITHUB_PRIVATE_KEY` deve ficar assim:

    ```
    GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
    ...
    HkVN9...
    ...
    -----END RSA PRIVATE KEY-----"
    ```

    Verifique novamente se você copiou a chave pública correta para o arquivo `.env`.

* **P:** Ao executar o servidor, ele trava com esse erro:

    ```shell
    > Octokit::Unauthorized ... 401 - Bad credentials`
    ```

    **R:** Você pode estar autenticado como um aplicativo GitHub, mas não como uma instalação. Certifique-se de seguir todas as etapas em "[Efetuar autenticação como uma instalação](#authenticating-as-an-installation) e use a variável de instância `@installation_client` (autenticada com um token de acesso de instalação) para as suas operações de API, não a variável de instância `@app_client` (autenticada com um JWT). O `@app_client` só pode recuperar informações de alto nível sobre seu aplicativo e obter tokens de acesso de instalação. Ele não pode fazer muito mais na API.

* **P:** Meu servidor não está ouvindo eventos! O cliente da Smee está sendo executado em uma janela do Terminal, e eu estou instalando o aplicativo em um repositório no GitHub, mas não vejo nenhuma saída na janela do Terminal onde estou executando o servidor.

    **R:** Você pode não estar executando o cliente Smee, executando o comando Smee com os parâmetros incorretos, ou você pode não ter o domínio Smee correto nas suas configurações do aplicativo GitHub. Primeiro verifique para certificar-se de que o cliente da Smee está em execução em uma aba do Terminal. Se esse não for o problema, acesse a sua [página de configurações do aplicativo](https://github.com/settings/apps) e verifique os campos exibidos na "[Etapa 2. Registre um novo aplicativo GitHub](#step-2-register-a-new-github-app)." Certifique-se de que o domínio nesses campos corresponde ao domínio que você usou no seu comando `smee -u <unique_channel>` na "[Etapa 1. Inicie um novo canal da Smee](#step-1-start-a-new-smee-channel)." Se nenhuma das tarefas acima funcionar, marque se você está executando o comando Smee completo, incluindo as opções `--path` e `--port`, por exemplo: `smee --url https://smee.io/qrfeVRbFbffd6vD --path /event_handler --port 3000` (replacing `https://smee.io/qrfeVRbFbffd6vD` with your own Smee domain).

* **P:** Eu recebi uma mensagem de erro `Octokit::NotFound` 404 error na minha saída de depuração:
    ```
    2018-12-06 15:00:56 - Octokit::NotFound - POST {% data variables.product.api_url_code %}/app/installations/500991/access_tokens: 404 - Not Found // See: /v3/apps/#create-a-new-installation-token:
    ```

    **R:** Certifique-se de que as variáveis no seu arquivo `.env` estejam corretas. Certifique-se de que você não definiu variáveis idênticas em qualquer outro arquivo de variável de ambiente como, por exemplo, `bash_profile`. Você pode verificar as variáveis de ambiente que seu aplicativo está usando adicionando `puts` ao código do seu aplicativo e reexecutando o código. Por exemplo, para garantir que você tenha a chave privada correta, você pode adicionar `puts PRIVATE_KEY` ao seu código do aplicativo:

    ```
    PRIVATE_KEY = OpenSSL::PKey::RSA.new(ENV['GITHUB_PRIVATE_KEY'].gsub('\n', "\n"))
    puts PRIVATE_KEY
    ```

## Conclusão

Depois de analisar este guia, você aprendeu os componentes básicos para o desenvolvimento dos aplicativos GitHub! Para resumir, você:

* Registrou um novo aplicativo GitHub
* Usou a Smee para receber cargas de webhook
* Executou um simples servidor web pelo Sinatra
* Efetuou a autenticação como um aplicativo GitHub
* Efetuou a autenticação como uma instalação

## Próximas etapas

Agora você tem um aplicativo GitHub em execução em um servidor. Ele ainda não faz nada especial, mas veja algumas maneiras de personalizar o seu modelo do aplicativo GitHub em outros [guias de início rápido](/apps/quickstart-guides/).
