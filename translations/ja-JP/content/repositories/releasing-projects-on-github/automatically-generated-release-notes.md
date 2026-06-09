---
title: Automatically generated release notes
intro: You can automatically generate release notes for your GitHub releases
permissions: Repository collaborators and people with write access to a repository can generate and customize automated release notes for a release.
versions:
  fpt: '*'
  ghec: '*'
  ghes: '>3.3'
  ghae: issue-4974
topics:
  - Repositories
shortTitle: Automated release notes
communityRedirect:
  name: Provide GitHub Feedback
  href: 'https://github.com/github/feedback/discussions/categories/general-feedback'
---

## About automatically generated release notes

Automatically generated release notes provide an automated alternative to manually writing release notes for your {% data variables.product.prodname_dotcom %} releases. With automatically generated release notes, you can quickly generate an overview of the contents of a release. You can also customize your automated release notes, using labels to create custom categories to organize pull requests you want to include, and exclude certain labels and users from appearing in the output.

## Creating automatically generated release notes for a new release

{% data reusables.repositories.navigate-to-repo %}
{% data reusables.repositories.releases %}
3. [**Draft a new release**] をクリックします。 ![新しいリリースのドラフトを作成するボタン](/assets/images/2021/10/help/releases/draft_release_button.png)
4. {% ifversion fpt or ghec %}Click **Choose a tag** and type{% else %}Type{% endif %} a version number for your release. Alternatively, select an existing tag.
  {% ifversion fpt or ghec %}
  ![Enter a tag](/assets/images/2021/10/help/releases/releases-tag-create.png)
5. If you are creating a new tag, click **Create new tag**. ![Confirm you want to create a new tag](/assets/images/2021/10/help/releases/releases-tag-create-confirm.png)
  {% else %}
  ![タグ付きバージョンのリリース](/assets/images/2021/10/enterprise/releases/releases-tag-version.png)
{% endif %}
6. If you have created a new tag, use the drop-down menu to select the branch that contains the project you want to release.
  {% ifversion fpt or ghec %}![Choose a branch](/assets/images/2021/10/help/releases/releases-choose-branch.png)
  {% else %}![タグ付きブランチのリリース](/assets/images/2021/10/enterprise/releases/releases-tag-branch.png)
  {% endif %}
7. To the top right of the description text box, click **Auto-generate release notes**. ![Auto-generate release notes](/assets/images/2021/10/help/releases/auto-generate-release-notes.png)
8. Check the generated notes to ensure they include all (and only) the information you want to include.
9. オプションで、コンパイルされたプログラムなどのバイナリファイルをリリースに含めるには、ドラッグアンドドロップするかバイナリボックスで手動で選択します。 ![リリースに DMG ファイルを含める](/assets/images/2021/10/help/releases/releases_adding_binary.gif)
10. リリースが不安定であり、運用準備ができていないことをユーザに通知するには、[**This is a pre-release**] を選択します。 ![リリースをプレリリースとしてマークするチェックボックス](/assets/images/2021/10/help/releases/prerelease_checkbox.png)
{%- ifversion fpt %}
11. 必要に応じて、[**Create a discussion for this release**] を選択し、[**Category**] ドロップダウンメニューを選択してリリースディスカッションのカテゴリをクリックします。 ![リリースディスカッションを作成するためのチェックボックスと、カテゴリを選択するドロップダウンメニュー](/assets/images/2021/10/help/releases/create-release-discussion.png)
{%- endif %}
12. リリースを公開する準備ができている場合は、[**Publish release**] をクリックします。 リリースの作業を後でする場合は、[**Save draft**] をクリックします。 ![[Publish release] と [Save draft] ボタン](/assets/images/2021/10/help/releases/release_buttons.png)


## Configuring automatically generated release notes

{% data reusables.repositories.navigate-to-repo %}
{% data reusables.files.add-file %}
3. In the file name field, type `.github/release.yml` to create the `release.yml` file in the `.github` directory. ![Create new file](/assets/images/2021/10/help/releases/release-yml.png)
4. In the file, using the configuration options below, specify in YAML the pull request labels and authors you want to exclude from this release. You can also create new categories and list the pull request labels to be included in each of them.

### 設定オプション

| Parameter                                 | 説明                                                                                                                                                             |
|:----------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `changelog.exclude.labels`                | A list of labels that exclude a pull request from appearing in release notes.                                                                                  |
| `changelog.exclude.authors`               | A list of user or bot login handles whose pull requests are to be excluded from release notes.                                                                 |
| `changelog.categories[*].title`           | **Required.** The title of a category of changes in release notes.                                                                                             |
| `changelog.categories[*].labels`          | **Required.** Labels that qualify a pull request for this category. Use `*` as a catch-all for pull requests that didn't match any of the previous categories. |
| `changelog.categories[*].exclude.labels`  | A list of labels that exclude a pull request from appearing in this category.                                                                                  |
| `changelog.categories[*].exclude.authors` | A list of user or bot login handles whose pull requests are to be excluded from this category.                                                                 |

### 設定例

{% raw %}
```yaml{:copy}
# .github/release.yml

changelog:
  exclude:
    labels:
      - ignore-for-release
    authors:
      - octocat
  categories:
    - title: Breaking Changes 🛠
      labels:
        - Semver-Major
        - breaking-change
    - title: Exciting New Features 🎉
      labels:
        - Semver-Minor
        - enhancement
    - title: Other Changes
      labels:
        - "*"
```
{% endraw %}

## 参考リンク

- "[Managing labels](/issues/using-labels-and-milestones-to-track-work/managing-labels)" 
