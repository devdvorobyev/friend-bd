INSERT INTO users
values((select max(id)+1 from usersw),'urod','urod@yandex.ru','20','user','101')