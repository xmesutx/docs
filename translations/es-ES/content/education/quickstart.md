---
title: Inicio rápido para GitHub Educators
intro: 'En cerca de 15 minutos, los maestros pueden iniciar con descuentos, capacitación y herramientas para {% data variables.product.company_short %}, posteriormente, pueden crear un aula para los alumnos en un curso de desarrollo de software utilizando {% data variables.product.prodname_classroom %}.'
allowTitleToDifferFromFilename: true
versions:
  fpt: '*'
shortTitle: Inicio Rápido
---

## Introducción

Los docentes que enseñan un curso de desarrollo de software pueden utilizar descuentos, alianzas, capacitación y herramientas de {% data variables.product.prodname_education %} para enseñar de forma efectiva las habilidades relevantes a los alumnos.

En esta guía, iniciarás con {% data variables.product.product_name %}, regístrate para las cuentas y servicios con descuento a través de {% data variables.product.prodname_education %} y crea un espacio para tu curso y tareas en {% data variables.product.prodname_classroom %}.

{% tip %}

**Tip**: Si eres un alumno y te gustaría sacar partido de un descuento académico, consulta la sección "[Postularse para un paquete de desarrollo para alumnos](/github/teaching-and-learning-with-github-education/applying-for-a-student-developer-pack)".

{% endtip %}

## Crear cuentas en {% data variables.product.product_name %}

Primero, necesitas crear una cuenta de usuario gratuita en {% data variables.product.product_name %}.

{% data reusables.accounts.create-account %}
1. Sigue las indicaciones para crear tu cuenta de usuario gratuita.

Después de que crees tu cuenta de usuario, crea una cuenta de organización gratuita. Utilizarás esta cuenta de organización para crear y administrar las aulas {% data variables.product.prodname_classroom %}.

{% data reusables.user-settings.access_settings %}
{% data reusables.user-settings.organizations %}
{% data reusables.organizations.new-organization %}
4. Sigue las indicaciones para crear una organización gratuita.

Para obtener más información, consulta la sección "[Tipos de cuentas de {% data variables.product.prodname_dotcom %}](/github/getting-started-with-github/types-of-github-accounts)".

## Postularse para un descuento de docente

A continuación, te registrarás para obtener descuentos en los servicios de {% data variables.product.company_short %}. {% data reusables.education.educator-requirements %}

{% tip %}

**Tip** Adicionalmente a los descuentos adicionales, {% data variables.product.company_short %} ofrece alianzas con las instituciones educativas mediante el {% data variables.product.prodname_campus_program %}. Para obtener más información, consulta el sitio web de [{% data variables.product.prodname_campus_program %}](https://education.github.com/schools).

{% endtip %}

{% data reusables.education.benefits-page %}
{% data reusables.education.click-get-teacher-benefits %}
{% data reusables.education.select-email-address %}
{% data reusables.education.upload-proof-status %}
{% data reusables.education.school-name %}
{% data reusables.education.plan-to-use-github %}
{% data reusables.education.submit-application %}

## Configura {% data variables.product.prodname_classroom %}

Con tu cuenta de usuario y cuenta de organización, ya estás listo para iniciar con {% data variables.product.prodname_classroom %}. {% data variables.product.prodname_classroom %} es de uso gratuito. Puedes rastrear y administrar las tareas, calificar los trabajos automáticamente y proporcionar retroalimentación a tus alumnos.

{% data reusables.classroom.sign-into-github-classroom %}
1. Para autorizar a {% data variables.product.prodname_classroom %} para que acceda a tu cuenta de usuario en {% data variables.product.prodname_dotcom %}, revisa la información y luego da clic en **Autorizar a {% data variables.product.prodname_classroom %}**. ![Botón de "Autorizar {% data variables.product.prodname_classroom %}" para una cuenta de usuario](/assets/images/2021/10/help/classroom/setup-click-authorize-github-classroom.png)
1. Revisa la información. Para autorizar a {% data variables.product.prodname_classroom %} para que acceda a tu cuenta de organización en {% data variables.product.prodname_dotcom %}, da clic en **Otorgar**. ![Botón de "Otorgar" para una organización](/assets/images/2021/10/help/classroom/setup-click-grant.png)

  {% tip %}

  **Tip**: si ves un botón de **Solicitar** en vez de uno de **Otorgar**, significa que eres un miembro de la organización y no un propietario. Un propietario deberá aprobar tu solicitud para {% data variables.product.prodname_classroom %}. Debes ser un propietario de la organización para crear y administrar las aulas y las tareas en {% data variables.product.prodname_classroom %}. Para obtener más información, consulta la sección "[Autorizar las Apps de OAuth](/github/authenticating-to-github/authorizing-oauth-apps#oauth-apps-and-organizations)".

  {% endtip %}

1. Da clic en **Autorizar github**. ![Clic en el botón "Autorizar" para una organización](/assets/images/2021/10/help/classroom/setup-click-authorize-github.png)

## Crea tu aula

{% data reusables.classroom.about-classrooms %}

{% data reusables.classroom.sign-into-github-classroom %}
1. Da clic en **Crear tu primer aula** o en **Aula nueva**.
{% data reusables.classroom.guide-create-new-classroom %}

## Pasos siguientes

¡Creaste un aula y estás listo para enriquecer tu curso con {% data variables.product.product_name %} y {% data variables.product.prodname_classroom %}!  🎉

- Mira algunos videos acerca de {% data variables.product.prodname_classroom %}. Para obtener más información, consulta la sección "[Puntos básicos para configurar {% data variables.product.prodname_classroom %}](/education/manage-coursework-with-github-classroom/basics-of-setting-up-github-classroom)".
- Administra tus aulas y administradores de aula y crea un registro de alumnos para aquellos que conforman tu aula. Para obtener más información, consulta la sección "[Administrar las aulas](/education/manage-coursework-with-github-classroom/manage-classrooms)".
- Utiliza la tarea de inicio de Git y {% data variables.product.company_short %} para proporcionar a los alumnos un resumen de lo básico de Git y {% data variables.product.product_name %}. Para obtener más información, consulta la sección "[Utilizar la tarea de inicio de Git y {% data variables.product.company_short %}](/education/manage-coursework-with-github-classroom/use-the-git-and-github-starter-assignment)".
- Crea una tarea para alumnos individuales o equipos. {% data reusables.classroom.for-more-information-about-assignment-creation %}
- Escribe e implementa pruebas automatizadas para proporcionar retroalimentación inmediata a los alumnos directamente en los repositorios de tareas. Para obtener más información, consulta la sección "[Utilizar calificaciones automáticas](/education/manage-coursework-with-github-classroom/use-autograding)".
- Participa en {% data variables.product.prodname_education_community_with_url %}.
