---
title: Configurar tu ambiente de desarrollo para crear una GitHub App
intro: 'Aprende los fundamentos para extender y crear {% data variables.product.prodname_github_apps %} nuevas.'
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
shortTitle: Ambiente de desarrollo
---

## Introducción

Esta guía te mostrará los pasos necesarios para configurar una GitHub App y para ejecutarla en un servidor. Las GitHub Apps necesitan algunos pasos de configuración para administrar eventos de webhook y así conectar el registro de la App en GitHub hacia tu código. La app en esta guía sirve como una base que puedes utilizar para extender y crear GitHub Apps nuevas.

Al finalizar esta guía habrás registrado una GitHub App y habrás configurado un servidor web para recibir eventos de webhook. Aprenderás como utilizar una herramienta llamada Smee para capturar las cargas útiles de los webhooks y reenviarlas a tu ambiente de desarrollo local. La app de plantilla que configurarás en esta sección no hará nada especial aún, pero funcionará como un marco de trabajo que puedes utilizar para comenzar a escribir tu código de aplicaciones utilizando la API o para completar otras [guías de inicio rápido](/apps/quickstart-guides/). {% ifversion fpt or ghec %}Puedes revisar los ejemplos exitosos de estas aplicaciones en [GitHub Marketplace](https://github.com/marketplace) y en [Compatible con GitHub](https://github.com/works-with).{% endif %}

Después de completar este proyecto entenderás cómo autenticarte como una GitHub App y como una instalación, así como la forma en que difieren estos métodos de autenticación.

Aquí están los pasos que tomarás para configurar la plantilla de la GitHub App:

1. [Inicia un canal nuevo de Smee](#step-1-start-a-new-smee-channel)
1. [Registrar una GitHub App nueva](#step-2-register-a-new-github-app)
1. [Guarda tu llave privada e ID de tu App](#step-3-save-your-private-key-and-app-id)
1. [Prepara el ambiente de ejecución](#step-4-prepare-the-runtime-environment)
1. [Revisar el código de la plantilla de la GitHub App](#step-5-review-the-github-app-template-code)
1. [Inicia el servidor](#step-6-start-the-server)
1. [Instala la app en tu cuenta](#step-7-install-the-app-on-your-account)

{% data reusables.apps.app-ruby-guides %}

## Prerrequisitos

Puede que te sea útil tener un entendimiento básico de lo siguiente:

* [GitHub Apps](/apps/about-apps)
* [Webhooks](/webhooks)
* [El lenguaje de programación Ruby](https://www.ruby-lang.org/en/)
* [Las API de REST](/rest)
* [Sinatra](http://sinatrarb.com/)

Pero puedes seguir esta guía sin importar tu nivel de experiencia. ¡Colocaremos enlaces para la información que requieras en cada fase!

Antes de comenzar, necesitarás clonar el repositorio con el código de la plantilla que se utiliza en esta guía de inicio rápido. Abre tu app de terminal y encuentra el directorio en donde quieras almacenar el código. Ejecuta este comando para clonar el repositorio [Plantilla de GitHub App](https://github.com/github-developer/github-app-template):

```shell
$ git clone https://github.com/github-developer/github-app-template.git
```

## Paso 1. Inicia un canal nuevo de Smee

Para ayudar a que GitHub envíe webhooks a tu máquina local sin exponerla al internet, puedes utilizar una herramienta llamada Smee. Primero, dirígete a https://smee.io y da clic en **Iniciar un canal nuevo**. Si ya estás a gusto con otras herramientas que exponen tu máquina local al internet, como [`ngrok`](https://dashboard.ngrok.com/get-started) o [`localtunnel`](https://localtunnel.github.io/www/), puedes utilizarlas.

![El botón de nuevo canal de Smee](/assets/images/2021/10/smee-new-channel.png)

El iniciar un canal de Smee nuevo crea un dominio único en donde GitHub puede enviar cargas útiles de webhooks. Necesitas saber cuál es este dominio para continuar con el siguiente paso. Aquí hay un ejemplo de un dominio único en `https://smee.io/qrfeVRbFbffd6vD`:

![Un canal de Smee único](/assets/images/2021/10/smee-unique-domain.png)

Posteriormente, regresa a la terminal y sigue estos pasos para ejecutar el cliente de la interface de línea de comandos (CLI) de Smee:

{% note %}

**Nota:** Los siguientes pasos son ligeramente diferentes que las instrucciones de "Utilizar la CLI" que encuentras en la página de tu canal de Smee. **No** necesitas seguir las instrucciones de las secciones "Utilizar el cliente de Node.js" o de "Utilizar el soporte integrado de Probot".

{% endnote %}

1. Instalar el cliente:

    ```shell
    $ npm install --global smee-client
    ```

2. Ejecuta el cliente (reemplazando a `https://smee.io/qrfeVRbFbffd6vD` con tu propio dominio):

    ```shell
    $ smee --url https://smee.io/qrfeVRbFbffd6vD --path /event_handler --port 3000
    ```

    Deberías ver una salida como ésta:

    ```shell
    Forwarding https://smee.io/qrfeVRbFbffd6vD to http://127.0.0.1:3000/event_handler
    Connected https://smee.io/qrfeVRbFbffd6vD
    ```

El comando `smee --url <unique_channel>` le dice a Smee que reenvíe todos los eventos de webhook que reciba el canal de Smee al cliente de Smee que se ejecuta en tu computadora. La opción `--path /event_handler` reenvía los eventos a la ruta `/event_handler`, lo cual cubriremos en una [sección subsecuente](#step-5-review-the-github-app-template-code). La opción `--port 3000` especifica al puerto 3000, el cual es aquél que escuchará tu servidor. Si utilizas Smee, tu máquina no necesita estar abierta al internet público para recibir webhooks de GitHub. También puedes abrir la URL de Smee en tu buscador para inspeccionar las cargas útiles de los webhooks como vayan llegando.

Te recomendamos dejar abierta esta ventana de terminal y mantener a Smee conectado mientras completas el resto de los pasos de esta guía. Aunque _puedes_ desconectar y volver a conectar el cliente de Smee sin perder tu dominio único (a diferencia de con `ngrok`), puede que te sea más fácil dejarlo conectado y realizar otras tareas de línea de comandos en una ventana diferente de la Terminal.

## Paso 2. Registrar una GitHub App nueva

Si aún no tienes una cuenta de GitHub, ahora es un [buen momento para unirte](https://github.com/join). ¡No te olvides de verificar tu dirección de correo electrónico antes de continuar! Para registrar una app nueva, visita la [página de configuración de la app](https://github.com/settings/apps) en tu perfil de GitHub, y da clic en **GitHub App nueva**.

![El sitio web de Github, mostrando la **App Nueva**](/assets/images/2021/10/new-app.png)

Verás un formato en el cual puedes ingresar detalles sobre tu app. Consulta la sección "[Crear una GitHub App](/apps/building-github-apps/creating-a-github-app/)" para obtener información general acerca de los campos de esta página. Para los fines de esta guía, necesitaras ingresar datos específicos en unos cuantos campos:

{% note %}

**Nota:** Siempre puedes actualizar esta configuración más adelante para apuntar a un servidor hospedado.

{% endnote %}

* En "URL de la página principal", utiliza el dominio que emitió Smee. Por ejemplo:

    ![Formato completado con el dominio de Smee para la URL de una página principal](/assets/images/2021/10/homepage-url.png)

* Para la "URL del webhook", utiliza nuevamente el dominio que emitió Smee. Por ejemplo:

    ![Formato completado con el dominio de Smee para la URl de un webhook](/assets/images/2021/10/webhook-url.png)

* Para el "Secreto del webhook", crea una contraseña para asegurar las terminales de tu webhook. Este debería ser algo que solo tú (y GitHub, a través de este formulario) sepas. El secreto es importante, ya que estarás recibiendo cargas útiles desde el internet público, y utilizarás este secreto para verificar el remitente del webhook. Nota que la configuración de la GitHub App dice que el secreto de webhook es opcional, lo cual es verdad en la mayoría de los casos, pero para que funcione el código de la plantilla de la app, debes configurar un secreto de webhook.

    ![Formato completado con el secreto de un webhook](/assets/images/2021/10/webhook-secret.png)

* En la página de permisos & webhooks, puedes especificar un conjunto de permisos para tu app, los cuales determinan la cantidad de datos a los cuales tiene acceso la misma. Debajo de la sección de "Permisos del repositorio", desplázate hacia abajo hasta "Metadatos" y selecciona `Acceso: Solo lectura`. Si decides extender esta app de plantilla, puedes actualizar estos permisos más adelante.

* En la parte inferior de la página de permisos & webhooks, especifica si es una app privada o pública. Esto se refiere a quién puede instalarla: ¿solo tú, o alguien más en general? Por el momento, deja la app como privada seleccionando **Solo en esta cuenta**.

    ![Privacidad de GitHub App](/assets/images/2021/10/create_app.png)

¡Da clic en **Crear GitHub App** para crear tu app!

## Paso 3. Guarda tu llave privada e ID de tu App

Después de que creas tu app, se te llevará de regreso a la [página de configuración de la app](https://github.com/settings/apps). Tienes dos cosas más para hacer aquí:

* **Generar una llave privada para tu app.** Esto es necesario para autenticar tu app más adelante. Baja en la página y da clic en **Generar una llave privada**. Guarda el archivo `PEM` resultante ( el cual tiene un nombre similar a  _`app-name`_-_`date`_-`private-key.pem`) en un directorio en donde puedas volver a encontrarlo fácilmente.

    ![El diálogo de generación de la llave privada](/assets/images/2021/10/private_key.png)

* **Guardar la ID de app que GitHub le asignó a ésta.** Esto se necesita para preparar tu ambiente de ejecución.

    <img src="/assets/images/2021/10/app_id.png" alt="Tu número de ID para la app" width="200px" />

## Paso 4. Prepara el ambiente de ejecución

Para mantener tu información segura, te recomendamos poner todos los secretos relacionados con tu app en la memoria de tu ordenador en donde tu app pueda encontrarlos, en vez de ponerlos directamente en tu código. Esta útil herramienta de desarrollo llamada [dotenv](https://github.com/bkeepers/dotenv) carga las variables de ambiente específicas del proyecto desde un archivo `.env` hacia `ENV`. Jamás ingreses tu archivo `.env` en GitHub. Este es un archivo local que almacena la información sensible que no quieres sacar al internet público. El archivo `.env` ya se incluye en el archivo [`.gitignore`](/github/getting-started-with-github/ignoring-files/) del repositorio para prevenir esto.

El código de la plantilla que descargaste en la [Sección de pre-requisitos](#prerequisites) ya tiene un archivo de ejemplo llamado `.env-example`. Renombra el archivo de ejemplo de `.env-example` a `.env` o crea una copia del archivo `.env-example` llamada `.env`. No has instalado dotenv aún, pero lo instalarás más adelante en esta guía de inicio rápido cuando ejecutes `bundle install`. **Nota:** Las guías de inicio rápido que hagan referencia a los pasos en ésta guía podrían incluir variables de ambiente adicionales en el archivo `.env-example`. Referencia la guía de inicio rápido para el proyecto que clonaste en GitHub para obtener orientación para configurar estas variables de ambiente adicionales.

Necesitas agregar estas variables al archivo `.env`:

* _`GITHUB_PRIVATE_KEY`_: Agerga la llave privada que [generaste y guardaste anteriormente](#step-3-save-your-private-key-and-app-id). Abre el archivo `.pem` con un editor de texto o utiliza la línea de comandos para mostrar el contenido del archivo: `cat path/to/your/private-key.pem`. Copia todo el contenido del archivo como el valor de `GITHUB_PRIVATE_KEY` en tu archivo `.env`. **Nota:** Ya que el archivo PEM tiene más de una línea de código, necesitarás encerrar el valor entre comillas como en el siguiente ejemplo.
* _`GITHUB_APP_IDENTIFIER`_: Utiliza la ID de app que anotaste en la sección anterior.
* _`GITHUB_WEBHOOK_SECRET`_: Agrega tu secreto de webhook.

Aquí se muestra un ejemplo de archivo `.env`:

```
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
HkVN9...
...
-----END DSA PRIVATE KEY-----"
GITHUB_APP_IDENTIFIER=12345
GITHUB_WEBHOOK_SECRET=your webhook secret
```

## Paso 5. Revisar el código de la plantilla de la GitHub App

Éste contiene código que todas las GitHub Apps necesitarán. Esta sección te muestra el código que ya existe en la plantilla de la GitHub App. No hay algún paso que necesites completar en esta sección. Si ya estás familiarizado con el código de la plantilla, puedes adelantarte al "[Paso 6. Iniciar el servidor](#step-6-start-the-server)".

Abre el archivo `template_server.rb` en tu editor de texto favorito. Verás los comentarios a lo largo de este archivo, los cuales proporcionan contexto adicional para el código de la plantilla. Te recomendamos leer estos comentarios cuidadosamente, e incluso, agregar tus propios comentarios para complementar el código que escribas.

En la parte superior del archivo verás `set :port 3000`, lo cual configura el puerto que se utiliza cuando inicias el servidor web para empatar con el puerto al cual redirigiste tus cargas útiles de webhook en el "[Paso 1. Iniciar un canal nuevo de Smee](#step-1-start-a-new-smee-channel)".

El siguiente código que verás es la declaración `class GHApp < Sinatra::Application`. Escribirás todo el código de tu GitHub App dentro de esta clase.

Fuera de esta caja, la clase en la plantilla realiza lo siguiente:
* [Lee las variables de ambiente](#read-the-environment-variables)
* [Activa el inicio de sesión](#turn-on-logging)
* [Define un filtro del antes](#define-a-before-filter)
* [Define el gestor de ruta](#define-a-route-handler)
* [Define los métodos auxiliares](#define-the-helper-methods)

### Lee las variables de ambiente

Lo primero que hace esta clase es leer las tres variables de ambiente que configuraste en el [Paso 4. Preparar el ambiente de ejecución](#step-4-prepare-the-runtime-environment)" y almacenarlas en variables para utilizarlas más adelante:

``` ruby
# Expects that the private key in PEM format. Converts the newlines
PRIVATE_KEY = OpenSSL::PKey::RSA.new(ENV['GITHUB_PRIVATE_KEY'].gsub('\n', "\n"))

# Your registered app must have a secret set. The secret is used to verify
# that webhooks are sent by GitHub.
WEBHOOK_SECRET = ENV['GITHUB_WEBHOOK_SECRET']

# The GitHub App's identifier (type integer) set when registering an app.
APP_IDENTIFIER = ENV['GITHUB_APP_IDENTIFIER']
```

### Activa el inicio de sesión

Posteriormente, hay un bloqueo de código que habilita el inicio de sesión durante el desarrollo, el cual es el ambiente predeterminado en Sinatra. Este código activa el inicio de sesión a nivel de `DEBUG` para mostrar una salida útil en la terminal mientras desarrollas la app:

``` ruby
# Turn on Sinatra's verbose logging during development
configure :development do
  set :logging, Logger::DEBUG
end
```

### Define un filtro del antes

Sintatra utiliza [filtros de anterioridad](https://github.com/sinatra/sinatra#filters) que te permiten ejecutar el código antes del gestor de la ruta. El bloque `before` en la plantilla llama a cuatro [métodos auxiliares](https://github.com/sinatra/sinatra#helpers). La app de plantilla define estos métodos auxiliares en una [sección posterior](#define-the-helper-methods).

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

### Define el gestor de la ruta

Se incluye una ruta vacía en el código de la plantilla. Este código gestiona las solicitudes de tipo `POST` hacia la ruta `/event_handler`. No escribirás este gestor de evento en esta guía de inicio rápido, sino que verás las otras [guías de inicio rápido](/apps/quickstart-guides/) para encontrar ejemplos de como extender esta app de planitlla.

``` ruby
post '/event_handler' do

end
```

### Define los métodos auxiliares

Los métodos auxiliares en esta plantilla hacen la mayoria del trabajo pesado. Se definen cuatro métodos auxiliares en esta sección del código.

#### Gestionar la carga útil del webhok

El primer método `get_payload_request` captura la carga útil del webhook y la convierte en formato JSON, lo cual hace mucho más fácil el acceder a los datos de la misma.

#### Verificar la firma del webhook

El segundo método `verify_webhook_signature` lleva a cabo la verificación de la firma del webhook para garantizar que GitHub generó el evento. Para aprender más acerca del código en el método auxiliar `verify_webhook_signature`, consulta la sección "[Asegurar tus webhooks](/webhooks/securing/)". Si los webhooks son seguros, este método registrará todas las cárgas útiles en tu terminal. El código de registro es útil para verificar que tu servidor web esté trabajando, pero siempre lo puedes eliminar más adelante.

#### Autenticarse como una GitHub App

Para hacer llamadas a la API, estarás utilizando la [Biblioteca Octokit](http://octokit.github.io/octokit.rb/). Para que puedas hacer algo interesante con esta biblioteca necesitarás, o más bien, tu app necesitará autenticarse. GitHub Apps tiene dos métodos de autenticación:

- Autenticación como una GitHub App utilizando un [Token Web de JSON (JWT)](https://jwt.io/introduction).
- Autenticación como una instalación específica de una GitHub App utilizando un token de acceso de instalación.

Aprenderás cómo autenticarte como una instalación en la [siguiente sección](#authenticating-as-an-installation).

El [autenticarte como una GitHub App](/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-a-github-app) te permite hacer un par de cosas:

 * Puedes recuperar información administrativa de alto nivel sobre tu GitHub App.
 * Puedes solicitar tokens de acceso para una instalación de la app.

Por ejemplo, te podrías autenticar como una GitHub App para solicitar una lista de las cuentas (de organización y de persona) que han instalado tu app. Pero este método de autenticación no te permite hacer mucho con la API. Para acceder a los datos del repositorio y realizar operaciones en nombre de la instalación, necesitas autenticarte como una instalación. Para hacerlo, primero necesitarás autenticarte como una GitHub App para solicitar un token de acceso a la instalación.

Antes de que puedas utilizar la biblioteca Octokit.rb para hacer llamados a la API, necesitarás inicializar un [cliente de Octokit](http://octokit.github.io/octokit.rb/Octokit/Client.html) autenticado como una GitHub App. ¡El método auxiliar `authenticate_app` hace exactamente eso!

``` ruby
# Instantiate an Octokit client authenticated as a GitHub App.
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

El código anterior genera un [Token Web de JSON (JWT)](https://jwt.io/introduction) y lo utiliza (junto con la llave privada de tu app) para inicializar el cliente de Octokit. GitHub revisa la autenticación de una solicitud verificando el token con la llave pública almacenada en la app. Para aprender más acerca de cómo funciona este código, consulta la sección "[Autenticarte como una GitHub App](/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-a-github-app)".

#### Autenticarse como una instalación

Una _instalación_ se refiere a cualquier cuenta de usuario o de organización que tenga la app instalada. Aún si alguien instala la app en más de un repositorio, esto únicamente cuenta como una instalación, ya que toma lugar en la misma cuenta. El último método auxiliar `authenticate_installation` inicializa un [cliente de Octokit](http://octokit.github.io/octokit.rb/Octokit/Client.html) autenticado como una instalación. Este cliente de Octokit es lo que utilizarás para hacer llamadas autenticadas a la API.

``` ruby
# Instantiate an Octokit client authenticated as an installation of a
# GitHub App to run API operations.
def authenticate_installation(payload)
  installation_id = payload['installation']['id']
  installation_token = @app_client.create_app_installation_access_token(installation_id)[:token]
  @installation_client = Octokit::Client.new(bearer_token: installation_token)
end
```

El método de Octokit [`create_app_installation_access_token`](http://octokit.github.io/octokit.rb/Octokit/Client/Apps.html#create_app_installation_access_token-instance_method) crea un token de instalación. Este método acepta dos argumentos:

* Instalación (número entero): la ID de la instalación de una GitHub App
* Opciones (un hash, predeterminadamente es `{}`): un conjunto de opciones personalizables

En cualquier momento en el que una GitHub App reciba un webhook, este incluirá un objeto de `installation` con una `id`. Utilizando el cliente autenticado como una GitHub App, pasarás la ID del método `create_app_installation_access_token` para generar un token de acceso para cada instalación. Ya que no estás pasando ninguna opción al método, ésta será un hash vacío predeterminadamente. Si te refieres a [los documentos](/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-an-installation), podrás ver que la respuesta de `create_app_installation_access_token` incluye dos campos: `token` y `expired_at`. El código de la plantilla selecciona al token en la respuesta e inicializa un cliente de instalación.

Una vez teniendo listo este métido, cada vez que tu app reciba una nueva carga útil de un webhook, este creará un cliente para la instalación que activó dicho evento. Este proceso de autenticación habilita a tu GitHub App para que trabaje para todas las instalaciones en cualquier cuenta.

¡Ahora estás listo para comenzar a hacer llamadas a la API!

## Paso 6. Inicia el servidor

Tu app no _hace_ nada aún, pero en este punto, puedes ponerla a ejecutarse en el servidor.

Mantén a Smee ejecutándose en la pestaña actual dentro de tu terminal. Abre una nueva pestaña y muévete al directorio en donde [clonaste el código de la plantilla de la app](#prerequisites) con el comando `cd`. El código de Ruby en este repositorio iniciará un servidor web de [Sinatra](http://sinatrarb.com/). Este código tiene algunas cuantas dependencias. Puedes instalarlas si ejecutas:

```shell
$ gem install bundler
```

Seguido de:

```shell
$ bundle install
```

Con las dependencias instaladas, puedes iniciar el servidor:

```shell
$ ruby template_server.rb
```

Deberás ver una respuesta como:

```shell
> == Sinatra (v2.0.3) has taken the stage on 3000 for development with backup from Puma
> Puma starting in single mode...
> * Version 3.11.2 (ruby 2.4.0-p0), codename: Love Song
> * Min threads: 0, max threads: 16
> * Environment: development
> * Listening on tcp://localhost:3000
> Use Ctrl-C to stop
```

Si ves un error, asegúrate de haber creado el archivo `.env` en el directorio que contiene a `template_server.rb`.

Una vez que esté ejecutándose el servidor, puedes probarlo si vas a `http://localhost:3000` en tu buscador. Si la app funciona como se espera, verás una página de error útil:

<img src="/assets/images/2021/10/sinatra-404.png" alt="Página de error 404 de Sinatra" width="500px" />

¡Esto es bueno! Aunque es una página de error, es una página de error de _Sinatra_, lo cual significa que tu app está conectada con el servidor como lo esperabas. Estás viendo este mensaje porque no le has dado nada más que mostrar a la app.

## Paso 7. Instala la app en tu cuenta

Puedes probar que el servidor está escuchando a tu app si activas un evento para que lo reciba. Un evento simple con el que puedes hacer la prueba es instalar la app en tu cuenta de GitHub, la cual deberá enviar el evento [`installation`](/webhooks/event-payloads/#installation). Si la app lo recibe, deberás ver alguna salida en la pestaña de la terminal en donde iniciaste el `template_server.rb`.

Para instalar la app, visita la [página de configuración de la app](https://github.com/settings/apps), elige tu app, y da clic en **Instalar App** en la barra lateral. Junto a tu nombre de usuario, da clic en **Instalar**.

Se te solicitará si quieres instalar la app en todos los repositorios o solo en los seleccionados. Si no quieres instalar la app en _todos_ tus repositorios, ¡no pasa nada! Tal vez quieras crear un repositorio de entorno de pruebas para e instalar tu app ahí.

<img src="/assets/images/2021/10/install_permissions.png" alt="Permisos de instalación de la aplicación" width="500px" />

Después de que des clic en **Instalar**, revisa la salida en tu terminal. Deberías encontrar algo como esto:

```shell
> D, [2018-06-29T15:45:43.773077 #30488] DEBUG -- : ---- received event integration_installation
> D, [2018-06-29T15:45:43.773141 #30488] DEBUG -- : ----         action created
> 192.30.252.44 - - [29/Jun/2018:15:45:43 -0400] "POST / HTTP/2" 200 2 0.0067
> D, [2018-06-29T15:45:43.833016 #30488] DEBUG -- : ---- received event installation
> D, [2018-06-29T15:45:43.833062 #30488] DEBUG -- : ----         action created
> 192.30.252.39 - - [29/Jun/2018:15:45:43 -0400] "POST / HTTP/2" 200 2 0.0019
```

¡Estas son buenas noticias! Esto significa que tu app recibió una notificación de que se instaló en tu cuenta de GitHub. Si ves algo como esto, tu app está ejecutándose en el servidor como lo esperabas. 🙌

Si no ves la salida, asegúrate de que Smee se esté ejecutando correctamente en otra pestaña de la terminal. Si necesitas reiniciar Smee, nota que también necesitarás _desinstalar_ y _reinstalar_ la app para enviar el evento de `installation` a tu app nuevamente y así ver la salida en la terminal. Si el problema no es con Smee, consulta la sección de "[Solución de problemas](#troubleshooting)" para darte otras ideas al respecto.

Si te estás preguntando de dónde viene la salida de la terminal que ya mostramos, esto se encuentra escrito en el [código de la plantilla de la app](#prerequisites) dentro de `template_server.rb`.

## Solución de problemas

Aquí te presentamos algunos problemas comunes y sus soluciones sugeridas. Si te encuentras con cualquier otro problema, puedes pedir ayuda o consejos en el {% data variables.product.prodname_support_forum_with_url %}.

* **P:** Cuando trato de instalar el cliente de línea de comandos de Smee, me encuentro con el siguiente error:

    ```shell
    > npm: command not found
    ```

    **R:** Parece que no instalaste npm. La mejor forma de isntalarlo es descargar el paquete de Node.js en https://nodejs.org y seguir las instrucciones de instalación para tu sistema. Se instalará npm junto con Node.js.

* **P:** Cuando ejecuto el servidor me aparece el siguiente error:

    ```shell
    > server.rb:38:in `initialize': Neither PUB key nor PRIV key: header too long (OpenSSL::PKey::RSAError)
    ```

    **R:** Probablemente no configuraste bien la variable de ambiente de tu llave privada. Tu variable de `GITHUB_PRIVATE_KEY` se debe ver así:

    ```
    GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
    ...
    HkVN9...
    ...
    -----END RSA PRIVATE KEY-----"
    ```

    Revisa otra vez si copiaste la llave pública correcta en tu archivo `.env`.

* **P:** Cuando ejecuto el servidor, produce un fallo con este error:

    ```shell
    > Octokit::Unauthorized ... 401 - Bad credentials`
    ```

    **R:** Tal vez estés autenticado como una GitHub App pero no como una instalación. Asegúrate de seguir todos los pasos de la sección "[Autenticarte como una instalación](#authenticating-as-an-installation)", y utilizar la variable de instancia `@installation_client` (autenticado con un token de acceso de instalación) para las operaciones de tu API, y no así la variable de instancia `@app_client` (autenticado con un JWT). El `@app_client` solopuede recuperar información de alto nivel acerca de tu app y obtener tokens de acceso a la instalación. No puede más que esto en la API.

* **P:** ¡Mi servidor no está escuchando los eventos! El cliente de Smee está ejecutándose en una ventana de la terminal, y estoy instalando la app en un repositorio con GitHub, pero no veo ninguna salida en la ventana de la terminal en donde estoy ejecutando el servidor.

    **R:** Puede que no estés ejecutando el cliente de Smee, que estés ejecutando el comando de Smee con los parámetros incorrectos, o que no tengas el dominio correcto de Smee en tu configuración de la GitHub App. Primero revisa para asegurarte de que se esté ejecutando el cliente de Smee en la pestaña de la terminal. Si ese no es el problema, visita tu [página de configuración de la app](https://github.com/settings/apps) y revisa los campos que se muestran en el "[Paso 2. Registra una GitHub App nueva](#step-2-register-a-new-github-app)". Asegúrate que el dominio en esos campos empata con aquél que utilizaste en tu comando de `smee -u <unique_channel>` en el "[Paso 1. Iniciar un canal nuevo de Smee](#step-1-start-a-new-smee-channel)". Si ninguna de las anteriores funciona, verifica que estés utilizando el comando completo de Smee incluyendo las opciones `--path` and `--port`, por ejemplo: `smee --url https://smee.io/qrfeVRbFbffd6vD --path /event_handler --port 3000` (reemplazando `https://smee.io/qrfeVRbFbffd6vD` con tu propio dominio de Smee).

* **P:** Se me está mostrando un error 404 de `Octokit::NotFound` en mi salida de depuración:
    ```
    2018-12-06 15:00:56 - Octokit::NotFound - POST {% data variables.product.api_url_code %}/app/installations/500991/access_tokens: 404 - Not Found // See: /v3/apps/#create-a-new-installation-token:
    ```

    **R:** Asegúrate que las variables en tu archivo `.env` son correctas. Asegúrate de que no has configurado variables idénticas en otros archivos de variable del ambiente como `bash_profile`. Puedes revisar las variables de ambiente que utiliza tu app si agregas una declaración de `puts` en el código de tu app y vuelves a ejecutar el código. Por ejemplo, para garantizar que tienes el conjunto de llaves correcto, podrías agregar `puts PRIVATE_KEY` al código de tu app:

    ```
    PRIVATE_KEY = OpenSSL::PKey::RSA.new(ENV['GITHUB_PRIVATE_KEY'].gsub('\n', "\n"))
    puts PRIVATE_KEY
    ```

## Conclusión

Después de seguir esta guía, ¡habrás aprendido los fundamentos básicos para desarrollar GitHub Apps! Para revisar todo, debes:

* Registrar una GitHub App nueva
* Utilizar Smee para recibir cargas útiles de los webhooks
* Ejecutar un servidor web simple a través de Sinatra
* Autenticarte como una GitHub App
* Autenticarte como una instalación

## Pasos siguientes

Ahora tienes una GitHub App ejecutándose en un servidor. Aún no hace nada especial, pero revisa en las otras [Guías de inicio rápido](/apps/quickstart-guides/) las formas en las que puedes personalizar la plantilla de GitHub App.
