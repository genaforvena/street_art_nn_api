drop table if exists art;
create table art (
  id integer primary key autoincrement,
  artist text not null,
  title text not null,
  year int not null,
  image text not null,
  address text not null,
  lng real not null,
  lat real not null
);
