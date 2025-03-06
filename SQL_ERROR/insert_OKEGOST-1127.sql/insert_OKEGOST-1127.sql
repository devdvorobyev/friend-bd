INSERT INTO users
values((select max(id)+1 from users21),'urod','urod@yandex.ru','20','user','101')