---
title: GitHub Actions 快速入门
intro: '在 5 分钟或更短的时间内尝试 {% data variables.product.prodname_actions %} 的功能。'
allowTitleToDifferFromFilename: true
redirect_from:
  - /actions/getting-started-with-github-actions/starting-with-preconfigured-workflow-templates
versions:
  fpt: '*'
  ghes: '*'
  ghae: '*'
  ghec: '*'
type: quick_start
topics:
  - Fundamentals
shortTitle: 快速入门
---

{% data reusables.actions.enterprise-beta %}
{% data reusables.actions.enterprise-github-hosted-runners %}

## 简介

您只需要 {% data variables.product.prodname_dotcom %} 仓库来创建和运行 {% data variables.product.prodname_actions %} 工作流程。 在本指南中，您将添加一个工作流程，演示 {% data variables.product.prodname_actions %} 的一些基本功能。

下面的示例显示 {% data variables.product.prodname_actions %} 作业如何自动触发、在哪里运行及其如何与仓库中的代码交互。

## 创建第一个工作流程

1. 如果 `.github/workflows` 目录不存在，请在 {% data variables.product.prodname_dotcom %} 的仓库中创建此目录。
2. 在 `.github/workflow` 目录中，创建一个名为 `github-actions-demo.yml` 的文件。 更多信息请参阅“[创建新文件](/github/managing-files-in-a-repository/creating-new-files)”。
3. 将以下 YAML 内容复制到 `github-actions-demo.yml` 文件中：
    {% raw %}
    ```yaml{:copy}
    name: GitHub Actions Demo
    on: [push]
    jobs:
      Explore-GitHub-Actions:
        runs-on: ubuntu-latest
        steps:
          - run: echo "🎉 The job was automatically triggered by a ${{ github.event_name }} event."
          - run: echo "🐧 This job is now running on a ${{ runner.os }} server hosted by GitHub!"
          - run: echo "🔎 The name of your branch is ${{ github.ref }} and your repository is ${{ github.repository }}."
          - name: Check out repository code
            uses: actions/checkout@v2
          - run: echo "💡 The ${{ github.repository }} repository has been cloned to the runner."
          - run: echo "🖥️ The workflow is now ready to test your code on the runner."
          - name: List files in the repository
            run: |
              ls ${{ github.workspace }}
          - run: echo "🍏 This job's status is ${{ job.status }}."

    ```
    {% endraw %}
3. 滚动到页面底部，然后选择 **Create a new branch for this commit and start a pull request（为此提交创建一个新分支并开始拉取请求）**。 然后，若要创建拉取请求，请单击 **Propose new file（提议新文件）**。 ![提交工作流程文件](/assets/images/2021/10/help/repository/actions-quickstart-commit-new-file.png)

向仓库的分支提交工作流程文件会触发 `push` 事件并运行工作流程。

## 查看工作流程结果

{% data reusables.repositories.navigate-to-repo %}
{% data reusables.repositories.actions-tab %}
1. 在左侧边栏中，单击您想要查看的工作流程。

   ![左侧边栏中的工作流程列表](/assets/images/2021/10/help/repository/actions-quickstart-workflow-sidebar.png)
1. 从工作流程运行列表中，单击要查看的运行的名称。

   ![工作流程运行的名称](/assets/images/2021/10/help/repository/actions-quickstart-run-name.png)
1. 在 **Jobs（作业）**下，单击 **Explore-GitHub-Actions** 作业。

   ![查找作业](/assets/images/2021/10/help/repository/actions-quickstart-job.png)
1. 日志显示每个步骤的处理方式。 展开任何步骤以查看其细节。

   ![示例工作流程结果](/assets/images/2021/10/help/repository/actions-quickstart-logs.png)

   例如，您可以在仓库中看到文件列表： ![示例操作详细信息](/assets/images/2021/10/help/repository/actions-quickstart-log-detail.png)

## 更多入门工作流程

{% data reusables.actions.workflow-template-overview %}

## 后续步骤

每次将代码推送到分支时，您刚刚添加的示例工作流程都会运行，并显示 {% data variables.product.prodname_actions %} 如何处理仓库的内容。 但是，这只是您可以对 {% data variables.product.prodname_actions %} 执行操作的开始：

- 您的仓库可以包含多个基于不同事件触发不同任务的工作流程。
- 您可以使用工作流程安装软件测试应用程序，并让它们自动在 {% data variables.product.prodname_dotcom %} 的运行器上测试您的代码。

{% data variables.product.prodname_actions %} 可以帮助您自动执行应用程序开发过程的几乎每个方面。 准备好开始了吗？ 以下是一些帮助您对 {% data variables.product.prodname_actions %} 执行后续操作的有用资源：

- “[了解 {% data variables.product.prodname_actions %}](/actions/learn-github-actions)”，以获取深入教程
