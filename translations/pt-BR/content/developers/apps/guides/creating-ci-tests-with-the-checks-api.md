---
title: Criar testes de CI com a API de verificações
intro: 'Crie um servidor de integração contínua para executar testes usando um {% data variables.product.prodname_github_app %} e a API de verificações.'
redirect_from:
  - /apps/quickstart-guides/creating-ci-tests-with-the-checks-api
  - /developers/apps/creating-ci-tests-with-the-checks-api
versions:
  fpt: '*'
  ghes: '*'
  ghae: '*'
  ghec: '*'
topics:
  - GitHub Apps
shortTitle: Testes de CI que usam a API Checks
---

## Introdução

Este guia irá apresentá-lo aos [aplicativos GitHub](/apps/) e à [API de verificação](/rest/reference/checks), que você usará para criar um servidor de integração contínua (CI) que executa testes.

A CI é uma prática de software que exige o commit do código em um repositório compartilhado. Fazer commits de códigos com frequência detecta erros com mais antecedência e reduz a quantidade de código necessária para depuração quando os desenvolvedores chegam à origem de um erro. As atualizações frequentes de código também facilitam o merge de alterações dos integrantes de uma equipe de desenvolvimento de software. Assim, os desenvolvedores podem se dedicar mais à gravação de códigos e se preocupar menos com erros de depuração ou conflitos de merge. 🙌

Um código de host do servidor de CI que executa testes de CI, como, por exemplo, linters de código (que verificam formatação de estilo), verificações de segurança, cobertura de código e outras verificações de novos commits de códigos em um repositório. OS ervidores de CI podem até criar e implementar código para servidores de treinamento ou produção. Para obter alguns exemplos dos tipos de testes de CI que você pode criar com um aplicativo GitHub, consulte os [aplicativos de integração contínua](https://github.com/marketplace/category/continuous-integration) disponíveis no GitHub Marketplace.

{% data reusables.apps.app-ruby-guides %}

### Visão geral da API de verificação

A [API de verificação](/rest/reference/checks) permite que você configure testes de CI executados automaticamente em cada commit de código em um repositório. A API de verificação relata informações detalhadas sobre cada verificação no GitHub na aba **Verificações** do pull request. Com a API de Verificações, você pode criar anotações com detalhes adicionais para linhas específicas de código. As anotações são visíveis na aba **Verificações**. Ao criar uma anotação para um arquivo que faz parte do pull request, as anotações também são exibidas na aba **Arquivos alterados**.

Um _conjunto de verificações_ é um grupo de _execuções de verificação _ (testes de CI individuais). Tanto o conjunto quanto a execução contêm _status_ visíveis em um pull request no GitHub. Você pode usar os status para determinar quando um commit de código introduz erros. Usar esses status com [branches protegidos](/rest/reference/repos#branches) pode impedir que as pessoas mesclem de pull requests prematuramente. Veja "[Sobre branches protegidos](/github/administering-a-repository/about-protected-branches#require-status-checks-before-merging)" para mais informações.

A API de verificações envia o evento do webhook [`check_suite` webhook](/webhooks/event-payloads/#check_suite) para todos os aplicativos GitHub instalados em um repositório sempre que um novo código for enviado para o repositório. Para receber todas as ações do evento de verificações da API, o aplicativo deverá ter a permissão de `checks:write`. O GitHub cria automaticamente eventos `check_suite` para novos códigos de commits em um repositório usando o fluxo-padrão, embora [Atualizar preferências do repositório para o conjunto de verificações](/rest/reference/checks#update-repository-preferences-for-check-suites) esteja disponível se desejar. Veja como funciona o fluxo-padrão:

1. Sempre que alguém fizer push do código para o repositório, o GitHub envia o evento `check_suite` com uma ação de `necessária` a todos os aplicativos GitHub instalados no repositório com a permissão `checks:write`. Este evento permite que os aplicativos saibam que o código foi enviado e que o GitHub criou um novo conjunto de verificações automaticamente.
1. Quando seu aplicativo recebe este evento, ele pode [adicionar uma verificação executa](/rest/reference/checks#create-a-check-run) para esse conjunto.
1. As suas execuções de verificação podem incluir [anotações](/rest/reference/checks#annotations-object), que são exibidas em linhas específicas de código.

**Neste guia, você aprenderá:**

* Parte 1: Configurar a estrutura para um servidor de CI usando a API de verificações.
  * Configurar um aplicativo GitHub como um servidor que recebe eventos de API de verificações.
  * Criar novas execuções de verificação para testes de CI quando um repositório recebe commits recém enviados.
  * Reexecutar a verificação quando um usuário solicita que a ação seja executada no GitHub.
* Parte 2: Aproveitar a estrutura do servidor de CI que você criou adicionando um teste de CI de linter.
  * Atualize uma verificação executada com um `status`, `conclusão` e informações de `saída`.
  * Crie anotações nas linhas de código que o GitHub exibe na aba **Verificações** e **Arquivos alterados** de um pull request.
  * Corrija automaticamente as recomendações do linter expondo um botão "Corrigir isso" na aba **Verificações** do pull request.

Para ter uma ideia do que seu servidor de CI da API de verificações fará quando você concluir este início rápido, confira a demonstração abaixo:

![Demonstração do início rápido do servidor de CI da API de verificações](/assets/images/2021/10/github-apps/github_apps_checks_api_ci_server.gif)

## Pré-requisitos

Antes de começar, é possível que você deseje familiarizar-se com os [aplicativos GitHub](/apps/), [Webhooks](/webhooks) e a [API de verificação](/rest/reference/checks), caso você ainda não esteja familiarizado. Você encontrará mais APIs na [documentação da API REST](/rest). A API de Verificações também está disponível para uso no [GraphQL]({% ifversion ghec %}/free-pro-team@latest{% endif %}/graphql), mas este início rápido foca no REST. Consulte o GraphQL [Conjunto de verificações]({% ifversion ghec %}/free-pro-team@latest{% endif %}/graphql/reference/objects#checksuite) e os objetos de [execução de verificação]({% ifversion ghec %}/free-pro-team@latest{% endif %}/graphql/reference/objects#checkrun) objetos para obter mais informações.

Você usará a [linguagem de programação Ruby](https://www.ruby-lang.org/en/), o serviço de entrega de da carga do webhook [Smee](https://smee.io/), a [biblioteca do Ruby Octokit.rb](http://octokit.github.io/octokit.rb/) para a API REST do GitHub e a [estrutura web Sinatra](http://sinatrarb.com/) para criar seu aplicativo do servidor de verificações de CI da API.

Não é necessário ser um especialista em nenhuma dessas ferramentas ou conceitos para concluir este projeto. Este guia irá orientá-lo em todas as etapas necessárias. Antes de começar a criar testes de CI com a API de verificações, você deverá fazer o seguinte:

1. Clone o repositório [Criando testes de CI a API de verificações](https://github.com/github-developer/creating-ci-tests-with-the-checks-api).
  ```shell
    $ git clone https://github.com/github-developer/creating-ci-tests-with-the-checks-api.git
  ```

  Dentro do diretório, você encontrará um arquivo `template_server.rb` com o código do template você usará neste início rápido e um arquivo `server.rb` arquivo com o código do projeto concluído.

1. Siga as etapas no início rápido "[Configurando seu ambiente de desenvolvimento](/apps/quickstart-guides/setting-up-your-development-environment/)" para configurar e executar o servidor do aplicativo. **Observação:** Em vez de [clonar o repositório de modelo do aplicativo GitHub](/apps/quickstart-guides/setting-up-your-development-environment/#prerequisites), use o arquivo `template_server.rb` arquivo no repositório que você clonou no passo anterior neste início rápido.

  Se você concluiu um início rápido do aplicativo GitHub antes disso, certifique-se de registrar um _novo_ aplicativo GitHub e iniciar um novo canal Smee para usar com este início rápido.

  Consulte a seção [Resolução de problemas](/apps/quickstart-guides/setting-up-your-development-environment/#troubleshooting) se você tiver problemas ao configurar o modelo do seu aplicativo GitHub.

## Parte 1. Criar a interface da API de verificações

Nesta parte, você irá adicionar o código necessário para receber os eventos do webhook `verific_suite` irá criar e atualizar as execuções de verificação. Você também aprenderá como criar uma execução de verificação quando solicitou-se a verificação novamente no GitHub. Ao final desta seção, você poderá visualizar a execução de verificação que você criou em um pull request do GitHub.

Sua execução de verificação não realizará nenhuma verificação no código nesta seção. Você adicionará essa funcionalidade na [Parte 2: Criando o teste de CI do Octo RuboCop](#part-2-creating-the-octo-rubocop-ci-test).

Você já deve ter um canal do Smee configurado que encaminha cargas do webhook para o seu servidor local. Seu servidor deve estar em execução e conectado ao aplicativo GitHub que você registrou e instalou em um repositório de teste. Se você não concluiu as etapas em "[Configurando seu ambiente de desenvolvimento](/apps/quickstart-guides/setting-up-your-development-environment/)", você deverá fazer isso antes de continuar.

Vamos começar! Estas são as etapas que você concluirá na Parte 1:

1. [Atualizar as permissões do aplicativo](#step-11-updating-app-permissions)
1. [Adicionar manipulação de evento](#step-12-adding-event-handling)
1. [Criar uma execução de verificação](#step-13-creating-a-check-run)
1. [Atualizar a execução de verificação](#step-14-updating-a-check-run)

## Etapa 1.1. Atualizar as permissões do aplicativo

Quando você [registrou seu aplicativo pela primeira vez](#prerequisites), você aceitou as permissões-padrão, o que significa que seu aplicativo não tem acesso à maioria dos recursos. Para este exemplo, seu aplicativo precisará de permissão para ler e gravar verificações.

Para atualizar as permissões do aplicativo:

1. Selecione seu aplicativo na [página de configurações do aplicativo](https://github.com/settings/apps) e clique em **Permissões & Webhooks** na barra lateral.
1. Na seção "Permissões", localize "Verificações" e selecione **Leitura & gravação** no menu suspenso de Acesso ao lado.
1. Na seção "Assinar eventos", selecione **Conjunto de verificações** e **Execução de verificações ** para assinar esses eventos.
{% data reusables.apps.accept_new_permissions_steps %}

Ótimo! Seu aplicativo tem permissão para realizar as tarefas que você deseja que ele realize. Agora você pode adicionar o código para gerenciar os eventos.

## Etapa 1.2. Adicionar manipulação de evento

Agora que seu aplicativo assinou os eventos **Conjunto de verificações** e na **Execução de verificações**, ele irá começar a receber os webhooks [`check_suite`](/webhooks/event-payloads/#check_suite) e [`check_run`](/webhooks/event-payloads/#check_run). O GitHub envia cargas do webhook como solicitações de `POST`. Porque você encaminhou as cargas do webhook do smee para `http://localhost/event_handler:3000`, seu servidor receberá as cargas de solicitação `POST` no encaminhamento `post '/event_handler'`.

Um encaminhamento vazio `post '/event_handler'` já está incluído no arquivo `template_server.rb`, que você baixou na seção [pré-requisitos](#prerequisites). O encaminhamento vazio tem a seguinte forma:

``` ruby
  post '/event_handler' do

    # # # # # # # # # # # #
    # ADD YOUR CODE HERE  #
    # # # # # # # # # # # #

    200 # success status
  end
```

Use este encaminhamento para gerenciar o evento `check_suite` adicionando o código a seguir:

``` ruby
# Obtenha o tipo de evento a partir do cabeçalho HTTP_X_GITHUB_EVENT 
case request.env['HTTP_X_GITHUB_EVENT']
quando 'check_suite'
  # Um novo check_suite foi criado. Crie uma nova execução de verificação com status enfileirado
  if @payload['action'] == 'requested' || @payload['action'] == 'rerequested'
    create_check_run
  end
end
```

Cada evento que o GitHub envia inclui um cabeçalho de solicitação denominado `HTTP_X_GITHUB_EVENT`, que indica o tipo de evento na solicitação de `POST`. No momento, você está interessado apenas em eventos do tipo `check_suite`, emitidos quando um novo conjunto de verificações é criado. Cada evento tem um campo `ação` adicional que indica o tipo de ação que acionou os eventos. Para `check_suite`, o campo `ação` pode ser `solicitado`, `ressolicitado` ou `concluído`.

A ação `solicitada` solicita uma execução de verificação cada vez que o código é enviado para o repositório, ao passo que a ação `ressolicitada` solicita que você execute novamente uma verificação para o código que já existe no repositório. Como as ações `solicitadas` e `ressolicitadas` exigem a criação de uma execução de verificação, você chamará um auxiliar denominado `create_check_run`. Vamos escrever esse método agora.

## Etapa 1.3. Criar uma execução de verificação

Você irá adicionar este novo método como um [Auxiliar do Sinatra](https://github.com/sinatra/sinatra#helpers), caso deseje que outros encaminhamentos o usem também. Em `auxiliares do`, adicione este método `create_check_run`:

``` ruby
# Create a new check run with the status queued
def create_check_run
  @installation_client.create_check_run(
    # [String, Integer, Hash, Octokit Repository object] A GitHub repository.
    @payload['repository']['full_name'],
    # [String] The name of your check run.
    'Octo RuboCop',
    # [String] The SHA of the commit to check 
    # The payload structure differs depending on whether a check run or a check suite event occurred.
    @payload['check_run'].nil? ? @payload['check_suite']['head_sha'] : @payload['check_run']['head_sha'],
    # [Hash] 'Accept' header option, to avoid a warning about the API not being ready for production use.
    accept: 'application/vnd.github.v3+json'
  )
end
```

Este código chama o ponto de extremidade "[Crie uma verificação de execução](/rest/reference/checks#create-a-check-run)" usando o [create_check_run method](https://rdoc.info/gems/octokit/Octokit%2FClient%2FChecks:create_check_run).

Para criar uma execução de verificação, são necessários apenas dois parâmetros de entrada: `nome` e `head_sha`. Vamos usar [RuboCop](https://rubocop.readthedocs.io/en/latest/) para implementar o teste de CI mais adiante neste início rápido. É por isso que o nome "Octo RuboCop" é usado aqui, mas você pode escolher qualquer nome que quiser para a verificação ser executada.

Você só está fornecendo os parâmetros necessários agora para que a funcionalidade básica funcione, mas você irá atualizar a verificação de execução posteriormente enquanto coleta mais informações sobre a verificação de execução. Por padrão, o GitHub define o `status` como `enfileirado`.

O GitHub cria uma execução de verificação para um commit SHA específico. É por isso que `head_sha` é um parâmetro necessário. Você pode encontrar commit SHA na carga do webhook. Embora você esteja apenas criando uma execução de verificação para o evento `check_suite` neste momento, é bom saber que o `head_sha` está incluído em ambos os objetos `check_suite` e `check_run` nas cargas do evento.

No código acima, você está usando o [operador ternário](https://ruby-doc.org/core-2.3.0/doc/syntax/control_expressions_rdoc.html#label-Ternary+if), que funciona como uma instrução `if/else` para verificar se a carga contém um objeto `check_run`. Em caso afirmativo, você lê o `head_sha` a partir do objeto `check_run`. Caso contrário você o lê a partir do objeto `check_suite`.

Para testar esse código, reinicie o servidor a partir do seu terminal:

```shell
$ ruby template_server.rb
```

{% data reusables.apps.sinatra_restart_instructions %}

Agora abra um pull request no repositório em que você instalou seu aplicativo. Seu aplicativo deve responder, criando uma verificação executada em seu pull request. Clique na aba **Verificações** e você deve ver algo parecido com isso:

![Execução de verificação enfileirada](/assets/images/2021/10/github-apps/github_apps_queued_check_run.png)

Se você vir outros aplicativos na aba Verificações, isso significa que você tem outros aplicativos instalados no seu repositório que têm acesso de **leitura & gravação ** para verificações e que estão inscritos em eventos **Conjunto de verificações** e **Execução de verificações**.

Ótimo! Você disse ao GitHub para criar uma execução de verificação. Você pode ver que o status da execução de verificação está definido como `enfileirado` ao lado de um ícone amarelo. Em seguida, você irá aguardar que o GitHub crie a execução de verificação e atualize seu status.

## Etapa 1.4. Atualizar a execução de verificação

Quando o seu método `create_check_run` é executado, ele pede ao GitHub para criar uma nova execução de verificação. Quando o GitHub terminar de criar a execução de verificação, você receberá o evento do webhook `check_run` com a ação `criada`. Esse evento é o sinal para começar a executar a verificação.

Você vai atualizar o manipulador do evento para procurar a ação `criada`. Enquanto você está atualizando o manipulador de eventos, você pode adicionar uma condição para a ação `ressolicitada`. Quando alguém executa novamente um único teste no GitHub clicando no botão "Reexecutar", o GitHub envia o evento da execução de verificação `ressolicitado` para o seu aplicativo. Quando a execução de uma verificação é `ressolicitada`, você irá iniciar todo o processo e criar uma nova execução de verificação.

Para incluir uma condição para o evento `check_run` no encaminhamento `post '/event_handler'`, adicione o seguinte código em `case request.env['HTTP_X_GITHUB_EVENT']`:

``` ruby
when 'check_run'
  # Check that the event is being sent to this app
  if @payload['check_run']['app']['id'].to_s === APP_IDENTIFIER
    case @payload['action']
    when 'created'
      initiate_check_run
    when 'rerequested'
      create_check_run
    end
  end
```

O GitHub envia todos os eventos para as execuções de verificação `criadas` para todos os aplicativos instalados em um repositório que tenha as permissões de verificações necessárias. Isso significa que seu aplicativo receberá uma verificação que será executada por outros aplicativos. Uma execução de verificação `criada` é um pouco diferente de um conjunto de verificações `solicitado` ou `ressolicitado`, que o GitHub envia apenas para aplicativos que estão sendo ressolicitados para executar uma verificação. O código acima procura o ID do aplicativo da execução de verificação. Isto filtra todas as execuções de verificação de outros aplicativos no repositório.

Em seguida, você irá escrever o método `initiate_check_run`, que é onde você vai atualizar o status da sua execução de verificação e preparar-se para iniciar o seu teste de CI.

Nesta seção, você não vai iniciar o teste de CI ainda, mas você verá como atualizar o status da verificação de execução de `enfileirado` até `pendente` e, em seguida, de `pendente` até `concluído` para ver o fluxo geral de uma execução de verificação. Na "[Parte 2: Criando o teste de CI do Octo RuboCop](#part-2-creating-the-octo-rubocop-ci-test)", você irá adicionar o código que realmente realiza o teste de CI.

Vamos criar o método `initiate_check_run` e atualizar o status da execução de verificação. Adicione o seguinte código à seção auxiliar:

``` ruby
# Start the CI process
def initiate_check_run
  # Once the check run is created, you'll update the status of the check run
  # to 'in_progress' and run the CI process. When the CI finishes, you'll
  # update the check run status to 'completed' and add the CI results.

  @installation_client.update_check_run(
    @payload['repository']['full_name'],
    @payload['check_run']['id'],
    status: 'in_progress',
    accept: 'application/vnd.github.v3+json'
  )

  # ***** RUN A CI TEST *****

  # Mark the check run as complete!
  @installation_client.update_check_run(
    @payload['repository']['full_name'],
    @payload['check_run']['id'],
    status: 'completed',
    conclusion: 'success',
    accept: 'application/vnd.github.v3+json'
  )
end
```

O código acima chama o ponto de extremidade da API de "[Atualizar uma execução de verificação](/rest/reference/checks#update-a-check-run)" usando o [`update_check_run` Octokit](https://rdoc.info/gems/octokit/Octokit%2FClient%2FChecks:update_check_run) para atualizar o método de verificação que você já criou.

Veja o que este código está fazendo. Primeiro, ele atualiza o status de verificação de execução para `in_progress` e define implicitamente a hora de `started_at` para o momento atual. Na [Parte 2](#part-2-creating-the-octo-rubocop-ci-test) deste início rápido, você irá adicionar um código que inicia um teste de CI real em `***** EXECUTAR UM TEST DE CI *****`. Por enquanto, você sairá da seção como um espaço reservado, para que o código que o segue apenas simule que o processo de CI seja bem-sucedido e todos os testes sejam aprovados. Finalmente, o código atualiza o status da execução de verificação novamente para `concluído`.

Na documentação "[Atualizar uma execução de verificação](/rest/reference/checks#update-a-check-run)", você observará que, ao fornecer um status de `concluído`, são necessários os parâmetros `conclusão` e `completed_at`. A conclusão `` resume o resultado de uma verificação de resultado e pode ser `sucesso`, `falha`, `neutro`, `cancelado`, `timed_out` ou `action_required`. Você irá definir a conclusão como `sucesso`, o tempo `completed_at` como a hora atual e o status como `concluído`.

Você também pode fornecer mais informações sobre o que a sua verificação está fazendo, mas você poderá fazer isso na próxima seção. Vamos testar este código de novo executando `template_server.rb` novamente:

```shell
$ ruby template_server.rb
```

Vá para seu pull request aberto e clique na aba **Verificações**. Clique no botão "Executar tudo novamente" no canto superior esquerdo. Você deverá ver a execução da verificação mover de `pendente` para `in_progress` e terminar com `sucesso`:

![Execução de verificação concluída](/assets/images/2021/10/github-apps/github_apps_complete_check_run.png)

## Parte 2. Criar o teste de CI do Octo RuboCop

[RuboCop](https://rubocop.readthedocs.io/en/latest/) é um linter do código do Ruby e um formatador. Ele verifica o código do Ruby para garantir que esteja de acordo com o "[Guia de estilo do Ruby](https://github.com/rubocop-hq/ruby-style-guide)". O RuboCop tem três funções principais:

* Linting para verificação do estilo do código
* Formatação do código
* Substitui os recursos de linting nativos do Rubi usando `ruby -w`

Agora que a interface foi criada para receber eventos da API de verificações e criar execuções de verificação, você pode criar uma execução de verificação que implemente um teste de CI.

Seu aplicativo irá executar o RuboCop no servidor de CI e irá criar uma execuções de verificação (neste caso, testes de CI), que relatarão os resultados que o RuboCop relata para o GitHub.

A API de verificações permite que você relate informações valiosas sobre cada execução de verificação, incluindo status, imagens, resumos, anotações e ações solicitadas.

As anotações são informações sobre linhas específicas de código em um repositório. Uma anotação permite que você identifique e visualize as partes exatas do código para as quais você gostaria de mostrar informações adicionais. Essas informações podem ser qualquer coisa: por exemplo, um comentário, um erro ou um aviso. Este início rápido usa anotações para visualizar erros no RuboCop.

Para aproveitar as ações solicitadas, os desenvolvedores de aplicativos podem criar botões na aba **Verificações** dos pull requests. Quando alguém clica em um desses botões, o clique envia um evento `requested_action` `check_run` para o aplicativo GitHub. A ação tomada pelo aplicativo é completamente configurável pelo desenvolvedor do aplicativo. Este início rápido irá orientá-lo no processo de adição de um botão que permite aos usuários solicitar que o RuboCop corrija os erros que encontrar. O RuboCop é compatível com a correção automática de erros usando uma opção de linha de comando, e você irá configurar a `requested_action` para aproveitar esta opção.

Vamos começar! Estas são as etapas que você concluirá nesta seção:

1. [Adicionar um arquivo do Ruby](#step-21-adding-a-ruby-file)
1. [Clonar um repositório](#step-22-cloning-the-repository)
1. [Executar o RuboCop](#step-23-running-rubocop)
1. [Coletar erros do RuboCop](#step-24-collecting-rubocop-errors)
1. [Atualizar a execução de verificação com resultados dos testes de CI](#step-25-updating-the-check-run-with-ci-test-results)
1. [Corrigir erros do RuboCop automaticamente](#step-26-automatically-fixing-rubocop-errors)
1. [Dicas de segurança](#step-27-security-tips)

## Etapa 2.1. Adicionar um arquivo do Ruby

Você pode passar arquivos específicos ou diretórios inteiros para o RuboCop verificar. Nesse início rápido, você irá executar o RuboCop em um diretório inteiro. Como RuboCop verifica apenas códigos Ruby, será necessário pelo menos um arquivo Ruby no seu repositório que contém erros. O arquivo de exemplo fornecido abaixo contém alguns erros. Adicione este exemplo de arquivo Ruby ao repositório onde seu aplicativo está instalado (certifique-se de nomear o arquivo com uma extensão `.rb`, como em `myfile.rb`):

```ruby
# The Octocat class tells you about different breeds of Octocat
class Octocat
  def initialize(name, *breeds)
    # Instance variables
    @name = name
    @breeds = breeds
  end

  def display
    breed = @breeds.join("-")

    puts "I am of #{breed} breed, and my name is #{@name}."
  end
end

m = Octocat.new("Mona", "cat", "octopus")
m.display
```

## Etapa 2.2. Clonar um repositório

O RuboCop está disponível como um utilitário da linha de comando. Isso significa que o seu aplicativo GitHub deverá clonar uma cópia local do repositório no servidor da CI para que RuboCop possa analisar os arquivos. Para executar operações do Git no seu aplicativo Ruby, você pode usar o gem de [ruby-git](https://github.com/ruby-git/ruby-git).

O `Gemfile` no repositório `building-a-checks-api-ci-server` já inclui a gem de ruby-git, e você o instalou quando executou a `instalação em conjunto` nas [etapas requisitadas](#prerequisites). Para usar a gem, adicione este código à parte superior do seu arquivo `template_server.rb`:

``` ruby
requer "git"
```

Seu aplicativo deve permissão de leitura para "Conteúdo do repositório" para clonar um repositório. Mais adiante neste início rápido, você deverá fazer push de conteúdo para o GitHub, o que exige permissão de gravação. Defina a permissão de "Conteúdo do repositório" do seu aplicativo como **leitura & gravação** agora, para que você não precise atualizar novamente mais tarde. Para atualizar as permissões do aplicativo:

1. Selecione seu aplicativo na [página de configurações do aplicativo](https://github.com/settings/apps) e clique em **Permissões & Webhooks** na barra lateral.
1. Na seção "Permissões", encontre "Conteúdo do repositório" e selecione **Leitura & gravação ** no menu suspenso "Acesso" ao lado.
{% data reusables.apps.accept_new_permissions_steps %}

Para clonar um repositório usando as permissões do seu aplicativo GitHub você pode usar o token de instalação do aplicativo (`x-access-token:<token>`) mostrado no exemplo abaixo:

```shell
git clone https://x-access-token:<token>@github.com/<owner>/<repo>.git
```

O código acima clone um repositório por HTTP. Isto exige o nome completo do repositório, que inclui o proprietário do repositório (usuário ou organização) e o nome do repositório. Por exemplo, o nome completo do repositório [octocat Hello-World](https://github.com/octocat/Hello-World) é `octocat/hello-world`.

Depois que seu aplicativo clonar o repositório, ele deverá resgatar as alterações mais recentes do código fazer checkout do Git ref específico. O código para fazer tudo isto encaixa-se perfeitamente no seu próprio método. Para realizar essas operações, o método precisa do nome e nome completo do repositório e que o ref faça checkout. O ref pode ser um commit SHA, branch ou tag. Adicione o método a seguir à seção do método auxiliar no `template_server.rb`:

``` ruby
# Clones the repository to the current working directory, updates the
# contents using Git pull, and checks out the ref.
#
# full_repo_name  - The owner and repo. Ex: octocat/hello-world
# repository      - The repository name
# ref             - The branch, commit SHA, or tag to check out
def clone_repository(full_repo_name, repository, ref)
  @git = Git.clone("https://x-access-token:#{@installation_token.to_s}@github.com/#{full_repo_name}.git", repository)
  pwd = Dir.getwd()
  Dir.chdir(repository)
  @git.pull
  @git.checkout(ref)
  Dir.chdir(pwd)
end
```

O código acima usa a gem `ruby-git` para clonar o repositório usando o token de instalação do aplicativo. Esse código clona o código no mesmo diretório como o `template_server.rb`. Para executar comandos Git no repositório, o código deve alterar para o diretório do repositório. Antes de mudar os diretórios, o código armazena o diretório de trabalho atual em uma variável (`pwd`) para lembrar para onde retornar antes de sair do método `clone_repository`.

No diretório do repositório, este código busca e mescla as últimas alterações (`@git.pull`), faz o checkout do ref (`@git. heckout(ref)`) e, em seguida, muda o diretório de volta para o diretório de trabalho original (`pwd`).

Agora você tem um método que clona um repositório e faz o checkout de um ref. Em seguida, você deve adicionar código para obter os parâmetros de entrada necessários e chamar o novo método `clone_repository`. Adicione o código a seguir no comentário `***** RUN A CI TEST *****` no seu método auxiliar `initiate_check_run`:

``` ruby
# ***** RUN A CI TEST *****
full_repo_name = @payload['repository']['full_name']
repository     = @payload['repository']['name']
head_sha       = @payload['check_run']['head_sha']

clone_repository(full_repo_name, repository, head_sha)
```

O código acima obtém o nome completo do repositório e o SHA principal do commit da carga do webhook `check_run`.

## Etapa 2.3. Executar o RuboCop

Ótimo! Você está clonando o repositório e criando execuções de verificação usando seu servidor de CI. Agora você irá entrar nas informações principais do [RuboCop linter](https://docs.rubocop.org/rubocop/usage/basic_usage.html#code-style-checker) e das [anotações da API de verificação](/rest/reference/checks#create-a-check-run).

O código a seguir executa RuboCop e salva os erros do código de estilo no formato JSON. Adicione este código abaixo da chamada para `clone_repository` que você adicionou na [etapa anterior](#step-22-cloning-the-repository) e acima do código que atualiza a execução de verificação para concluir.

``` ruby
# Run RuboCop on all files in the repository
@report = `rubocop '#{repository}' --format json`
logger.debug @report
`rm -rf #{repository}`
@output = JSON.parse @report
```

O código acima executa o RuboCop em todos os arquivos no diretório do repositório. A opção `--format json` é uma maneira útil de salvar uma cópia dos resultados de linting, em um formato analisável por máquina. Consulte a [documentação do RuboCop](https://docs.rubocop.org/rubocop/formatters.html#json-formatter) para obter informações e um exemplo do formato JSON.

Como esse código armazena os resultados do RuboCop em uma variável `@report`, ele pode remover o checkout do repositório com segurança. Este código também analisa o JSON para que possa acessar facilmente as chaves e valores no seu aplicativo GitHub usando a variável `@output`.

{% note %}

**Observação:** Não é possível desfazer o comando usado para remover o repositório (`rm -rf`). Consulte [Etapa 2.7. Dicas de segurança](#step-27-security-tips) para aprender como verificar webhooks sobre comandos maliciosos injetados que podem ser usados para remover um diretório diferente do que era esperado pelo seu aplicativo. Por exemplo, se um ator ruim enviasse um webhook com o nome do repositório `./`, seu aplicativo removeria o diretório-raiz. 😱 Se, por algum motivo, você _não_ está usando o método `verify_webhook_signature` (incluído no `template_server.rb`) para validar o remetente do webhook, certifique-se de que o nome do repositório seja válido.

{% endnote %}

Você pode testar se este código funciona e ver os erros relatados pelo RuboCop na saída de depuração do seu servidor. Reinicie o servidor `template_server.rb` e crie um novo pull request no repositório em que você está testando seu aplicativo:

```shell
$ ruby template_server.rb
```

Você deve ver os erros de linting na saída de depuração, embora não sejam impressos com a formatação. Você pode usar uma ferramenta como o[formatador JSON](https://jsonformatter.org/) para formatar sua saída do JSON como esta saída de erro de do linting formatado:

```json
{
  "metadata": {
    "rubocop_version": "0.60.0",
    "ruby_engine": "ruby",
    "ruby_version": "2.3.7",
    "ruby_patchlevel": "456",
    "ruby_platform": "universal.x86_64-darwin18"
  },
  "files": [
    {
      "path": "Octocat-breeds/octocat.rb",
      "offenses": [
        {
          "severity": "convention",
          "message": "Style/StringLiterals: Prefer single-quoted strings when you don't need string interpolation or special symbols.",
          "cop_name": "Style/StringLiterals",
          "corrected": false,
          "location": {
            "start_line": 17,
            "start_column": 17,
            "last_line": 17,
            "last_column": 22,
            "length": 6,
            "line": 17,
            "column": 17
          }
        },
        {
          "severity": "convention",
          "message": "Style/StringLiterals: Prefer single-quoted strings when you don't need string interpolation or special symbols.",
          "cop_name": "Style/StringLiterals",
          "corrected": false,
          "location": {
            "start_line": 17,
            "start_column": 25,
            "last_line": 17,
            "last_column": 29,
            "length": 5,
            "line": 17,
            "column": 25
          }
        }
      ]
    }
  ],
  "summary": {
    "offense_count": 2,
    "target_file_count": 1,
    "inspected_file_count": 1
  }
}
```

## Etapa 2.4. Coletar erros do RuboCop

A variável `@output` contém os resultados do JSON analisados do relatório do RuboCop. Conforme mostrado acima, os resultados contêm uma seção `resumo` que seu código pode usar para determinar rapidamente se existem erros. O código a seguir definirá a conclusão de execução de verificação para o `sucesso` quando não houver erros relatados. O RuboCop relata erros para cada arquivo no array dos `arquivos`. Portanto, se houver erros, você deverá extrair alguns dados do objeto arquivo.

A API de verificação permite que você crie anotações para linhas específicas do código. Ao criar ou atualizar uma execução de verificação, você pode adicionar anotações. Neste início rápido, você está [atualizando a execução de verificações](/rest/reference/checks#update-a-check-run) com anotações.

A API de verificação limita o número de anotações a um máximo de 50 por solicitação de API. Para criar mais de 50 anotações, você deverá fazer várias solicitações para o ponto de extremidade [Atualizar uma execução de verificação](/rest/reference/checks#update-a-check-run). Por exemplo, para criar 105 anotações você deve chamar o ponto de extremidade [Atualizar uma execução de verificação](/rest/reference/checks#update-a-check-run) três vezes. Cada uma das duas primeiras solicitações teria 50 anotações e a terceira solicitação incluiria as cinco anotações restantes. Cada vez que você atualizar a execução de verificação, as anotações são anexadas à lista de anotações que já existem para a execução de verificação.

Uma execução de verificação espera anotações como um array de objetos. Cada objeto de anotação deve incluir o `caminho`, `start_line`,, `end_line`, `annotation_level` e `mensagem`. O RuboCop também fornece `start_column` e `end_column`. Portanto, você pode incluir esses parâmetros opcionais na anotação. As anotações são compatíveis apenas com `start_column` e `end_column` na mesma linha. Para obter mais informações, consulte a documentação de referência do objeto [`anotações`](/rest/reference/checks#annotations-object-1).

Você irá extrair as informações necessárias do RuboCop para criar cada anotação. Acrescente o seguinte código ao código que você adicionou na [seção anterior](#step-23-running-rubocop):

``` ruby
annotations = []
# You can create a maximum of 50 annotations per request to the Checks
# API. To add more than 50 annotations, use the "Update a check run" API
# endpoint. Este código de exemplo limita o número de anotações a 50.
# See /rest/reference/checks#update-a-check-run
# for details.
max_annotations = 50

# RuboCop reports the number of errors found in "offense_count"
if @output['summary']['offense_count'] == 0
  conclusion = 'success'
else
  conclusion = 'neutral'
  @output['files'].each do |file|

    # Only parse offenses for files in this app's repository
    file_path = file['path'].gsub(/#{repository}\//,'')
    annotation_level = 'notice'

    # Parse each offense to get details and location
    file['offenses'].each do |offense|
      # Limit the number of annotations to 50
      next if max_annotations == 0
      max_annotations -= 1

      start_line   = offense['location']['start_line']
      end_line     = offense['location']['last_line']
      start_column = offense['location']['start_column']
      end_column   = offense['location']['last_column']
      message      = offense['message']

      # Create a new annotation for each error
      annotation = {
        path: file_path,
        start_line: start_line,
        end_line: end_line,
        start_column: start_column,
        end_column: end_column,
        annotation_level: annotation_level,
        message: message
      }
      # Annotations only support start and end columns on the same line
      if start_line == end_line
        annotation.merge({start_column: start_column, end_column: end_column})
      end

      annotations.push(annotation)
    end
  end
end
```

Este código limita o número total de anotações a 50. Mas você pode modificar este código para atualizar a verificação de execução para cada lote de 50 anotações. O código acima inclui a variável `max_annotations` que define o limite para 50, que é usado no loop que itera por meio das ofensas.

Quando o `offense_count` é zero, o teste de CI é um `sucesso`. Se houver erros, este código definirá a conclusão como `neutro` para evitar estritamente a imposição de erros dos linters do código. Mas você pode alterar a conclusão para `falha` se desejar garantir que o conjunto de verificações falhe quando houver erros de linting.

Quando os erros são relatados, o código acima afirma por meio da array de `arquivos` no relatório do RuboCop. Para cada arquivo, ele extrai o caminho do arquivo e define o nível de anotação como `aviso`. Você pode ir além e definir os níveis específicos de aviso para cada tipo de [RuboCop Cop](https://docs.rubocop.org/rubocop/cops.html), mas simplificar as coisas neste início rápido, todos os erros são definidos para um nível de `aviso`.

Este código também é afirmado por meio de cada erro no array de `ofensas` e coleta o local da mensagem de erro e de ofensa. Após extrair as informações necessárias, o código cria uma anotação para cada erro e a armazena no array de `anotações`. Uma vez que as anotações são compatíveis apenas com colunas iniciais e finais na mesma linha, `start_column` e `end_column` só são adicionados ao objeto `anotação` se os valores da linha inicial e final forem iguais.

Esse código ainda não cria uma anotação para a execução de verificação. Você irá adicionar esse código na próxima seção.

## Etapa 2.5. Atualizar a execução de verificação com resultados dos testes de CI

Cada execução de verificação no GitHub contém um objeto de `saída` que inclui um `título`, `resumo`, `texto`, `anotações` e `imagens`. O `resumo` e o `título` são os únicos parâmetros necessários para a `saída`, mas eles não oferecem muitas informações. Portanto, este início rápido adiciona também `texto` e `anotações`. Aqui, o código não adiciona uma imagem, mas sinta-se à vontade para adicionar uma, se desejar!

Para o `resumo`, este exemplo usa a informação de resumo do RuboCop e adiciona algumas novas linhas (`\n`) para formatar a saída. É possível personalizar o que você adiciona ao parâmetro `texto`, mas este exemplo define o parâmetro `texto` para a versão do RuboCop. Para definir o `resumo` e o `texto`, adicione este código ao código que você adicionou na [seção anterior](#step-24-collecting-rubocop-errors):

``` ruby
# Updated check run summary and text parameters
summary = "Octo RuboCop summary\n-Offense count: #{@output['summary']['offense_count']}\n-File count: #{@output['summary']['target_file_count']}\n-Target file count: #{@output['summary']['inspected_file_count']}"
text = "Octo RuboCop version: #{@output['metadata']['rubocop_version']}"
```

Agora você tem todas as informações de que precisa para atualizar sua execução de verificação. Na [primeira metade deste início rápido](#step-14-updating-a-check-run), você adicionou este código para definir o status da execução de verificação de `sucesso`:

``` ruby
# Mark the check run as complete!
@installation_client.update_check_run(
  @payload['repository']['full_name'],
  @payload['check_run']['id'],
  status: 'completed',
  conclusion: 'success',
  accept: 'application/vnd.github.v3+json'
)
```

Você deverá atualizar esse código para usar a variável de `conclusão` definida com base nos resultados do RuboCop (para `sucesso` ou `neutro`). Você pode atualizar o código com o seguinte:

``` ruby
# Mark the check run as complete! E, se houver avisos, compartilhe-os.
@installation_client.update_check_run(
  @payload['repository']['full_name'],
  @payload['check_run']['id'],
  status: 'completed',
  conclusion: conclusion,
  output: {
    title: 'Octo RuboCop',
    summary: summary,
    text: text,
    annotations: annotations
  },
  actions: [{
    label: 'Fix this',
    description: 'Automatically fix all linter notices.',
    identifier: 'fix_rubocop_notices'
  }],
  accept: 'application/vnd.github.v3+json'
)
```

Agora que você está definindo uma conclusão com base no status do teste CI e que você adicionou a saída dos resultados do RuboCop, você criou um teste de CI! Parabéns. 🙌

O código acima também adiciona um recurso ao seu servidor de CI denominado [ações solicitadas](https://developer.github.com/changes/2018-05-23-request-actions-on-checks/) por meio do objeto `ações`. {% ifversion fpt or ghec %}(Observe que isto não está relacionado ao [GitHub Actions](/actions).) {% endif %}As ações solicitadas adicionam um botão à aba **Verificações** no GitHub que permite que alguém solicite execução de verificação para tomar medidas adicionais. A ação adicional é completamente configurável pelo seu aplicativo. Por exemplo, uma vez que o RuboCop tem um recurso para corrigir automaticamente os erros que encontra no código Ruby, seu servidor de CI pode usar um botão de ações solicitadas para permitir que as pessoas solicitem correções automáticas de erros. Quando alguém clica no botão, o aplicativo recebe o evento de `check_run` com uma ação `requested_action`. Cada ação solicitada tem um `identificador` que o aplicativo usa para determinar em qual botão foi clicado.

O código acima ainda não exige que o RuboCop corrija erros automaticamente. Você irá adicionar isso na próxima seção. Mas, primeiro, dê uma olhada no teste de CI que você acabou de criar ao iniciar o servidor `template_server.rb` novamente e ao criar um novo pull request:

```shell
$ ruby template_server.rb
```

As anotações serão exibidas na aba **Verificações**.

![Anotações da execução de verificação na aba verificações](/assets/images/2021/10/github-apps/github_apps_checks_annotations.png)

Observe o botão "Corrija isso" que você criou ao adicionar uma ação solicitada.

![Botão de ação solicitada de execução de verificação](/assets/images/2021/10/github-apps/github_apps_checks_fix_this_button.png)

Se as anotações estiverem relacionadas a um arquivo já incluído no PR, as anotações também serão exibidas na aba **Arquivos alterados**.

![Anotações da execução de verificação na aba Arquivos alterados](/assets/images/2021/10/github-apps/github_apps_checks_annotation_diff.png)

## Etapa 2.6. Corrigir erros do RuboCop automaticamente

Se você chegou até aqui, parabéns! 👏 Você já criou um teste de CI. Nesta seção, você irá adicionar mais um recurso que usa RuboCop para corrigir automaticamente os erros que encontra. Você já adicionou o botão "Corrija isso" na [seção anterior](#step-25-updating-the-check-run-with-ci-test-results). Agora você irá adicionar o código para lidar com o evento de execução de verificação `requested_action` acionado quando alguém clica no botão "Corrija isso".

A ferramenta do RuboCop [oferece](https://docs.rubocop.org/rubocop/usage/basic_usage.html#auto-correcting-offenses) a opção de linha de comando `--auto-correct` para corrigir automaticamente os erros que encontra. Ao usar o recurso `--auto-correct`, as atualizações são aplicadas aos arquivos locais do servidor. Você deverá fazer push das alterações no GitHub depois que o RuboCop fizer sua mágica.

Para fazer push para um repositório, seu aplicativo deve ter permissões de "conteúdo do repositório". Você redefiniu essa permissão na [Etapa 2.2. Clonar o repositório](#step-22-cloning-the-repository) para **Leitura & gravação**. Agora, você está pronto.

Para enviar arquivos do commit, o Git deve saber qual o [nome de usuário](/github/getting-started-with-github/setting-your-username-in-git/) e [e-mail](/articles/setting-your-commit-email-address-in-git/) devem ser associados ao commit. Adicione mais duas variáveis de ambiente ao seu arquivo `.env` para armazenar as configurações do nome (`GITHUB_APP_USER_NAME`) e do e-mail (`GITHUB_APP_USER_EMAIL`). Seu nome pode ser o nome do seu aplicativo e o e-mail pode ser qualquer e-mail que desejar para este exemplo. Por exemplo:

```ini
GITHUB_APP_USER_NAME=Octoapp
GITHUB_APP_USER_EMAIL=octoapp@octo-org.com
```

Uma vez atualizado o seu arquivo `.env` com o nome e o e-mail do autor e do committer, você estará pronto para adicionar código para ler as variáveis de ambiente e definir a configuração do Git. Você irá adicionar esse código em breve.

Quando alguém clica no botão "Corrija isso", seu aplicativo recebe o [webhook da execução de verificação](/webhooks/event-payloads/#check_run) com o tipo de ação `requested_action`.

Na [Etapa 1.4. Ao atualizar uma verificação, ](#step-14-updating-a-check-run) você atualizou o seu `event_handler` para lidar com a procura de ações no evento `check_run`. Você já tem uma afirmação de caso para lidar com os tipos de ação `criado` e `ressolicitado`:

``` ruby
when 'check_run'
  # Check that the event is being sent to this app
  if @payload['check_run']['app']['id'].to_s === APP_IDENTIFIER
    case @payload['action']
    when 'created'
      initiate_check_run
    when 'rerequested'
      create_check_run
  end
end
```

Adicione outra afirmação de `quando` após o caso `ressolicitado` para lidar com o evento `rerequested_action`:

``` ruby
quando 'requested_action'
  take_requested_action
```

Este código chama um novo método que irá lidar com todos os eventos `requested_action` para seu aplicativo. Adicione o seguinte método à seção de métodos auxiliares do seu código:

``` ruby
# Handles the check run `requested_action` event
# See /webhooks/event-payloads/#check_run
def take_requested_action
  full_repo_name = @payload['repository']['full_name']
  repository     = @payload['repository']['name']
  head_branch    = @payload['check_run']['check_suite']['head_branch']

  if (@payload['requested_action']['identifier'] == 'fix_rubocop_notices')
    clone_repository(full_repo_name, repository, head_branch)

    # Sets your commit username and email address
    @git.config('user.name', ENV['GITHUB_APP_USER_NAME'])
    @git.config('user.email', ENV['GITHUB_APP_USER_EMAIL'])

    # Automatically correct RuboCop style errors
    @report = `rubocop '#{repository}/*' --format json --auto-correct`

    pwd = Dir.getwd()
    Dir.chdir(repository)
    begin
      @git.commit_all('Automatically fix Octo RuboCop notices.')
      @git.push("https://x-access-token:#{@installation_token.to_s}@github.com/#{full_repo_name}.git", head_branch)
    rescue
      # Nothing to commit!
      puts 'Nothing to commit'
    end
    Dir.chdir(pwd)
    `rm -rf '#{repository}'`
  end
end
```

O código acima clona um repositório como o código que você adicionou na [Etapa 2.2. Clonar o repositório](#step-22-cloning-the-repository). Uma afirmação `se` verifica se o identificador da ação solicitada corresponde ao identificador do botão do RuboCop (`fix_rubocop_notices`). Quando correspondem, o código clona o repositório, define o nome de usuário e e-mail do Git e executa o RuboCop com a opção `--auto-correct`. A opção `--auto-correct` aplica automaticamente as alterações para os arquivos locais do servidor de CI.

Os arquivos são alterados localmente, mas você ainda deverá enviá-los para o GitHub. Você usará a gem útil `ruby-git` novamente para comprometer todos os arquivos. O Git tem um único comando que monta todos os arquivos modificados ou excluídos e compromete-os: `git commit -a`. Para fazer a mesma coisa utilizando o `ruby-git`, o código acima usa o método `commit_all`. Em seguida, o código faz push dos arquivos comprometidos para o GitHub usando o token de instalação, que usa o mesmo método de autenticação do comando `clonar` do Git. Por fim, ele remove o diretório do repositório para garantir que o diretório de trabalho seja preparado para o próximo evento.

Pronto! O código que você escreveu agora conclui o servidor de CI da API de verificação. 💪 Reinicie seu servidor `template_server.rb` e crie um novo pull request:

```shell
$ ruby template_server.rb
```

{% data reusables.apps.sinatra_restart_instructions %}

Desta vez, clique no botão "Corrija isso" para corrigir automaticamente os erros encontrados no RuboCop na aba **Verificações**.

Na aba **Commits**, você verá um novo commit pelo nome de usuário que você definiu na sua configuração do Git. Talvez seja necessário atualizar seu navegador para ver a atualização.

![Um novo commit para corrigir as notificações do Octo RuboCop automaticamente](/assets/images/2021/10/github-apps/github_apps_new_requested_action_commit.png)

Como um novo commit foi enviado para o repositório, você verá um novo conjunto de verificações para Octo RuboCop na aba **Verificações**. Mas desta vez não haverá erros, porque o RuboCop resolveu todos eles. 🎉

![Nenhum erro de conjunto de verificação ou de execução de verificação](/assets/images/2021/10/github-apps/github_apps_checks_api_success.png)

Você pode encontrar o código concluído para o aplicativo que você acabou de criar no arquivo `server.rb` no repositório [Criar testes de CI com a API de verificações](https://github.com/github-developer/creating-ci-tests-with-the-checks-api).

## Etapa 2.7. Dicas de segurança

O modelo de código do aplicativo GitHub já possui um método para verificar as cargas do webhook de entrada para garantir que sejam de uma fonte confiável. Se você não estiver validando as cargas do webhook, você deverá garantir que, quando nomes do repositório estiverem incluídos na carga do webhook, este não conterá comandos arbitrários que possam ser usados maliciosamente. O código abaixo valida que o nome do repositório contém apenas caracteres alfabéticos latinos, hifens e sublinhados. Para dar um exemplo completo, o código completo completo `server.rb` disponível no [repositório complementar](https://github.com/github-developer/creating-ci-tests-with-the-checks-api) para este início rápido inclui tanto o método de validação de recebimento das cargas do webhook quanto esta verificação do nome do repositório.

``` ruby
# This quickstart example uses the repository name in the webhook with
# command-line utilities. For security reasons, you should validate the
# repository name to ensure that a bad actor isn't attempting to execute
# arbitrary commands or inject false repository names. Se um nome de repositório
# for fornecido no webhook, certifique-se de que consiste apenas de
# caracteres alfabéticos latinos `-`, e `_`.
unless @payload['repository'].nil?
  halt 400 if (@payload['repository']['name'] =~ /[0-9A-Za-z\-\_]+/).nil?
end
```

## Solução de Problemas

Aqui estão alguns problemas comuns e algumas soluções sugeridas. Se você tiver qualquer outro problema, poderá pedir ajuda ou orientação em {% data variables.product.prodname_support_forum_with_url %}.

* **P:** Meu aplicativo não está enviando código para o GitHub. Eu não vejo as correções que o RuboCop faz automaticamente!

    **R:** Certifique-se de que você tem permissões de **Leitura & gravação** para "conteúdo de repositório" e que você está clonando o repositório com seu token de instalação. Consulte [Etapa 2.2. Clonar o repositório](#step-22-cloning-the-repository) para obter detalhes.

* **P:** Vejo um erro no saída de depuração de `template_server.rb` relacionado à clonagem do meu repositório.

    **R:** Se você vir o erro a seguir, você não excluiu o excluiu ou fez o checkout do repositório em um ou ambos os métodos `initiate_check_run` ou `take_requested_action`:

    ```shell
    2018-11-26 16:55:13 - Git::GitExecuteError - git  clone '--' 'https://x-access-token:ghs_9b2080277016f797074c4dEbD350745f4257@github.com/codertocat/octocat-breeds.git' 'Octocat-breeds'  2>&1:fatal: destination path 'Octocat-breeds' already exists and is not an empty directory.:
    ```

    Compare seu código com o arquivo `server.rb` para garantir que você tenha o mesmo código nos seus métodos `initiate_check_run` e `take_requested_action`.

* **P:** As novas execuções de verificação não estão aparecendo na aba "Verificações" no GitHub.

    **R:** Reinicie o Smee e execute novamente o seu servidor `template_server.rb`.

* **P:** Eu não vejo o botão "Executar tudo novamente" na aba "Verificações" no GitHub.

    **R:** Reinicie o Smee e execute novamente o seu servidor `template_server.rb`.

## Conclusão

Depois ler este guia, você aprendeu os princípios básicos para usar a API de verificação para criar um servidor de CI! Para resumir, você:

* Configurou seu servidor para receber eventos de API de verificação e criar execuções de verificação.
* Usou o RuboCop para verificar códigos nos repositórios e criar anotações para os erros.
* Implementou uma ação solicitada que corrige os erros do linter automaticamente.

## Próximas etapas

Aqui estão algumas ideias do que você pode fazer a seguir:

* Atualmente, o botão "Corrija isso" sempre é exibido. Atualize o código que você escreveu para exibir o botão "Corrija isso" somente quando o RuboCop encontrar erros.
* Se preferir que RuboCop não comprometa os arquivos diretamente para o branch principal, você pode atualizar o código para [criar um pull request](/rest/reference/pulls#create-a-pull-request) com um novo branch baseado no branch principal.
