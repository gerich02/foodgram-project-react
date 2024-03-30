![badge](https://github.com/gerich02/foodgram-project-react/actions/workflows/main.yml/badge.svg)
#  Описание проекта "foodgram-project-react"

## Описание
Foodgram является социальной сетью для любителей поесть. Вы можете как узнать для себя что-то новое в мире гастрономических удовольствий, 
так и поделиться с миром своими кулинарными изысканиями.

Сервис доступен по адресу: (https://foodgram.servegame.com/)

**Инструменты и стек:** #Python #Django #Docker-compose #PostgreSQL #API #Nginx #Djoser #Gunicorn #Python-dotenv #JSON #YAML #VsCode #GitHub

## Запуск
Этот проект настроен на автоматическую проверку  тестами и деплой на удалённый Linux сервер, но для этого
необходима некоторая подготовка.

## Установка проекта

1. Клонируйте репозиторий:

    ```
    git clone git@github.com:gerich02/foodgram-project-react.git
    ```
2. Перейдите в папку с проектом:
    ```
    cd foodgram-project-react
    ```
2. Создайте файл .env и заполните его своими данными:
    ```bash
    POSTGRES_USER=user                      #Имя пользователя для подключения к базе данных PostgreSQL.
    POSTGRES_PASSWORD=password              #Пароль пользователя для подключения к базе данных PostgreSQL.
    POSTGRES_DB=django                      #Название базы данных PostgreSQL.
    DB_HOST=db                              #Хост базы данных.
    DB_PORT=5432                            #Порт для подключения к базе данных.
    SECRET_KEY='secret_key'                 #Секретный ключ приложения Django, используемый для шифрования данных и безопасности. 
    DEBUG='true'                            #Параметр, определяющий, включен ли режим отладки. Установка значения 'true' включает режим отладки.
    ALLOWED_HOSTS='localhost,127.0.0.1'     #писок доменных имен или IP-адресов, которым разрешено подключаться к приложению.
    TEST_DATABASE='sqlite'                  #Тип базы данных, используемой для тестирования. В данном случае используется 'sqlite'.
    ```


### Создание Docker-образов

1.  Замените username на ваш логин на DockerHub:

    ```
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```
2. Проверьте, что на вашем компьютере созданы необходимые образы, выполните команду: 
    ``` 
    docker image ls
    ``` 

5. Загрузите образы на DockerHub:

    ```
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```

### Деплой на сервере

1. Подключитесь к удалённому серверу:

    ```
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ```

2. Создайте на сервере директорию foodgram через терминал:

    ```
    mkdir foodgram
    ```


3. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env:

    ```
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
    * path_to_SSH — путь к файлу с SSH-ключом;
    * SSH_name — имя файла с SSH-ключом (без расширения);
    * username — ваше имя пользователя на сервере;
    * server_ip — IP вашего сервера.
    ```

4. Запустите docker compose в режиме демона:

    ```
    sudo docker compose -f docker-compose.production.yml up -d
    ```

5. Выполните миграции, сделайте импорт данных из файлов, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:

    ```
    docker compose -f docker-compose.yml exec backend python manage.py migrate
    docker compose -f docker-compose.yml exec backend python manage.py import_ingredient_csv
    docker compose -f docker-compose.yml exec backend python manage.py import_tags_csv
    docker compose -f docker-compose.yml exec backend python manage.py collectstatic
    docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static
    ```

6. На сервере в редакторе nano откройте конфиг Nginx:

    ```
    sudo nano /etc/nginx/sites-enabled/default
    ```

7. Измените настройки location в секции server:

    ```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:6000;
    }
    ```

8. Проверьте работоспособность конфига Nginx:

    ```bash
    sudo nginx -t
    ```

9.  Перезапустите Nginx
    ```bash
    sudo service nginx reload
    ```

### Настройка CI/CD

1. Файл workflow уже написан. Он находится в директории

    ```
    foodgram-project-react/.github/workflows/main.yml
    ```

2. Для адаптации его на сервере добавьте секреты в GitHub Actions:

    ```bash
    DOCKER_USERNAME                # логин пользователя в DockerHub
    DOCKER_PASSWORD                # пароль пользователя в DockerHub
    DOCKER_NICKNAME                # имя пользователя в DockerHub
    HOST                           # ip_address сервера
    USER                           # имя пользователя
    SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa)
    SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа

    TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
    TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
    ```


[Документация](https://foodgram.servegame.com/api/docs/)

## Об авторе
- [Варивода Георгий](https://github.com/gerich02)
