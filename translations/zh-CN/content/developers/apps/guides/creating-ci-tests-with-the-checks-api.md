---
title: 使用检查 API 创建 CI 测试
intro: '使用 {% data variables.product.prodname_github_app %} 和检查 API 构建一个持续集成服务器以运行测试。'
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
shortTitle: 使用 Checks API 的 CI 测试
---

## 简介

本指南将介绍 [GitHub 应用程序](/apps/)和[检查 API](/rest/reference/checks)，您将使用它们来构建运行测试的持续集成 (CI) 服务器。

CI 是一种需要频繁提交代码到共享仓库的软件实践。 频繁提交代码能较早检测到错误，减少在查找错误来源时开发者需要调试的代码量。 频繁的代码更新也更便于从软件开发团队的不同成员合并更改。 这对开发者非常有益，他们可以将更多时间用于编写代码，而减少在调试错误或解决合并冲突上所花的时间。 🙌

CI 服务器托管运行 CI 测试的代码，如代码语法检查（检查样式格式）、安全检查、代码覆盖率以及针对仓库中新代码提交的其他检查。 CI 服务器甚至可以构建代码并将其部署到暂存或生产服务器。 有关您可以使用 GitHub 应用程序创建的 CI 测试类型的一些示例，请查看 GitHub Marketplace 中提供的[持续集成应用程序](https://github.com/marketplace/category/continuous-integration)。

{% data reusables.apps.app-ruby-guides %}

### 检查 API 概述

[检查 API](/rest/reference/checks) 允许您设置针对仓库中的每个代码提交自动运行的 CI 测试。 检查 API 在拉取请求的 **Checks（检查）**选项卡中报告 GitHub 上每个检查的详细信息。 使用检查 API，您可以创建带有特定代码行附加细节的注释。 注释在 **Checks（检查）**选项卡中可见。 当您为拉取请求中的文件创建注释时，注释也会显示在 **Files changed（文件已更改）**选项卡中。

_检查套件_是一组_检查运行_（单个 CI 测试）。 套件和运行都包含 GitHub 上的拉取请求中可见的_状态_。 您可以使用状态来确定何时代码提交引入错误。 对[受保护分支](/rest/reference/repos#branches)使用这些状态可防止用户草率地合并拉取请求。 更多信息请参阅“[关于受保护分支](/github/administering-a-repository/about-protected-branches#require-status-checks-before-merging)”。

每当有新代码推送到仓库时，检查 API 会将 [`check_suite` web 挂钩事件](/webhooks/event-payloads/#check_suite)发送到仓库中安装的所有 GitHub 应用程序。 要接收所有检查 API 事件操作，应用程序必须具有 `checks:write` 权限。 GitHub 使用默认流程自动为仓库中的新代码提交创建 `check_suite` 事件，但您可以根据需要[更新检查套件的仓库首选项](/rest/reference/checks#update-repository-preferences-for-check-suites)。 以下是默认流程的工作方式：

1. 每当有人向仓库推送代码时，GitHub 会将带有 `requested` 操作的 `check_suite` 事件发送到仓库中安装的所有具有 `checks:write` 权限的 GitHub 应用程序。 此事件让应用程序知道推送了代码，并且 GitHub 已自动创建新的检查套件。
1. 应用程序收到此事件后，它可以[添加检查运行](/rest/reference/checks#create-a-check-run)到该套件。
1. 检查运行可包括显示在特定代码行上的[注释](/rest/reference/checks#annotations-object)。

**在本指南中，您将学习如何：**

* 第 1 部分：使用检查 API 为 CI 服务器设置框架。
  * 将 GitHub 应用程序配置为接收检查 API 事件的服务器。
  * 当仓库收到新推送的提交时，为 CI 测试创建新的检查运行。
  * 当用户在 GitHub 上请求该操作时，重新运行检查。
* 第 2 部分：通过添加语法检查 CI 测试在您创建的 CI 服务器框架上构建。
  * 使用 `status`、`conclusion` 和 `output` 详细信息更新检查运行。
  * 在 GitHub 显示在**Checks（检查）** 和**Files Changed（文件已更改）**选项卡中的 代码行上创建注释。
  * 通过在 **Checks（检查）**选项卡中显示 “Fix this（修复此问题）”按钮来自动修复语法检查建议。

要了解完成此快速入门后检查 API CI 服务器将执行的操作，请查看以下演示：

![检查 API CI 服务器快速入门演示](/assets/images/2021/10/github-apps/github_apps_checks_api_ci_server.gif)

## 基本要求

在开始之前，如果您尚未熟悉 [GitHub 应用程序](/apps/)、[web 挂钩](/webhooks)和[检查 API](/rest/reference/checks)，可能需要先熟悉一下。 您将在 [REST API 文档](/rest)中找到更多 API。 检查 API 也可用于 [GraphQL]({% ifversion ghec %}/free-pro-team@latest{% endif %}/graphql)，但本快速入门指南侧重于 REST。 更多信息请参阅 GraphQL [检查套件]({% ifversion ghec %}/free-pro-team@latest{% endif %}/graphql/reference/objects#checksuite)和[检查运行]({% ifversion ghec %}/free-pro-team@latest{% endif %}/graphql/reference/objects#checkrun)对象。

您将使用 [Ruby 编程语言](https://www.ruby-lang.org/en/)、[Smee](https://smee.io/) web 挂钩有效负载交付服务、用于 GitHub REST API 的 [Octokit.rb Ruby 库](http://octokit.github.io/octokit.rb/)以及 [Sinatra web 框架](http://sinatrarb.com/)来创建检查 API CI 服务器应用程序。

完成此项目并不需要您精通任何这些工具或概念。 本指南将引导您完成所有必需的步骤。 在开始使用检查 API 创建 CI 测试之前，您需要执行以下操作：

1. 克隆[使用检查 API 创建 CI 测试](https://github.com/github-developer/creating-ci-tests-with-the-checks-api)仓库。
  ```shell
    $ git clone https://github.com/github-developer/creating-ci-tests-with-the-checks-api.git
  ```

  在目录中，您将找到包含本快速入门将要使用的模板代码的 `template_server.rb` 文件以及包含已完成项目代码的 `server.rb` 文件。

1. 请按照“[设置开发环境](/apps/quickstart-guides/setting-up-your-development-environment/)”快速入门中的步骤来配置和运行应用程序服务器。 **注：**不要[克隆 GitHub 应用程序模板仓库](/apps/quickstart-guides/setting-up-your-development-environment/#prerequisites)，而应使用在本快速入门的上一步中克隆的仓库中的 `template_server.rb` 文件。

  如果您之前已完成 GitHub 应用程序快速入门，请确保注册一个_新_ GitHub 应用程序，并开启一个新的 Smee 通道用于本快速入门。

  如果在设置模板 GitHub 应用程序时遇到问题，请参阅[故障排除](/apps/quickstart-guides/setting-up-your-development-environment/#troubleshooting)部分。

## 第 1 部分。 创建检查 API 接口

在本部分，您将添加必要的代码以接收 `check_suite` web 挂钩事件并创建和更新检查运行。 您还将学习在 GitHub 上重新请求检查时如何创建检查运行。 在本节的最后，您将能够查看在 GitHub 拉取请求中创建的检查运行。

您的检查运行不会对本节中的代码执行任何检查。 您将在[第 2 部分：创建 Octo RuboCop CI 测试](#part-2-creating-the-octo-rubocop-ci-test)中添加该功能。

您应该已经配置了可将 web 挂钩有效负载转发到本地服务器的 Smee 通道。 您的服务器应该正在运行并连接到您注册并安装在测试仓库的 GitHub 应用程序。 如果您尚未完成“[设置开发环境](/apps/quickstart-guides/setting-up-your-development-environment/)”中的步骤，则需要先完成这些步骤才能继续。

让我们开始吧！ 以下是您将在第 1 部分中完成的步骤：

1. [更新应用程序权限](#step-11-updating-app-permissions)
1. [添加事件处理](#step-12-adding-event-handling)
1. [创建检查运行](#step-13-creating-a-check-run)
1. [更新检查运行](#step-14-updating-a-check-run)

## 步骤 1.1. 更新应用程序权限

如果您在[首次注册应用程序](#prerequisites)时接受了 默认权限，则意味着您的应用程序无法访问大多数资源。 对于此示例，您的应用程序将需要读取和写入检查的权限。

要更新应用程序的权限：

1. 从[应用程序设置页面](https://github.com/settings/apps)选择应用程序，然后单击边栏中的 **Permissions & Webhooks（权限和 web 挂钩）**。
1. 在“Permissions（权限）”部分，找到“Checks（检查）”，然后在其旁边的“Access（访问权限）”下拉列表中选择 **Read & write（读取和写入）**。
1. 在“Subscribe to events（订阅事件）”部分，选择 **Check suite（检查套件）**和 **Check run（检查运行）**以订阅这些事件。
{% data reusables.apps.accept_new_permissions_steps %}

太好了！ 您的应用程序现在有权限执行所需的任务。 现在您可以添加代码来处理事件。

## 步骤 1.2. 添加事件处理

现在，您的应用程序已订阅**检查套件**和**检查运行**事件，它将开始接收 [`check_suite`](/webhooks/event-payloads/#check_suite) 和 [`check_run`](/webhooks/event-payloads/#check_run) web 挂钩。 GitHub 将 web 挂钩有效负载作为 `POST` 请求发送。 因为您已将 Smee web 挂钩有效负载转发到 `http://localhost/event_handler:3000`，因此您的服务器将在 `post '/event_handler'` 路由中接收 `POST` 请求有效负载。

您在[前提条件](#prerequisites)部分中下载的 `template_server.rb` 文件中已包括空 `post '/event_handler'` 路由。 空路由如下所示：

``` ruby
  post '/event_handler' do

    # # # # # # # # # # # #
    # ADD YOUR CODE HERE  #
    # # # # # # # # # # # #

    200 # success status
  end
```

通过添加以下代码，使用此路由来处理 `check_suite` 事件：

``` ruby
# Get the event type from the HTTP_X_GITHUB_EVENT header
case request.env['HTTP_X_GITHUB_EVENT']
when 'check_suite'
  # A new check_suite has been created. Create a new check run with status queued
  if @payload['action'] == 'requested' || @payload['action'] == 'rerequested'
    create_check_run
  end
end
```

GitHub 发送的每个事件都包含一个名为 `HTTP_X_GITHUB_EVENT` 的请求标头，它指示 `POST` 请求中的事件类型。 现在，您只关注类型为 `check_suite` 的事件，它在创建新的检查套件时触发。 每个事件都有一个附加的 `action` 字段，它指示触发事件的操作类型。 对于 `check_suite`，`action` 字段可以是 `requested`、`rerequested` 或 `completed`。

每当有代码推送到仓库时，`requested` 操作会请求检查运行，而 `rerequested` 操作则请求您对仓库中已经存在的代码重新运行检查。 由于 `requested` 和 `rerequested` 操作都需要创建检查运行，因此您将调用名为 `create_check_run` 的小助手。 现在我们来编写该方法。

## 步骤 1.3. 创建检查运行

如果希望其他路由也使用此新方法，您可以将其添加为 [Sinatra 小助手](https://github.com/sinatra/sinatra#helpers)。 在 `helpers do` 下，添加此 `create_check_run` 方法：

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

此代码使用 [create_check_run 方法](https://rdoc.info/gems/octokit/Octokit%2FClient%2FChecks:create_check_run)调用“[创建检查运行](/rest/reference/checks#create-a-check-run)”端点。

要创建检查运行，只有两个输入参数是必需的：`name` 和 `head_sha`。 在本快速入门的后面部分，我们将使用 [RuboCop](https://rubocop.readthedocs.io/en/latest/) 来实现 CI 测试，这就是此处使用名称 "Octo RuboCop" 的原因，但您可以选择任何想要用于检查运行的名称。

您现在仅提供必需的参数以使基本功能正常工作，但是稍后您将在收集有关检查运行的更多信息时更新检查运行。 默认情况下，GitHub 将 `status` 设置为 `queued`。

GitHub 为特定的提交 SHA 创建检查运行，这就是 `head_sha` 是必需参数的原因。 您可以在 web 挂钩有效负载中找到提交 SHA。 虽然您现在只为 `check_suite` 事件创建了检查运行，但是已经知道事件有效负载中的 `check_suite` 和 `check_run` 对象中都包含了 `head_sha`。

在上面的代码中，您使用[三元运算符](https://ruby-doc.org/core-2.3.0/doc/syntax/control_expressions_rdoc.html#label-Ternary+if)（其工作方式类似于 `if/else` 语句）检查有效负载是否包含 `check_run` 对象。 如果是，则从 `check_run` 对象读取 `head_sha`，否则将从 `check_suite` 对象读取它。

要测试此代码，请从您的终端重启服务器：

```shell
$ ruby template_server.rb
```

{% data reusables.apps.sinatra_restart_instructions %}

现在，在安装应用程序的仓库中打开拉取请求。 您的应用程序应该通过对拉取请求创建检查运行来响应。 单击 **Checks（检查）**选项卡，您应该会看到以下内容：

![排队检查运行](/assets/images/2021/10/github-apps/github_apps_queued_check_run.png)

如果您在“Checks（检查）”选项卡中看到其他应用程序，则意味着您的仓库中安装了其他应用程序，它们对检查具有 **Read & write（读取和写入）** 权限，并且订阅了 **Check suite（检查套件）**和 **Check run（检查运行）**事件。

太好了！ 您已告诉 GitHub 创建检查运行。 您可以在黄色图标旁边看到检查运行状态设置为 `queued`。 接下来，您需要等待 GitHub 创建检查运行并更新其状态。

## 步骤 1.4. 更新检查运行

当 `create_check_run` 方法运行时，它会要求 GitHub 创建新的检查运行。 当 GitHub 完成创建检查运行时，您将收到带有 `created` 操作的 `check_run` web 挂钩事件。 该事件是您开始运行检查的信号。

您需要更新事件处理程序以查找 `created` 操作。 在更新事件处理程序时，可以为 `rerequested` 操作添加条件。 当某人通过单击“Re-run（重新运行）”按钮在 GitHub 上重新运行单个测试时，GitHub 将 `rerequested` 检查运行事件发送到您的应用程序。 当检查运行为 `rerequested` 时，您需要启动整个进程并创建新的检查运行。

要在 `post '/event_handler'` 路由中包含 </code>check_run</code> 事件的条件，请在 `case request.env['HTTP_X_GITHUB_EVENT']</0> 案例下添加以下代码：</p>

<pre><code class="ruby">when 'check_run'
  # Check that the event is being sent to this app
  if @payload['check_run']['app']['id'].to_s === APP_IDENTIFIER
    case @payload['action']
    when 'created'
      initiate_check_run
    when 'rerequested'
      create_check_run
    end
  end
`</pre>

GitHub 将 `created` 检查运行的所有事件发送到仓库中安装的每个具有必要检查权限的应用程序。 这意味着您的应用程序将收到其他应用程序创建的检查运行。 `created` 检查运行与 `requested` 或 `rerequested` 检查套件稍有不同，GitHub 只将其发送给被请求运行检查的应用程序。 上面的代码查找检查运行的应用程序 ID。 这将过滤掉仓库中其他应用程序的所有检查运行。

接下来，您将编写 `initiate_check_run` 方法，您将在其中更新检查运行状态并准备开始 CI 测试。

在本节中，您尚未开始 CI 测试，但是您将演练如何更新检查运行的状态，从 `queued` 到 `pending` 然后从 `pending` 到 `completed`，以查看检查运行的总体流程。 在“[第 2 部分：创建 Octo RuboCop CI 测试](#part-2-creating-the-octo-rubocop-ci-test)”中，您将添加实际执行 CI 测试的代码。

让我们创建 `initiate_check_run` 方法并更新检查运行的状态。 将以下代码添加到小助手部分：

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

上述代码使用 [`update_check_run` Octokit 方法](https://rdoc.info/gems/octokit/Octokit%2FClient%2FChecks:update_check_run) 调用“[更新检查运行](/rest/reference/checks#update-a-check-run)”API 端点，以更新已创建的检查运行。

以下是此代码的作用。 首先，它将检查运行的状态更新为 `in_progress`，并默示将 `started_at` 时间设置为当前时间。 在本快速入门的[第 2 部分](#part-2-creating-the-octo-rubocop-ci-test)，您将添加代码以在 `***** RUN A CI TEST *****` 下开始真正的 CI 测试。 现在，您将该部分保留为占位符，因此后面的代码将模拟 CI 流程成功并且所有测试都通过。 最后，代码将检查运行的状态再次更新为 `completed`。

在“[更新检查运行](/rest/reference/checks#update-a-check-run)”文档中，您会注意到，当您提供状态 `completed` 时，`conclusion` 和 `completed_at` 参数是必需的。 `conclusion` 总结检查运行的结果，可以是 `success`、`failure`、`neutral`、`cancelled`、`timed_out` 或 `action_required`。 您将结论设置为 `success`，将 `completed_at` 时间设置为当前时间，并将状态设置为 `completed`。

您还可以提供有关检查操作的更多详细信息，但这些内容将在下一部分进行介绍。 让我们重新运行 `template_server.rb` 来测试此代码：

```shell
$ ruby template_server.rb
```

转到打开的拉取请求，然后单击 **Checks（检查）**选项卡。 单击左上角的“Re-run all（全部重新运行）”按钮。 您应该会看到检查运行的状态从 `pending` 变成 `in_progress`，最后变成 `success`：

![完整的检查运行](/assets/images/2021/10/github-apps/github_apps_complete_check_run.png)

## 第 2 部分。 创建 Octo RuboCop CI 测试

[RuboCop](https://rubocop.readthedocs.io/en/latest/) 是 Ruby 代码语法检查和格式化工具。 它检查 Ruby 代码以确保其符合“[Ruby 样式指南](https://github.com/rubocop-hq/ruby-style-guide)”。 RuboCop 有三个主要功能：

* 分析检查代码样式
* 代码格式化
* 使用 `ruby -w` 替换本地 Ruby 分析功能。

您已经创建了用于接收检查 API 事件和创建检查运行的接口，现在，您可以创建实现 CI 测试的检查运行。

您的应用程序将在 CI 服务器上运行 RuboCop，并创建检查运行（本例中为 CI 测试），以报告 RuboCop 向 GitHub 报告的结果。

检查 API 允许您报告关于每个检查运行的丰富细节，包括状态、图像、摘要、注释和请求的操作。

注释是关于仓库中特定代码行的信息。 注释允许您精确定位和可视化要显示其他信息的代码确切部分。 这些信息可以是任何内容：例如，注释、错误或警告。 本快速入门使用注释来可视化 RuboCop 错误。

为了利用请求的操作，应用程序开发者可以在拉取请求的 **Checks（检查）**选项卡中创建按钮。 当有人单击这些按钮之一时，该单击操作将发送 `requested_action` `check_run` 事件到 GitHub 应用程序。 应用程序执行的操作完全由应用程序开发者配置。 此快速入门将引导您添加一个按钮，允许用户请求 RuboCop 修复它发现的错误。 RuboCop 支持使用命令行选项自动修复错误，您将配置 `requested_action` 以利用此选项。

让我们开始吧！ 以下是您将在本部分中完成的步骤：

1. [添加 Ruby 文件](#step-21-adding-a-ruby-file)
1. [克隆仓库](#step-22-cloning-the-repository)
1. [运行 RuboCop](#step-23-running-rubocop)
1. [收集 RuboCop 错误](#step-24-collecting-rubocop-errors)
1. [使用 CI 测试结果更新检查运行](#step-25-updating-the-check-run-with-ci-test-results)
1. [自动修复 RuboCop 错误](#step-26-automatically-fixing-rubocop-errors)
1. [安全提示](#step-27-security-tips)

## 步骤 2.1. 添加 Ruby 文件

您可以传递特定文件或整个目录供 RuboCop 检查。 在本快速入门中，您将在整个目录上运行 RuboCop。 由于 RuboCop 只检查 Ruby 代码，因此您的仓库中至少需要一个含有错误的 Ruby 文件。 下面提供的示例文件包含一些错误。 将此示例 Ruby 文件添加到安装应用程序的仓库（确保使用 `.rb` 扩展名命名文件，如 `myfile.rb`）：

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

## 步骤 2.2. 克隆仓库

RuboCop 可用作命令行实用工具。 这意味着您的 GitHub 应用程序将需要克隆 CI 服务器上仓库的本地副本，以便 RuboCop 可以解析文件。 要在 Ruby 应用程序中运行 Git 操作，您可以使用 [ruby-git](https://github.com/ruby-git/ruby-git) gem。

`building-a-checks-api-ci-server` 仓库中的 `Gemfile` 已包含 ruby-git gem，您在[前提步骤](#prerequisites)中运行 `bundle install` 时安装了它。 要使用 gem，请将此代码添加到 `template_server.rb` 文件的顶部：

``` ruby
require 'git'
```

您的应用程序需要“仓库内容”的读取权限才能克隆仓库。 在本快速入门后面的部分，您需要将内容推送到 GitHub，这需要写入权限。 现在将应用程序的“仓库内容”权限设置为 **Read & write（读取和写入）**，这样以后就不需要再更新它了。 要更新应用程序的权限：

1. 从[应用程序设置页面](https://github.com/settings/apps)选择应用程序，然后单击边栏中的 **Permissions & Webhooks（权限和 web 挂钩）**。
1. 在“Permissions（权限）”部分，找到“Repository contents（仓库内容）”，然后在其旁边的“Access（访问权限）”下拉列表中选择 **Read & write（读取和写入）**。
{% data reusables.apps.accept_new_permissions_steps %}

要使用 GitHub 应用程序的权限克隆仓库，您可以使用该应用程序的安装令牌 (`x-access-token:<token>`)，如下例所示：

```shell
git clone https://x-access-token:<token>@github.com/<owner>/<repo>.git
```

上面的代码通过 HTTP 克隆仓库。 它需要完整的仓库名称，其中包括仓库所有者（用户或组织）和仓库名称。 例如，[octocat Hello-World](https://github.com/octocat/Hello-World) 仓库的全名是 `octocat/hello-world`。

应用程序克隆仓库后，它需要拉取最新的代码更改并检出特定的 Git ref。 执行所有这些操作的代码将很好地适应其自己的方法。 要执行这些操作，该方法需要仓库的名称和全名以及要检出的 ref。 Ref 可以是提交 SHA、分支或标记。 将以下新方法添加到 `template_server.rb` 中的辅助方法部分：

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

上面的代码通过应用程序的安装令牌使用 `rubby-git` gem 来克隆仓库。 此代码在 `template_server.rb` 的目录中克隆代码。 要在仓库中运行 Git 命令，代码需要更改为仓库目录。 在更改目录之前，代码将当前工作目录存储在变量 (`pwd`) 中，以便在退出 `clone_repository` 方法之前记住要返回的位置。

此代码从仓库目录获取并合并最新的更改 (`@git.pull`)，检出 ref (`@git.checkout(ref)`)，然后将目录改回原始工作目录 (`pwd`)。

现在，您有了克隆仓库并检出 ref 的方法。 接下来，您需要添加代码来获取所需的输入参数，并调用新的 `clone_repository` 方法。 在 `initiate_check_run` 辅助方法的 `***** RUN A CI TEST *****` 注释下添加以下代码：

``` ruby
# ***** RUN A CI TEST *****
full_repo_name = @payload['repository']['full_name']
repository     = @payload['repository']['name']
head_sha       = @payload['check_run']['head_sha']

clone_repository(full_repo_name, repository, head_sha)
```

上面的代码从 `check_run` web 挂钩有效负载获取完整的仓库名称和注释的头部 SHA。

## 步骤 2.3. 运行 RuboCop

太好了！ 您正在克隆仓库并使用 CI 服务器创建检查运行。 现在，您将了解 [RuboCop 语法检查](https://docs.rubocop.org/rubocop/usage/basic_usage.html#code-style-checker)和[检查 API 注释](/rest/reference/checks#create-a-check-run)的实质内容。

下面的代码运行 RuboCop 并以 JSON 格式保存样式代码错误。 将此代码添加到您在[上一步](#step-22-cloning-the-repository)中添加的 `clone_repository` 调用之下，更新要完成检查运行的代码之上。

``` ruby
# Run RuboCop on all files in the repository
@report = `rubocop '#{repository}' --format json`
logger.debug @report
`rm -rf #{repository}`
@output = JSON.parse @report
```

上面的代码在仓库目录中的所有文件上运行 RuboCop 。 选项 `--format json` 是将分析结果的副本保存为机器可解析格式的方便方法。 有关 JSON 格式的详细信息和示例，请参阅 [RuboCop 文档](https://docs.rubocop.org/rubocop/formatters.html#json-formatter)。

由于此代码将 RuboCop 结果存储在 `@report` 变量中，因此可以安全地删除仓库的检出。 此代码还解析 JSON，因此您可以使用 `@output` 变量轻松访问 GitHub 应用程序中的键和值。

{% note %}

**注：**用于删除仓库的命令 (`rm -rf`) 无法撤销。 请参阅[步骤 2.7. 安全提示](#step-27-security-tips)了解如何检查 web 挂钩中是否注入了可用于删除与应用程序预期不同的目录的恶意命令。 例如，如果一个恶意行为者发送了一个仓库名称为 `./` 的 web 挂钩，您的应用程序将会删除根目录。 😱 如果出于某些原因，您_没有_使用方法 `verify_webhook_signature`（包含在 `template_server.rb` 中）来验证 web 挂钩的发送者，请确保检查仓库名称是否有效。

{% endnote %}

您可以测试此代码是否有效，并在服务器的调试输出中查看 RuboCop 报告的错误。 再次启动 `template_server.rb` 服务器，并在测试应用程序的仓库中创建新的拉取请求：

```shell
$ ruby template_server.rb
```

您应该在调试输出中看到分析错误，尽管它们不是用格式打印的。 您可以使用 [JSON 格式化程序](https://jsonformatter.org/)之类的 web 工具来格式化 JSON 输出，例如以下格式化的分析错误输出：

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

## 步骤 2.4. 收集 RuboCop 错误

`@output` 变量包含 RuboCop 报告的已解析 JSON 结果。 如上所示，结果包含 `summary` 部分，您的代码可使用它快速确定是否存在错误。 如果没有报告错误，以下代码将检查运行结论设置为 `success`。 RuboCop 报告 `files` 数组中每个文件的错误，如果存在错误，则需要从文件对象中提取一些数据。

检查 API 允许您为特定代码行创建注释。 创建或更新检查运行时，可以添加注释。 在本快速入门中，您将使用注释[更新检查运行](/rest/reference/checks#update-a-check-run)。

检查 API 将注释数量限制为每个 API 请求最多 50 个注释。 要创建 50 个以上的注释，您必须向[更新检查运行](/rest/reference/checks#update-a-check-run)端点发出多个请求。 例如，要创建 105 个注释，您需要调用[更新检查运行](/rest/reference/checks#update-a-check-run)端点三次。 前两个请求各有 50 个注释，第三个请求将包括其余五个注释。 每次更新检查运行时，注释都会添加到已经存在的检查运行注释列表中。

检查运行会将注释作为对象数组。 每个注释对象必须包括 `path`、`start_line`、`end_line`、`annotation_level` 和 `message`。 RuboCop 还提供 `start_column` 和 `end_column`， 因此您可以在注释中包括这些可选参数。 注释只支持同一行上的 `start_column` 和 `end_column`。 更多信息请参阅 [`annotations` 对象](/rest/reference/checks#annotations-object-1)参考文档。

您将从 RuboCop 中提取创建每个注释所需的信息。 将以下代码追加到您[上一节](#step-23-running-rubocop)中添加的代码：

``` ruby
annotations = []
# You can create a maximum of 50 annotations per request to the Checks
# API. To add more than 50 annotations, use the "Update a check run" API
# endpoint. This example code limits the number of annotations to 50.
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

此代码将注释总数限制为 50。 但是，您可以修改此代码以更新每批 50 个注释的检查运行。 上面的代码包含变量 `max_annotations`，它将限制设置为 50，用于循环遍历超限问题。

当 `offense_count` 为零时，CI 测试为 `success`。 如果存在错误，此代码会将结论设置为 `neutral`，以防止严格执行来自代码语法检查的错误。 但如果您想确保检查套件在发现分析错误时失败，您可以将结论更改为 `failure`。

当报告错误时，上面的代码将遍历 RuboCop 报告中的 `files` 数组。 对于每个文件，它会提取文件路径，并将注释级别设置为 `notice`。 您可以更进一步，为每种类型的 [RuboCop Cop](https://docs.rubocop.org/rubocop/cops.html) 设置特定的警告级别，但本快速入门为简单起见，将所有错误都设置为 `notice` 级别。

此代码还会遍历 `offenses` 数组中的每个错误，并收集超限和错误消息的位置。 提取所需的信息后，代码将为每个错误创建一个注释，并将其存储在 `annotations` 数组中。 由于注释只支持同一行上的开始和结束列，因此，只有在开始和结束行的值相同的情况下，才会将 `start_column` 和 `end_column` 添加到 `annotation` 对象中。

此代码尚未为检查运行创建注释。 您将在下一节中添加该代码。

## 步骤 2.5. 使用 CI 测试结果更新检查运行

GitHub 的每个检查运行都包括 `output` 对象，其中包含 `title`、`summary`、`text`、`annotations` 和 `images`。 只有 `summary` 和 `title` 是 `output` 的必需参数，但仅仅这些参数并不能提供太多细节，因此本快速入门还添加了 `text` 和 `annotations`。 此处的代码没有添加图片，但是您可以根据需要随意添加！

对于 `summary`，此示例使用 RuboCop 的摘要信息，并添加一些换行符 (`\n`) 来格式化输出。 您可以自定义要添加到 `text` 参数的内容，而此示例将 `text` 参数设置为 RuboCop 版本。 要设置 `summary` 和 `text`，请将此代码追加到您在[上一节](#step-24-collecting-rubocop-errors)中添加的代码中：

``` ruby
# Updated check run summary and text parameters
summary = "Octo RuboCop summary\n-Offense count: #{@output['summary']['offense_count']}\n-File count: #{@output['summary']['target_file_count']}\n-Target file count: #{@output['summary']['inspected_file_count']}"
text = "Octo RuboCop version: #{@output['metadata']['rubocop_version']}"
```

现在您已经获得了更新检查运行所需的所有信息。 在[本快速入门的前半部分](#step-14-updating-a-check-run)，您添加了此代码以将检查运行的状态设置为 `success`：

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

您需要更新该代码以使用基于 RuboCop 结果设置的 `conclusion` 变量（`success` 或 `neutral`）。 您可以使用以下内容更新代码：

``` ruby
# Mark the check run as complete! And if there are warnings, share them.
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

现在，您正在根据 CI 测试的状态设置结论，并且添加了 RuboCop 结果的输出，您已经创建了 CI 测试！ 恭喜。 🙌

上面的代码还通过 `actions` 对象向您的 CI 服务器添加了一个名为 [requested actions](https://developer.github.com/changes/2018-05-23-request-actions-on-checks/) 的功能。 {% ifversion fpt or ghec %}（请注意，这与 [GitHub 操作](/actions)无关。） {% endif %}请求的操作在 GitHub 的 **Checks（检查）**选项卡中添加一个按钮，允许用户请求检查运行执行附加操作。 附加操作完全由您的应用程序配置。 例如，由于 RuboCop 具有自动修复在 Ruby 代码中发现的错误的功能，因此您的 CI 服务器可以使用请求操作按钮来允许用户请求自动修复错误。 当有人单击该按钮时，应用程序会收到带有 `requested_action` 操作的 `check_run` 事件。 每个请求的操作都有一个 `identifier`，应用程序使用它来确定哪个按钮被单击。

上面的代码还没有让 RuboCop 自动修复错误。 您将在下一节中添加该功能。 但我们先通过再次启动 `template_server.rb` 服务器并创建一个新的拉取请求，来看看您刚刚创建的 CI 测试：

```shell
$ ruby template_server.rb
```

注释将显示在 **Checks（检查）**选项卡中。

![检查选项卡中的检查运行注释](/assets/images/2021/10/github-apps/github_apps_checks_annotations.png)

请注意您通过添加请求的操作创建的“Fix this（修复此问题）”按钮。

![检查运行请求操作按钮](/assets/images/2021/10/github-apps/github_apps_checks_fix_this_button.png)

如果注释与 PR 中已包含的文件有关，则注释还将显示在 **Files changed（文件已更改）**选项卡中。

![文件已更改选项卡中的检查运行注释](/assets/images/2021/10/github-apps/github_apps_checks_annotation_diff.png)

## 步骤 2.6. 自动修复 RuboCop 错误

如果您走到了这一步，为您点赞！ 👏 您已经创建了 CI 测试。 在本节中，您将添加另外一个功能，即使用 RuboCop 自动修复它发现的错误。 您在[上一节](#step-25-updating-the-check-run-with-ci-test-results)中已经添加了“Fix this（修复此问题）”按钮。 现在，您将添加代码以处理当有人单击“Fix this（修复此问题）”按钮时触发的 `requested_action` 检查运行事件。

RuboCop 工具[提供](https://docs.rubocop.org/rubocop/usage/basic_usage.html#auto-correcting-offenses) `--auto-correct` 命令行选项，以自动修复它发现的错误。 使用 `--auto-correct` 功能时，更新将应用于服务器上的本地文件。 在 RuboCop 发挥作用之后，您需要将更改推送到 GitHub。

要推送到仓库，您的应用程序必须具备“仓库内容”的写入权限。 您在[步骤 2.2 中重新设置了该权限。 将仓库克隆](#step-22-cloning-the-repository)为**Read & write（读取和写入）**，现在所有设置就绪。

要提交文件，Git 必须知道哪些[用户名](/github/getting-started-with-github/setting-your-username-in-git/)和[电子邮件](/articles/setting-your-commit-email-address-in-git/)与提交关联。 在 `.env` 文件中再添加两个变量，以存储名称 (`GITHUB_APP_USER_NAME`) 和电子邮件 (`GITHUB_APP_USER_EMAIL`) 设置。 您的名称可以是应用程序名称，电子邮件可以是您在本例中想使用的任何电子邮件地址。 例如：

```ini
GITHUB_APP_USER_NAME=Octoapp
GITHUB_APP_USER_EMAIL=octoapp@octo-org.com
```

使用作者和提交者的名称和电子邮件更新 `.env` 文件后，即可准备添加代码以读取环境变量并设置 Git 配置。 您很快就将添加该代码。

当有人单击“Fix this（修复此问题）”按钮时，应用程序会收到操作类型为 `requested_action` 的[检查运行 web 挂钩](/webhooks/event-payloads/#check_run)。

在[步骤 1.4. 更新检查运行时，](#step-14-updating-a-check-run)您更新了 `event_handler` 以处理 `check_run` 事件中的查找操作。 您已经有一个 case 语句来处理 `created` 和 `rerequested` 操作类型：

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

在 `rerequested` case 之后添加另一个 `when` 语句来处理 `rerequested_action` 事件：

``` ruby
when 'requested_action'
  take_requested_action
```

这个代码调用一个新方法来处理应用程序的所有 `requested_action` 事件。 将以下方法添加到代码的辅助方法部分：

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

上面的代码将克隆仓库，就像您在[步骤 2.2. 中添加的代码一样。 克隆仓库](#step-22-cloning-the-repository)。 `if` 语句检查请求操作的标识符是否匹配 RuboCop 按钮标识符 (`fix_rubocop_notices`)。 当它们匹配时，代码将克隆仓库，设置 Git 用户名和电子邮件，并使用选项 `--auto-correct` 运行 RuboCop。 `--auto-correct` 选项将更改自动应用于本地 CI 服务器文件。

文件在本地更改，但您仍然需要将它们推送到 GitHub。 您将再次使用方便的 `ruby-git` gem 提交所有文件。 Git 有一个命令可以暂存所有已修改或删除的文件并提交它们：`git commit -a`。 为了使用 `rubby-git` 实现同样的功能，上面的代码使用 `commit_all` 方法。 然后，代码使用与 Git `clone` 命令相同的身份验证方法，通过安装令牌将提交的文件推送到GitHub。 最后，它删除仓库目录，以确保为下一个事件准备工作目录。

搞定！ 您编写的代码现在完成了检查 API CI 服务器的构建。 💪 再次重新启动 `template_server.rb` 服务器并创建新的拉取请求：

```shell
$ ruby template_server.rb
```

{% data reusables.apps.sinatra_restart_instructions %}

现在，单击“Fix this（修复此问题）”按钮以自动修复 RuboCop 在 **Checks（检查）**选项卡中发现的错误。

在 **Commits（提交）**选项卡中，您会看到由 Git 配置中设置的用户名提供的全新提交。 您可能需要刷新浏览器才能看到更新。

![自动修复 Octo RuboCop 通知的新提交](/assets/images/2021/10/github-apps/github_apps_new_requested_action_commit.png)

由于新的提交被推送到仓库，您将在 **Checks（检查）**选项卡中看到新的 Octo RuboCop 检查套件。 但这次没有任何错误，因为 RuboCop 已经修复了所有错误。 🎉

![没有检查套件或检查运行错误](/assets/images/2021/10/github-apps/github_apps_checks_api_success.png)

您可以在[使用检查 API 创建 CI 测试](https://github.com/github-developer/creating-ci-tests-with-the-checks-api)仓库的 `server.rb` 文件中找到您刚才构建的应用程序的完整代码。

## 步骤 2.7. 安全提示

模板 GitHub 应用程序代码已经有方法来验证传入的 web 挂钩有效负载，以确保它们来自受信任的源。 如果不验证 web 挂钩有效负载，则需要确保当仓库名称包含在 web 挂钩有效负载中时，该 web 挂钩不包含可能被恶意使用的任意命令。 下面的代码将验证仅包含拉丁字母、连字符和下划线的仓库名称。 为了提供完整的示例，[配套仓库](https://github.com/github-developer/creating-ci-tests-with-the-checks-api)中提供本快速入门的完整 `server.rb` 代码，包括验证传入 web 挂钩有效负载的方法和验证仓库名称的检查。

``` ruby
# This quickstart example uses the repository name in the webhook with
# command-line utilities. For security reasons, you should validate the
# repository name to ensure that a bad actor isn't attempting to execute
# arbitrary commands or inject false repository names. If a repository name
# is provided in the webhook, validate that it consists only of latin
# alphabetic characters, `-`, and `_`.
unless @payload['repository'].nil?
  halt 400 if (@payload['repository']['name'] =~ /[0-9A-Za-z\-\_]+/).nil?
end
```

## 疑难解答

以下是一些常见问题和一些建议的解决方案。 如果您遇到任何其他问题，可以在 {% data variables.product.prodname_support_forum_with_url %} 中寻求帮助或建议。

* **问：**我的应用程序没有将代码推送到 GitHub。 我没有看到 RuboCop 自动进行修复！

    **答：**确保您对“仓库内容”具有 **Read & write（读取和写入）**权限，并且使用安装令牌克隆仓库。 请参阅[步骤 2.2. 克隆仓库](#step-22-cloning-the-repository)了解详细信息。

* **问：**我在 `template_server.rb` 调试输出中看到与克隆仓库相关的错误。

    **答：**如果您看到以下错误，则说明您没有在 `initiate_check_run` 和/或 `take_requested_action` 方法中删除仓库的检出：

    ```shell
    2018-11-26 16:55:13 - Git::GitExecuteError - git  clone '--' 'https://x-access-token:ghs_9b2080277016f797074c4dEbD350745f4257@github.com/codertocat/octocat-breeds.git' 'Octocat-breeds'  2>&1:fatal: destination path 'Octocat-breeds' already exists and is not an empty directory.:
    ```

    将您的代码与 `server.rb` 文件进行比较，以确保您的 `initiate_check_run` 和 `take_requested_action` 方法中具有相同的代码。

* **问：**新的检查运行未显示在 GitHub 的“Checks（检查）”选项卡中。

    **答：**重新启动 Smee 并重新运行 `template_server.rb` 服务器。

* **问：**我在 GitHub 的“Checks（检查）”选项卡 中没有看到“Re-run all（全部重新运行）”按钮。

    **答：**重新启动 Smee 并重新运行 `template_server.rb` 服务器。

## 结论

完成本指南后，您已经学会了使用检查 API 创建 CI 服务器的基础知识！ 回顾一下：

* 配置您的服务器来接收检查 API 事件并创建检查运行。
* 使用 RuboCop 来检查仓库中的代码并为错误创建注释。
* 实现自动修复语法检查错误的请求操作。

## 后续步骤

以下是有关接下来可以做什么的一些想法：

* 目前，始终显示“Fix this（修复此问题）”按钮。 更新您编写的代码，仅在 RuboCop 发现错误时显示“Fix this（修复此问题）”按钮。
* 如果您不希望 RuboCop 将文件直接提交到头部分支，您可以更新代码，以使用基于头部分支的新分支[创建拉取请求](/rest/reference/pulls#create-a-pull-request)。
