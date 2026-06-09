---
title: リポジトリ内のディスカッションのカテゴリを管理する
intro: リポジトリ内のディスカッションを分類して、コミュニティメンバーの会話を整理したり、カテゴリごとに形式を選択したりすることができます。
permissions: Repository administrators and people with write or greater access to a repository can manage categories for discussions in the repository.
versions:
  fpt: '*'
  ghec: '*'
shortTitle: Manage categories
---


## ディスカッションのカテゴリについて

{% data reusables.discussions.about-discussions %} {% data reusables.discussions.about-categories-and-formats %}

{% data reusables.discussions.about-announcement-format %}

各カテゴリには一意の名前と絵文字の組み合わせが必要で、その目的を示す詳しい説明を付けることができます。 Categories help maintainers organize how conversations are filed and are customizable to help distinguish categories that are Q&A or more open-ended conversations. {% data reusables.discussions.repository-category-limit %}詳しい情報については、「[ディスカッションについて](/discussions/collaborating-with-your-community-using-discussions/about-discussions#about-categories-and-formats-for-discussions)」を参照してください。

## デフォルトのカテゴリ

| カテゴリ            | 目的                                        | Format          |
|:--------------- |:----------------------------------------- |:--------------- |
| 📣 Announcements | Updates and news from project maintainers | Announcement    |
| #️⃣ 全般          | プロジェクトに関連するすべての事柄                         | 自由回答形式のディスカッション |
| 💡 Ideas         | プロジェクトを変更または改善するためのアイデア                   | 自由回答形式のディスカッション |
| 🙏 Q&A           | コミュニティが回答する質問 (質問/回答形式)                   | 質問と回答           |
| 🙌 展示と説明         | プロジェクトに関連する作成物、実験、またはテスト                  | 自由回答形式のディスカッション |

## カテゴリを作成する

{% data reusables.repositories.navigate-to-repo %}
{% data reusables.discussions.discussions-tab %}
{% data reusables.discussions.edit-categories %}
1. [**New category**] をクリックします。 ![リポジトリのディスカッションカテゴリのリストの上にある [New category] ボタン](/assets/images/2021/10/help/discussions/click-new-category-button.png)
1. カテゴリの絵文字、タイトル、説明、ディスカッション形式を編集します。 ディスカッション形式の詳細については、「[ディスカッションについて](/discussions/collaborating-with-your-community-using-discussions/about-discussions#about-categories-and-formats-for-discussions)」を参照してください。 ![新しいカテゴリの絵文字、タイトル、説明、ディスカッション形式](/assets/images/2021/10/help/discussions/edit-category-details.png)
1. ** Create（作成）**をクリックしてください。 ![新しいカテゴリの [Create] ボタン](/assets/images/2021/10/help/discussions/new-category-click-create-button.png)

## カテゴリを編集する

カテゴリを編集して、カテゴリの絵文字、タイトル、説明、およびディスカッション形式を変更できます。

{% data reusables.repositories.navigate-to-repo %}
{% data reusables.discussions.discussions-tab %}
1. リストのカテゴリの右側にある {% octicon "pencil" aria-label="The pencil icon" %} をクリックします ![リポジトリのカテゴリリストのカテゴリの右側にある [Edit] ボタン](/assets/images/2021/10/help/discussions/click-edit-for-category.png)
1. {% data reusables.discussions.edit-category-details %}
![既存のカテゴリの絵文字、タイトル、説明、ディスカッション形式を編集する](/assets/images/2021/10/help/discussions/edit-existing-category-details.png)
1. [**Save changes**] をクリックします。 ![既存のカテゴリの [Save changes] ボタン](/assets/images/2021/10/help/discussions/existing-category-click-save-changes-button.png)

## カテゴリを削除する

カテゴリを削除すると、{% data variables.product.product_name %} は、削除されたカテゴリのすべてのディスカッションを、選択した既存のカテゴリに移動します。

{% data reusables.repositories.navigate-to-repo %}
{% data reusables.discussions.discussions-tab %}
1. リストのカテゴリの右側にある {% octicon "trash" aria-label="The trash icon" %} をクリックします ![リポジトリのカテゴリリストのカテゴリの右側にある [Trash] ボタン](/assets/images/2021/10/help/discussions/click-delete-for-category.png)
1. ドロップダウンメニューを使用して、削除するカテゴリのディスカッションの新しいカテゴリを選択します。 ![既存のカテゴリを削除するときに新しいカテゴリを選択するためのドロップダウンメニュー](/assets/images/2021/10/help/discussions/choose-new-category.png)
1. [**Delete & Move**] をクリックします。 ![既存のカテゴリを削除するときに新しいカテゴリを選択するためのドロップダウンメニュー](/assets/images/2021/10/help/discussions/click-delete-and-move-button.png)
