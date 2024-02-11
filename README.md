![badge](https://github.com/gerich02/foodgram-project-react/actions/workflows/main.yml/badge.svg)
#  Описание проекта "Kittygram final"

## Описание
Foodgram является социальной сетью для любителей поесть. Вы можете как узнать для себя что-то новое в мире гастрономических удовольствий, 
так и поделиться с миром своими кулинарными изысканиями.

**Инструменты и стек:** #Python #Django #Docker-compose #PostgreSQL #API #Nginx #Djoser #Gunicorn #Python-dotenv #JSON #YAML #VsCode #GitHub

## Запуск
Этот проект настроен на автоматическую проверку  тестами и деплой на удалённый Linux сервер, но для этого
необходима некоторая подготовка.

1. Подготовим переменные виртуального окружения в директории проекта на сервере создадим файл .env:
```bash
nano .env
```

2. Добавляем следующие переменные:
```nano
POSTGRES_DB=django
POSTGRES_USER=test_user
POSTGRES_PASSWORD=usersecretpassword
DB_HOST=db
DB_PORT=5432
SECRET_KEY='qolwvjicds5p53gvod1pyrz*%2uykjw&a^&c4moab!w=&16ou7'
DEBUG=... # True/False
ALLOWED_HOSTS=127.0.0.1,localhost
```
Данные выше указаны для примера.

3. Устанавливаем  Docker Compose на сервер:
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

4. В проекте foodgram есть несколько "секретных" переменных в файле main.yml, необходимых для автоматизации процесса, храниться они будут в "секретах" Вашего репозитория на гитхабе. Чтобы их объявить на GitHub в Вашем репозитории foodgram-project-react идём во вкладку __Settings__,выберите на панели слева __Secets and variables__/__Actions__, нажмите __New repository secret__.
Вам необходимо добавить такие переменные как:
- **DOCKER_USERNAME** = <Ваш логин на DockerHub>
- **DOCKER_PASSWORD** = <Ваш пароль на DockerHub>
- **DOCKER_NICKNAME** = <Ваш  ник на DockerHub>
- **HOST** = < ip Вашего сервера>
- **USER** = <имя пользователя>
- **SSH_KEY** = <закрытый SSH ключ>
- **SSH_PASSPHRASE** =  < passphrase для доступа к серверу>
- **TELEGRAM_TO** = < id Вашего телеграмм аккаунта>
- **TELEGRAM_TOKEN** = < token Вашего телеграмм бота>

Возможны различные варианты, в зависимости от типа вашего сервера и способа подключения.

5.  Обязательно вносим изменения во внешний файл конфигурации nginx на сервере:

    ```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:7000;
    }
    ```

6. Сохраняем все локальные изменения, и отправляем изменения в Ваш репозиторий на GitHub:
```bash
git add .
git commit -m 'Ваш коммит'
git push
```
7. Проверяем работу автоматизации через вкладку **Actions** Вашего репозитория foodgram-project-react


## Об авторе
Ученик курса "Python-разработчик" на платформе "Яндекс Практикум"
>[Gerich02](https://github.com/gerich02).
