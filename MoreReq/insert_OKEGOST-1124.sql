INSERT INTO users
values((select max(id)+1 from users),'urod','urod@yandex.ru','20','user','101')